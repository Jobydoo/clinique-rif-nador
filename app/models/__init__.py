import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(30), nullable=False) # ADMIN, DOCTOR, NURSE, RECEPTIONIST, PHARMACIST, LAB_TECH
    specialty = db.Column(db.String(100), nullable=True) # Ex: Cardiologie, Pédiatrie, Médecine Interne
    phone = db.Column(db.String(30), nullable=True)
    doctor_type = db.Column(db.String(20), default='PERMANENT') # PERMANENT, VACATAIRE
    fee_rate = db.Column(db.Float, default=70.0) # 70% rétrocession médecin
    is_active = db.Column(db.Boolean, default=True)
    cndp_consent = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    consultations = db.relationship('Consultation', backref='doctor', lazy=True)
    admissions = db.relationship('Admission', backref='doctor', lazy=True)
    shifts = db.relationship('StaffShift', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'specialty': self.specialty,
            'phone': self.phone,
            'doctor_type': self.doctor_type,
            'fee_rate': self.fee_rate,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_number = db.Column(db.String(30), unique=True, nullable=False, index=True) # CNR-2026-XXXX
    cin = db.Column(db.String(20), unique=True, nullable=False, index=True) # Carte Nationale Marocaine
    first_name_fr = db.Column(db.String(60), nullable=False)
    last_name_fr = db.Column(db.String(60), nullable=False)
    first_name_ar = db.Column(db.String(60), nullable=True)
    last_name_ar = db.Column(db.String(60), nullable=True)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False, default='M') # M, F
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    neighborhood = db.Column(db.String(100), nullable=False, default='Hay Al Matar') # Nador quartiers
    blood_group = db.Column(db.String(10), nullable=True) # A+, B+, AB+, O+, etc.
    allergies = db.Column(db.Text, nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    surgical_history = db.Column(db.Text, nullable=True)
    mutuelle_type = db.Column(db.String(30), default='PRIVE') # CNOPS, CNSS, FAR, MGPAP, SAHAM, WAFA, ATLANTA, RMA, PRIVE
    mutuelle_number = db.Column(db.String(50), nullable=True)
    mutuelle_rate = db.Column(db.Float, default=0.0) # Ex: 80% (CNOPS), 70% (CNSS)
    emergency_contact = db.Column(db.String(120), nullable=True)
    is_archived = db.Column(db.Boolean, default=False, index=True)
    archived_at = db.Column(db.DateTime, nullable=True)
    archived_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    waiting_queue = db.relationship('WaitingRoom', backref='patient', lazy=True)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    vital_signs = db.relationship('VitalSigns', backref='patient', lazy=True, order_by='desc(VitalSigns.created_at)')
    consultations = db.relationship('Consultation', backref='patient', lazy=True, order_by='desc(Consultation.date)')
    admissions = db.relationship('Admission', backref='patient', lazy=True, order_by='desc(Admission.admission_date)')
    invoices = db.relationship('Invoice', backref='patient', lazy=True, order_by='desc(Invoice.date)')
    documents = db.relationship('MedicalDocument', backref='patient', lazy=True, order_by='desc(MedicalDocument.created_at)')

    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'patient_number': self.patient_number,
            'cin': self.cin,
            'first_name_fr': self.first_name_fr,
            'last_name_fr': self.last_name_fr,
            'first_name_ar': self.first_name_ar,
            'last_name_ar': self.last_name_ar,
            'full_name_fr': f"{self.first_name_fr} {self.last_name_fr}",
            'full_name_ar': f"{self.first_name_ar or ''} {self.last_name_ar or ''}".strip(),
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'gender': self.gender,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'neighborhood': self.neighborhood,
            'blood_group': self.blood_group,
            'allergies': self.allergies,
            'medical_history': self.medical_history,
            'surgical_history': self.surgical_history,
            'mutuelle_type': self.mutuelle_type,
            'mutuelle_number': self.mutuelle_number,
            'mutuelle_rate': self.mutuelle_rate,
            'emergency_contact': self.emergency_contact,
            'is_archived': self.is_archived,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None,
            'archived_reason': self.archived_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_relations:
            data['vital_signs'] = [v.to_dict() for v in self.vital_signs[:5]]
            data['consultations'] = [c.to_dict(include_items=True) for c in self.consultations]
            data['invoices'] = [i.to_dict() for i in self.invoices]
            data['documents'] = [d.to_dict() for d in self.documents]
        return data

class WaitingRoom(db.Model):
    __tablename__ = 'waiting_room'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.String(36), nullable=True)
    status = db.Column(db.String(30), default='WAITING', index=True) # WAITING, TRIAGE, IN_CONSULTATION, IN_EXAM, COMPLETED
    priority = db.Column(db.String(20), default='NORMAL') # NORMAL, URGENT, ELDERLY, PREGNANT
    arrival_time = db.Column(db.DateTime, default=datetime.utcnow)
    triage_time = db.Column(db.DateTime, nullable=True)
    consult_start_time = db.Column(db.DateTime, nullable=True)
    completed_time = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        now = datetime.utcnow()
        wait_minutes = int((now - self.arrival_time).total_seconds() / 60) if self.arrival_time else 0
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient': self.patient.to_dict() if self.patient else None,
            'doctor_id': self.doctor_id,
            'status': self.status,
            'priority': self.priority,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'triage_time': self.triage_time.isoformat() if self.triage_time else None,
            'consult_start_time': self.consult_start_time.isoformat() if self.consult_start_time else None,
            'completed_time': self.completed_time.isoformat() if self.completed_time else None,
            'wait_minutes': wait_minutes,
            'notes': self.notes,
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.String(36), nullable=False)
    doctor_name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    time_slot = db.Column(db.String(10), nullable=False) # e.g. "09:30"
    status = db.Column(db.String(20), default='SCHEDULED') # SCHEDULED, CONFIRMED, COMPLETED, CANCELLED
    reason = db.Column(db.String(255), nullable=False)
    whatsapp_sent = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient': self.patient.to_dict() if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor_name,
            'specialty': self.specialty,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'time_slot': self.time_slot,
            'status': self.status,
            'reason': self.reason,
            'whatsapp_sent': self.whatsapp_sent,
            'notes': self.notes,
        }

