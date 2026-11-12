from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.models import db, Patient
from app.services.audit_service import log_audit

patients_bp = Blueprint('patients', __name__)

def generate_patient_number():
    year = datetime.utcnow().year
    count = Patient.query.count()
    return f"CNR-{year}-{str(count + 1).zfill(4)}"

@patients_bp.route('', methods=['GET'])
def get_patients():
    search = request.args.get('search', '').strip()
    mutuelle = request.args.get('mutuelle', 'ALL')
    neighborhood = request.args.get('neighborhood', 'ALL')
    include_archived = request.args.get('include_archived', 'false').lower() == 'true'

    query = Patient.query
    if not include_archived:
        query = query.filter_by(is_archived=False)

    if mutuelle != 'ALL':
        query = query.filter_by(mutuelle_type=mutuelle)

    if neighborhood != 'ALL':
        query = query.filter_by(neighborhood=neighborhood)

    if search:
        s = f"%{search}%"
        query = query.filter(
            db.or_(
                Patient.cin.ilike(s),
                Patient.first_name_fr.ilike(s),
                Patient.last_name_fr.ilike(s),
                Patient.first_name_ar.ilike(s),
                Patient.last_name_ar.ilike(s),
                Patient.phone.ilike(s),
                Patient.patient_number.ilike(s)
            )
        )

    patients = query.order_by(Patient.created_at.desc()).all()
    return jsonify([p.to_dict() for p in patients])

@patients_bp.route('/<patient_id>', methods=['GET'])
def get_patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Audit Log CNDP
    log_audit(
        action='VIEW',
        entity_type='PATIENT',
        details=f"Consultation dossier médical du patient {patient.first_name_fr} {patient.last_name_fr} (CIN: {patient.cin})",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Praticien'),
        user_role=session.get('user_role', 'DOCTOR')
    )

    return jsonify(patient.to_dict(include_relations=True))

@patients_bp.route('', methods=['POST'])
def create_patient():
    data = request.get_json() or {}
    cin = data.get('cin', '').strip().upper()
    first_name_fr = data.get('first_name_fr', '').strip()
    last_name_fr = data.get('last_name_fr', '').strip()
    phone = data.get('phone', '').strip()

    if not cin or not first_name_fr or not last_name_fr or not phone:
        return jsonify({'error': 'CIN, Nom, Prénom et Téléphone sont obligatoires'}), 400

    existing = Patient.query.filter_by(cin=cin).first()
    if existing:
        return jsonify({'error': f'Un patient existe déjà avec la CIN {cin} ({existing.first_name_fr} {existing.last_name_fr})'}), 400

    birth_date_str = data.get('birth_date')
    try:
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else datetime.strptime('1990-01-01', '%Y-%m-%d').date()
    except Exception:
        birth_date = datetime.strptime('1990-01-01', '%Y-%m-%d').date()

    patient = Patient(
        patient_number=generate_patient_number(),
        cin=cin,
        first_name_fr=first_name_fr,
        last_name_fr=last_name_fr,
        first_name_ar=data.get('first_name_ar'),
        last_name_ar=data.get('last_name_ar'),
        birth_date=birth_date,
        gender=data.get('gender', 'M'),
        phone=phone,
        email=data.get('email'),
        address=data.get('address'),
        neighborhood=data.get('neighborhood', 'Hay Al Matar'),
        blood_group=data.get('blood_group'),
        allergies=data.get('allergies'),
        medical_history=data.get('medical_history'),
        surgical_history=data.get('surgical_history'),
        mutuelle_type=data.get('mutuelle_type', 'PRIVE'),
        mutuelle_number=data.get('mutuelle_number'),
        mutuelle_rate=float(data.get('mutuelle_rate', 0.0)),
        emergency_contact=data.get('emergency_contact'),
        is_archived=False
    )

    db.session.add(patient)
    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='PATIENT',
        details=f"Inscription nouveau patient {patient.first_name_fr} {patient.last_name_fr} ({patient.patient_number}, CIN: {patient.cin})",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Secrétariat'),
        user_role=session.get('user_role', 'RECEPTIONIST')
    )

    return jsonify(patient.to_dict()), 201

@patients_bp.route('/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json() or {}

    for field in ['first_name_fr', 'last_name_fr', 'first_name_ar', 'last_name_ar', 'phone', 'email', 'address', 'neighborhood', 'blood_group', 'allergies', 'medical_history', 'surgical_history', 'mutuelle_type', 'mutuelle_number', 'emergency_contact']:
        if field in data:
            setattr(patient, field, data[field])

    if 'mutuelle_rate' in data:
        patient.mutuelle_rate = float(data['mutuelle_rate'])

    if 'birth_date' in data and data['birth_date']:
        try:
            patient.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        except Exception:
            pass

    patient.updated_at = datetime.utcnow()
    db.session.commit()

    log_audit(
        action='UPDATE',
        entity_type='PATIENT',
        details=f"Mise à jour fiche patient {patient.first_name_fr} {patient.last_name_fr}",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Secrétariat'),
        user_role=session.get('user_role', 'RECEPTIONIST')
    )

    return jsonify(patient.to_dict())

@patients_bp.route('/<patient_id>/archive', methods=['POST'])
def archive_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json() or {}
    reason = data.get('reason', 'Clôture administrative du dossier patient')

    patient.is_archived = True
    patient.archived_at = datetime.utcnow()
    patient.archived_reason = reason
    db.session.commit()

    log_audit(
        action='ARCHIVE',
        entity_type='PATIENT',
        details=f"Transfert aux archives sécurisées du dossier de {patient.first_name_fr} {patient.last_name_fr} (Motif: {reason})",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Direction'),
        user_role=session.get('user_role', 'ADMIN')
    )

    return jsonify({'message': 'Dossier archivé avec succès', 'patient': patient.to_dict()})

@patients_bp.route('/<patient_id>/restore', methods=['POST'])
def restore_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.is_archived = False
    patient.archived_at = None
    patient.archived_reason = None
    db.session.commit()

    log_audit(
        action='RESTORE',
        entity_type='PATIENT',
        details=f"Restauration du dossier patient {patient.first_name_fr} {patient.last_name_fr} depuis les archives",
        entity_id=patient.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Direction'),
        user_role=session.get('user_role', 'ADMIN')
    )

    return jsonify({'message': 'Dossier restauré dans la base active', 'patient': patient.to_dict()})
