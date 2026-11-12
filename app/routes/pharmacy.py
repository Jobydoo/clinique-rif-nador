from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.models import db, MedicationStock, StockMovement
from app.services.audit_service import log_audit

pharmacy_bp = Blueprint('pharmacy', __name__)

@pharmacy_bp.route('/stock', methods=['GET'])
def get_stock():
    category = request.args.get('category', 'ALL')
    alert = request.args.get('alert', 'ALL') # LOW, EXPIRING, EXPIRED, ALL
    search = request.args.get('search', '').strip()

    query = MedicationStock.query

    if category != 'ALL':
        query = query.filter_by(category=category)

    if search:
        s = f"%{search}%"
        query = query.filter(
            db.or_(
                MedicationStock.name.ilike(s),
                MedicationStock.code.ilike(s),
                MedicationStock.dci.ilike(s)
            )
        )

    items = query.order_by(MedicationStock.name.asc()).all()
    results = [item.to_dict() for item in items]

    if alert == 'LOW':
        results = [r for r in results if r['is_low_stock']]
    elif alert == 'EXPIRING':
        results = [r for r in results if r['is_near_expiry']]
    elif alert == 'EXPIRED':
        results = [r for r in results if r['is_expired']]

    return jsonify(results)

@pharmacy_bp.route('/stock', methods=['POST'])
def add_stock_item():
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()
    name = data.get('name', '').strip()
    category = data.get('category', 'MEDICAMENT')
    unit = data.get('unit', 'Boîte')
    quantity = int(data.get('current_quantity', 0))
    min_alert = int(data.get('min_quantity_alert', 10))
    exp_str = data.get('expiration_date')

    if not code or not name or not exp_str:
        return jsonify({'error': 'Code, Désignation et Date d’expiration sont obligatoires'}), 400

    exp_date = datetime.strptime(exp_str, '%Y-%m-%d').date()

    item = MedicationStock(
        code=code,
        name=name,
        category=category,
        dci=data.get('dci'),
        unit=unit,
        current_quantity=quantity,
        min_quantity_alert=min_alert,
        expiration_date=exp_date,
        unit_price=float(data.get('unit_price', 0.0)),
        location=data.get('location', 'Pharmacie Centrale'),
        batch_number=data.get('batch_number')
    )

    db.session.add(item)
    db.session.flush()

    if quantity > 0:
        movement = StockMovement(
            medication_id=item.id,
            type='IN',
            quantity=quantity,
            reason='Stock initial / Réception commande',
            reference=data.get('batch_number', 'INIT'),
            performed_by=session.get('user_name', 'Pharmacien Responsable')
        )
        db.session.add(movement)

    db.session.commit()

    log_audit(
        action='CREATE',
        entity_type='STOCK',
        details=f"Ajout au stock pharmacie : {item.name} ({item.code}, Qté: {item.current_quantity})",
        entity_id=item.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Pharmacie'),
        user_role=session.get('user_role', 'PHARMACIST')
    )

    return jsonify(item.to_dict()), 201

@pharmacy_bp.route('/stock/<item_id>/movement', methods=['POST'])
def record_movement(item_id):
    item = MedicationStock.query.get_or_404(item_id)
    data = request.get_json() or {}
    mov_type = data.get('type') # IN, OUT, ADJUSTMENT
    quantity = int(data.get('quantity', 0))
    reason = data.get('reason', 'Mouvement de stock')
    reference = data.get('reference')

    if not mov_type or quantity <= 0:
        return jsonify({'error': 'Type de mouvement et Quantité positive requis'}), 400

    if mov_type == 'OUT' and item.current_quantity < quantity:
        return jsonify({'error': f'Stock insuffisant (Disponible: {item.current_quantity})'}), 400

    if mov_type == 'IN':
        item.current_quantity += quantity
    elif mov_type == 'OUT':
        item.current_quantity -= quantity
    elif mov_type == 'ADJUSTMENT':
        item.current_quantity = quantity

    movement = StockMovement(
        medication_id=item.id,
        type=mov_type,
        quantity=quantity,
        reason=reason,
        reference=reference,
        performed_by=session.get('user_name', 'Pharmacien Responsable')
    )

    db.session.add(movement)
    db.session.commit()

    log_audit(
        action='UPDATE',
        entity_type='STOCK',
        details=f"Mouvement stock ({mov_type}) sur {item.name} : {quantity} {item.unit} (Reste: {item.current_quantity}) - Motif: {reason}",
        entity_id=item.id,
        user_id=session.get('user_id'),
        user_name=session.get('user_name', 'Pharmacie'),
        user_role=session.get('user_role', 'PHARMACIST')
    )

    return jsonify({'item': item.to_dict(), 'movement': movement.to_dict()})

@pharmacy_bp.route('/movements', methods=['GET'])
def get_movements():
    movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(100).all()
    return jsonify([m.to_dict() for m in movements])
