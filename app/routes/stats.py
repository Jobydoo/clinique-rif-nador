from datetime import datetime
from flask import Blueprint, jsonify
from app.models import db, Patient, Invoice, Bed, WaitingRoom, Consultation, MedicationStock, Appointment

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    today = datetime.utcnow().date()

    # Total patients
    total_patients = Patient.query.count()
    active_patients = Patient.query.filter_by(is_archived=False).count()
    archived_patients = Patient.query.filter_by(is_archived=True).count()

    # Salle d'attente
    waiting_active = WaitingRoom.query.filter(WaitingRoom.status != 'COMPLETED').count()
    triage_count = WaitingRoom.query.filter_by(status='TRIAGE').count()
    in_consult_count = WaitingRoom.query.filter_by(status='IN_CONSULTATION').count()

    # Lits & Hospitalisation
    total_beds = Bed.query.count()
    occupied_beds = Bed.query.filter_by(status='OCCUPIED').count()
    cleaning_beds = Bed.query.filter_by(status='CLEANING').count()
    available_beds = Bed.query.filter_by(status='AVAILABLE').count()
    occupancy_rate = round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0.0

    # Facturation & Revenus
    today_invoices = Invoice.query.filter(db.func.date(Invoice.date) == today).all()
    today_revenue = sum(inv.total_amount for inv in today_invoices)
    today_collected = sum(inv.patient_share for inv in today_invoices if inv.status == 'PAID')

    all_invoices = Invoice.query.all()
    total_revenue = sum(inv.total_amount for inv in all_invoices)
    mutuelle_total = sum(inv.mutuelle_amount for inv in all_invoices)
    patient_total = sum(inv.patient_share for inv in all_invoices)

    # Répartition par mutuelle marocaine
    mutuelle_stats = {}
    for p in Patient.query.filter_by(is_archived=False).all():
        m = p.mutuelle_type or 'PRIVE'
        mutuelle_stats[m] = mutuelle_stats.get(m, 0) + 1

    # Alertes pharmacie
    stock_items = MedicationStock.query.all()
    low_stock_count = sum(1 for m in stock_items if m.current_quantity <= m.min_quantity_alert)
    near_expiry_count = sum(1 for m in stock_items if 0 < (m.expiration_date - today).days <= 60)

    # Consultations & RDV du jour
    today_appointments = Appointment.query.filter_by(date=today).count()
    today_consultations = Consultation.query.filter(db.func.date(Consultation.date) == today).count()

    return jsonify({
        'kpis': {
            'total_patients': total_patients,
            'active_patients': active_patients,
            'archived_patients': archived_patients,
            'waiting_active': waiting_active,
            'triage_count': triage_count,
            'in_consult_count': in_consult_count,
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'cleaning_beds': cleaning_beds,
            'available_beds': available_beds,
            'occupancy_rate': occupancy_rate,
            'today_revenue': round(today_revenue, 2),
            'today_collected': round(today_collected, 2),
            'total_revenue': round(total_revenue, 2),
            'mutuelle_total': round(mutuelle_total, 2),
            'patient_total': round(patient_total, 2),
            'low_stock_count': low_stock_count,
            'near_expiry_count': near_expiry_count,
            'today_appointments': today_appointments,
            'today_consultations': today_consultations
        },
        'mutuelle_distribution': mutuelle_stats,
        'city': 'Nador',
        'clinic_name': 'Clinique Médico-Chirurgicale du Rif - Nador'
    })
