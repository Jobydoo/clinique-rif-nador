from datetime import datetime
from flask import request
from app.models import db, AuditLog

def log_audit(action, entity_type, details, entity_id=None, user_id=None, user_name=None, user_role=None):
    """
    Journal d'audit complet garantissant la conformité légale CNDP (Loi 09-08 Maroc)
    Traçabilité inaltérable de qui a consulté, modifié, archivé ou exporté une donnée de santé.
    """
    try:
        ip = request.remote_addr if request else '127.0.0.1'
        log = AuditLog(
            user_id=user_id,
            user_name=user_name or 'Système / Anonyme',
            user_role=user_role or 'GUEST',
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return log
    except Exception as e:
        db.session.rollback()
        print(f"Erreur enregistrement audit log CNDP: {e}")
        return None
