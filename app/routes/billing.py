from datetime import datetime
from flask import Blueprint, request, jsonify, session, Response
from app.models import db, Invoice, InvoiceItem, Payment, DailyCashClosure, Patient
from app.services.audit_service import log_audit
from app.services.pdf_service import generate_invoice_pdf

billing_bp = Blueprint('billing', __name__)

# Catalogue officiel de la nomenclature des actes médicaux au Maroc (Tarifs en MAD)
ACTS_CATALOG = [
    {"code": "CS", "description": "Consultation Médecin Spécialiste", "unit_price": 250.0, "category": "Consultation"},
    {"code": "C", "description": "Consultation Médecine Générale", "unit_price": 150.0, "category": "Consultation"},
    {"code": "URG", "description": "Consultation d'Urgence Nuit / Férié", "unit_price": 300.0, "category": "Urgences"},
    {"code": "ECG", "description": "Électrocardiogramme de repos (ECG)", "unit_price": 180.0, "category": "Cardiologie"},
    {"code": "ECHO-ABD", "description": "Échographie Abdomino-pelvienne", "unit_price": 400.0, "category": "Imagerie"},
    {"code": "RX-THORAX", "description": "Radiographie Pulmonaire Thoracique", "unit_price": 200.0, "category": "Imagerie"},
    {"code": "BIO-STD", "description": "Bilan Biologique Standard (NFS + Glycémie + Urée/Créat)", "unit_price": 350.0, "category": "Laboratoire"},
    {"code": "BIO-COMPL", "description": "Bilan Métabolique Complet + Bilan Lipidique", "unit_price": 550.0, "category": "Laboratoire"},
    {"code": "SEJOUR-INDIV", "description": "Séjour Hospitalisation Chambre Individuelle (par jour)", "unit_price": 600.0, "category": "Hospitalisation"},
    {"code": "SEJOUR-USI", "description": "Journée Soins Intensifs / Réanimation (USI)", "unit_price": 1800.0, "category": "Hospitalisation"},
    {"code": "BLOC-CHIR-1", "description": "Acte Chirurgical Majeur Bloc Opératoire", "unit_price": 4500.0, "category": "Chirurgie"},
    {"code": "PANSEMENT-AMI", "description": "Pansement complexe et soins infirmiers à domicile/clinique", "unit_price": 100.0, "category": "Soins Infirmiers"}
]

def generate_invoice_number():
    year = datetime.utcnow().year
    count = Invoice.query.count()
    return f"FACT-{year}-{str(count + 1).zfill(4)}"

def generate_receipt_number():
    year = datetime.utcnow().year
    count = Payment.query.count()
    return f"REC-{year}-{str(count + 1).zfill(4)}"

@billing_bp.route('/acts-catalog', methods=['GET'])
def get_acts_catalog():
    return jsonify(ACTS_CATALOG)

@billing_bp.route('/invoices', methods=['GET'])
def get_invoices():
    status = request.args.get('status', 'ALL')
    patient_id = request.args.get('patient_id')

    query = Invoice.query
    if status != 'ALL':
        query = query.filter_by(status=status)
    if patient_id:
        query = query.filter_by(patient_id=patient_id)

    invoices = query.order_by(Invoice.date.desc()).all()
    return jsonify([inv.to_dict() for inv in invoices])

