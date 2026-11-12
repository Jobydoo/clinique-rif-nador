import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nador-clinique-rif-secret-key-2026-cndp-secured')
    
    # Base de données : 100% compatible SQLite (Local) & PostgreSQL (Neon / Supabase Cloud)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Adaptation pour Neon / Supabase si le schéma postgres:// est utilisé au lieu de postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Base locale SQLite par défaut
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'clinique_nador.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sécurité & Conformité CNDP Maroc (Loi 09-08)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Identité Officielle de la Clinique à Nador
    CLINIC_NAME = "Clinique Médico-Chirurgicale du Rif"
    CLINIC_NAME_AR = "مصحة الريف للطب والجراحة - الناظور"
    CLINIC_CITY = "Nador"
    CLINIC_ADDRESS = "Boulevard Hassan II, Hay Al Matar, Nador, Maroc"
    CLINIC_PHONE = "+212 536 60 44 20"
    CLINIC_EMAIL = "contact@clinique-rif-nador.ma"
    CLINIC_INPE = "053421987"
    CLINIC_PATENTE = "28471920"
    CLINIC_ICE = "002391823000045"
    
    # Dossiers de stockage
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    BACKUP_FOLDER = os.path.join(BASE_DIR, 'backups')
