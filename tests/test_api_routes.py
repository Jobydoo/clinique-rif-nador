import os
import tempfile
import pytest
import json
from app import create_app
from app.models import db, Patient, User, Room, Bed, Consultation, Prescription, Invoice
from seed_data import seed_database

from app.config import Config

TEST_DB_FILE = os.path.join(tempfile.gettempdir(), f"clinique_test_{os.getpid()}.db")

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{TEST_DB_FILE}"
    WTF_CSRF_ENABLED = False

@pytest.fixture(scope="session")
def test_app():
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        seed_database()

    yield app

    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

@pytest.fixture
def client(test_app):
    return test_app.test_client()

# 1. Tests Routes Générales & PWA
def test_static_and_pwa_routes(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b"Clinique" in res.data

    res_manifest = client.get('/manifest.json')
    assert res_manifest.status_code == 200

    res_sw = client.get('/sw.js')
    assert res_sw.status_code == 200

# 2. Tests Authentification & Rôles
def test_auth_routes(client):
    res = client.get('/api/auth/demo-accounts')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['accounts']) >= 6

    # Test login avec compte démo
    res_login = client.post('/api/auth/login', json={
        'email': 'admin@clinique-rif-nador.ma',
        'password': 'Password123!'
    })
    assert res_login.status_code == 200
    login_data = res_login.get_json()
    assert login_data['user']['role'] == 'ADMIN'

    # Test route /me
    res_me = client.get('/api/auth/me')
    assert res_me.status_code == 200

    # Test liste des utilisateurs
    res_users = client.get('/api/auth/users')
    assert res_users.status_code == 200
    assert len(res_users.get_json()) >= 6

    # Test logout
    res_logout = client.post('/api/auth/logout')
    assert res_logout.status_code == 200

# 3. Tests Patients & Dossiers Médicaux (DME)
def test_patients_crud_and_archive(client, test_app):
    # Liste des patients
    res = client.get('/api/patients')
    assert res.status_code == 200
    patients = res.get_json()
    assert len(patients) >= 13

    # Création nouveau patient
    res_create = client.post('/api/patients', json={
        'cin': 'TEST999',
        'first_name_fr': 'Karim',
        'last_name_fr': 'Alami',
        'phone': '0661999999',
        'neighborhood': 'Hay Al Matar',
        'mutuelle_type': 'CNOPS',
        'mutuelle_rate': 80.0
    })
    assert res_create.status_code == 201
    new_p = res_create.get_json()
    assert new_p['cin'] == 'TEST999'

    # Fiche complète
    res_detail = client.get(f"/api/patients/{new_p['id']}")
    assert res_detail.status_code == 200

    # Modification patient
    res_update = client.put(f"/api/patients/{new_p['id']}", json={
        'phone': '0662000000',
        'medical_history': 'Suivi cardiologique'
    })
    assert res_update.status_code == 200
    assert res_update.get_json()['phone'] == '0662000000'

    # Archivage sécurisé (Soft delete)
    res_arch = client.post(f"/api/patients/{new_p['id']}/archive", json={
        'reason': 'Dossier soldé'
    })
    assert res_arch.status_code == 200

    # Restauration depuis les archives
    res_rest = client.post(f"/api/patients/{new_p['id']}/restore")
    assert res_rest.status_code == 200

# 4. Tests Salle d'Attente Intelligente
def test_waiting_room_flow(client):
    res_q = client.get('/api/waiting-room')
    assert res_q.status_code == 200
    queue = res_q.get_json()
    assert len(queue) >= 1

    entry_id = queue[0]['id']

    # Changement de statut
    res_st = client.put(f'/api/waiting-room/{entry_id}/status', json={'status': 'TRIAGE'})
    assert res_st.status_code == 200
    assert res_st.get_json()['status'] == 'TRIAGE'

    # Appel patient (Carillon & Annonce)
    res_call = client.post(f'/api/waiting-room/{entry_id}/call', json={'cabinet': 'Cabinet 2'})
    assert res_call.status_code == 200
    assert res_call.get_json()['success'] is True

