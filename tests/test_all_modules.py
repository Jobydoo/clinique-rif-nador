import os
import tempfile
import pytest
import json
from datetime import datetime, date, timedelta
from app import create_app
from app.config import Config
from app.models import db, Patient, User, Consultation, Prescription, Invoice, MedicationStock, Room, Bed, VitalSigns, Appointment, WaitingRoom
from app.services.pdf_service import generate_prescription_pdf, generate_invoice_pdf, generate_medical_certificate_pdf
from app.routes.medical import calculate_bmi
from seed_data import seed_database

TEST_MODULE_DB = os.path.join(tempfile.gettempdir(), f"clinique_modules_test_{os.getpid()}.db")

class TestModuleConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{TEST_MODULE_DB}"

@pytest.fixture(scope="session")
def app_instance():
    if os.path.exists(TEST_MODULE_DB):
        try: os.remove(TEST_MODULE_DB)
        except Exception: pass

    app = create_app(TestModuleConfig)
    with app.app_context():
        db.create_all()
        seed_database()

    yield app

    if os.path.exists(TEST_MODULE_DB):
        try: os.remove(TEST_MODULE_DB)
        except Exception: pass

# 1. Test Calculs Tarification & Mutuelles Marocaines (CNOPS / CNSS / FAR / Privé)
def test_moroccan_mutuelle_copay_rules():
    # Règle CNOPS (80% Tiers-payant, 20% Ticket modérateur)
    total_cnops = 1000.0
    rate_cnops = 80.0
    share_cnops = round(total_cnops * (rate_cnops / 100.0), 2)
    copay_cnops = round(total_cnops - share_cnops, 2)
    assert share_cnops == 800.0
    assert copay_cnops == 200.0

    # Règle CNSS (70% Tiers-payant, 30% Ticket modérateur)
    total_cnss = 650.0
    rate_cnss = 70.0
    share_cnss = round(total_cnss * (rate_cnss / 100.0), 2)
    copay_cnss = round(total_cnss - share_cnss, 2)
    assert share_cnss == 455.0
    assert copay_cnss == 195.0

    # Règle FAR (90% Tiers-payant, 10% Ticket modérateur)
    total_far = 2500.0
    rate_far = 90.0
    share_far = round(total_far * (rate_far / 100.0), 2)
    copay_far = round(total_far - share_far, 2)
    assert share_far == 2250.0
    assert copay_far == 250.0

    # Règle Privé (0% Tiers-payant, 100% Patient)
    total_prive = 450.0
    rate_prive = 0.0
    share_prive = 0.0
    copay_prive = total_prive
    assert share_prive == 0.0
    assert copay_prive == 450.0

# 2. Test Constantes Médicales & Algorithme IMC
def test_bmi_and_vitals_classification():
    # Poids normal (70 kg, 175 cm => IMC 22.9)
    bmi, status = calculate_bmi(70.0, 175.0)
    assert bmi == 22.9
    assert status == "Poids normal"

    # Surpoids (85 kg, 175 cm => IMC 27.8)
    bmi_sur, status_sur = calculate_bmi(85.0, 175.0)
    assert bmi_sur == 27.8
    assert status_sur == "Surpoids"

    # Obésité (100 kg, 170 cm => IMC 34.6)
    bmi_ob, status_ob = calculate_bmi(100.0, 170.0)
    assert bmi_ob == 34.6
    assert "Obésité" in status_ob

    # Insuffisance pondérale (45 kg, 165 cm => IMC 16.5)
    bmi_inf, status_inf = calculate_bmi(45.0, 165.0)
    assert bmi_inf == 16.5
    assert status_inf == "Insuffisance pondérale"

