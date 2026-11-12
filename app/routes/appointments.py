import urllib.parse
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.models import db, Appointment, Patient, User
from app.services.audit_service import log_audit
from app.config import Config

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('', methods=['GET'])
def get_appointments():
    date_str = request.args.get('date')
    doctor_id = request.args.get('doctor_id', 'ALL')
    specialty = request.args.get('specialty', 'ALL')
    status = request.args.get('status', 'ALL')

    query = Appointment.query
    if date_str:
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(date=d)
        except Exception:
            pass

    if doctor_id != 'ALL':
        query = query.filter_by(doctor_id=doctor_id)

    if specialty != 'ALL':
        query = query.filter_by(specialty=specialty)

    if status != 'ALL':
        query = query.filter_by(status=status)

    appointments = query.order_by(Appointment.date.asc(), Appointment.time_slot.asc()).all()
    return jsonify([a.to_dict() for a in appointments])

@appointments_bp.route('', methods=['POST'])
def create_appointment():
    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    date_str = data.get('date')
    time_slot = data.get('time_slot')
    reason = data.get('reason', 'Consultation médicale')

    if not patient_id or not doctor_id or not date_str or not time_slot:
        return jsonify({'error': 'Patient, Médecin, Date et Heure sont obligatoires'}), 400

    patient = Patient.query.get_or_404(patient_id)
    doctor = User.query.get_or_404(doctor_id)

    app_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        doctor_name=doctor.name,
        specialty=doctor.specialty or 'Médecine Spécialisée',
        date=app_date,
        time_slot=time_slot,
        reason=reason,
        notes=data.get('notes'),
        status='SCHEDULED'
    )

    db.session.add(appointment)
    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='PATIENT',
        details=f"Planification RDV le {date_str} à {time_slot} avec {doctor.name} pour {patient.first_name_fr} {patient.last_name_fr}",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Accueil'),
        user_role=session.get('user_role', 'RECEPTIONIST')
    )

    return jsonify(appointment.to_dict()), 201

@appointments_bp.route('/<app_id>/status', methods=['PUT'])
def update_appointment_status(app_id):
    appointment = Appointment.query.get_or_404(app_id)
    data = request.get_json() or {}
    new_status = data.get('status')

    if not new_status:
        return jsonify({'error': 'Statut requis'}), 400

    appointment.status = new_status
    db.session.commit()

    return jsonify(appointment.to_dict())

@appointments_bp.route('/<app_id>/whatsapp', methods=['GET'])
def get_whatsapp_reminder(app_id):
    appointment = Appointment.query.get_or_404(app_id)
    patient = appointment.patient

    # Formatage du numéro marocain (+212)
    phone_clean = patient.phone.replace(' ', '').replace('-', '').replace('.', '')
    if phone_clean.startswith('0'):
        phone_intl = '212' + phone_clean[1:]
    elif phone_clean.startswith('+212'):
        phone_intl = phone_clean[1:]
    elif not phone_clean.startswith('212'):
        phone_intl = '212' + phone_clean
    else:
        phone_intl = phone_clean

    date_formatted = appointment.date.strftime('%d/%m/%Y')
    
    msg_fr = (
        f"Bonjour M./Mme *{patient.last_name_fr}*,\n\n"
        f"Nous vous confirmons votre rendez-vous à la *{Config.CLINIC_NAME}* (Nador) :\n\n"
        f"📅 Date : *{date_formatted}*\n"
        f"⏰ Heure : *{appointment.time_slot}*\n"
        f"👨‍⚕️ Praticien : *Dr. {appointment.doctor_name}* ({appointment.specialty})\n"
        f"📍 Lieu : {Config.CLINIC_ADDRESS}\n\n"
        f"En cas d'empêchement, merci de prévenir la clinique au {Config.CLINIC_PHONE}.\n\n"
        f"نتمنى لكم دوام الصحة والعافية بمصحة الريف بالناظور."
    )

    encoded_text = urllib.parse.quote(msg_fr)
    whatsapp_url = f"https://wa.me/{phone_intl}?text={encoded_text}"

    appointment.whatsapp_sent = True
    db.session.commit()

    return jsonify({
        'phone': phone_intl,
        'message': msg_fr,
        'whatsapp_url': whatsapp_url
    })
