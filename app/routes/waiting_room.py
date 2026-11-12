from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.models import db, WaitingRoom, Patient
from app.services.audit_service import log_audit

waiting_room_bp = Blueprint('waiting_room', __name__)

@waiting_room_bp.route('', methods=['GET'])
def get_waiting_queue():
    status = request.args.get('status', 'ACTIVE')
    doctor_id = request.args.get('doctor_id', 'ALL')

    query = WaitingRoom.query
    if status == 'ACTIVE':
        query = query.filter(WaitingRoom.status != 'COMPLETED')
    elif status != 'ALL':
        query = query.filter_by(status=status)

    if doctor_id != 'ALL':
        query = query.filter_by(doctor_id=doctor_id)

    # Priorité URGENT en premier, puis date d'arrivée
    entries = query.order_by(
        db.case(
            (WaitingRoom.priority == 'URGENT', 1),
            (WaitingRoom.priority == 'PREGNANT', 2),
            (WaitingRoom.priority == 'ELDERLY', 3),
            else_=4
        ),
        WaitingRoom.arrival_time.asc()
    ).all()

    now = datetime.utcnow()
    result = []
    for idx, item in enumerate(entries):
        d = item.to_dict()
        # Calcul temps d'attente restant estimé (environ 15 min par patient en amont)
        d['estimated_remaining_minutes'] = max(0, idx * 15)
        result.append(d)

    return jsonify(result)

@waiting_room_bp.route('/enqueue', methods=['POST'])
def enqueue_patient():
    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    priority = data.get('priority', 'NORMAL')
    doctor_id = data.get('doctor_id')
    notes = data.get('notes')

    if not patient_id:
        return jsonify({'error': 'Patient requis'}), 400

    patient = Patient.query.get_or_404(patient_id)

    # Vérifier si déjà en attente active
    active = WaitingRoom.query.filter_by(patient_id=patient_id).filter(WaitingRoom.status != 'COMPLETED').first()
    if active:
        return jsonify({'error': f'Le patient {patient.first_name_fr} {patient.last_name_fr} est déjà en salle d’attente'}), 400

    entry = WaitingRoom(
        patient_id=patient_id,
        doctor_id=doctor_id,
        priority=priority,
        notes=notes,
        status='WAITING',
        arrival_time=datetime.utcnow()
    )

    db.session.add(entry)
    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='PATIENT',
        details=f"Admission en salle d'attente pour {patient.first_name_fr} {patient.last_name_fr} (Priorité: {priority})",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Accueil'),
        user_role=session.get('user_role', 'RECEPTIONIST')
    )

    return jsonify(entry.to_dict()), 201

@waiting_room_bp.route('/<entry_id>/status', methods=['PUT'])
def update_status(entry_id):
    entry = WaitingRoom.query.get_or_404(entry_id)
    data = request.get_json() or {}
    new_status = data.get('status')
    now = datetime.utcnow()

    if not new_status:
        return jsonify({'error': 'Statut requis'}), 400

    entry.status = new_status
    if new_status == 'TRIAGE':
        entry.triage_time = now
    elif new_status == 'IN_CONSULTATION':
        entry.consult_start_time = now
        if 'doctor_id' in data:
            entry.doctor_id = data['doctor_id']
    elif new_status == 'COMPLETED':
        entry.completed_time = now

    if 'notes' in data:
        entry.notes = data['notes']

    db.session.commit()

    log_audit(
        action='UPDATE',
        entity_type='PATIENT',
        details=f"File d'attente: Statut passé à {new_status} pour {entry.patient.first_name_fr} {entry.patient.last_name_fr}",
        entity_id=entry.patient_id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Personnel'),
        user_role=session.get('user_role', 'NURSE')
    )

    return jsonify(entry.to_dict())

@waiting_room_bp.route('/<entry_id>/call', methods=['POST'])
def call_patient(entry_id):
    entry = WaitingRoom.query.get_or_404(entry_id)
    data = request.get_json() or {}
    cabinet = data.get('cabinet', 'Cabinet de Consultation N° 1')

    patient = entry.patient
    name_fr = f"{patient.first_name_fr} {patient.last_name_fr}"
    name_ar = f"{patient.first_name_ar or patient.first_name_fr} {patient.last_name_ar or patient.last_name_fr}"

    call_data = {
        'patient_id': patient.id,
        'name_fr': name_fr,
        'name_ar': name_ar,
        'cabinet': cabinet,
        'called_at': datetime.utcnow().strftime('%H:%M:%S'),
        'chime': True,
        'announcement_fr': f"Le patient {name_fr} est prié de se présenter en {cabinet}",
        'announcement_ar': f"المريض(ة) {name_ar}، يرجى التوجه إلى {cabinet}"
    }

    log_audit(
        action='VIEW',
        entity_type='PATIENT',
        details=f"Appel du patient {name_fr} vers {cabinet}",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Soignants'),
        user_role=session.get('user_role', 'NURSE')
    )

    return jsonify({'success': True, 'call': call_data})
