-- ============================================================================
-- CLINIQUE MÉDICO-CHIRURGICALE DU RIF - NADOR (MAROC)
-- مصحة الريف للطب والجراحة - الناظور
-- SCHEMA COMPLET ET DONNÉES DE DÉMONSTRATION (SEED DATA)
-- Compatible PostgreSQL (Neon, Supabase) & SQLite
-- ============================================================================

-- 1. TABLE UTILISATEURS & AUTHENTIFICATION (RBAC)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    full_name_ar VARCHAR(120),
    role VARCHAR(30) NOT NULL, -- admin, doctor, nurse, receptionist, pharmacist, lab
    specialty VARCHAR(100),
    phone VARCHAR(30),
    inpe VARCHAR(50), -- Identifiant National des Professionnels de Santé
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLE DOSSIER PATIENT (DME)
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_number VARCHAR(50) UNIQUE NOT NULL, -- e.g. RIF-2026-0001
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    first_name_ar VARCHAR(100),
    last_name_ar VARCHAR(100),
    cin VARCHAR(20) UNIQUE NOT NULL,
    birth_date VARCHAR(20) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(120),
    address TEXT NOT NULL,
    neighborhood VARCHAR(100), -- Hay Al Matar, Bouizazarène, Selouane, etc.
    blood_group VARCHAR(10),
    mutuelle VARCHAR(50) NOT NULL, -- CNOPS, CNSS, FAR, MGPAP, Saham, Wafa Assurance, AtlantaSanad, Privé
    mutuelle_number VARCHAR(50),
    allergies TEXT,
    medical_antecedents TEXT,
    surgical_antecedents TEXT,
    family_antecedents TEXT,
    is_archived BOOLEAN DEFAULT 0,
    archived_at TIMESTAMP,
    archive_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLE SALLE D'ATTENTE EN TEMPS RÉEL
CREATE TABLE IF NOT EXISTS waiting_room (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    doctor_id INTEGER REFERENCES users(id),
    status VARCHAR(30) DEFAULT 'waiting', -- waiting, triage, consultation, exam, completed
    priority VARCHAR(20) DEFAULT 'routine', -- routine, urgent, critical
    ticket_number VARCHAR(20) NOT NULL,
    arrival_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    call_time TIMESTAMP,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    notes TEXT
);

-- 4. TABLE RENDEZ-VOUS (AGENDA MULTI-PRATICIENS)
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    doctor_id INTEGER NOT NULL REFERENCES users(id),
    scheduled_date VARCHAR(20) NOT NULL,
    scheduled_time VARCHAR(20) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'scheduled', -- scheduled, confirmed, in_consultation, completed, cancelled, no_show
    reminder_sent BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. TABLE CONSTANTES VITALES (TRIAGE)
CREATE TABLE IF NOT EXISTS vital_signs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    nurse_id INTEGER REFERENCES users(id),
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    heart_rate INTEGER,
    temperature REAL,
    weight REAL,
    height REAL,
    bmi REAL,
    spo2 INTEGER,
    blood_sugar REAL,
    pain_scale INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. TABLE CONSULTATIONS MÉDICALES (CIM-10)
CREATE TABLE IF NOT EXISTS consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    doctor_id INTEGER NOT NULL REFERENCES users(id),
    consultation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chief_complaint TEXT NOT NULL,
    clinical_examination TEXT,
    diagnosis_code VARCHAR(30), -- CIM-10 (e.g. I10, E11, J06.9)
    diagnosis_label TEXT,
    notes TEXT,
    follow_up_date VARCHAR(20)
);

-- 7. TABLE PRESCRIPTIONS (ORDONNANCES)
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id INTEGER REFERENCES consultations(id),
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    doctor_id INTEGER NOT NULL REFERENCES users(id),
    prescription_code VARCHAR(50) UNIQUE NOT NULL,
    verification_hash VARCHAR(100),
    instructions TEXT,
    duration_days INTEGER DEFAULT 7,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. TABLE LIGNES D'ORDONNANCE
CREATE TABLE IF NOT EXISTS prescription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER NOT NULL REFERENCES prescriptions(id),
    medication_name VARCHAR(150) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration VARCHAR(50) NOT NULL,
    instructions TEXT
);

