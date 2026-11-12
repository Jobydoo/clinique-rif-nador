import os
from flask import Flask, render_template, send_from_directory, jsonify
from app.config import Config
from app.models import db

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)

    # Initialisation Base de données
    db.init_app(app)

    # Enregistrement des Blueprints API
    from app.routes.auth import auth_bp
    from app.routes.patients import patients_bp
    from app.routes.waiting_room import waiting_room_bp
    from app.routes.appointments import appointments_bp
    from app.routes.medical import medical_bp
    from app.routes.inpatient import inpatient_bp
    from app.routes.billing import billing_bp
    from app.routes.pharmacy import pharmacy_bp
    from app.routes.staff import staff_bp
    from app.routes.archive import archive_bp
    from app.routes.audit import audit_bp
    from app.routes.stats import stats_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(patients_bp, url_prefix='/api/patients')
    app.register_blueprint(waiting_room_bp, url_prefix='/api/waiting-room')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(medical_bp, url_prefix='/api/medical')
    app.register_blueprint(inpatient_bp, url_prefix='/api/inpatient')
    app.register_blueprint(billing_bp, url_prefix='/api/billing')
    app.register_blueprint(pharmacy_bp, url_prefix='/api/pharmacy')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(archive_bp, url_prefix='/api/archive')
    app.register_blueprint(audit_bp, url_prefix='/api/audit')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')

    # Route principale : Interface Single-Page Application (SPA)
    @app.route('/')
    @app.route('/<path:path>')
    def index(path=None):
        if path and path.startswith('api/'):
            return jsonify({'error': 'Endpoint API introuvable'}), 404
        return render_template('index.html')

    # Manifest PWA & Service Worker
    @app.route('/manifest.json')
    def manifest():
        return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

    @app.route('/sw.js')
    def service_worker():
        return send_from_directory('static', 'sw.js', mimetype='application/javascript')

    return app
