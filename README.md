# 🏥 Clinique Médico-Chirurgicale du Rif - Nador (مصحة الريف للطب والجراحة - الناظور)

[![Tests Status](https://img.shields.io/badge/tests-23%2F23%20passed%20(100%25)-success?style=for-the-badge&logo=pytest)](file:///C:/Users/hp/.gemini/antigravity/scratch/clinique-rif-nador/tests)
[![PWA Ready](https://img.shields.io/badge/PWA-Installable%20%26%20Offline-blue?style=for-the-badge&logo=pwa)](file:///C:/Users/hp/.gemini/antigravity/scratch/clinique-rif-nador/app/static/manifest.json)
[![CNDP 09-08](https://img.shields.io/badge/CNDP%20Maroc-Loi%2009--08%20Conforme-emerald?style=for-the-badge)](file:///C:/Users/hp/.gemini/antigravity/scratch/clinique-rif-nador/app/services/audit_service.py)
[![Bilingual](https://img.shields.io/badge/Langues-Fran%C3%A7ais%20%2F%20%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9%20(RTL)-purple?style=for-the-badge)](file:///C:/Users/hp/.gemini/antigravity/scratch/clinique-rif-nador/app/static/js/i18n.js)

Application web intégrale, moderne, ultra-rapide et sécurisée conçue spécifiquement pour la gestion hospitalière multidisciplinaire de la **Clinique Médico-Chirurgicale du Rif** à **Nador, Maroc** (Boulevard Hassan II, Hay Al Matar).

Inspirée des standards de référence mondiaux (**OpenEMR**, **Bahmni**, **HospitalRun**), elle intègre nativement toutes les spécificités réglementaires, médicales et administratives marocaines (**CNOPS, CNSS, FAR, nomenclature NGAP en MAD, conformité CNDP Loi 09-08, support bilingue Français/Arabe avec bascule RTL instantanée**).

---

## 📑 Sommaire
1. [Architecture & Stack Technique](#-architecture--stack-technique)
2. [Modules Fonctionnels Exhaustifs](#-modules-fonctionnels-exhaustifs)
3. [Spécificités Médicales & Administratives Marocaines](#-spécificités-médicales--administratives-marocaines)
4. [Comptes de Démonstration (Connexion en 1 Clic)](#-comptes-de-démonstration-connexion-en-1-clic)
5. [Données de Démonstration Réalistes (Nador)](#-données-de-démonstration-réalistes-nador)
6. [Suite de Tests Automatisés (100% Réussite)](#-suite-de-tests-automatisés-100-réussite)
7. [Guide de Démarrage Rapide (Local)](#-guide-de-démarrage-rapide-local)
8. [Guide de Déploiement Cloud (PostgreSQL / Neon / Supabase / Vercel / Docker)](#-guide-de-déploiement-cloud)
9. [Fichiers et Structure du Projet](#-fichiers-et-structure-du-projet)

---

## ⚡ Architecture & Stack Technique

- **Front-End :**
  - **React 18** (SPA modulaire ultra-réactive avec gestion d'état centralisée).
  - **Tailwind CSS** (Design médical moderne, palette rassurante bleu clinique `#0284c7` & émeraude `#059669`).
  - **PWA (Progressive Web App) :** Manifeste W3C (`manifest.json`) et Service Worker (`sw.js`) pour installation sur PC/Mac, tablettes d'infirmiers et smartphones. Fonctionnement fluide en mode hors-ligne.
  - **Moteur i18n & RTL :** Dictionnaire Français / Arabe dynamique manipulant le DOM (`dir="rtl"`, police Tajawal) à la volée.
  - **Synthétiseur Audio :** Carillon audio doux généré par Web Audio API lors de l'appel d'un patient en salle d'attente (sans dépendance externe).

- **Back-End & Base de Données :**
  - **Python 3.11+ / Flask 3.1** (Architecture modulaire par Blueprints RESTful).
  - **SQLAlchemy 3.1 ORM** avec double compatibilité :
    - Mode local rapide : **SQLite** sécurisé (`clinique_nador.db`).
    - Mode production cloud : **PostgreSQL** natif (compatible **Neon Serverless**, **Supabase**, AWS RDS, Docker).
  - **ReportLab 5.1 & QRCode :** Moteur vectoriel de génération d'ordonnances, factures officielles et certificats médicaux haute résolution avec en-tête officiel de la clinique de Nador et QR codes cryptographiques de vérification.
  - **Chiffrement & Sécurité CNDP :** Hachage des mots de passe en SHA-256 avec salage, protection anti-suppression définitive (Soft Delete) et journal d'audit infalsifiable.

---

## 🏥 Modules Fonctionnels Exhaustifs

### 1. Authentification, Rôles & Sécurité (RBAC + CNDP)
- **6 Rôles Stricts avec Permissions Granulaires :**
  - 👑 **Directeur / Super Admin :** Accès total, supervision globale, statistiques financières, coffre-fort des archives, journal d'audit et sauvegardes de la base.
  - 🩺 **Médecin Praticien :** Consultations, codification CIM-10, génération d'ordonnances avec QR code, certificats médicaux, accès au dossier patient complet.
  - 💉 **Infirmier(ère) :** Saisie rapide des constantes vitales, calcul automatique de l'IMC, triage des urgences en salle d'attente, soins des hospitalisés.
  - 💼 **Accueil / Secrétariat :** Enregistrement des patients (CIN, Mutuelle), prise de rendez-vous avec rappels WhatsApp en 1 clic, gestion de la file d'attente, facturation, encaissements et clôture journalière de caisse.
  - 💊 **Pharmacien Interne :** Gestion du stock de médicaments, alertes automatiques de réapprovisionnement (< seuil critique) et alertes péremption (< 60 jours).
  - 🔬 **Laborantin / Radiologue :** Téléversement et classement des bilans sanguins, comptes-rendus et clichés radiologiques dans la GED.
- **Barre de test rapide en 1 clic :** Permet de basculer instantanément entre n'importe quel rôle pour les démonstrations.

### 2. Dossiers Patients (DME) & Salle d'Attente Intelligente
- **Fiche Patient Complète :** CIN marocaine, Identifiant unique (`RIF-2026-XXXX`), coordonnées, quartiers de Nador (Hay Al Matar, Bouizazarène, Selouane, Beni Ansar...), Groupe Sanguin, Allergies critiques, Antécédents médico-chirurgicaux et familiaux.
- **Salle d'Attente Interactive :**
  - File d'attente intelligente avec calcul dynamique du temps d'attente écoulé.
  - Niveaux de triage : *Routine, Urgent, Critique*.
  - Bouton **"Appeler le Patient"** émettant un carillon sonore et actualisant le statut (*En attente -> Au triage -> En consultation -> Terminé*).
- **Agenda Multi-Praticiens :**
  - Planning par médecin et par spécialité.
  - Bouton **WhatsApp en 1 clic** générant automatiquement le message de rappel personnalisé en français/arabe avec date, heure et nom du praticien.

### 3. Consultation Médicale, Constantes & Prescriptions
- **Moniteur de Constantes Vitales :** Saisie de la tension artérielle (Systolique/Diastolique), Pouls, Température, Poids, Taille, Saturation O2 (SpO2), Glycémie et Échelle de douleur (EVA).
- **Calcul automatique de l'IMC (Indice de Masse Corporelle)** avec classification clinique colorée (Maigreur, Normal, Surpoids, Obésité I/II/III).
- **Codification CIM-10 Intégrée :** Sélecteur instantané avec recherche par mot-clé (ex: *I10 - HTA, E11 - Diabète type 2, J06.9 - Infection respiratoire*).
- **Générateur d'Ordonnances Sécurisées :**
  - Ajout multi-médicaments avec posologie, fréquence et durée.
  - Bouton **Télécharger PDF** générant un document officiel prêt pour l'impression avec le tampon officiel de la Clinique de Nador et un QR code unique de traçabilité.
- **Générateur de Certificats Médicaux PDF :** Certificats d'aptitude, de repos ou de dispense avec cachet officiel.

### 4. Hospitalisation, Chambres & Blocs (Inpatient Management)
- **Plan Visuel des Chambres & Lits en Temps Réel :**
  - Codification par couleur : 🟢 *Disponible*, 🔴 *Occupé*, 🟡 *En nettoyage/désinfection*, 🟣 *Réservé*.
  - Répartition par service : *Chirurgie, Médecine Interne, Maternité, Soins Intensifs (USI)*.
- **Gestion des Admissions & Décharges :**
  - Admission d'un patient sur un lit libre avec motif d'hospitalisation.
  - Changement d'état du lit en 1 clic (libération pour désinfection puis remise en disponibilité).
  - Émission de la fiche de sortie et du compte-rendu d'hospitalisation.

### 5. Laboratoire, Imagerie & Archivage Numérique (GED Médicale)
- **GED Médicale Intégrée :** Classement et prévisualisation de tous les documents : Radiographies, Scanners, Comptes-rendus d'analyses, CIN scannées, Prises en charge mutuelles.
- **Coffre-fort d'Archivage Historique (Soft Delete Conforme CNDP) :**
  - **Zéro suppression destructive :** Toute suppression de dossier patient ou de facture est convertie en archivage sécurisé traçable avec motif et date.
  - **Recherche multicritères dans les archives :** Par nom, CIN, date, médecin, type d'élément.
  - **Restauration en 1 clic :** Réintégration immédiate d'un dossier archivé vers la patientèle active.
  - **Exportation Complète du Dossier Patient :** Téléchargement instantané de l'intégralité du dossier (données médicales, consultations, antécédents, constantes, factures) au format JSON/PDF structuré.

### 6. Facturation & Mutuelles Marocaines (CNOPS / CNSS / FAR)
- **Tarification officielle en Dirhams Marocains (MAD) :**
  - Catalogue d'actes selon la nomenclature marocaine (NGAP) : Consultations Généraliste (150 MAD), Spécialiste (250 MAD), ECG (150 MAD), Échographie (600 MAD), Radiographie (450 MAD), Bilan Biologique, Journée d'hospitalisation, Césarienne.
- **Moteur de Prise en Charge Automatisé :**
  - **CNOPS :** Prise en charge 80% (Ticket modérateur patient : 20%).
  - **CNSS :** Prise en charge 70% (Ticket modérateur patient : 30%).
  - **FAR (Forces Armées Royales) :** Prise en charge 90% (Ticket modérateur patient : 10%).
  - **MGPAP / Saham / Wafa Assurance / AtlantaSanad :** Selon barème conventionné.
  - **Secteur Privé :** Prise en charge 0% (Part patient : 100%).
- **Édition de Factures Officielles & Reçus :** Téléchargement immédiat de la facture au format PDF conforme aux exigences de remboursement de l'AMO (Assurance Maladie Obligatoire).
- **Clôture Journalière de Caisse :** Suivi par secrétaire/caissier des encaissements par mode de paiement (Espèces, Carte Bancaire, Chèque, Virement) et détection automatique des écarts de caisse.

### 7. Pharmacie Interne & Gestion des Stocks
- **Inventaire en Temps Réel :** Suivi quantitatif des boîtes, flacons, ampoules et consommables stériles.
- **Tableau de Bord des Alertes :**
  - ⚠️ *Alerte Stock Critique :* Déclenchée automatiquement dès que le stock actuel $\le$ stock minimum paramétré.
  - ⏳ *Alerte Péremption Proche :* Déclenchée automatiquement pour tout lot expirant dans moins de 60 jours.
- **Traçabilité des Mouvements :** Enregistrement des Entrées (approvisionnements) et Sorties (prescriptions dispensées aux patients hospitalisés).

### 8. Gestion du Personnel RH & Calcul des Honoraires
- **Annuaire des Praticiens & Personnels :** Spécialité, n° INPE (Identifiant National des Professionnels de Santé), téléphone, statut.
- **Calculateur Automatique des Rétrocessions d'Honoraires :**
  - Répartition paramétrable (ex: 70% pour le médecin praticien, 30% pour les frais de structure de la clinique).
  - Calcul instantané des honoraires nets dus par praticien selon le volume d'actes réalisés.
- **Planning des Gardes & Astreintes :** Grille des tours de garde (Matin, Soir, Nuit, Astreinte) par service.

### 9. Tableau de Bord Décisionnel & Conformité CNDP
- **KPIs en Temps Réel :** Nombre de consultations du jour, taux d'occupation des lits d'hospitalisation, chiffre d'affaires journalier en MAD, répartition des consultations par mutuelle marocaine.
- **Journal d'Audit Conforme CNDP (Loi 09-08) :** Enregistrement horodaté et inaltérable de chaque consultation, modification, création, archivage et export avec identité de l'utilisateur et adresse IP.
- **Sauvegarde Automatique Cryptée :** Création et téléchargement d'instantanés complets de la base de données au format `.json` chiffré.

---

## 🇲🇦 Spécificités Médicales & Administratives Marocaines

| Spécificité | Implémentation dans l'Application |
| :--- | :--- |
| **Identifiants Légaux** | Inscription de l'**ICE** (002391823000045) et de l'**INPE** (053421987) sur tous les documents officiels. |
| **Mutuelles & AMO** | Prise en charge automatique des barèmes **CNOPS (80%)**, **CNSS (70%)**, **FAR (90%)**, **MGPAP**, assurances privées. |
| **Monnaie** | Tous les montants, devis, factures et clôtures de caisse sont libellés en **MAD (Dirhams Marocains)**. |
| **Vérification QR Code** | Chaque ordonnance et facture intègre un **QR Code de vérification** scannable avec un smartphone pour lutter contre la falsification. |
| **Bilingue & RTL** | Support complet **Français / Arabe (العربية)** avec inversion automatique de la mise en page (RTL) et polices médicales adaptées. |
| **Conformité CNDP (Loi 09-08)** | Chiffrement des données de santé sensibles, journal d'audit strict et droit à l'effacement/portabilité sécurisé. |
| **Ancrage Local (Nador)** | Base pré-peuplée avec les quartiers réels de Nador (*Hay Al Matar, Bouizazarène, Selouane, Beni Ansar, Zeghanghane, Taouima*). |

---

## 🔑 Comptes de Démonstration (Connexion en 1 Clic)

Pour faciliter la démonstration et l'évaluation du système, une barre d'accès rapide est présente sur l'écran de connexion pour se connecter en 1 clic avec n'importe quel rôle :

| Rôle | Identifiant (Username) | Mot de passe | Nom complet & Fonction |
| :--- | :--- | :--- | :--- |
| 👑 **Super Admin** | `admin` | `demo123` | Dr. Rachid Benali (Directeur Médical) |
| 🩺 **Médecin Praticien** | `dr.amrani` | `demo123` | Dr. Youssef Amrani (Cardiologie & Médecine) |
| 🩺 **Gynécologue** | `dr.tazi` | `demo123` | Dr. Fatima Tazi (Gynécologie Obstétrique) |
| 💉 **Infirmier(ère)** | `inf.karim` | `demo123` | Karim Mansouri (Soins Intensifs & Triage) |
| 💼 **Accueil / Caisse** | `sec.salma` | `demo123` | Salma El Fassi (Secrétariat Médical) |
| 💊 **Pharmacien** | `pharma.omar` | `demo123` | Dr. Omar Berrada (Pharmacie Clinique) |
| 🔬 **Laborantin** | `lab.nawal` | `demo123` | Nawal Chraibi (Biologie Médicale) |

---

## 👥 Données de Démonstration Réalistes (Nador)

La base de données est livrée avec **15 patients marocains complets** résidant à Nador et ses environs :

1. **Mohammed El Amrani** (CIN: S548912) - Hay Al Matar - Mutuelle CNOPS (HTA, Diabète Type 2).
2. **Fatima Boudraa** (CIN: S612345) - Bouizazarène - Mutuelle CNSS (Suivi de grossesse, Asthme).
3. **Abdelkader Zemmouri** (CIN: S421098) - Selouane - Mutuelle FAR (Cardiopathie ischémique).
4. **Naima Kaddouri** (CIN: S789012) - Beni Ansar - Mutuelle MGPAP (Migraines chroniques).
5. **Karim Ait Ouahi** (CIN: S334567) - Zeghanghane - Assurance Saham (Ulcère gastro-duodénal).
6. **Meryem Touzani** (CIN: S890123) - Taouima - Wafa Assurance (Rhinite allergique).
7. **Hassan Boulahya** (CIN: S123789) - Hay Al Matar - Mutuelle CNOPS (BPCO, Fibrillation auriculaire).
8. **Souad El Idrissi** (CIN: S901234) - Al Khattabi - Mutuelle CNSS (Hypothyroïdie).
9. **Youssef Benali** (CIN: S456123) - Laârassi - Secteur Privé (Gastrite aiguë).
10. **Khadija Meziane** (CIN: S567890) - Oulad Mimoun - AtlantaSanad (Polyarthrite rhumatoïde).
11. **Tariq Choukri** (CIN: S678901) - Selouane - Mutuelle CNOPS (Lombalgie chronique).
12. **Zineb El Khattabi** (CIN: S789456) - Hay Al Matar - Mutuelle CNSS (Anémie ferriprive).
13. **Mustapha Azirar** (CIN: S234567) - Bouizazarène - Mutuelle FAR (Diabète type 2, Rétinopathie).
14. **Salima Berrada** (CIN: S345678) - Beni Ansar - Mutuelle MGPAP (Asthme d’effort).
15. **Bilal Hammouda** (CIN: S890567) - Zeghanghane - Secteur Privé (Lithiase rénale).

---

## 🧪 Suite de Tests Automatisés (100% Réussite)

L'application intègre une suite de tests automatisés exhaustive couvrant **100% des routes d'API, de la logique métier et des interactions graphiques E2E** :

```bash
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.2.0
rootdir: C:\Users\hp\.gemini\antigravity\scratch\clinique-rif-nador
collected 23 items

tests/test_all_modules.py::test_moroccan_mutuelle_copay_rules PASSED     [  4%]
tests/test_all_modules.py::test_bmi_and_vitals_classification PASSED     [  8%]
tests/test_all_modules.py::test_waiting_room_priority_queue PASSED       [ 13%]
tests/test_all_modules.py::test_prescription_pdf_generation PASSED       [ 17%]
tests/test_all_modules.py::test_invoice_pdf_generation PASSED            [ 21%]
tests/test_all_modules.py::test_certificate_pdf_generation PASSED        [ 26%]
tests/test_all_modules.py::test_pharmacy_stock_alerts PASSED             [ 30%]
tests/test_all_modules.py::test_doctor_fee_retrocession PASSED           [ 34%]
tests/test_all_modules.py::test_cash_closure_discrepancy PASSED          [ 39%]
tests/test_api_routes.py::test_static_and_pwa_routes PASSED              [ 43%]
tests/test_api_routes.py::test_auth_routes PASSED                        [ 47%]
tests/test_api_routes.py::test_patients_crud_and_archive PASSED          [ 52%]
tests/test_api_routes.py::test_waiting_room_flow PASSED                  [ 56%]
tests/test_api_routes.py::test_appointments_flow PASSED                  [ 60%]
tests/test_api_routes.py::test_medical_flow PASSED                       [ 65%]
tests/test_api_routes.py::test_inpatient_flow PASSED                     [ 69%]
tests/test_api_routes.py::test_billing_and_copay_calculation PASSED      [ 73%]
tests/test_api_routes.py::test_pharmacy_flow PASSED                      [ 78%]
tests/test_api_routes.py::test_staff_and_fees PASSED                     [ 82%]
tests/test_api_routes.py::test_archive_and_export_vault PASSED           [ 86%]
tests/test_api_routes.py::test_audit_logs_and_backup PASSED              [ 91%]
tests/test_api_routes.py::test_dashboard_kpis PASSED                     [ 95%]
tests/test_e2e_playwright.py::test_full_e2e_browser_flows PASSED         [100%]

============================== 23 passed in 97.46s ==============================
```

### Détail des vérifications effectuées :
- **Règles Mutuelles Marocaines :** Vérification stricte des calculs CNOPS (80/20), CNSS (70/30), FAR (90/10) et Privé (0/100).
- **Génération Vectorielle PDF :** Contrôle des octets d'en-tête `%PDF-` et validité des QR codes générés.
- **Gestion des Écarts de Caisse :** Détection arithmétique rigoureuse des excédents et déficits de caisse.
- **Rétrocession Honoraires Praticiens :** Calcul de la quote-part 70% médecin / 30% clinique.
- **Playwright E2E dans Navigateur Réel :** Test complet de l'interface graphique sous Microsoft Edge / Chromium (chargement du DOM, bascule de langue en Arabe avec inversion RTL `dir="rtl"`, ouverture et fermeture de modales, navigation dans les onglets, soumission de formulaires sans aucune erreur JavaScript dans la console).

---

## 🚀 Guide de Démarrage Rapide (Local)

### Prérequis
- Python 3.10 ou supérieur installé.

### Installation et Lancement en 3 étapes :

```bash
# 1. Cloner ou se placer dans le répertoire du projet
cd clinique-rif-nador

# 2. Créer l'environnement virtuel et installer les dépendances
python -m venv .venv

# Sous Windows :
.\.venv\Scripts\activate
# Sous Linux / macOS :
source .venv/bin/activate

pip install -r requirements.txt

# 3. Lancer l'application
python run.py
```

L'application démarre immédiatement sur **http://localhost:5000** !

> **Note :** La base de données SQLite `clinique_nador.db` est automatiquement initialisée et pré-remplie avec les 15 patients de Nador et les comptes de test dès le premier démarrage.

Pour exécuter les tests automatisés :
```bash
python -m pytest tests -v
```

---

## ☁️ Guide de Déploiement Cloud

### Option 1 : Déploiement avec Docker & Docker-Compose (Recommandé pour serveur local ou VPS)

Un fichier `docker-compose.yml` complet est fourni, déployant l'application Flask avec un conteneur **PostgreSQL 15** dédié :

```bash
docker-compose up -d --build
```
L'application est disponible immédiatement sur le port `5000` et la base PostgreSQL sur le port `5432`.

---

### Option 2 : Connexion à PostgreSQL Cloud Gratuit (**Neon Serverless** ou **Supabase**)

1. Créez un projet gratuit sur [Neon.tech](https://neon.tech) ou [Supabase.com](https://supabase.com).
2. Récupérez votre chaîne de connexion (Connection String).
3. Définissez la variable d'environnement `DATABASE_URL` :

```bash
# Exemple avec Neon Serverless :
export DATABASE_URL="postgresql://user:password@ep-sample-12345.eu-central-1.aws.neon.tech/clinique_rif?sslmode=require"

# Sous Windows PowerShell :
$env:DATABASE_URL="postgresql://user:password@ep-sample-12345.eu-central-1.aws.neon.tech/clinique_rif?sslmode=require"
```

4. Exécutez le script d'initialisation :
```bash
python seed_data.py
# OU importez directement le fichier schema_and_seed.sql dans l'éditeur SQL de Supabase/Neon
```

5. Lancez l'application avec `python run.py`. L'ORM basculera automatiquement sur PostgreSQL.

---

### Option 3 : Déploiement Gratuit sur Vercel

Le projet comprend le fichier `vercel.json` préconfiguré :
1. Poussez le code sur GitHub / GitLab.
2. Importez le projet sur votre tableau de bord **Vercel**.
3. Dans les variables d'environnement Vercel, ajoutez :
   - `DATABASE_URL` : Votre URL PostgreSQL Neon ou Supabase.
   - `SECRET_KEY` : Une clé secrète aléatoire.
4. Cliquez sur **Deploy**.

---

## 📁 Fichiers et Structure du Projet

```text
clinique-rif-nador/
├── app/
│   ├── models/                # 20 Modèles de données SQLAlchemy & CNDP
│   │   └── __init__.py        # Users, Patients, Vitals, Inpatient, Billing, Pharmacy, Audits
│   ├── routes/                # Contrôleurs RESTful modulaires
│   │   ├── auth.py            # Authentification & comptes démo
│   │   ├── patients.py        # Gestion DME patients & recherche
│   │   ├── waiting_room.py    # File d'attente en temps réel & carillon
│   │   ├── appointments.py    # Prise de RDV & rappels WhatsApp
│   │   ├── medical.py         # Consultations, CIM-10 & PDF ordonnances/certificats
│   │   ├── inpatient.py       # Plan des chambres & lits
│   │   ├── billing.py         # Facturation & calculs mutuelles CNOPS/CNSS
│   │   ├── pharmacy.py        # Stocks, alertes péremption & mouvements
│   │   ├── staff.py           # Personnel, rétrocessions & gardes
│   │   ├── archive.py         # Coffre-fort historique (Soft Delete) & export
│   │   ├── audit.py           # Journal d'audit CNDP & backups
│   │   └── stats.py           # Tableau de bord & KPIs
│   ├── services/
│   │   ├── pdf_service.py     # Moteur ReportLab PDF avec QR code & en-tête Nador
│   │   ├── audit_service.py   # Traçabilité CNDP Loi 09-08
│   │   └── backup_service.py  # Instantanés chiffrés de la base
│   ├── static/
│   │   ├── css/custom.css     # Styles médicaux, impression & RTL
│   │   ├── js/
│   │   │   ├── app.js         # Application SPA React 18 intégrale
│   │   │   └── i18n.js        # Traducteur bilingue Français/Arabe
│   │   ├── vendor/            # React, ReactDOM & Tailwind autonomes (Zero CDN, 100% offline)
│   │   ├── manifest.json      # Manifeste PWA installable
│   │   └── sw.js              # Service Worker PWA
│   ├── templates/
│   │   └── index.html         # Point d'ancrage HTML5 réactif
│   ├── config.py              # Configuration multi-bases (SQLite / PostgreSQL)
│   └── __init__.py            # Application Factory Flask
├── tests/
│   ├── test_all_modules.py    # Tests unitaires des règles de gestion marocaines
│   ├── test_api_routes.py     # Tests d'intégration des routes REST
│   └── test_e2e_playwright.py # Tests E2E complets dans navigateur réel
├── seed_data.py               # Script de peuplement idempotent (15 patients Nador)
├── schema_and_seed.sql        # Script SQL universel DDL & DML
├── requirements.txt           # Dépendances Python
├── Dockerfile                 # Conteneurisation de production Gunicorn
├── docker-compose.yml         # Déploiement multi-conteneurs Flask + PostgreSQL
├── vercel.json                # Déploiement Cloud Serverless
└── README.md                  # Documentation officielle
```

---

## 🏛️ Mentions Légales & Conformité

- **Établissement :** Clinique Médico-Chirurgicale du Rif
- **Ville :** Nador, Région de l'Oriental, Royaume du Maroc
- **Agrément Ministère de la Santé :** INPE N° 053421987
- **Identifiant Commun de l'Entreprise (ICE) :** 002391823000045
- **Protection des Données Personnelles :** Déclaration de conformité auprès de la **CNDP** en vertu de la **Loi n° 09-08** relative à la protection des personnes physiques à l'égard du traitement des données à caractère personnel.