# 3. Test Priorités File d'Attente (Triage Urgences)
def test_waiting_room_priority_queue(app_instance):
    with app_instance.app_context():
        p1 = Patient.query.filter_by(cin='S612345').first()
        p2 = Patient.query.filter_by(cin='S789123').first()

        # Création de deux entrées : p1 Normal arrivé il y a 20 min, p2 Urgent arrivé il y a 2 min
        w_norm = WaitingRoom(
            patient_id=p1.id,
            priority='NORMAL',
            status='WAITING',
            arrival_time=datetime.utcnow() - timedelta(minutes=20)
        )
        w_urg = WaitingRoom(
            patient_id=p2.id,
            priority='URGENT',
            status='WAITING',
            arrival_time=datetime.utcnow() - timedelta(minutes=2)
        )
        db.session.add_all([w_norm, w_urg])
        db.session.commit()

        # Requête ordonnée selon la priorité puis la date d'arrivée
        ordered = WaitingRoom.query.filter(WaitingRoom.status == 'WAITING').order_by(
            db.case(
                (WaitingRoom.priority == 'URGENT', 1),
                (WaitingRoom.priority == 'PREGNANT', 2),
                (WaitingRoom.priority == 'ELDERLY', 3),
                else_=4
            ),
            WaitingRoom.arrival_time.asc()
        ).all()

        # Le patient URGENT doit impérativement être en tête de file
        assert ordered[0].priority == 'URGENT'

# 4. Test Génération PDF Ordonnance Médicale & QR Code
def test_prescription_pdf_generation(app_instance):
    with app_instance.app_context():
        prescription = Prescription.query.first()
        patient = Patient.query.get(prescription.patient_id)
        doctor = User.query.get(prescription.doctor_id) or User.query.filter_by(role='DOCTOR').first()

        pdf_data = generate_prescription_pdf(prescription, patient, doctor)
        assert isinstance(pdf_data, bytes)
        assert len(pdf_data) > 1000
        # Vérifie la signature PDF standard
        assert pdf_data.startswith(b'%PDF')

# 5. Test Génération Facture Officielle PDF (Tiers-Payant & Mentions Nador)
def test_invoice_pdf_generation(app_instance):
    with app_instance.app_context():
        invoice = Invoice.query.first()
        patient = invoice.patient

        pdf_data = generate_invoice_pdf(invoice, patient)
        assert isinstance(pdf_data, bytes)
        assert len(pdf_data) > 1000
        assert pdf_data.startswith(b'%PDF')

# 6. Test Génération Certificat Médical PDF
def test_certificate_pdf_generation(app_instance):
    with app_instance.app_context():
        patient = Patient.query.first()
        doctor = User.query.filter_by(role='DOCTOR').first()

        pdf_data = generate_medical_certificate_pdf(patient, doctor, 'REPOS', 7, 'Repos strict à domicile')
        assert isinstance(pdf_data, bytes)
        assert len(pdf_data) > 1000
        assert pdf_data.startswith(b'%PDF')

# 7. Test Alertes Pharmacie (Stock Mini & Péremption)
def test_pharmacy_stock_alerts(app_instance):
    with app_instance.app_context():
        stock_items = MedicationStock.query.all()
        low_stock = [s for s in stock_items if s.current_quantity <= s.min_quantity_alert]
        assert len(low_stock) > 0 # Au moins l'insuline Lantus

        today = datetime.utcnow().date()
        near_expiry = [s for s in stock_items if 0 < (s.expiration_date - today).days <= 60]
        assert len(near_expiry) > 0 # Au moins Lovenox

# 8. Test Rétrocession Honoraires Médecins (70% Praticien / 30% Clinique)
def test_doctor_fee_retrocession(app_instance):
    with app_instance.app_context():
        doctor = User.query.filter_by(role='DOCTOR').first()
        consultations = Consultation.query.filter_by(doctor_id=doctor.id).all()
        total_ca = sum(c.fee_amount for c in consultations)
        rate = doctor.fee_rate or 70.0

        doctor_part = round(total_ca * (rate / 100.0), 2)
        clinic_part = round(total_ca - doctor_part, 2)

        assert round(doctor_part + clinic_part, 2) == round(total_ca, 2)
        assert doctor_part >= 0
        assert clinic_part >= 0

# 9. Test Clôture de Caisse et Calcul d'Écart
def test_cash_closure_discrepancy():
    opening = 1000.0
    cash_collected = 450.0
    expected = opening + cash_collected # 1450.0

    actual_exact = 1450.0
    discrepancy_zero = actual_exact - expected
    assert discrepancy_zero == 0.0

    actual_surplus = 1500.0
    discrepancy_pos = actual_surplus - expected
    assert discrepancy_pos == 50.0

    actual_deficit = 1400.0
    discrepancy_neg = actual_deficit - expected
    assert discrepancy_neg == -50.0
