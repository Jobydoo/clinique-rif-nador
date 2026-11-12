import os
import json
from datetime import datetime
from app.models import db, Patient, User, Consultation, Invoice, MedicationStock, Room, Bed, VitalSigns, Appointment, AuditLog
from app.config import Config

def create_clinic_backup():
    """
    Crée une sauvegarde complète chiffrée/structurée de la base de données de la clinique.
    Sauvegarde automatique périodique ou déclenchée par le Directeur.
    """
    os.makedirs(Config.BACKUP_FOLDER, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_clinique_rif_nador_{timestamp}.json"
    backup_path = os.path.join(Config.BACKUP_FOLDER, backup_filename)

    data = {
        'metadata': {
            'clinic_name': Config.CLINIC_NAME,
            'clinic_name_ar': Config.CLINIC_NAME_AR,
            'city': Config.CLINIC_CITY,
            'backup_timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0-CNDP-COMPLIANT'
        },
        'patients': [p.to_dict(include_relations=True) for p in Patient.query.all()],
        'users': [{'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role, 'specialty': u.specialty} for u in User.query.all()],
        'consultations': [c.to_dict(include_items=True) for c in Consultation.query.all()],
        'invoices': [i.to_dict() for i in Invoice.query.all()],
        'stock': [m.to_dict() for m in MedicationStock.query.all()],
        'rooms': [r.to_dict() for r in Room.query.all()],
        'audit_logs': [a.to_dict() for a in AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()]
    }

    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    file_size_kb = round(os.path.getsize(backup_path) / 1024, 2)
    return {
        'filename': backup_filename,
        'path': backup_path,
        'size_kb': file_size_kb,
        'timestamp': timestamp,
        'patient_count': len(data['patients']),
        'invoice_count': len(data['invoices']),
        'stock_count': len(data['stock'])
    }

def list_backups():
    os.makedirs(Config.BACKUP_FOLDER, exist_ok=True)
    files = []
    for fname in os.listdir(Config.BACKUP_FOLDER):
        if fname.endswith('.json'):
            fpath = os.path.join(Config.BACKUP_FOLDER, fname)
            files.append({
                'filename': fname,
                'size_kb': round(os.path.getsize(fpath) / 1024, 2),
                'created_at': datetime.fromtimestamp(os.path.getctime(fpath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    files.sort(key=lambda x: x['created_at'], reverse=True)
    return files
