from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.models import db, User, StaffShift, Consultation, Admission
from app.services.audit_service import log_audit

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('', methods=['GET'])
def get_staff():
    role = request.args.get('role', 'ALL')
    query = User.query.filter_by(is_active=True)
    if role != 'ALL':
        query = query.filter_by(role=role)
    users = query.order_by(User.role.asc(), User.name.asc()).all()
    return jsonify([u.to_dict() for u in users])

@staff_bp.route('/fees-calculator', methods=['GET'])
def calculate_doctor_fees():
    """
    Calcul automatique des honoraires et rétrocessions des médecins selon le barème clinique de Nador.
    Chaque consultation ou acte génère la part médecin (ex: 70%) et la part clinique (ex: 30%).
    """
    doctors = User.query.filter(User.role.in_(['DOCTOR', 'ADMIN'])).all()
    report = []

    for doc in doctors:
        consultations = Consultation.query.filter_by(doctor_id=doc.id).all()
        admissions = Admission.query.filter_by(admitting_doctor_id=doc.id).all()

        total_consult_ca = sum(c.fee_amount for c in consultations)
        total_acts_ca = sum(a.total_stay_cost for a in admissions)
        grand_total_ca = total_consult_ca + total_acts_ca

        rate = doc.fee_rate or 70.0 # Par défaut 70% pour le médecin
        doctor_share = round(grand_total_ca * (rate / 100.0), 2)
        clinic_share = round(grand_total_ca - doctor_share, 2)

        report.append({
            'doctor_id': doc.id,
            'doctor_name': doc.name,
            'specialty': doc.specialty,
            'doctor_type': doc.doctor_type or 'PERMANENT',
            'fee_rate': rate,
            'consultations_count': len(consultations),
            'admissions_count': len(admissions),
            'total_consult_ca': total_consult_ca,
            'total_acts_ca': total_acts_ca,
            'grand_total_ca': grand_total_ca,
            'doctor_share': doctor_share,
            'clinic_share': clinic_share
        })

    return jsonify(report)

@staff_bp.route('/shifts', methods=['GET'])
def get_shifts():
    shifts = StaffShift.query.order_by(StaffShift.shift_date.asc()).all()
    return jsonify([s.to_dict() for s in shifts])

@staff_bp.route('/shifts', methods=['POST'])
def add_shift():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    shift_date_str = data.get('shift_date')
    shift_type = data.get('shift_type', 'GARDE_NUIT')
    notes = data.get('notes')

    if not user_id or not shift_date_str:
        return jsonify({'error': 'Professionnel de santé et Date requis'}), 400

    shift_date = datetime.strptime(shift_date_str, '%Y-%m-%d').date()
    shift = StaffShift(
        user_id=user_id,
        shift_date=shift_date,
        shift_type=shift_type,
        notes=notes,
        status='SCHEDULED'
    )

    db.session.add(shift)
    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='SYSTEM',
        details=f"Planification garde/astreinte ({shift_type}) pour {shift.user.name} le {shift_date_str}",
        entity_id=shift.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Direction RH'),
        user_role=session.get('user_role', 'ADMIN')
    )

    return jsonify(shift.to_dict()), 201