class VitalSigns(db.Model):
    __tablename__ = 'vital_signs'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    recorded_by = db.Column(db.String(100), nullable=False)
    systolic_bp = db.Column(db.Integer, nullable=True) # mmHg
    diastolic_bp = db.Column(db.Integer, nullable=True) # mmHg
    heart_rate = db.Column(db.Integer, nullable=True) # bpm
    temperature = db.Column(db.Float, nullable=True) # °C
    weight = db.Column(db.Float, nullable=True) # kg
    height = db.Column(db.Float, nullable=True) # cm
    bmi = db.Column(db.Float, nullable=True) # Indice de Masse Corporelle calculé
    bmi_status = db.Column(db.String(50), nullable=True) # Poids normal, Surpoids, Obésité
    spo2 = db.Column(db.Integer, nullable=True) # %
    blood_glucose = db.Column(db.Float, nullable=True) # g/L
    pain_level = db.Column(db.Integer, nullable=True) # 0-10
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'recorded_by': self.recorded_by,
            'systolic_bp': self.systolic_bp,
            'diastolic_bp': self.diastolic_bp,
            'heart_rate': self.heart_rate,
            'temperature': self.temperature,
            'weight': self.weight,
            'height': self.height,
            'bmi': self.bmi,
            'bmi_status': self.bmi_status,
            'spo2': self.spo2,
            'blood_glucose': self.blood_glucose,
            'pain_level': self.pain_level,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
        }