@billing_bp.route('/invoices', methods=['POST'])
def create_invoice():
    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    items = data.get('items', [])
    payment_method = data.get('payment_method', 'CASH')
    consultation_id = data.get('consultation_id')
    admission_id = data.get('admission_id')

    if not patient_id or not items:
        return jsonify({'error': 'Patient et au moins un acte médical sont obligatoires'}), 400

    patient = Patient.query.get_or_404(patient_id)

    # Calcul du total brut
    total_amount = sum(float(item.get('unit_price', 0)) * int(item.get('quantity', 1)) for item in items)

    # Calcul Tiers-payant vs Part patient selon mutuelle marocaine
    mutuelle_rate = patient.mutuelle_rate or 0.0
    mutuelle_type = patient.mutuelle_type or 'PRIVE'

    if mutuelle_type != 'PRIVE' and mutuelle_rate > 0:
        mutuelle_amount = round(total_amount * (mutuelle_rate / 100.0), 2)
        patient_share = round(total_amount - mutuelle_amount, 2)
    else:
        mutuelle_amount = 0.0
        patient_share = total_amount

    invoice = Invoice(
        invoice_number=generate_invoice_number(),
        patient_id=patient_id,
        consultation_id=consultation_id,
        admission_id=admission_id,
        date=datetime.utcnow(),
        status='PAID' if data.get('is_paid', True) else 'PENDING',
        total_amount=total_amount,
        mutuelle_amount=mutuelle_amount,
        patient_share=patient_share,
        mutuelle_type=mutuelle_type,
        payment_method=payment_method,
        notes=data.get('notes'),
        is_archived=False
    )

    db.session.add(invoice)
    db.session.flush()

    for item in items:
        inv_item = InvoiceItem(
            invoice_id=invoice.id,
            act_code=item.get('act_code', 'CS'),
            description=item.get('description', 'Prestation médicale'),
            quantity=int(item.get('quantity', 1)),
            unit_price=float(item.get('unit_price', 0)),
            total=float(item.get('unit_price', 0)) * int(item.get('quantity', 1))
        )
        db.session.add(inv_item)

    # Si payé immédiatement, enregistrer le reçu de paiement
    if invoice.status == 'PAID':
        payment = Payment(
            invoice_id=invoice.id,
            amount=patient_share,
            payment_method=payment_method,
            payment_date=datetime.utcnow(),
            recorded_by=session.get('user_name', 'Secrétariat Caisse'),
            receipt_number=generate_receipt_number(),
            notes=f"Règlement part patient pour facture {invoice.invoice_number}"
        )
        db.session.add(payment)

    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='INVOICE',
        details=f"Émission facture {invoice.invoice_number} pour {patient.first_name_fr} {patient.last_name_fr} - Total: {invoice.total_amount} MAD (Mutuelle {mutuelle_type}: {invoice.mutuelle_amount} MAD, Patient: {invoice.patient_share} MAD)",
        entity_id=invoice.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Secrétariat Caisse'),
        user_role=session.get('user_role', 'RECEPTIONIST')
    )

    return jsonify(invoice.to_dict()), 201

@billing_bp.route('/invoices/<invoice_id>/pdf', methods=['GET'])
def get_invoice_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    patient = invoice.patient

    pdf_bytes = generate_invoice_pdf(invoice, patient)

    log_audit(
        action='EXPORT',
        entity_type='INVOICE',
        details=f"Téléchargement / Impression facture officielle {invoice.invoice_number} pour {patient.first_name_fr} {patient.last_name_fr}",
        entity_id=invoice.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Caisse'),
        user_role=session.get('user_role', 'RECEPTIONIST')
    )

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'inline; filename=Facture_{invoice.invoice_number}.pdf'}
    )

# Clôture journalière de caisse
@billing_bp.route('/cash-closures', methods=['GET'])
def get_cash_closures():
    closures = DailyCashClosure.query.order_by(DailyCashClosure.date.desc()).all()
    return jsonify([c.to_dict() for c in closures])

@billing_bp.route('/cash-closures', methods=['POST'])
def create_cash_closure():
    data = request.get_json() or {}
    opening_amount = float(data.get('opening_amount', 1000.0))
    actual_cash = float(data.get('actual_cash', 0.0))
    notes = data.get('notes', '')

    today = datetime.utcnow().date()
    # Calculer automatiquement les paiements de la journée
    today_payments = Payment.query.filter(
        db.func.date(Payment.payment_date) == today
    ).all()

    cash_collected = sum(p.amount for p in today_payments if p.payment_method == 'CASH')
    card_collected = sum(p.amount for p in today_payments if p.payment_method == 'CARD')
    check_collected = sum(p.amount for p in today_payments if p.payment_method in ['CHECK', 'TRANSFER'])
    total_collected = cash_collected + card_collected + check_collected

    expected_cash = opening_amount + cash_collected
    discrepancy = actual_cash - expected_cash

    closure = DailyCashClosure(
        date=today,
        closed_by=session.get('user_name', 'Secrétariat Caisse'),
        opening_amount=opening_amount,
        cash_collected=cash_collected,
        card_collected=card_collected,
        check_collected=check_collected,
        total_collected=total_collected,
        expected_cash=expected_cash,
        actual_cash=actual_cash,
        discrepancy=discrepancy,
        status='CLOSED',
        notes=notes
    )

    db.session.add(closure)
    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='INVOICE',
        details=f"Clôture journalière de caisse du {today.strftime('%d/%m/%Y')} - Total encaissé: {total_collected:.2f} MAD (Espèces: {cash_collected:.2f}, Écart: {discrepancy:.2f} MAD)",
        entity_id=closure.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Caisse'),
        user_role=session.get('user_role', 'RECEPTIONIST')
    )

    return jsonify(closure.to_dict()), 201
