from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.models import db, Room, Bed, Admission, Patient, User
from app.services.audit_service import log_audit

inpatient_bp = Blueprint('inpatient', __name__)

@inpatient_bp.route('/rooms', methods=['GET'])
def get_rooms():
    department = request.args.get('department', 'ALL')
    query = Room.query
    if department != 'ALL':
        query = query.filter_by(department=department)
    rooms = query.order_by(Room.floor.asc(), Room.room_number.asc()).all()
    return jsonify([r.to_dict() for r in rooms])

@inpatient_bp.route('/beds/<bed_id>/status', methods=['PUT'])
def update_bed_status(bed_id):
    bed = Bed.query.get_or_404(bed_id)
    data = request.get_json() or {}
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'Statut requis'}), 400

    bed.status = new_status
    if 'notes' in data:
        bed.notes = data['notes']
    db.session.commit()

    log_audit(
        action='UPDATE',
        entity_type='BED',
        details=f"Mise à jour état du lit {bed.bed_number} ({bed.room.room_number}) : {new_status}",
        entity_id=bed.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Personnel'),
        user_role=session.get('user_role', 'NURSE')
    )

    return jsonify(bed.to_dict())

@inpatient_bp.route('/admissions', methods=['GET'])
def get_admissions():
    status = request.args.get('status', 'ACTIVE')
    query = Admission.query
    if status != 'ALL':
        query = query.filter_by(status=status)
    admissions = query.order_by(Admission.admission_date.desc()).all()
    return jsonify([a.to_dict() for a in admissions])

@inpatient_bp.route('/admissions', methods=['POST'])
def admit_patient():
    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    bed_id = data.get('bed_id')
    reason = data.get('reason')
    doctor_id = data.get('doctor_id') or session.get('user_id')

    if not patient_id or not bed_id or not reason:
        return jsonify({'error': 'Patient, Lit et Motif d’hospitalisation sont obligatoires'}), 400

    patient = Patient.query.get_or_404(patient_id)
    bed = Bed.query.get_or_404(bed_id)

    if bed.status == 'OCCUPIED':
        return jsonify({'error': 'Ce lit est actuellement déjà occupé'}), 400

    if not doctor_id:
        doc = User.query.filter_by(role='DOCTOR').first()
        doctor_id = doc.id if doc else None

    admission = Admission(
        patient_id=patient_id,
        bed_id=bed_id,
        admitting_doctor_id=doctor_id,
        admission_date=datetime.utcnow(),
        reason=reason,
        surgical_acts=data.get('surgical_acts'),
        status='ACTIVE'
    )

    # Passer le lit en statut OCCUPIED
    bed.status = 'OCCUPIED'

    db.session.add(admission)
    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='BED',
        details=f"Admission et hospitalisation de {patient.first_name_fr} {patient.last_name_fr} dans {bed.room.room_number} - {bed.bed_number} (Motif: {reason})",
        entity_id=admission.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Médecin/Accueil'),
        user_role=session.get('user_role', 'DOCTOR')
    )

    return jsonify(admission.to_dict()), 201

@inpatient_bp.route('/admissions/<adm_id>/discharge', methods=['POST'])
def discharge_patient(adm_id):
    admission = Admission.query.get_or_404(adm_id)
    data = request.get_json() or {}
    summary = data.get('discharge_summary', 'Sortie autorisée par le médecin traitant.')

    admission.status = 'DISCHARGED'
    admission.discharge_date = datetime.utcnow()
    admission.discharge_summary = summary

    # Calcul du coût du séjour
    if admission.bed and admission.bed.room:
        days = max(1, (admission.discharge_date - admission.admission_date).days)
        admission.total_stay_cost = days * admission.bed.room.daily_rate

    # Passer le lit en nettoyage/désinfection
    if admission.bed:
        admission.bed.status = 'CLEANING'

    db.session.commit()

    log_audit(
        action='UPDATE',
        entity_type='BED',
        details=f"Clôture hospitalisation et sortie patient {admission.patient.first_name_fr} {admission.patient.last_name_fr} - Lit {admission.bed.bed_number} basculé en désinfection",
        entity_id=admission.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Soignants'),
        user_role=session.get('user_role', 'DOCTOR')
    )

    return jsonify(admission.to_dict())