class Consultation(db.Model):
    __tablename__ = 'consultations'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reason = db.Column(db.String(255), nullable=False)
    symptoms = db.Column(db.Text, nullable=True)
    examination = db.Column(db.Text, nullable=True)
    cim10_code = db.Column(db.String(20), nullable=True) # e.g. I10, E11.9
    cim10_description = db.Column(db.String(255), nullable=True)
    diagnosis = db.Column(db.Text, nullable=False)
    clinical_notes = db.Column(db.Text, nullable=True)
    fee_amount = db.Column(db.Float, default=250.0) # Tarif en MAD
    is_archived = db.Column(db.Boolean, default=False, index=True)
    archived_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    prescriptions = db.relationship('Prescription', backref='consultation', lazy=True)
    invoices = db.relationship('Invoice', backref='consultation', lazy=True)

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else 'Praticien',
            'specialty': self.doctor.specialty if self.doctor else 'Médecine',
            'date': self.date.strftime('%Y-%m-%d %H:%M') if self.date else None,
            'reason': self.reason,
            'symptoms': self.symptoms,
            'examination': self.examination,
            'cim10_code': self.cim10_code,
            'cim10_description': self.cim10_description,
            'diagnosis': self.diagnosis,
            'clinical_notes': self.clinical_notes,
            'fee_amount': self.fee_amount,
            'is_archived': self.is_archived,
        }
        if include_items:
            data['prescriptions'] = [p.to_dict() for p in self.prescriptions]
        return data

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    consultation_id = db.Column(db.String(36), db.ForeignKey('consultations.id'), nullable=True)
    patient_id = db.Column(db.String(36), nullable=False)
    doctor_id = db.Column(db.String(36), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code_data = db.Column(db.String(255), nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('PrescriptionItem', backref='prescription', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'consultation_id': self.consultation_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'qr_code_data': self.qr_code_data,
            'instructions': self.instructions,
            'is_archived': self.is_archived,
            'items': [item.to_dict() for item in self.items],
        }

class PrescriptionItem(db.Model):
    __tablename__ = 'prescription_items'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    prescription_id = db.Column(db.String(36), db.ForeignKey('prescriptions.id'), nullable=False)
    medication_name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(60), nullable=False) # e.g. "1 comprimé"
    frequency = db.Column(db.String(100), nullable=False) # e.g. "3 fois par jour après repas"
    duration = db.Column(db.String(60), nullable=False) # e.g. "7 jours"
    precautions = db.Column(db.String(255), nullable=True)
    allow_substitution = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'medication_name': self.medication_name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'duration': self.duration,
            'precautions': self.precautions,
            'allow_substitution': self.allow_substitution,
        }

class MedicalDocument(db.Model):
    __tablename__ = 'medical_documents'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    type = db.Column(db.String(40), nullable=False) # ORDONNANCE, CERTIFICAT, BILAN_DEMANDE, LETTRE_ORIENTATION, RADIO, SCANNER, LAB_RESULT, CIN_SCAN, PEC_MUTUELLE, CONSENT_FORM
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(255), nullable=True)
    file_data = db.Column(db.Text, nullable=True) # Metadata ou texte/base64
    doctor_id = db.Column(db.String(36), nullable=True)
    is_archived = db.Column(db.Boolean, default=False, index=True)
    archived_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'file_url': self.file_url,
            'doctor_id': self.doctor_id,
            'is_archived': self.is_archived,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
        }

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    room_number = db.Column(db.String(30), unique=True, nullable=False) # e.g. "Chambre 101", "USI-01"
    department = db.Column(db.String(40), nullable=False) # USI, CHIRURGIE, MEDECINE, MATERNITE, AMBULATOIRE, BLOC
    floor = db.Column(db.Integer, default=1)
    daily_rate = db.Column(db.Float, default=600.0) # Tarif journalier en MAD
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    beds = db.relationship('Bed', backref='room', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'room_number': self.room_number,
            'department': self.department,
            'floor': self.floor,
            'daily_rate': self.daily_rate,
            'beds': [bed.to_dict() for bed in self.beds],
        }

class Bed(db.Model):
    __tablename__ = 'beds'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    room_id = db.Column(db.String(36), db.ForeignKey('rooms.id'), nullable=False)
    bed_number = db.Column(db.String(20), nullable=False) # e.g. "Lit A", "Lit B"
    status = db.Column(db.String(20), default='AVAILABLE') # AVAILABLE, OCCUPIED, CLEANING, RESERVED
    notes = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    admissions = db.relationship('Admission', backref='bed', lazy=True)

    def to_dict(self):
        active_adm = next((a for a in self.admissions if a.status == 'ACTIVE'), None)
        return {
            'id': self.id,
            'room_id': self.room_id,
            'bed_number': self.bed_number,
            'status': self.status,
            'notes': self.notes,
            'active_patient': active_adm.patient.to_dict() if active_adm and active_adm.patient else None,
            'active_admission_id': active_adm.id if active_adm else None,
        }

