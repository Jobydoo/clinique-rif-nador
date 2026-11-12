import os
from datetime import datetime, date, timedelta
from app import create_app
from app.models import (
    db, User, Patient, WaitingRoom, Appointment, VitalSigns,
    Consultation, Prescription, PrescriptionItem, Room, Bed,
    Admission, Invoice, InvoiceItem, Payment, DailyCashClosure,
    MedicationStock, StockMovement, StaffShift, AuditLog
)

def seed_database():
    print("Insertion des comptes utilisateurs et rôles (RBAC)...")
    
    # 1. Utilisateurs / Rôles
    users_data = [
        {
            'email': 'admin@clinique-rif-nador.ma',
            'name': 'Dr. Mohamed Amrani',
            'role': 'ADMIN',
            'specialty': 'Direction Médicale & Chirurgie Générale',
            'phone': '+212 661 20 30 40',
            'doctor_type': 'PERMANENT',
            'fee_rate': 75.0,
        },
        {
            'email': 'medecin@clinique-rif-nador.ma',
            'name': 'Dr. Youssef Benali',
            'role': 'DOCTOR',
            'specialty': 'Cardiologie & Médecine Interne',
            'phone': '+212 662 33 44 55',
            'doctor_type': 'PERMANENT',
            'fee_rate': 70.0,
        },
        {
            'email': 'chirurgien@clinique-rif-nador.ma',
            'name': 'Dr. Amina El Fassi',
            'role': 'DOCTOR',
            'specialty': 'Chirurgie Orthopédique & Traumatologie',
            'phone': '+212 663 55 66 77',
            'doctor_type': 'VACATAIRE',
            'fee_rate': 70.0,
        },
        {
            'email': 'infirmier@clinique-rif-nador.ma',
            'name': 'Fatima Zahra Mansouri',
            'role': 'NURSE',
            'specialty': 'Soins Infirmiers & Triage Urgences',
            'phone': '+212 664 77 88 99',
            'fee_rate': 0.0,
        },
        {
            'email': 'reception@clinique-rif-nador.ma',
            'name': 'Khadija El Idrissi',
            'role': 'RECEPTIONIST',
            'specialty': 'Accueil, Facturation & Admissions',
            'phone': '+212 665 11 22 33',
            'fee_rate': 0.0,
        },
        {
            'email': 'pharmacie@clinique-rif-nador.ma',
            'name': 'Dr. Rachid Berrada',
            'role': 'PHARMACIST',
            'specialty': 'Pharmacie Hospitalière & Consommables',
            'phone': '+212 666 44 55 66',
            'fee_rate': 0.0,
        },
        {
            'email': 'labo@clinique-rif-nador.ma',
            'name': 'Nadia Tazi',
            'role': 'LAB_TECH',
            'specialty': 'Analyses Médicales & Imagerie',
            'phone': '+212 667 88 99 00',
            'fee_rate': 0.0,
        }
    ]

    created_users = {}
    for u in users_data:
        user = User.query.filter_by(email=u['email']).first()
        if not user:
            user = User(
                email=u['email'],
                name=u['name'],
                role=u['role'],
                specialty=u['specialty'],
                phone=u['phone'],
                doctor_type=u.get('doctor_type'),
                fee_rate=u['fee_rate']
            )
            user.set_password('Password123!')
            db.session.add(user)
            db.session.flush()
        created_users[u['email']] = user

    print("Insertion des 15 patients réalistes pour Nador...")
    
    # 2. Patients de Nador
    patients_data = [
        {
            'patient_number': 'CNR-2026-0001',
            'cin': 'S612345',
            'first_name_fr': 'Yassine',
            'last_name_fr': 'El Amrani',
            'first_name_ar': 'ياسين',
            'last_name_ar': 'العمراني',
            'birth_date': date(1982, 4, 15),
            'gender': 'M',
            'phone': '0661123456',
            'neighborhood': 'Hay Al Matar',
            'blood_group': 'O+',
            'allergies': 'Pénicilline',
            'medical_history': 'Hypertension artérielle sous traitement',
            'mutuelle_type': 'CNOPS',
            'mutuelle_number': '109827364',
            'mutuelle_rate': 80.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0002',
            'cin': 'S789123',
            'first_name_fr': 'Fatima Zohra',
            'last_name_fr': 'Boussouf',
            'first_name_ar': 'فاطمة الزهراء',
            'last_name_ar': 'بوصوف',
            'birth_date': date(1990, 8, 22),
            'gender': 'F',
            'phone': '0662987654',
            'neighborhood': 'Bouizazarène',
            'blood_group': 'A+',
            'allergies': 'Aucune allergie connue',
            'medical_history': 'Grossesse en cours (28 SA)',
            'mutuelle_type': 'CNSS',
            'mutuelle_number': '239847192',
            'mutuelle_rate': 70.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0003',
            'cin': 'S541289',
            'first_name_fr': 'Mohamed',
            'last_name_fr': 'Chaouki',
            'first_name_ar': 'محمد',
            'last_name_ar': 'شوقي',
            'birth_date': date(1968, 11, 5),
            'gender': 'M',
            'phone': '0663456789',
            'neighborhood': 'Selouane',
            'blood_group': 'B+',
            'allergies': 'Aspirine',
            'medical_history': 'Diabète de type 2 depuis 10 ans',
            'mutuelle_type': 'FAR',
            'mutuelle_number': 'FAR-892341',
            'mutuelle_rate': 90.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0004',
            'cin': 'S321987',
            'first_name_fr': 'Samira',
            'last_name_fr': 'Touzani',
            'first_name_ar': 'سميرة',
            'last_name_ar': 'التوزاني',
            'birth_date': date(1975, 2, 18),
            'gender': 'F',
            'phone': '0664321987',
            'neighborhood': 'Beni Ansar',
            'blood_group': 'AB+',
            'allergies': 'Sulfamides',
            'medical_history': 'Hypothyroïdie sous Lévothyrox',
            'mutuelle_type': 'MGPAP',
            'mutuelle_number': 'MGP-55421',
            'mutuelle_rate': 80.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0005',
            'cin': 'S908765',
            'first_name_fr': 'Karim',
            'last_name_fr': 'Mansouri',
            'first_name_ar': 'كريم',
            'last_name_ar': 'المنصوري',
            'birth_date': date(1995, 6, 30),
            'gender': 'M',
            'phone': '0665908765',
            'neighborhood': 'Hay Al Qods',
            'blood_group': 'O-',
            'allergies': 'Aucune',
            'medical_history': 'Traumatisme sportif au genou',
            'mutuelle_type': 'SAHAM',
            'mutuelle_number': 'SHM-98124',
            'mutuelle_rate': 85.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0006',
            'cin': 'S432109',
            'first_name_fr': 'Rachida',
            'last_name_fr': 'Benali',
            'first_name_ar': 'رشيدة',
            'last_name_ar': 'بن علي',
            'birth_date': date(1963, 12, 10),
            'gender': 'F',
            'phone': '0666432109',
            'neighborhood': 'Ulad Mimoun',
            'blood_group': 'A-',
            'allergies': 'Poussière / Acariens',
            'medical_history': 'Asthme bronchique chronique',
            'mutuelle_type': 'WAFA',
            'mutuelle_number': 'WAF-77654',
            'mutuelle_rate': 80.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0007',
            'cin': 'S765432',
            'first_name_fr': 'Abdelkader',
            'last_name_fr': 'Bouazzaoui',
            'first_name_ar': 'عبد القادر',
            'last_name_ar': 'بوعزاوي',
            'birth_date': date(1955, 3, 25),
            'gender': 'M',
            'phone': '0667765432',
            'neighborhood': 'Zeghanghane',
            'blood_group': 'O+',
            'allergies': 'AINS',
            'medical_history': 'Insuffisance coronarienne, pontage en 2021',
            'mutuelle_type': 'ATLANTA',
            'mutuelle_number': 'ATL-12098',
            'mutuelle_rate': 75.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0008',
            'cin': 'S112233',
            'first_name_fr': 'Najat',
            'last_name_fr': 'El Khattabi',
            'first_name_ar': 'نجاة',
            'last_name_ar': 'الخطابي',
            'birth_date': date(1988, 9, 14),
            'gender': 'F',
            'phone': '0668112233',
            'neighborhood': 'Al Aroui',
            'blood_group': 'B-',
            'allergies': 'Aucune',
            'medical_history': 'Migraines ophtalmiques récurrentes',
            'mutuelle_type': 'CNOPS',
            'mutuelle_number': 'CNO-99881',
            'mutuelle_rate': 80.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0009',
            'cin': 'S998877',
            'first_name_fr': 'Omar',
            'last_name_fr': 'Boutahar',
            'first_name_ar': 'عمر',
            'last_name_ar': 'بوطاهر',
            'birth_date': date(1972, 7, 8),
            'gender': 'M',
            'phone': '0669998877',
            'neighborhood': 'Zaio',
            'blood_group': 'A+',
            'allergies': 'Iode',
            'medical_history': 'Calcul rénal récidivant',
            'mutuelle_type': 'CNSS',
            'mutuelle_number': 'CNS-66554',
            'mutuelle_rate': 70.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0010',
            'cin': 'S445566',
            'first_name_fr': 'Zineb',
            'last_name_fr': 'Achahbar',
            'first_name_ar': 'زينب',
            'last_name_ar': 'أشهبار',
            'birth_date': date(2001, 1, 19),
            'gender': 'F',
            'phone': '0670445566',
            'neighborhood': 'Driouch',
            'blood_group': 'O+',
            'allergies': 'Aucune',
            'medical_history': 'Gastrite aiguë',
            'mutuelle_type': 'PRIVE',
            'mutuelle_number': None,
            'mutuelle_rate': 0.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0011',
            'cin': 'S334455',
            'first_name_fr': 'Mourad',
            'last_name_fr': 'Chamlali',
            'first_name_ar': 'مراد',
            'last_name_ar': 'الشملالي',
            'birth_date': date(1985, 5, 12),
            'gender': 'M',
            'phone': '0671334455',
            'neighborhood': 'Bouarg',
            'blood_group': 'B+',
            'allergies': 'Pénicilline',
            'medical_history': 'Lombalgie chronique L4-L5',
            'mutuelle_type': 'CNOPS',
            'mutuelle_number': 'CNO-44332',
            'mutuelle_rate': 80.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0012',
            'cin': 'S776655',
            'first_name_fr': 'Latifa',
            'last_name_fr': 'El Morabit',
            'first_name_ar': 'لطيفة',
            'last_name_ar': 'المرابط',
            'birth_date': date(1979, 10, 3),
            'gender': 'F',
            'phone': '0672776655',
            'neighborhood': 'Hay Al Matar',
            'blood_group': 'AB-',
            'allergies': 'Aucune',
            'medical_history': 'Colopathie fonctionnelle',
            'mutuelle_type': 'CNSS',
            'mutuelle_number': 'CNS-88776',
            'mutuelle_rate': 70.0,
            'is_archived': False
        },
        {
            'patient_number': 'CNR-2026-0013',
            'cin': 'S223344',
            'first_name_fr': 'Hassan',
            'last_name_fr': 'Aznag',
            'first_name_ar': 'حسن',
            'last_name_ar': 'أزناغ',
            'birth_date': date(1966, 8, 27),
            'gender': 'M',
            'phone': '0673223344',
            'neighborhood': 'Beni Ansar Port',
            'blood_group': 'A+',
            'allergies': 'Latex',
            'medical_history': 'Ancien fumeur, bronchite chronique',
            'mutuelle_type': 'FAR',
            'mutuelle_number': 'FAR-11223',
            'mutuelle_rate': 90.0,
            'is_archived': False
        },
        # Patient archivé 1 (pour test des archives et restauration)
        {
            'patient_number': 'CNR-2026-0014',
            'cin': 'S667788',
            'first_name_fr': 'Houda',
            'last_name_fr': 'Yahyaoui',
            'first_name_ar': 'هدى',
            'last_name_ar': 'اليحياوي',
            'birth_date': date(1993, 11, 14),
            'gender': 'F',
            'phone': '0674667788',
            'neighborhood': 'Selouane Université',
            'blood_group': 'O-',
            'allergies': 'Arachides',
            'medical_history': 'Dossier clos suite à déménagement à Tanger',
            'mutuelle_type': 'CNOPS',
            'mutuelle_number': 'CNO-55667',
            'mutuelle_rate': 80.0,
            'is_archived': True,
            'archived_at': datetime.utcnow() - timedelta(days=20),
            'archived_reason': 'Déménagement du patient hors de la région de Nador'
        },
        # Patient archivé 2 (pour test des archives et restauration)
        {
            'patient_number': 'CNR-2026-0015',
            'cin': 'S889900',
            'first_name_fr': 'Bilal',
            'last_name_fr': 'El Ouazzani',
            'first_name_ar': 'بلال',
            'last_name_ar': 'الوزاني',
            'birth_date': date(1980, 5, 9),
            'gender': 'M',
            'phone': '0675889900',
            'neighborhood': 'Bouizazarène',
            'blood_group': 'B+',
            'allergies': 'Aucune',
            'medical_history': 'Fin de protocole de soins post-opératoire',
            'mutuelle_type': 'CNSS',
            'mutuelle_number': 'CNS-33221',
            'mutuelle_rate': 70.0,
            'is_archived': True,
            'archived_at': datetime.utcnow() - timedelta(days=45),
            'archived_reason': 'Guérison totale et clôture médicale du dossier'
        }
    ]

    created_patients = []
    for p in patients_data:
        patient = Patient.query.filter_by(cin=p['cin']).first()
        if not patient:
            patient = Patient(
                patient_number=p['patient_number'],
                cin=p['cin'],
                first_name_fr=p['first_name_fr'],
                last_name_fr=p['last_name_fr'],
                first_name_ar=p['first_name_ar'],
                last_name_ar=p['last_name_ar'],
                birth_date=p['birth_date'],
                gender=p['gender'],
                phone=p['phone'],
                neighborhood=p['neighborhood'],
                blood_group=p['blood_group'],
                allergies=p['allergies'],
                medical_history=p['medical_history'],
                mutuelle_type=p['mutuelle_type'],
                mutuelle_number=p['mutuelle_number'],
                mutuelle_rate=p['mutuelle_rate'],
                is_archived=p['is_archived'],
                archived_at=p.get('archived_at'),
                archived_reason=p.get('archived_reason')
            )
            db.session.add(patient)
            db.session.flush()
        created_patients.append(patient)

    print("Insertion des chambres et des lits hospitaliers...")
    
    # 3. Chambres & Lits
    rooms_data = [
        {'room_number': 'Chambre 101', 'department': 'MEDECINE', 'floor': 1, 'daily_rate': 600.0, 'beds': ['Lit 101-A', 'Lit 101-B']},
        {'room_number': 'Chambre 102', 'department': 'MEDECINE', 'floor': 1, 'daily_rate': 600.0, 'beds': ['Lit 102-A', 'Lit 102-B']},
        {'room_number': 'Chambre 201 (VIP)', 'department': 'CHIRURGIE', 'floor': 2, 'daily_rate': 900.0, 'beds': ['Lit 201-VIP']},
        {'room_number': 'Chambre 202', 'department': 'CHIRURGIE', 'floor': 2, 'daily_rate': 600.0, 'beds': ['Lit 202-A', 'Lit 202-B']},
        {'room_number': 'Maternité M1', 'department': 'MATERNITE', 'floor': 2, 'daily_rate': 750.0, 'beds': ['Lit M1-A', 'Lit M1-B']},
        {'room_number': 'USI Réanimation', 'department': 'USI', 'floor': 1, 'daily_rate': 1800.0, 'beds': ['Lit USI-1', 'Lit USI-2']},
        {'room_number': 'Bloc Opératoire A', 'department': 'BLOC', 'floor': 3, 'daily_rate': 3000.0, 'beds': ['Table Opératoire A']},
        {'room_number': 'Hôpital de Jour', 'department': 'AMBULATOIRE', 'floor': 1, 'daily_rate': 400.0, 'beds': ['Fauteuil HDJ-1', 'Fauteuil HDJ-2']}
    ]

    all_beds = []
    for r in rooms_data:
        room = Room.query.filter_by(room_number=r['room_number']).first()
        if not room:
            room = Room(
                room_number=r['room_number'],
                department=r['department'],
                floor=r['floor'],
                daily_rate=r['daily_rate']
            )
            db.session.add(room)
            db.session.flush()

        for b_num in r['beds']:
            bed = Bed.query.filter_by(room_id=room.id, bed_number=b_num).first()
            if not bed:
                bed = Bed(
                    room_id=room.id,
                    bed_number=b_num,
                    status='AVAILABLE'
                )
                db.session.add(bed)
                db.session.flush()
            all_beds.append(bed)

    print("Insertion des données médicales (Constantes, File d'attente, Consultations, Factures)...")
    
    # 4. Constantes vitales pour plusieurs patients
    doc_benali = created_users['medecin@clinique-rif-nador.ma']
    doc_amrani = created_users['admin@clinique-rif-nador.ma']

    p1 = created_patients[0] # Yassine
    p2 = created_patients[1] # Fatima Zohra
    p3 = created_patients[2] # Mohamed Chaouki
    p5 = created_patients[4] # Karim Mansouri

    if VitalSigns.query.filter_by(patient_id=p1.id).count() == 0:
        # Vitals pour Yassine
        v1 = VitalSigns(
            patient_id=p1.id,
            recorded_by='Fatima Zahra Mansouri',
            systolic_bp=135,
            diastolic_bp=85,
            heart_rate=76,
            temperature=37.1,
            weight=82.0,
            height=178.0,
            bmi=25.9,
            bmi_status='Surpoids',
            spo2=98,
            blood_glucose=1.10,
            pain_level=2,
            notes='Tension légèrement élevée à surveiller'
        )
        db.session.add(v1)

        # Vitals pour Fatima Zohra
        v2 = VitalSigns(
            patient_id=p2.id,
            recorded_by='Fatima Zahra Mansouri',
            systolic_bp=115,
            diastolic_bp=75,
            heart_rate=80,
            temperature=36.8,
            weight=68.0,
            height=165.0,
            bmi=25.0,
            bmi_status='Poids normal',
            spo2=99,
            blood_glucose=0.92,
            pain_level=1,
            notes='Constantes stables, contrôle obstétrical'
        )
        db.session.add(v2)

        # Vitals pour Mohamed Chaouki
        v3 = VitalSigns(
            patient_id=p3.id,
            recorded_by='Fatima Zahra Mansouri',
            systolic_bp=140,
            diastolic_bp=90,
            heart_rate=72,
            temperature=37.0,
            weight=79.0,
            height=172.0,
            bmi=26.7,
            bmi_status='Surpoids',
            spo2=97,
            blood_glucose=1.65,
            pain_level=3,
            notes='Glycémie à jeun élevée (1.65 g/L), ajustement thérapeutique diabète'
        )
        db.session.add(v3)

    # 5. File d'attente intelligente (Waiting Room)
    if WaitingRoom.query.filter_by(patient_id=p1.id).count() == 0:
        w1 = WaitingRoom(
            patient_id=p1.id,
            doctor_id=doc_benali.id,
            status='IN_CONSULTATION',
            priority='NORMAL',
            arrival_time=datetime.utcnow() - timedelta(minutes=25),
            consult_start_time=datetime.utcnow() - timedelta(minutes=5),
            notes='Contrôle annuel cardiologie'
        )
        w2 = WaitingRoom(
            patient_id=p2.id,
            doctor_id=doc_amrani.id,
            status='TRIAGE',
            priority='PREGNANT',
            arrival_time=datetime.utcnow() - timedelta(minutes=15),
            triage_time=datetime.utcnow() - timedelta(minutes=2),
            notes='Échographie de contrôle T2'
        )
        w3 = WaitingRoom(
            patient_id=p5.id,
            doctor_id=doc_amrani.id,
            status='WAITING',
            priority='URGENT',
            arrival_time=datetime.utcnow() - timedelta(minutes=10),
            notes='Traumatisme aigu au poignet droit'
        )
        db.session.add_all([w1, w2, w3])

    # 6. Rendez-vous du jour et de la semaine
    today = date.today()
    if Appointment.query.filter_by(patient_id=p1.id).count() == 0:
        app1 = Appointment(
            patient_id=p1.id,
            doctor_id=doc_benali.id,
            doctor_name=doc_benali.name,
            specialty=doc_benali.specialty,
            date=today,
            time_slot='10:00',
            status='CONFIRMED',
            reason='Bilan cardiovasculaire et ECG',
            whatsapp_sent=True
        )
        app2 = Appointment(
            patient_id=p2.id,
            doctor_id=doc_amrani.id,
            doctor_name=doc_amrani.name,
            specialty=doc_amrani.specialty,
            date=today,
            time_slot='11:30',
            status='CONFIRMED',
            reason='Échographie morphologique',
            whatsapp_sent=True
        )
        app3 = Appointment(
            patient_id=created_patients[3].id, # Samira
            doctor_id=doc_benali.id,
            doctor_name=doc_benali.name,
            specialty=doc_benali.specialty,
            date=today + timedelta(days=1),
            time_slot='09:30',
            status='SCHEDULED',
            reason='Dosage TSH et suivi thyroïdien',
            whatsapp_sent=False
        )
        db.session.add_all([app1, app2, app3])

    # 7. Consultations médicales & Prescriptions avec QR code
    if Consultation.query.filter_by(patient_id=p1.id).count() == 0:
        c1 = Consultation(
            patient_id=p1.id,
            doctor_id=doc_benali.id,
            date=datetime.utcnow() - timedelta(days=1),
            reason='Douleur thoracique atypique et essoufflement à l’effort',
            symptoms='Palpitations nocturnes, oppression légère',
            examination='Auscultation cardiaque normale, pas de bruits surajoutés. Pouls régulier 76 bpm. TA 135/85 mmHg.',
            cim10_code='I10',
            cim10_description='Hypertension artérielle essentielle',
            diagnosis='Hypertension artérielle stade 1 bien tolérée sans signe d\'insuffisance cardiaque',
            clinical_notes='Régime hyposodé strict. Arrêt du café. Reprise d\'une activité physique douce (marche 30 min/j).',
            fee_amount=250.0
        )
        db.session.add(c1)
        db.session.flush()

        presc1 = Prescription(
            consultation_id=c1.id,
            patient_id=p1.id,
            doctor_id=doc_benali.id,
            date=datetime.utcnow() - timedelta(days=1),
            qr_code_data=f"CLINIQUE_DU_RIF_NADOR|PRESCRIPTION:{c1.id}|CIN:{p1.cin}|DATE:{today}",
            instructions='Traitement à prendre le matin au petit-déjeuner sans interruption.'
        )
        db.session.add(presc1)
        db.session.flush()

        item1 = PrescriptionItem(
            prescription_id=presc1.id,
            medication_name='Amlodipine 5mg (Amlor)',
            dosage='1 gélule',
            frequency='1 fois par jour le matin',
            duration='3 mois renouvelable',
            precautions='Surveiller l’apparition éventuelle d’œdèmes des membres inférieurs',
            allow_substitution=True
        )
        item2 = PrescriptionItem(
            prescription_id=presc1.id,
            medication_name='Kardégic 75mg',
            dosage='1 sachet',
            frequency='1 fois par jour le midi au milieu du repas',
            duration='3 mois',
            precautions='À diluer dans un verre d’eau',
            allow_substitution=False
        )
        db.session.add_all([item1, item2])

    # 8. Factures et encaissements avec part mutuelle
    if not Invoice.query.filter_by(invoice_number='FACT-2026-0001').first():
        inv1 = Invoice(
            invoice_number='FACT-2026-0001',
            patient_id=p1.id,
            consultation_id=Consultation.query.filter_by(patient_id=p1.id).first().id if Consultation.query.filter_by(patient_id=p1.id).first() else None,
            date=datetime.utcnow() - timedelta(days=1),
            status='PAID',
            total_amount=430.0, # CS (250) + ECG (180)
            mutuelle_amount=344.0, # CNOPS 80%
            patient_share=86.0, # 20% ticket modérateur
            mutuelle_type='CNOPS',
            payment_method='CASH',
            notes='Prise en charge CNOPS 80% appliquée.'
        )
        db.session.add(inv1)
        db.session.flush()

        ii1 = InvoiceItem(invoice_id=inv1.id, act_code='CS', description='Consultation Médecin Spécialiste Cardiologue', quantity=1, unit_price=250.0, total=250.0)
        ii2 = InvoiceItem(invoice_id=inv1.id, act_code='ECG', description='Électrocardiogramme 12 dérivations', quantity=1, unit_price=180.0, total=180.0)
        pay1 = Payment(invoice_id=inv1.id, amount=86.0, payment_method='CASH', payment_date=datetime.utcnow() - timedelta(days=1), recorded_by='Khadija El Idrissi', receipt_number='REC-2026-0001', notes='Règlement espèces ticket modérateur')
        db.session.add_all([ii1, ii2, pay1])

    # Facture 2 (Patient CNSS)
    if not Invoice.query.filter_by(invoice_number='FACT-2026-0002').first():
        inv2 = Invoice(
            invoice_number='FACT-2026-0002',
            patient_id=p2.id,
            date=datetime.utcnow(),
            status='PAID',
            total_amount=650.0, # CS (250) + Echo Obstétricale (400)
            mutuelle_amount=455.0, # CNSS 70%
            patient_share=195.0, # 30% ticket modérateur
            mutuelle_type='CNSS',
            payment_method='CARD',
            notes='Paiement par carte bancaire TPE'
        )
        db.session.add(inv2)
        db.session.flush()

        ii3 = InvoiceItem(invoice_id=inv2.id, act_code='CS', description='Consultation Spécialiste Gynécologue-Obstétrique', quantity=1, unit_price=250.0, total=250.0)
        ii4 = InvoiceItem(invoice_id=inv2.id, act_code='ECHO-ABD', description='Échographie Obstétricale T2', quantity=1, unit_price=400.0, total=400.0)
        pay2 = Payment(invoice_id=inv2.id, amount=195.0, payment_method='CARD', payment_date=datetime.utcnow(), recorded_by='Khadija El Idrissi', receipt_number='REC-2026-0002', notes='Paiement TPE CMI Maroc')
        db.session.add_all([ii3, ii4, pay2])

    # 9. Hospitalisation active (Chambre occupée)
    if all_beds and Admission.query.filter_by(patient_id=p3.id).count() == 0:
        bed_occupied = all_beds[0] # Lit 101-A
        bed_occupied.status = 'OCCUPIED'
        
        adm1 = Admission(
            patient_id=p3.id, # Mohamed Chaouki
            bed_id=bed_occupied.id,
            admission_date=datetime.utcnow() - timedelta(days=2),
            admitting_doctor_id=doc_benali.id,
            reason='Déséquilibre glycémique sévère et déshydratation aiguë',
            surgical_acts='Mise sous perfusion insulinique IVSE et réhydratation hydro-électrolytique',
            status='ACTIVE',
            total_stay_cost=1200.0
        )
        db.session.add(adm1)

    # 10. Pharmacie interne & Alertes Stock / Péremption
    stock_data = [
        {'code': 'MED-AMOX-1G', 'name': 'Amoxicilline 1g (Clamoxyl)', 'category': 'MEDICAMENT', 'dci': 'Amoxicilline', 'unit': 'Boîte 14 cp', 'current_quantity': 45, 'min_quantity_alert': 15, 'expiration_date': date(2027, 8, 1), 'unit_price': 54.0},
        {'code': 'MED-PARA-1G', 'name': 'Paracétamol 1g (Doliprane)', 'category': 'MEDICAMENT', 'dci': 'Paracétamol', 'unit': 'Boîte 8 cp', 'current_quantity': 120, 'min_quantity_alert': 30, 'expiration_date': date(2028, 1, 1), 'unit_price': 16.50},
        # Alerte stock faible
        {'code': 'MED-INSU-LANT', 'name': 'Insuline Lantus Solostar 100UI/ml', 'category': 'MEDICAMENT', 'dci': 'Insuline Glargine', 'unit': 'Boîte 5 stylos', 'current_quantity': 3, 'min_quantity_alert': 10, 'expiration_date': date(2027, 3, 1), 'unit_price': 420.0},
        # Alerte péremption proche (< 30 jours)
        {'code': 'MED-LOVENOX-40', 'name': 'Lovenox 4000 UI / 0.4ml', 'category': 'URGENCE', 'dci': 'Énoxaparine sodique', 'unit': 'Boîte 2 seringues', 'current_quantity': 18, 'min_quantity_alert': 10, 'expiration_date': date(2026, 12, 5), 'unit_price': 110.0},
        {'code': 'CSM-GANTS-M', 'name': 'Gants d’examen en latex poudrés (Taille M)', 'category': 'CONSOMMABLE', 'dci': 'Latex', 'unit': 'Boîte 100 unités', 'current_quantity': 80, 'min_quantity_alert': 20, 'expiration_date': date(2029, 6, 1), 'unit_price': 75.0},
        {'code': 'CSM-SER-5ML', 'name': 'Seringues stériles 3 pièces 5ml', 'category': 'CONSOMMABLE', 'dci': 'Polypropylène', 'unit': 'Boîte 100 unités', 'current_quantity': 65, 'min_quantity_alert': 25, 'expiration_date': date(2029, 12, 1), 'unit_price': 85.0},
        {'code': 'URG-ADRENALINE', 'name': 'Adrénaline 1mg/1ml injectable', 'category': 'URGENCE', 'dci': 'Épinéphrine', 'unit': 'Ampoule 1ml', 'current_quantity': 12, 'min_quantity_alert': 10, 'expiration_date': date(2027, 5, 1), 'unit_price': 22.0},
        {'code': 'MED-AUGM-1G', 'name': 'Augmentin 1g/125mg', 'category': 'MEDICAMENT', 'dci': 'Amoxicilline + Ac. Clavulanique', 'unit': 'Boîte 16 sachets', 'current_quantity': 8, 'min_quantity_alert': 15, 'expiration_date': date(2027, 2, 15), 'unit_price': 89.0}
    ]

    for s in stock_data:
        m = MedicationStock.query.filter_by(code=s['code']).first()
        if not m:
            m = MedicationStock(
                code=s['code'],
                name=s['name'],
                category=s['category'],
                dci=s['dci'],
                unit=s['unit'],
                current_quantity=s['current_quantity'],
                min_quantity_alert=s['min_quantity_alert'],
                expiration_date=s['expiration_date'],
                unit_price=s['unit_price'],
                location='Pharmacie Centrale - Rayon ' + s['category'][:3]
            )
            db.session.add(m)

    # 11. Planning des gardes du personnel (Staff Shift)
    shift1 = StaffShift(user_id=doc_benali.id, shift_date=today, shift_type='GARDE_NUIT', notes='Garde de nuit urgences cardiologiques')
    shift2 = StaffShift(user_id=created_users['infirmier@clinique-rif-nador.ma'].id, shift_date=today, shift_type='GARDE_NUIT', notes='Équipe de nuit hospitalisation')
    shift3 = StaffShift(user_id=doc_amrani.id, shift_date=today + timedelta(days=2), shift_type='ASTREINTE_WEEKEND', notes='Astreinte chirurgicale')
    db.session.add_all([shift1, shift2, shift3])

    # 12. Audit Logs d'initialisation CNDP
    audit1 = AuditLog(
        user_name='Système',
        user_role='SYSTEM',
        action='CREATE',
        entity_type='SYSTEM',
        details='Initialisation complète du SIH de la Clinique Médico-Chirurgicale du Rif - Nador avec 15 patients et données de démonstration conformes CNDP.',
        ip_address='127.0.0.1',
        timestamp=datetime.utcnow()
    )
    db.session.add(audit1)

    db.session.commit()
    print("Seed data terminé avec 100% de succès !")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_database()