# 5. Tests Rendez-vous & Rappel WhatsApp
def test_appointments_flow(client):
    res_app = client.get('/api/appointments')
    assert res_app.status_code == 200
    apps = res_app.get_json()
    assert len(apps) >= 1

    app_id = apps[0]['id']

    # WhatsApp Link Generator
    res_wa = client.get(f'/api/appointments/{app_id}/whatsapp')
    assert res_wa.status_code == 200
    wa_data = res_wa.get_json()
    assert 'wa.me' in wa_data['whatsapp_url']
    assert 'Nador' in wa_data['message']

# 6. Tests Médical : Constantes, Consultations & Prescriptions
def test_medical_flow(client, test_app):
    # CIM-10
    res_cim = client.get('/api/medical/cim10')
    assert res_cim.status_code == 200
    assert len(res_cim.get_json()) > 0

    with test_app.app_context():
        patient = Patient.query.first()
        doctor = User.query.filter_by(role='DOCTOR').first()
        p_id = patient.id
        doc_id = doctor.id

    # Prise de constantes avec calcul IMC automatique
    res_vit = client.post('/api/medical/vitals', json={
        'patient_id': p_id,
        'weight': 80.0,
        'height': 180.0,
        'systolic_bp': 120,
        'diastolic_bp': 80,
        'spo2': 99
    })
    assert res_vit.status_code == 201
    vit_data = res_vit.get_json()
    assert vit_data['bmi'] == 24.7
    assert vit_data['bmi_status'] == 'Poids normal'

    # Création consultation & prescription
    res_cons = client.post('/api/medical/consultations', json={
        'patient_id': p_id,
        'doctor_id': doc_id,
        'reason': 'Contrôle annuel',
        'diagnosis': 'Bilan de santé satisfaisant',
        'fee_amount': 250.0,
        'medications': [
            {'name': 'Vitamine D 100 000 UI', 'dosage': '1 ampoule', 'frequency': '1 fois par mois', 'duration': '3 mois'}
        ]
    })
    assert res_cons.status_code == 201
    cons_data = res_cons.get_json()
    assert len(cons_data['prescriptions']) == 1

    presc_id = cons_data['prescriptions'][0]['id']

    # Génération PDF Ordonnance Officielle
    res_pdf = client.get(f'/api/medical/prescriptions/{presc_id}/pdf')
    assert res_pdf.status_code == 200
    assert res_pdf.mimetype == 'application/pdf'
    assert len(res_pdf.data) > 1000

    # Génération Certificat Médical PDF
    res_cert = client.post('/api/medical/certificates/pdf', json={
        'patient_id': p_id,
        'days_rest': 5,
        'notes': 'Repos strict'
    })
    assert res_cert.status_code == 200
    assert res_cert.mimetype == 'application/pdf'

# 7. Tests Hospitalisation & Lits
def test_inpatient_flow(client):
    res_rooms = client.get('/api/inpatient/rooms')
    assert res_rooms.status_code == 200
    rooms = res_rooms.get_json()
    assert len(rooms) >= 6

    # Test changement de statut lit
    first_bed = rooms[0]['beds'][0]
    res_bed = client.put(f"/api/inpatient/beds/{first_bed['id']}/status", json={'status': 'RESERVED'})
    assert res_bed.status_code == 200
    assert res_bed.get_json()['status'] == 'RESERVED'

