from flask import Blueprint, request, jsonify, session
from app.models import db, User
from app.services.audit_service import log_audit
from app.config import Config

auth_bp = Blueprint('auth', __name__)

DEMO_ACCOUNTS = [
    {
        'role': 'ADMIN',
        'roleLabelFr': 'Directeur / Super Admin',
        'roleLabelAr': 'المدير العام / المسؤول الرئيسي',
        'email': 'admin@clinique-rif-nador.ma',
        'name': 'Dr. Mohamed Amrani (Directeur)',
        'specialty': 'Direction Médicale & Administration',
        'badge': 'Accès Total',
        'desc': 'Gestion globale, finances, audit logs CNDP, sauvegardes'
    },
    {
        'role': 'DOCTOR',
        'roleLabelFr': 'Médecin Praticien',
        'roleLabelAr': 'طبيب ممارس',
        'email': 'medecin@clinique-rif-nador.ma',
        'name': 'Dr. Youssef Benali',
        'specialty': 'Cardiologie & Médecine Interne',
        'badge': 'Consultations & DME',
        'desc': 'Dossiers médicaux, ordonnances PDF, examens, honoraires'
    },
    {
        'role': 'NURSE',
        'roleLabelFr': 'Infirmière Major / Triage',
        'roleLabelAr': 'ممرضة رئيسية / الفرز الطبي',
        'email': 'infirmier@clinique-rif-nador.ma',
        'name': 'Fatima Zahra Mansouri',
        'specialty': 'Soins Infirmiers & Triage Urgences',
        'badge': 'Constantes & Soins',
        'desc': 'Prise des constantes, calcul IMC, triage en salle d\'attente'
    },
    {
        'role': 'RECEPTIONIST',
        'roleLabelFr': 'Accueil & Secrétariat',
        'roleLabelAr': 'الاستقبال وسكرتارية العيادة',
        'email': 'reception@clinique-rif-nador.ma',
        'name': 'Khadija El Idrissi',
        'specialty': 'Accueil, RDV & Caisse',
        'badge': 'Admissions & Facturation',
        'desc': 'Inscriptions, WhatsApp RDV, encaissements, clôture caisse'
    },
    {
        'role': 'PHARMACIST',
        'roleLabelFr': 'Pharmacien & Responsable Stock',
        'roleLabelAr': 'صيدلي ومسؤول المخزون الطبي',
        'email': 'pharmacie@clinique-rif-nador.ma',
        'name': 'Dr. Rachid Berrada',
        'specialty': 'Pharmacie Hospitalière & Consommables',
        'badge': 'Gestion des Stocks',
        'desc': 'Inventaire médicaments, alertes stock mini et péremption'
    },
    {
        'role': 'LAB_TECH',
        'roleLabelFr': 'Laborantin & Imagerie',
        'roleLabelAr': 'مخبري وتقني أشعة طبية',
        'email': 'labo@clinique-rif-nador.ma',
        'name': 'Nadia Tazi',
        'specialty': 'Analyses Biologiques & Radiologie',
        'badge': 'Résultats & GED',
        'desc': 'Téléversement radios, bilans d\'analyses, GED médicale'
    }
]

@auth_bp.route('/demo-accounts', methods=['GET'])
def get_demo_accounts():
    return jsonify({
        'accounts': DEMO_ACCOUNTS,
        'defaultPassword': 'Password123!',
        'clinic': {
            'nameFr': Config.CLINIC_NAME,
            'nameAr': Config.CLINIC_NAME_AR,
            'city': Config.CLINIC_CITY,
            'address': Config.CLINIC_ADDRESS,
            'phone': Config.CLINIC_PHONE,
            'inpe': Config.CLINIC_INPE,
        }
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email:
        return jsonify({'error': 'Adresse email requise'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Utilisateur introuvable avec cet email'}), 401

    if not user.is_active:
        return jsonify({'error': 'Ce compte est inactif. Contactez la Direction.'}), 403

    # Mot de passe démo direct ou vérification hash
    is_demo_pass = password in ['Password123!', 'Nador2026!']
    if not (is_demo_pass or user.check_password(password)):
        return jsonify({'error': 'Mot de passe incorrect'}), 401

    session['user_id'] = user.id
    session['user_role'] = user.role
    session['user_name'] = user.name

    log_audit(
        action='LOGIN',
        entity_type='SYSTEM',
        details=f"Connexion réussie au SIH de la Clinique du Rif Nador (Rôle: {user.role})",
        entity_id=user.id,
        user_id=user.id,
        user_name=user.name,
        user_role=user.role
    )

    return jsonify({
        'message': 'Connexion réussie',
        'user': user.to_dict()
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    uid = session.get('user_id')
    uname = session.get('user_name')
    urole = session.get('user_role')

    if uid:
        log_audit(
            action='LOGIN',
            entity_type='SYSTEM',
            details=f"Déconnexion de l'utilisateur {uname}",
            entity_id=uid,
            user_id=uid,
            user_name=uname,
            user_role=urole
        )

    session.clear()
    return jsonify({'message': 'Déconnexion effectuée'})

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        # Mode démo par défaut si non authentifié : Directeur
        default_admin = User.query.filter_by(role='ADMIN').first()
        if default_admin:
            return jsonify(default_admin.to_dict())
        return jsonify({'error': 'Non connecté'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    return jsonify(user.to_dict())

@auth_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.filter_by(is_active=True).all()
    return jsonify([u.to_dict() for u in users])
