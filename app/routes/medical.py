from datetime import datetime
from flask import Blueprint, request, jsonify, session, Response
from app.models import db, VitalSigns, Consultation, Prescription, PrescriptionItem, Patient, User, MedicalDocument
from app.services.audit_service import log_audit
from app.services.pdf_service import generate_prescription_pdf, generate_medical_certificate_pdf

medical_bp = Blueprint('medical', __name__)

def calculate_bmi(weight_kg, height_cm):
    if not weight_kg or not height_cm or height_cm <= 0:
        return None, None
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)
    
    if bmi < 18.5:
        status = "Insuffisance pondérale"
    elif bmi < 25.0:
        status = "Poids normal"
    elif bmi < 30.0:
        status = "Surpoids"
    elif bmi < 35.0:
        status = "Obésité modérée (Classe I)"
    else:
        status = "Obésité sévère (Classe II/III)"
        
    return bmi, status

# Liste des diagnostics fréquents CIM-10 au Maroc
CIM10_COMMON = [
    {"code": "I10", "description": "Hypertension artérielle essentielle (primitive)"},
    {"code": "E11.9", "description": "Diabète de type 2 sans complication"},
    {"code": "J00", "description": "Rhinopharyngite aiguë (rhume banal)"},
    {"code": "J20.9", "description": "Bronchite aiguë, sans précision"},
    {"code": "K29.7", "description": "Gastrite, sans précision"},
    {"code": "A09", "description": "Gastro-entérite et colite d'origine infectieuse"},
    {"code": "M54.5", "description": "Lombalgie commune"},
    {"code": "J45.9", "description": "Asthme, sans précision"},
    {"code": "N39.0", "description": "Infection des voies urinaires, siège non précisé"},
    {"code": "R10.4", "description": "Douleurs abdominales autres et non précisées"},
    {"code": "S93.4", "description": "Entorse et foulure de la cheville"},
    {"code": "K80.2", "description": "Calcul de la vésicule biliaire sans cholécystite"}
]

@medical_bp.route('/cim10', methods=['GET'])
def get_cim10():
    return jsonify(CIM10_COMMON)

# Constantes vitales
@medical_bp.route('/vitals', methods=['POST'])
def record_vitals():
    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    if not patient_id:
        return jsonify({'error': 'Patient requis'}), 400

    patient = Patient.query.get_or_404(patient_id)
    weight = float(data.get('weight')) if data.get('weight') else None
    height = float(data.get('height')) if data.get('height') else None

    bmi, bmi_status = calculate_bmi(weight, height)

    vitals = VitalSigns(
        patient_id=patient_id,
        recorded_by=data.get('recorded_by') or session.get('user_name', 'Infirmière Major'),
        systolic_bp=int(data.get('systolic_bp')) if data.get('systolic_bp') else None,
        diastolic_bp=int(data.get('diastolic_bp')) if data.get('diastolic_bp') else None,
        heart_rate=int(data.get('heart_rate')) if data.get('heart_rate') else None,
        temperature=float(data.get('temperature')) if data.get('temperature') else None,
        weight=weight,
        height=height,
        bmi=bmi,
        bmi_status=bmi_status,
        spo2=int(data.get('spo2')) if data.get('spo2') else None,
        blood_glucose=float(data.get('blood_glucose')) if data.get('blood_glucose') else None,
        pain_level=int(data.get('pain_level')) if data.get('pain_level') is not None else None,
        notes=data.get('notes')
    )

    db.session.add(vitals)
    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='PATIENT',
        details=f"Prise des constantes vitales pour {patient.first_name_fr} {patient.last_name_fr} (TA: {vitals.systolic_bp}/{vitals.diastolic_bp}, SpO2: {vitals.spo2}%, IMC: {vitals.bmi})",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Soignants'),
        user_role=session.get('user_role', 'NURSE')
    )

    return jsonify(vitals.to_dict()), 201

