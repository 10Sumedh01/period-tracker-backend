from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import db
from src.models.ovulation import Ovulation

ovulation_bp = Blueprint('ovulation', __name__)

@ovulation_bp.route('/ovulation', methods=['GET'])
@jwt_required()
def get_ovulations():
    try:
        current_user_id = get_jwt_identity()
        ovulations = Ovulation.query.filter_by(user_id=current_user_id).order_by(Ovulation.ovulation_date.desc()).all()
        return jsonify([ovulation.to_dict() for ovulation in ovulations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ovulation_bp.route('/ovulation', methods=['POST'])
@jwt_required()
def create_ovulation():
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        # Validate required fields
        if not data or not data.get('ovulation_date'):
            return jsonify({'error': 'Ovulation date is required'}), 400
        
        # Parse date
        ovulation_date = datetime.strptime(data['ovulation_date'], '%Y-%m-%d').date()
        
        # Create new ovulation record
        ovulation = Ovulation(
            user_id=current_user_id,
            ovulation_date=ovulation_date,
            basal_body_temperature=data.get('basal_body_temperature'),
            cervical_mucus=data.get('cervical_mucus'),
            symptoms=data.get('symptoms')
        )
        
        db.session.add(ovulation)
        db.session.commit()
        
        return jsonify({
            'message': 'Ovulation record created successfully',
            'ovulation': ovulation.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ovulation_bp.route('/ovulation/<int:ovulation_id>', methods=['GET'])
@jwt_required()
def get_ovulation(ovulation_id):
    try:
        current_user_id = get_jwt_identity()
        ovulation = Ovulation.query.filter_by(id=ovulation_id, user_id=current_user_id).first()
        
        if not ovulation:
            return jsonify({'error': 'Ovulation record not found'}), 404
        
        return jsonify(ovulation.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ovulation_bp.route('/ovulation/<int:ovulation_id>', methods=['PUT'])
@jwt_required()
def update_ovulation(ovulation_id):
    try:
        current_user_id = get_jwt_identity()
        ovulation = Ovulation.query.filter_by(id=ovulation_id, user_id=current_user_id).first()
        
        if not ovulation:
            return jsonify({'error': 'Ovulation record not found'}), 404
        
        data = request.json
        
        # Update fields if provided
        if data.get('ovulation_date'):
            ovulation.ovulation_date = datetime.strptime(data['ovulation_date'], '%Y-%m-%d').date()
        
        if 'basal_body_temperature' in data:
            ovulation.basal_body_temperature = data['basal_body_temperature']
        
        if 'cervical_mucus' in data:
            ovulation.cervical_mucus = data['cervical_mucus']
        
        if 'symptoms' in data:
            ovulation.symptoms = data['symptoms']
        
        ovulation.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Ovulation record updated successfully',
            'ovulation': ovulation.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ovulation_bp.route('/ovulation/<int:ovulation_id>', methods=['DELETE'])
@jwt_required()
def delete_ovulation(ovulation_id):
    try:
        current_user_id = get_jwt_identity()
        ovulation = Ovulation.query.filter_by(id=ovulation_id, user_id=current_user_id).first()
        
        if not ovulation:
            return jsonify({'error': 'Ovulation record not found'}), 404
        
        db.session.delete(ovulation)
        db.session.commit()
        
        return jsonify({'message': 'Ovulation record deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