class Admission(db.Model):
    __tablename__ = 'admissions'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    bed_id = db.Column(db.String(36), db.ForeignKey('beds.id'), nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    discharge_date = db.Column(db.DateTime, nullable=True)
    admitting_doctor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    surgical_acts = db.Column(db.Text, nullable=True) # Actes chirurgicaux
    status = db.Column(db.String(20), default='ACTIVE') # ACTIVE, DISCHARGED, CANCELLED
    discharge_summary = db.Column(db.Text, nullable=True) # Fiche de sortie
    total_stay_cost = db.Column(db.Float, default=0.0)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoices = db.relationship('Invoice', backref='admission', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient': self.patient.to_dict() if self.patient else None,
            'bed_id': self.bed_id,
            'bed_number': self.bed.bed_number if self.bed else None,
            'room_number': self.bed.room.room_number if self.bed and self.bed.room else None,
            'department': self.bed.room.department if self.bed and self.bed.room else None,
            'admission_date': self.admission_date.strftime('%Y-%m-%d %H:%M') if self.admission_date else None,
            'discharge_date': self.discharge_date.strftime('%Y-%m-%d %H:%M') if self.discharge_date else None,
            'admitting_doctor_id': self.admitting_doctor_id,
            'doctor_name': self.doctor.name if self.doctor else 'Praticien',
            'reason': self.reason,
            'surgical_acts': self.surgical_acts,
            'status': self.status,
            'discharge_summary': self.discharge_summary,
            'total_stay_cost': self.total_stay_cost,
            'is_archived': self.is_archived,
        }

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    invoice_number = db.Column(db.String(30), unique=True, nullable=False, index=True) # FACT-2026-XXXX
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    consultation_id = db.Column(db.String(36), db.ForeignKey('consultations.id'), nullable=True)
    admission_id = db.Column(db.String(36), db.ForeignKey('admissions.id'), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    status = db.Column(db.String(20), default='PAID') # PAID, PENDING, PARTIAL, CANCELLED
    total_amount = db.Column(db.Float, nullable=False) # Total TTC en MAD
    mutuelle_amount = db.Column(db.Float, default=0.0) # Part Tiers-payant
    patient_share = db.Column(db.Float, nullable=False) # Ticket modérateur
    mutuelle_type = db.Column(db.String(30), default='PRIVE')
    payment_method = db.Column(db.String(20), default='CASH') # CASH, CARD, CHECK, TRANSFER
    notes = db.Column(db.String(255), nullable=True)
    is_archived = db.Column(db.Boolean, default=False, index=True)
    archived_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('InvoiceItem', backref='invoice', cascade='all, delete-orphan', lazy=True)
    payments = db.relationship('Payment', backref='invoice', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'patient_id': self.patient_id,
            'patient': self.patient.to_dict() if self.patient else None,
            'consultation_id': self.consultation_id,
            'admission_id': self.admission_id,
            'date': self.date.strftime('%Y-%m-%d %H:%M') if self.date else None,
            'status': self.status,
            'total_amount': self.total_amount,
            'mutuelle_amount': self.mutuelle_amount,
            'patient_share': self.patient_share,
            'mutuelle_type': self.mutuelle_type,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'is_archived': self.is_archived,
            'items': [item.to_dict() for item in self.items],
            'payments': [p.to_dict() for p in self.payments],
        }

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    invoice_id = db.Column(db.String(36), db.ForeignKey('invoices.id'), nullable=False)
    act_code = db.Column(db.String(30), nullable=False) # Code NGAP (e.g. CS, K50, AMI)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'act_code': self.act_code,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total': self.total,
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    invoice_id = db.Column(db.String(36), db.ForeignKey('invoices.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), default='CASH')
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    recorded_by = db.Column(db.String(100), nullable=False)
    receipt_number = db.Column(db.String(30), unique=True, nullable=False) # REC-2026-XXXX
    notes = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.strftime('%Y-%m-%d %H:%M') if self.payment_date else None,
            'recorded_by': self.recorded_by,
            'receipt_number': self.receipt_number,
            'notes': self.notes,
        }

class DailyCashClosure(db.Model):
    __tablename__ = 'daily_cash_closures'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    date = db.Column(db.Date, default=datetime.utcnow().date, index=True)
    closed_by = db.Column(db.String(100), nullable=False)
    opening_amount = db.Column(db.Float, default=1000.0) # Fond de caisse en MAD
    cash_collected = db.Column(db.Float, default=0.0)
    card_collected = db.Column(db.Float, default=0.0)
    check_collected = db.Column(db.Float, default=0.0)
    total_collected = db.Column(db.Float, default=0.0)
    expected_cash = db.Column(db.Float, default=0.0)
    actual_cash = db.Column(db.Float, default=0.0)
    discrepancy = db.Column(db.Float, default=0.0) # Écart éventuel
    status = db.Column(db.String(20), default='CLOSED')
    notes = db.Column(db.Text, nullable=True)
    closed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'closed_by': self.closed_by,
            'opening_amount': self.opening_amount,
            'cash_collected': self.cash_collected,
            'card_collected': self.card_collected,
            'check_collected': self.check_collected,
            'total_collected': self.total_collected,
            'expected_cash': self.expected_cash,
            'actual_cash': self.actual_cash,
            'discrepancy': self.discrepancy,
            'status': self.status,
            'notes': self.notes,
            'closed_at': self.closed_at.strftime('%Y-%m-%d %H:%M') if self.closed_at else None,
        }

class MedicationStock(db.Model):
    __tablename__ = 'medication_stock'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(30), nullable=False) # MEDICAMENT, CONSOMMABLE, MATERIEL, URGENCE
    dci = db.Column(db.String(120), nullable=True)
    unit = db.Column(db.String(30), nullable=False) # Boîte, Flacon, Ampoule, Pièce
    current_quantity = db.Column(db.Integer, default=0)
    min_quantity_alert = db.Column(db.Integer, default=10)
    expiration_date = db.Column(db.Date, nullable=False, index=True)
    unit_price = db.Column(db.Float, default=0.0)
    location = db.Column(db.String(60), nullable=True) # Rayon / Armoire
    batch_number = db.Column(db.String(40), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    movements = db.relationship('StockMovement', backref='medication', lazy=True)

    def to_dict(self):
        today = datetime.utcnow().date()
        days_to_expire = (self.expiration_date - today).days if self.expiration_date else 999
        is_expired = days_to_expire <= 0
        is_near_expiry = 0 < days_to_expire <= 60
        is_low_stock = self.current_quantity <= self.min_quantity_alert

        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'category': self.category,
            'dci': self.dci,
            'unit': self.unit,
            'current_quantity': self.current_quantity,
            'min_quantity_alert': self.min_quantity_alert,
            'expiration_date': self.expiration_date.strftime('%Y-%m-%d') if self.expiration_date else None,
            'unit_price': self.unit_price,
            'location': self.location,
            'batch_number': self.batch_number,
            'days_to_expire': days_to_expire,
            'is_expired': is_expired,
            'is_near_expiry': is_near_expiry,
            'is_low_stock': is_low_stock,
        }

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    medication_id = db.Column(db.String(36), db.ForeignKey('medication_stock.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False) # IN, OUT, ADJUSTMENT
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(120), nullable=False)
    reference = db.Column(db.String(60), nullable=True)
    performed_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'medication_id': self.medication_id,
            'type': self.type,
            'quantity': self.quantity,
            'reason': self.reason,
            'reference': self.reference,
            'performed_by': self.performed_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
        }

class StaffShift(db.Model):
    __tablename__ = 'staff_shifts'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    shift_date = db.Column(db.Date, nullable=False, index=True)
    shift_type = db.Column(db.String(30), nullable=False) # GARDE_NUIT, ASTREINTE_WEEKEND, JOUR_NORMAL, URGENCE
    status = db.Column(db.String(20), default='SCHEDULED')
    notes = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_role': self.user.role if self.user else None,
            'specialty': self.user.specialty if self.user else None,
            'shift_date': self.shift_date.strftime('%Y-%m-%d') if self.shift_date else None,
            'shift_type': self.shift_type,
            'status': self.status,
            'notes': self.notes,
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), nullable=True)
    user_name = db.Column(db.String(120), nullable=False)
    user_role = db.Column(db.String(30), nullable=False)
    action = db.Column(db.String(20), nullable=False) # VIEW, CREATE, UPDATE, DELETE, ARCHIVE, RESTORE, EXPORT, LOGIN
    entity_type = db.Column(db.String(30), nullable=False) # PATIENT, CONSULTATION, INVOICE, PRESCRIPTION, STOCK, BED, SYSTEM
    entity_id = db.Column(db.String(36), nullable=True)
    details = db.Column(db.Text, nullable=False) # Détails complets CNDP
    ip_address = db.Column(db.String(45), default='127.0.0.1')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_role': self.user_role,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
        }
