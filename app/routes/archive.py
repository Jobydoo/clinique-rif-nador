import json
from datetime import datetime
from flask import Blueprint, request, jsonify, session, Response
from app.models import db, Patient, Consultation, Invoice, Admission, MedicalDocument
from app.services.audit_service import log_audit

archive_bp = Blueprint('archive', __name__)

@archive_bp.route('', methods=['GET'])
def search_archives():
    """
    Moteur de recherche multicritères dans le coffre-fort des archives :
    Recherche par Nom, CIN, Type d'acte/entité, Médecin, Date.
    """
    search = request.args.get('search', '').strip()
    entity_type = request.args.get('entity_type', 'ALL') # PATIENT, CONSULTATION, INVOICE, ALL

    results = []

    # 1. Patients archivés
    if entity_type in ['ALL', 'PATIENT']:
        p_query = Patient.query.filter_by(is_archived=True)
        if search:
            s = f"%{search}%"
            p_query = p_query.filter(
                db.or_(
                    Patient.cin.ilike(s),
                    Patient.first_name_fr.ilike(s),
                    Patient.last_name_fr.ilike(s),
                    Patient.patient_number.ilike(s),
                    Patient.phone.ilike(s)
                )
            )
        for p in p_query.all():
            results.append({
                'entity_id': p.id,
                'entity_type': 'PATIENT',
                'title': f"Dossier Patient : {p.first_name_fr} {p.last_name_fr}",
                'cin': p.cin,
                'reference': p.patient_number,
                'archived_at': p.archived_at.strftime('%Y-%m-%d %H:%M') if p.archived_at else 'N/A',
                'reason': p.archived_reason or 'Clôture de dossier',
                'details': f"Mutuelle: {p.mutuelle_type} | Quartier: {p.neighborhood}",
                'can_restore': True
            })

    # 2. Consultations archivées
    if entity_type in ['ALL', 'CONSULTATION']:
        c_query = Consultation.query.filter_by(is_archived=True)
        if search:
            s = f"%{search}%"
            c_query = c_query.filter(
                db.or_(
                    Consultation.diagnosis.ilike(s),
                    Consultation.reason.ilike(s),
                    Consultation.cim10_code.ilike(s)
                )
            )
        for c in c_query.all():
            p = c.patient
            results.append({
                'entity_id': c.id,
                'entity_type': 'CONSULTATION',
                'title': f"Consultation : {c.diagnosis}",
                'cin': p.cin if p else 'N/A',
                'reference': f"CIM10: {c.cim10_code or 'N/A'}",
                'archived_at': c.archived_at.strftime('%Y-%m-%d %H:%M') if c.archived_at else 'N/A',
                'reason': 'Archivage consultation médicale',
                'details': f"Patient: {p.first_name_fr} {p.last_name_fr} | Praticien: {c.doctor.name if c.doctor else 'N/A'}",
                'can_restore': True
            })

    # 3. Factures archivées
    if entity_type in ['ALL', 'INVOICE']:
        i_query = Invoice.query.filter_by(is_archived=True)
        if search:
            s = f"%{search}%"
            i_query = i_query.filter(Invoice.invoice_number.ilike(s))
        for inv in i_query.all():
            p = inv.patient
            results.append({
                'entity_id': inv.id,
                'entity_type': 'INVOICE',
                'title': f"Facture {inv.invoice_number} ({inv.total_amount:.2f} MAD)",
                'cin': p.cin if p else 'N/A',
                'reference': inv.invoice_number,
                'archived_at': inv.archived_at.strftime('%Y-%m-%d %H:%M') if inv.archived_at else 'N/A',
                'reason': 'Exercice comptable clôturé',
                'details': f"Patient: {p.first_name_fr} {p.last_name_fr} | Organisme: {inv.mutuelle_type}",
                'can_restore': True
            })

    # Tri par date d'archivage décroissante
    results.sort(key=lambda x: x['archived_at'], reverse=True)
    return jsonify(results)

@archive_bp.route('/<entity_type>/<entity_id>/restore', methods=['POST'])
def restore_archived_item(entity_type, entity_id):
    """Restaure un élément depuis le coffre-fort vers la base de données active"""
    if entity_type == 'PATIENT':
        item = Patient.query.get_or_404(entity_id)
        item.is_archived = False
        item.archived_at = None
        item.archived_reason = None
        desc = f"Patient {item.first_name_fr} {item.last_name_fr}"
    elif entity_type == 'CONSULTATION':
        item = Consultation.query.get_or_404(entity_id)
        item.is_archived = False
        item.archived_at = None
        desc = f"Consultation {item.id}"
    elif entity_type == 'INVOICE':
        item = Invoice.query.get_or_404(entity_id)
        item.is_archived = False
        item.archived_at = None
        desc = f"Facture {item.invoice_number}"
    else:
        return jsonify({'error': 'Type d’entité invalide'}), 400

    db.session.commit()

    log_audit(
        action='RESTORE',
        entity_type=entity_type,
        details=f"Restauration réussie depuis le coffre-fort des archives : {desc}",
        entity_id=entity_id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Direction'),
        user_role=session.get('user_role', 'ADMIN')
    )

    return jsonify({'success': True, 'message': f'{desc} a été restauré avec succès dans le système actif'})

@archive_bp.route('/patients/<patient_id>/export', methods=['GET'])
def export_patient_dossier(patient_id):
    """
    Export complet du dossier patient (DME) : JSON structuré contenant l'identité,
    l'historique des constantes vitales, les consultations, les ordonnances,
    les factures et les documents enregistrés (Conformité CNDP portabilité des données).
    """
    patient = Patient.query.get_or_404(patient_id)
    full_data = patient.to_dict(include_relations=True)
    full_data['export_metadata'] = {
        'exported_at': datetime.utcnow().isoformat(),
        'exported_by': session.get('user_name', 'Direction'),
        'clinic_stamp': 'Clinique Médico-Chirurgicale du Rif - Nador',
        'cndp_law_morocco': 'Conforme Loi 09-08 relative à la protection des données à caractère personnel'
    }

    log_audit(
        action='EXPORT',
        entity_type='PATIENT',
        details=f"Export numérique complet du dossier patient de {patient.first_name_fr} {patient.last_name_fr} (CIN: {patient.cin})",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Direction'),
        user_role=session.get('user_role', 'ADMIN')
    )

    json_str = json.dumps(full_data, ensure_ascii=False, indent=2)
    return Response(
        json_str,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=Dossier_Medical_{patient.cin}_{patient.patient_number}.json'}
    )
