from flask import Blueprint, request, jsonify, session, send_file
from app.models import AuditLog
from app.services.backup_service import create_clinic_backup, list_backups
from app.services.audit_service import log_audit

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/logs', methods=['GET'])
def get_audit_logs():
    action = request.args.get('action', 'ALL')
    entity_type = request.args.get('entity_type', 'ALL')
    limit = int(request.args.get('limit', 150))

    query = AuditLog.query
    if action != 'ALL':
        query = query.filter_by(action=action)
    if entity_type != 'ALL':
        query = query.filter_by(entity_type=entity_type)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return jsonify([l.to_dict() for l in logs])

@audit_bp.route('/backups', methods=['GET'])
def get_backups():
    backups = list_backups()
    return jsonify(backups)

@audit_bp.route('/backups/create', methods=['POST'])
def trigger_backup():
    result = create_clinic_backup()
    log_audit(
        action='EXPORT',
        entity_type='SYSTEM',
        details=f"Création sauvegarde automatique de sécurité de la base de données ({result['filename']}, {result['size_kb']} KB)",
        entity_id=result['filename'],
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Directeur'),
        user_role=session.get('user_role', 'ADMIN')
    )
    return jsonify(result), 201
