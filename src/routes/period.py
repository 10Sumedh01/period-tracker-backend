from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import db
from src.models.period import Period

period_bp = Blueprint('period', __name__)

@period_bp.route('/periods', methods=['GET'])
@jwt_required()
def get_periods():
    try:
        current_user_id = get_jwt_identity()
        periods = Period.query.filter_by(user_id=current_user_id).order_by(Period.start_date.desc()).all()
        return jsonify([period.to_dict() for period in periods]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@period_bp.route('/periods', methods=['POST'])
@jwt_required()
def create_period():
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        # Validate required fields
        if not data or not data.get('start_date'):
            return jsonify({'error': 'Start date is required'}), 400
        
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = None
        if data.get('end_date'):
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Create new period
        period = Period(
            user_id=current_user_id,
            start_date=start_date,
            end_date=end_date,
            flow_intensity=data.get('flow_intensity'),
            symptoms=data.get('symptoms')
        )
        
        db.session.add(period)
        db.session.commit()
        
        return jsonify({
            'message': 'Period created successfully',
            'period': period.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@period_bp.route('/periods/<int:period_id>', methods=['GET'])
@jwt_required()
def get_period(period_id):
    try:
        current_user_id = get_jwt_identity()
        period = Period.query.filter_by(id=period_id, user_id=current_user_id).first()
        
        if not period:
            return jsonify({'error': 'Period not found'}), 404
        
        return jsonify(period.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@period_bp.route('/periods/<int:period_id>', methods=['PUT'])
@jwt_required()
def update_period(period_id):
    try:
        current_user_id = get_jwt_identity()
        period = Period.query.filter_by(id=period_id, user_id=current_user_id).first()
        
        if not period:
            return jsonify({'error': 'Period not found'}), 404
        
        data = request.json
        
        # Update fields if provided
        if data.get('start_date'):
            period.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        if data.get('end_date'):
            period.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        elif 'end_date' in data and data['end_date'] is None:
            period.end_date = None
        
        if 'flow_intensity' in data:
            period.flow_intensity = data['flow_intensity']
        
        if 'symptoms' in data:
            period.symptoms = data['symptoms']
        
        period.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Period updated successfully',
            'period': period.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@period_bp.route('/periods/<int:period_id>', methods=['DELETE'])
@jwt_required()
def delete_period(period_id):
    try:
        current_user_id = get_jwt_identity()
        period = Period.query.filter_by(id=period_id, user_id=current_user_id).first()
        
        if not period:
            return jsonify({'error': 'Period not found'}), 404
        
        db.session.delete(period)
        db.session.commit()
        
        return jsonify({'message': 'Period deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