-- 9. TABLE GESTION ÉLECTRONIQUE DES DOCUMENTS (GED MÉDICALE)
CREATE TABLE IF NOT EXISTS medical_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    uploader_id INTEGER REFERENCES users(id),
    document_type VARCHAR(50) NOT NULL, -- radio, scanner, biology, cin, prise_en_charge, consent, other
    title VARCHAR(200) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    is_archived BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. TABLE CHAMBRES & LITS (HOSPITALISATION)
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number VARCHAR(20) UNIQUE NOT NULL,
    floor INTEGER NOT NULL,
    department VARCHAR(50) NOT NULL, -- chirurgie, medecine, maternite, soins_intensifs
    room_type VARCHAR(30) NOT NULL, -- standard, double, vip, icu
    daily_rate REAL DEFAULT 400.0
);

CREATE TABLE IF NOT EXISTS beds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    bed_number VARCHAR(20) NOT NULL,
    status VARCHAR(30) DEFAULT 'available', -- available, occupied, cleaning, reserved
    notes TEXT
);

-- 11. TABLE ADMISSIONS & SÉJOURS
CREATE TABLE IF NOT EXISTS admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    bed_id INTEGER NOT NULL REFERENCES beds(id),
    doctor_id INTEGER NOT NULL REFERENCES users(id),
    admission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    discharge_date TIMESTAMP,
    reason TEXT NOT NULL,
    discharge_summary TEXT,
    status VARCHAR(30) DEFAULT 'active' -- active, discharged
);

-- 12. TABLE FACTURATION & MUTUELLES MAROCAINES
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number VARCHAR(50) UNIQUE NOT NULL, -- RIF-FACT-2026-XXXX
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    created_by INTEGER REFERENCES users(id),
    total_amount REAL NOT NULL,
    mutuelle_name VARCHAR(50) NOT NULL,
    mutuelle_coverage_percent REAL NOT NULL, -- e.g. 80% (CNOPS), 70% (CNSS), 90% (FAR)
    mutuelle_share REAL NOT NULL,
    patient_share REAL NOT NULL,
    status VARCHAR(30) DEFAULT 'pending', -- pending, paid, partial, cancelled, archived
    is_archived BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id),
    act_code VARCHAR(30) NOT NULL, -- NGAP / Nomenclature Marocaine (e.g. C, CS, K15, KE20)
    description VARCHAR(200) NOT NULL,
    unit_price REAL NOT NULL,
    quantity INTEGER DEFAULT 1,
    total REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id),
    amount REAL NOT NULL,
    payment_method VARCHAR(30) NOT NULL, -- cash, card, cheque, bank_transfer
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    cashier_id INTEGER REFERENCES users(id),
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_cash_closures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    closure_date VARCHAR(20) NOT NULL,
    cashier_id INTEGER NOT NULL REFERENCES users(id),
    total_cash REAL DEFAULT 0.0,
    total_card REAL DEFAULT 0.0,
    total_cheque REAL DEFAULT 0.0,
    total_transfer REAL DEFAULT 0.0,
    grand_total REAL DEFAULT 0.0,
    declared_cash REAL DEFAULT 0.0,
    discrepancy REAL DEFAULT 0.0,
    notes TEXT,
    closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. TABLE GESTION DE PHARMACIE & STOCKS MÉDICAUX
CREATE TABLE IF NOT EXISTS medication_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL, -- antibiotique, antalgique, anti-inflammatoire, consommable, anesthésique
    dosage VARCHAR(100),
    unit VARCHAR(30) NOT NULL, -- boîte, flacon, ampoule, sachet
    current_stock INTEGER NOT NULL DEFAULT 0,
    min_stock_alert INTEGER NOT NULL DEFAULT 10,
    unit_price_mad REAL NOT NULL,
    expiry_date VARCHAR(20) NOT NULL,
    batch_number VARCHAR(50),
    supplier VARCHAR(100) DEFAULT 'Pharmacie Centrale Nador',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_id INTEGER NOT NULL REFERENCES medication_stock(id),
    movement_type VARCHAR(20) NOT NULL, -- IN, OUT
    quantity INTEGER NOT NULL,
    reason VARCHAR(100),
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. TABLE PERSONNEL RH & PLANNING DES GARDES
CREATE TABLE IF NOT EXISTS staff_shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    shift_date VARCHAR(20) NOT NULL,
    shift_type VARCHAR(30) NOT NULL, -- morning, afternoon, night, on_call
    department VARCHAR(50) NOT NULL,
    is_confirmed BOOLEAN DEFAULT 1,
    notes TEXT
);