# 8. Tests Facturation & Mutuelles (Calcul Tiers-payant / Copay)
def test_billing_and_copay_calculation(client, test_app):
    res_cat = client.get('/api/billing/acts-catalog')
    assert res_cat.status_code == 200
    assert len(res_cat.get_json()) > 0

    with test_app.app_context():
        patient_cnops = Patient.query.filter_by(mutuelle_type='CNOPS').first()
        p_id = patient_cnops.id

    # Facture de 1000 MAD avec CNOPS 80%
    res_inv = client.post('/api/billing/invoices', json={
        'patient_id': p_id,
        'items': [
            {'act_code': 'BLOC', 'description': 'Chirurgie', 'quantity': 1, 'unit_price': 1000.0}
        ],
        'payment_method': 'CASH',
        'is_paid': True
    })
    assert res_inv.status_code == 201
    inv_data = res_inv.get_json()
    assert inv_data['total_amount'] == 1000.0
    assert inv_data['mutuelle_amount'] == 800.0 # 80% CNOPS
    assert inv_data['patient_share'] == 200.0   # 20% ticket modérateur

    # Génération Facture PDF Officielle
    res_pdf = client.get(f"/api/billing/invoices/{inv_data['id']}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.mimetype == 'application/pdf'

    # Clôture journalière de caisse
    res_closure = client.post('/api/billing/cash-closures', json={
        'opening_amount': 1000.0,
        'actual_cash': 1200.0,
        'notes': 'Caisse équilibrée'
    })
    assert res_closure.status_code == 201

# 9. Tests Pharmacie & Mouvements de Stock
def test_pharmacy_flow(client):
    res_stock = client.get('/api/pharmacy/stock')
    assert res_stock.status_code == 200
    stock = res_stock.get_json()
    assert len(stock) >= 5

    item = stock[0]

    # Mouvement de stock IN
    res_mov = client.post(f"/api/pharmacy/stock/{item['id']}/movement", json={
        'type': 'IN',
        'quantity': 10,
        'reason': 'Approvisionnement'
    })
    assert res_mov.status_code == 200
    assert res_mov.get_json()['item']['current_quantity'] == item['current_quantity'] + 10

# 10. Tests RH & Calcul des Honoraires Médecins
def test_staff_and_fees(client):
    res_staff = client.get('/api/staff')
    assert res_staff.status_code == 200

    res_fees = client.get('/api/staff/fees-calculator')
    assert res_fees.status_code == 200
    fees = res_fees.get_json()
    assert len(fees) > 0
    for f in fees:
        assert round(f['doctor_share'] + f['clinic_share'], 1) == round(f['grand_total_ca'], 1)

# 11. Tests Coffre-fort Archives & Export Dossier Complet
def test_archive_and_export_vault(client, test_app):
    res_arch = client.get('/api/archive')
    assert res_arch.status_code == 200
    archives = res_arch.get_json()
    assert len(archives) >= 2

    target = archives[0]
    res_rest = client.post(f"/api/archive/{target['entity_type']}/{target['entity_id']}/restore")
    assert res_rest.status_code == 200
    assert res_rest.get_json()['success'] is True

    with test_app.app_context():
        patient = Patient.query.first()
        p_id = patient.id
        cin = patient.cin

    res_export = client.get(f"/api/archive/patients/{p_id}/export")
    assert res_export.status_code == 200
    assert res_export.mimetype == 'application/json'
    export_data = json.loads(res_export.data)
    assert 'export_metadata' in export_data
    assert export_data['cin'] == cin

# 12. Tests Audit Logs CNDP & Sauvegardes Automatiques
def test_audit_logs_and_backup(client):
    res_logs = client.get('/api/audit/logs')
    assert res_logs.status_code == 200
    assert len(res_logs.get_json()) > 0

    res_backup = client.post('/api/audit/backups/create')
    assert res_backup.status_code == 201
    b_data = res_backup.get_json()
    assert 'backup_clinique_rif_nador' in b_data['filename']
    assert b_data['size_kb'] > 0

# 13. Test Dashboard KPIs
def test_dashboard_kpis(client):
    res_stats = client.get('/api/stats/dashboard')
    assert res_stats.status_code == 200
    data = res_stats.get_json()
    kpis = data['kpis']
    assert kpis['total_patients'] >= 15
    assert 'mutuelle_distribution' in data