# Consultations
@medical_bp.route('/consultations', methods=['POST'])
def create_consultation():
    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id') or session.get('user_id')

    if not patient_id:
        return jsonify({'error': 'Patient requis'}), 400

    patient = Patient.query.get_or_404(patient_id)
    
    if not doctor_id:
        doc = User.query.filter_by(role='DOCTOR').first()
        doctor_id = doc.id if doc else None

    consultation = Consultation(
        patient_id=patient_id,
        doctor_id=doctor_id,
        reason=data.get('reason', 'Consultation générale'),
        symptoms=data.get('symptoms'),
        examination=data.get('examination'),
        cim10_code=data.get('cim10_code'),
        cim10_description=data.get('cim10_description'),
        diagnosis=data.get('diagnosis', 'Examen clinique standard'),
        clinical_notes=data.get('clinical_notes'),
        fee_amount=float(data.get('fee_amount', 250.0)),
        is_archived=False
    )

    db.session.add(consultation)
    db.session.flush() # Pour avoir l'ID

    # Si des médicaments sont prescrits directement
    medications = data.get('medications', [])
    if medications:
        prescription = Prescription(
            consultation_id=consultation.id,
            patient_id=patient.id,
            doctor_id=doctor_id,
            date=datetime.utcnow(),
            qr_code_data=f"CNR-PRES-{consultation.id}",
            instructions=data.get('prescription_instructions')
        )
        db.session.add(prescription)
        db.session.flush()

        for med in medications:
            item = PrescriptionItem(
                prescription_id=prescription.id,
                medication_name=med.get('name', 'Médicament'),
                dosage=med.get('dosage', '1 prise'),
                frequency=med.get('frequency', '2 fois par jour'),
                duration=med.get('duration', '5 jours'),
                precautions=med.get('precautions'),
                allow_substitution=med.get('allow_substitution', True)
            )
            db.session.add(item)

    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='CONSULTATION',
        details=f"Création consultation médicale pour {patient.first_name_fr} {patient.last_name_fr} - Diagnostic: {consultation.diagnosis}",
        entity_id=consultation.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Médecin'),
        user_role=session.get('user_role', 'DOCTOR')
    )

    return jsonify(consultation.to_dict(include_items=True)), 201

# Téléchargement Ordonnance PDF
@medical_bp.route('/prescriptions/<prescription_id>/pdf', methods=['GET'])
def get_prescription_pdf(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    patient = Patient.query.get(prescription.patient_id)
    doctor = User.query.get(prescription.doctor_id) or User.query.filter_by(role='DOCTOR').first()

    pdf_bytes = generate_prescription_pdf(prescription, patient, doctor)
    
    log_audit(
        action='EXPORT',
        entity_type='PRESCRIPTION',
        details=f"Impression / Export PDF de l'ordonnance de {patient.first_name_fr} {patient.last_name_fr}",
        entity_id=prescription.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Praticien'),
        user_role=session.get('user_role', 'DOCTOR')
    )

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'inline; filename=Ordonnance_{patient.cin}_{prescription.id[:8]}.pdf'}
    )

# Génération Certificat Médical PDF
@medical_bp.route('/certificates/pdf', methods=['POST'])
def generate_cert_pdf():
    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    days_rest = int(data.get('days_rest', 3))
    notes = data.get('notes', '')

    patient = Patient.query.get_or_404(patient_id)
    doctor_id = session.get('user_id')
    doctor = User.query.get(doctor_id) if doctor_id else User.query.filter_by(role='DOCTOR').first()

    pdf_bytes = generate_medical_certificate_pdf(patient, doctor, 'REPOS', days_rest, notes)

    log_audit(
        action='EXPORT',
        entity_type='PATIENT',
        details=f"Génération certificat médical d'arrêt de travail ({days_rest} jours) pour {patient.first_name_fr} {patient.last_name_fr}",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Médecin'),
        user_role=session.get('user_role', 'DOCTOR')
    )

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'inline; filename=Certificat_{patient.cin}.pdf'}
    )