-- 15. TABLE JOURNAL D'AUDIT (CONFORMITÉ CNDP LOI 09-08)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    username VARCHAR(80),
    role VARCHAR(30),
    action VARCHAR(50) NOT NULL, -- LOGIN, VIEW, CREATE, UPDATE, ARCHIVE, RESTORE, EXPORT
    entity_type VARCHAR(50) NOT NULL, -- Patient, Consultation, Prescription, Invoice, User
    entity_id VARCHAR(50),
    details TEXT,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INSERTION DES UTILISATEURS DE TEST (COMPTES DÉMO CLINIQUES NADOR)
-- Mot de passe pour tous les comptes de test : "demo123"
-- Hash SHA256 : a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
-- ============================================================================

INSERT INTO users (username, email, password_hash, full_name, full_name_ar, role, specialty, phone, inpe) VALUES
('admin', 'directeur@clinique-rif-nador.ma', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Dr. Rachid Benali', 'د. رشيد بنعلي', 'admin', 'Chirurgie Générale & Direction', '+212 5 36 60 11 22', '053421987'),
('dr.amrani', 'dr.amrani@clinique-rif-nador.ma', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Dr. Youssef Amrani', 'د. يوسف العمراني', 'doctor', 'Cardiologie & Médecine Interne', '+212 6 61 23 45 67', '053421988'),
('dr.tazi', 'dr.tazi@clinique-rif-nador.ma', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Dr. Fatima Tazi', 'د. فاطمة التازي', 'doctor', 'Gynécologie Obstétrique', '+212 6 62 34 56 78', '053421989'),
('inf.karim', 'karim.inf@clinique-rif-nador.ma', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Karim Mansouri', 'كريم المنصوري', 'nurse', 'Soins Intensifs & Triage', '+212 6 70 12 34 56', NULL),
('sec.salma', 'accueil@clinique-rif-nador.ma', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Salma El Fassi', 'سلمى الفاسي', 'receptionist', 'Accueil & Facturation', '+212 5 36 60 11 20', NULL),
('pharma.omar', 'pharmacie@clinique-rif-nador.ma', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Dr. Omar Berrada', 'د. عمر برادة', 'pharmacist', 'Pharmacie Clinique', '+212 6 63 98 76 54', '053421990'),
('lab.nawal', 'labo@clinique-rif-nador.ma', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Nawal Chraibi', 'نوال الشرايبي', 'lab', 'Biologie & Analyses Médicales', '+212 6 64 11 22 33', NULL);

-- ============================================================================
-- INSERTION DES 15 PATIENTS RÉALISTES DE NADOR ET ENVIRONS
-- ============================================================================

INSERT INTO patients (file_number, first_name, last_name, first_name_ar, last_name_ar, cin, birth_date, gender, phone, email, address, neighborhood, blood_group, mutuelle, mutuelle_number, allergies, medical_antecedents, surgical_antecedents, family_antecedents) VALUES
('RIF-2026-0001', 'Mohammed', 'El Amrani', 'محمد', 'العمراني', 'S548912', '1975-04-12', 'M', '+212 6 61 12 34 56', 'm.amrani@gmail.com', 'Avenue des FAR, Résidence Al Manar', 'Hay Al Matar', 'O+', 'CNOPS', 'CN-894210', 'Pénicilline', 'Hypertension artérielle, Diabète Type 2', 'Appendicectomie (1998)', 'Diabète maternel'),
('RIF-2026-0002', 'Fatima', 'Boudraa', 'فاطمة', 'بودراع', 'S612345', '1982-08-25', 'F', '+212 6 62 45 67 89', 'f.boudraa@outlook.ma', 'Rue Ibn Khaldoun, N° 14', 'Bouizazarène', 'A+', 'CNSS', 'CS-771209', 'Aspirine, AINS', 'Asthme modéré intermittent', 'Césarienne (2012)', 'Aucun'),
('RIF-2026-0003', 'Abdelkader', 'Zemmouri', 'عبد القادر', 'الزموري', 'S421098', '1960-11-03', 'M', '+212 6 63 78 90 12', 'a.zemmouri@menara.ma', 'Quartier Al Wifaq, Imm B', 'Selouane', 'B+', 'FAR', 'FAR-990145', 'Aucune', 'Insuffisance coronarienne, Dyslipidémie', 'Pontage aorto-coronarien (2018)', 'Infarctus paternel à 55 ans'),
('RIF-2026-0004', 'Naima', 'Kaddouri', 'نعيمة', 'قدوري', 'S789012', '1990-02-17', 'F', '+212 6 64 32 10 98', 'naima.kadd@gmail.com', 'Bd Mohamed V, Résidence Ennakhil', 'Beni Ansar', 'AB+', 'MGPAP', 'MG-334187', 'Sulfamides', 'Migraine chronique', 'Aucun', 'HTA'),
('RIF-2026-0005', 'Karim', 'Ait Ouahi', 'كريم', 'أيت واحي', 'S334567', '1988-06-30', 'M', '+212 6 65 99 88 77', 'karim.ait@gmail.com', 'Lotissement Al Firdaous', 'Zeghanghane', 'O-', 'Saham', 'SH-551092', 'Aucune', 'Ulcère gastro-duodénal', 'Ostéosynthèse tibia droit (2015)', 'Ulcère gastrique'),
('RIF-2026-0006', 'Meryem', 'Touzani', 'مريم', 'التوزاني', 'S890123', '1995-12-08', 'F', '+212 6 66 11 22 44', 'meryem.t@yahoo.fr', 'Rue Taouima, N° 88', 'Taouima', 'A-', 'Wafa Assurance', 'WA-881230', 'Pollen, Acariens', 'Rhinite allergique', 'Amydalectomie (2005)', 'Asthme'),
('RIF-2026-0007', 'Hassan', 'Boulahya', 'حسن', 'بولحية', 'S123789', '1952-09-14', 'M', '+212 6 67 44 55 66', 'hassan.bou@gmail.com', 'Avenue Zerktouni', 'Hay Al Matar', 'B-', 'CNOPS', 'CN-441029', 'Iode', 'BPCO stade II, Fibrillation auriculaire', 'Cholécystectomie (2010)', 'Cardiopathie'),
('RIF-2026-0008', 'Souad', 'El Idrissi', 'سعاد', 'الإدريسي', 'S901234', '1979-03-21', 'F', '+212 6 68 77 88 99', 'souad.idrissi@gmail.com', 'Rue Casablanca, N° 45', 'Al Khattabi', 'O+', 'CNSS', 'CS-889123', 'Latex', 'Hypothyroïdie sous L-Thyroxine', 'Hystérectomie (2020)', 'Cancer du sein maternel'),
('RIF-2026-0009', 'Youssef', 'Benali', 'يوسف', 'بنعلي', 'S456123', '2001-07-19', 'M', '+212 6 69 00 11 22', 'youssef.benali@gmail.com', 'Bd Hassan I, Imm Jasmine', 'Laârassi', 'A+', 'Privé', NULL, 'Aucune', 'Gastrite aiguë', 'Fracture radius gauche (2019)', 'Aucun'),
('RIF-2026-0010', 'Khadija', 'Meziane', 'خديجة', 'مزيان', 'S567890', '1968-10-05', 'F', '+212 6 70 33 44 55', 'khadija.m@menara.ma', 'Rue Tanger, N° 12', 'Oulad Mimoun', 'AB-', 'AtlantaSanad', 'AS-441982', 'Aspirine', 'Polyarthrite rhumatoïde', 'Prothèse totale de genou gauche', 'Arthrose'),
('RIF-2026-0011', 'Tariq', 'Choukri', 'طارق', 'شكري', 'S678901', '1984-05-11', 'M', '+212 6 71 66 77 88', 'tariq.ch@gmail.com', 'Route d’Al Hoceima, Km 4', 'Selouane', 'O+', 'CNOPS', 'CN-662391', 'Aucune', 'Lombalgie chronique L4-L5', 'Hernie discale opérée (2021)', 'Lombalgies'),
('RIF-2026-0012', 'Zineb', 'El Khattabi', 'زينب', 'الخطابي', 'S789456', '1992-01-29', 'F', '+212 6 72 88 99 00', 'zineb.kh@gmail.com', 'Hay Riad, Villa 24', 'Hay Al Matar', 'A+', 'CNSS', 'CS-112948', 'Céphalosporines', 'Anémie ferriprive', 'Césarienne (2023)', 'Anémie'),
('RIF-2026-0013', 'Mustapha', 'Azirar', 'مصطفى', 'أزيرار', 'S234567', '1958-12-18', 'M', '+212 6 73 11 33 55', 'mustapha.az@gmail.com', 'Avenue Mohammed VI', 'Bouizazarène', 'B+', 'FAR', 'FAR-332019', 'Aucune', 'Diabète type 2, Rétinopathie', 'Cataracte bilatérale (2022)', 'Diabète'),
('RIF-2026-0014', 'Salima', 'Berrada', 'سليمة', 'برادة', 'S345678', '2004-09-02', 'F', '+212 6 74 22 44 66', 'salima.b@gmail.com', 'Rue Fès, Résidence El Majd', 'Beni Ansar', 'O-', 'MGPAP', 'MG-992381', 'Amoxicilline', 'Asthme d’effort', 'Aucun', 'Asthme'),
('RIF-2026-0015', 'Bilal', 'Hammouda', 'بلال', 'حمودة', 'S890567', '1986-04-14', 'M', '+212 6 75 55 66 77', 'bilal.h@gmail.com', 'Bd Al Qods, Imm C', 'Zeghanghane', 'A+', 'Privé', NULL, 'Aucune', 'Calculs rénaux récidivants', 'Lithotripsie extracorporelle (2024)', 'Lithiases');

-- ============================================================================
-- INSERTION DES CHAMBRES ET LITS
-- ============================================================================

INSERT INTO rooms (room_number, floor, department, room_type, daily_rate) VALUES
('101', 1, 'Chirurgie', 'standard', 350.0),
('102', 1, 'Chirurgie', 'double', 250.0),
('103', 1, 'Chirurgie', 'vip', 750.0),
('201', 2, 'Médecine Interne', 'standard', 350.0),
('202', 2, 'Médecine Interne', 'double', 250.0),
('203', 2, 'Médecine Interne', 'vip', 750.0),
('301', 3, 'Maternité', 'vip', 800.0),
('302', 3, 'Maternité', 'standard', 400.0),
('401', 4, 'Soins Intensifs (USI)', 'icu', 1500.0);

INSERT INTO beds (room_id, bed_number, status, notes) VALUES
(1, '101-A', 'available', 'Prêt pour admission chirurgicale'),
(2, '102-A', 'occupied', 'Patient admis post-opératoire'),
(2, '102-B', 'available', 'Désinfecté'),
(3, '103-VIP', 'available', 'Chambre de luxe avec salon'),
(4, '201-A', 'cleaning', 'Désinfection en cours'),
(5, '202-A', 'occupied', 'Suivi cardiologique'),
(5, '202-B', 'reserved', 'Réservé pour transfert du 13/11'),
(6, '203-VIP', 'available', 'Prêt'),
(7, '301-VIP', 'occupied', 'Patiente césarienne J+1'),
(8, '302-A', 'available', 'Chambre maternité prête'),
(9, '401-ICU1', 'occupied', 'Patient sous surveillance ECG & O2'),
(9, '401-ICU2', 'available', 'Lit réanimation équipé');

-- ============================================================================
-- INSERTION DU STOCK PHARMACEUTIQUE (MÉDICAMENTS & CONSOMMABLES)
-- ============================================================================

INSERT INTO medication_stock (code, name, category, dosage, unit, current_stock, min_stock_alert, unit_price_mad, expiry_date, batch_number) VALUES
('MED-001', 'Amoxicilline + Acide Clavulanique (Augmentin)', 'antibiotique', '1g / 125mg', 'boîte', 48, 15, 68.50, '2027-05-30', 'LOT-AUG-2024-88'),
('MED-002', 'Paracétamol Injectable (Perfalgan)', 'antalgique', '1g / 100ml', 'flacon', 120, 30, 24.00, '2027-11-15', 'LOT-PERF-5541'),
('MED-003', 'Ceftriaxone IV (Rocéphine)', 'antibiotique', '1g poudre IV', 'flacon', 35, 10, 85.00, '2026-12-31', 'LOT-CEF-9901'),
('MED-004', 'Enoxaparine (Lovenox)', 'anticoagulant', '4000 UI / 0.4ml', 'boîte', 22, 12, 185.00, '2026-08-20', 'LOT-LOV-4421'),
('MED-005', 'Oméprazole Injectable', 'anti-ulcéreux', '40mg IV', 'ampoule', 60, 20, 45.00, '2027-03-10', 'LOT-OMP-1120'),
('MED-006', 'Sérum Salé Isotonique 0.9%', 'soluté', '500ml poche', 'poche', 200, 50, 12.50, '2028-01-01', 'LOT-SSI-0091'),
('MED-007', 'Compressez Stériles 10x10cm', 'consommable', 'Boîte de 100', 'boîte', 80, 25, 38.00, '2029-06-30', 'LOT-CMP-2024'),
('MED-008', 'Gants d’Examen Sans Poudre (Taille M)', 'consommable', 'Boîte de 100', 'boîte', 150, 40, 55.00, '2029-12-31', 'LOT-GNT-M12'),
('MED-009', 'Adrénaline 1mg/ml', 'urgence', '1mg ampoule', 'ampoule', 18, 10, 15.00, '2026-10-31', 'LOT-ADR-3310'),
('MED-010', 'Morphine Chlorhydrate', 'stupéfiant', '10mg/ml', 'ampoule', 8, 5, 32.00, '2027-02-28', 'LOT-MOR-0087');

-- ============================================================================
-- INSERTION DES CONSTANTES VITALES, SALLE D'ATTENTE & RENDEZ-VOUS DU JOUR
-- ============================================================================

INSERT INTO vital_signs (patient_id, nurse_id, systolic_bp, diastolic_bp, heart_rate, temperature, weight, height, bmi, spo2, blood_sugar, pain_scale) VALUES
(1, 4, 138, 85, 76, 36.8, 82.0, 1.75, 26.8, 98, 1.35, 2),
(2, 4, 122, 78, 80, 37.1, 65.0, 1.63, 24.5, 99, 0.95, 1),
(3, 4, 145, 92, 88, 36.9, 78.0, 1.70, 27.0, 96, 1.60, 4),
(4, 4, 115, 75, 72, 36.7, 58.0, 1.65, 21.3, 99, 0.90, 0);

INSERT INTO waiting_room (patient_id, doctor_id, status, priority, ticket_number, notes) VALUES
(1, 2, 'in_consultation', 'routine', 'T-001', 'Suivi cardiologie et HTA'),
(2, 3, 'triage', 'routine', 'T-002', 'Contrôle prénatal 6ème mois'),
(3, 2, 'waiting', 'urgent', 'T-003', 'Douleur thoracique atypique - Priorité cardiologie'),
(4, 3, 'waiting', 'routine', 'T-004', 'Suivi gynécologique périodique');

INSERT INTO appointments (patient_id, doctor_id, scheduled_date, scheduled_time, reason, status) VALUES
(1, 2, '2026-11-12', '09:00', 'Bilan tensionnel semestriel', 'in_consultation'),
(2, 3, '2026-11-12', '10:00', 'Échographie morphologique obstétricale', 'confirmed'),
(3, 2, '2026-11-12', '11:15', 'Douleur thoracique post-effort', 'scheduled'),
(5, 1, '2026-11-12', '14:30', 'Contrôle cicatrice abdominale', 'confirmed'),
(6, 2, '2026-11-12', '16:00', 'Palpitations et essoufflement d’effort', 'scheduled');

-- ============================================================================
-- INSERTION DES CONSULTATIONS, PRESCRIPTIONS & FACTURES
-- ============================================================================

INSERT INTO consultations (patient_id, doctor_id, chief_complaint, clinical_examination, diagnosis_code, diagnosis_label, notes, follow_up_date) VALUES
(1, 2, 'Céphalées matinales et vertiges occasionnels', 'TA 138/85 mmHg, bruits du coeur réguliers, pas de souffle. Auscultation pulmonaire libre.', 'I10', 'Hypertension artérielle essentielle', 'Renforcement du traitement anti-hypertenseur et adaptation du régime hyposodé.', '2026-12-12'),
(3, 2, 'Précordialgies d’allure coronarienne à la marche rapide', 'TA 145/92 mmHg, FC 88 bpm. ECG de repos montre des ondes T négatives en V5-V6.', 'I20.9', 'Angine de poitrine, sans précision', 'Hospitalisation en cardiologie recommandée pour surveillance enzymatique et coroscanner.', '2026-11-15');

INSERT INTO prescriptions (consultation_id, patient_id, doctor_id, prescription_code, verification_hash, instructions, duration_days) VALUES
(1, 1, 2, 'ORD-2026-0001', 'HASH-ORD-AMRANI-0001-NADOR-OK', 'Prendre les comprimés le matin à jeun avec un verre d’eau.', 30);

INSERT INTO prescription_items (prescription_id, medication_name, dosage, frequency, duration, instructions) VALUES
(1, 'Amlodipine (Amlor)', '5mg', '1 comprimé par jour', '30 jours', 'Le matin au réveil'),
(1, 'Périndopril (Coversyl)', '5mg', '1 comprimé par jour', '30 jours', 'Le matin'),
(1, 'Atorvastatine (Tahor)', '20mg', '1 comprimé par jour', '30 jours', 'Le soir au coucher');

INSERT INTO invoices (invoice_number, patient_id, created_by, total_amount, mutuelle_name, mutuelle_coverage_percent, mutuelle_share, patient_share, status) VALUES
('RIF-FACT-2026-0001', 1, 5, 400.0, 'CNOPS', 80.0, 320.0, 80.0, 'paid'),
('RIF-FACT-2026-0002', 2, 5, 600.0, 'CNSS', 70.0, 420.0, 180.0, 'paid'),
('RIF-FACT-2026-0003', 3, 5, 1200.0, 'FAR', 90.0, 1080.0, 120.0, 'pending');

INSERT INTO invoice_items (invoice_id, act_code, description, unit_price, quantity, total) VALUES
(1, 'CS', 'Consultation Médecin Spécialiste Cardiologue', 250.0, 1, 250.0),
(1, 'ECG', 'Électrocardiogramme standard 12 dérivations', 150.0, 1, 150.0),
(2, 'ECHO-OBS', 'Échographie obstétricale morphologique 2D/3D', 600.0, 1, 600.0),
(3, 'CS', 'Consultation Spécialisée Urgence Cardio', 300.0, 1, 300.0),
(3, 'BIO-TROP', 'Dosage sanguin Troponine ultrasensible + CPK-MB', 450.0, 1, 450.0),
(3, 'RX-THOR', 'Radiographie pulmonaire face et profil', 450.0, 1, 450.0);

INSERT INTO payments (invoice_id, amount, payment_method, receipt_number, cashier_id) VALUES
(1, 80.0, 'cash', 'REC-2026-0001', 5),
(2, 180.0, 'card', 'REC-2026-0002', 5);

INSERT INTO daily_cash_closures (closure_date, cashier_id, total_cash, total_card, total_cheque, total_transfer, grand_total, declared_cash, discrepancy, notes) VALUES
('2026-11-11', 5, 2450.0, 1800.0, 500.0, 0.0, 4750.0, 2450.0, 0.0, 'Clôture de caisse du 11/11/2026 sans écart.');

-- ============================================================================
-- INSERTION DES LOGS D'AUDIT CNDP LOI 09-08
-- ============================================================================

INSERT INTO audit_logs (user_id, username, role, action, entity_type, entity_id, details, ip_address) VALUES
(1, 'admin', 'admin', 'LOGIN', 'User', '1', 'Connexion réussie Administrateur Directeur', '127.0.0.1'),
(5, 'sec.salma', 'receptionist', 'CREATE', 'Patient', '1', 'Enregistrement nouveau dossier patient RIF-2026-0001', '127.0.0.1'),
(2, 'dr.amrani', 'doctor', 'CREATE', 'Consultation', '1', 'Création consultation cardiologique pour Mohammed El Amrani', '127.0.0.1'),
(2, 'dr.amrani', 'doctor', 'CREATE', 'Prescription', '1', 'Ordonnance ORD-2026-0001 générée avec signature numérique', '127.0.0.1'),
(5, 'sec.salma', 'receptionist', 'CREATE', 'Invoice', '1', 'Facturation RIF-FACT-2026-0001 prise en charge CNOPS 80%', '127.0.0.1');

-- FIN DU FICHIER SCHEMA ET DONNEES DE SEED
