from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from src.models.period import Period
from src.models.ovulation import Ovulation
import statistics

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/predict/period', methods=['GET'])
@jwt_required()
def predict_next_period():
    try:
        current_user_id = get_jwt_identity()
        
        # Get the last 6 periods to calculate average cycle length
        periods = Period.query.filter_by(user_id=current_user_id).order_by(Period.start_date.desc()).limit(6).all()
        
        if len(periods) < 2:
            return jsonify({
                'error': 'Not enough data to predict. Need at least 2 period records.',
                'predicted_date': None,
                'confidence': 'low'
            }), 200
        
        # Calculate cycle lengths
        cycle_lengths = []
        for i in range(len(periods) - 1):
            current_period = periods[i]
            previous_period = periods[i + 1]
            cycle_length = (current_period.start_date - previous_period.start_date).days
            cycle_lengths.append(cycle_length)
        
        # Calculate average cycle length
        avg_cycle_length = statistics.mean(cycle_lengths)
        
        # Get the last period start date
        last_period = periods[0]
        
        # Predict next period date
        predicted_date = last_period.start_date + timedelta(days=int(avg_cycle_length))
        
        # Calculate confidence based on cycle regularity
        if len(cycle_lengths) >= 3:
            std_dev = statistics.stdev(cycle_lengths)
            if std_dev <= 2:
                confidence = 'high'
            elif std_dev <= 5:
                confidence = 'medium'
            else:
                confidence = 'low'
        else:
            confidence = 'medium'
        
        return jsonify({
            'predicted_date': predicted_date.isoformat(),
            'average_cycle_length': round(avg_cycle_length, 1),
            'confidence': confidence,
            'cycles_analyzed': len(cycle_lengths)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/predict/ovulation', methods=['GET'])
@jwt_required()
def predict_next_ovulation():
    try:
        current_user_id = get_jwt_identity()
        
        # Get the last period to calculate ovulation
        last_period = Period.query.filter_by(user_id=current_user_id).order_by(Period.start_date.desc()).first()
        
        if not last_period:
            return jsonify({
                'error': 'No period data found. Need at least one period record.',
                'predicted_date': None
            }), 200
        
        # Get historical ovulation data to improve prediction
        ovulations = Ovulation.query.filter_by(user_id=current_user_id).order_by(Ovulation.ovulation_date.desc()).limit(6).all()
        periods = Period.query.filter_by(user_id=current_user_id).order_by(Period.start_date.desc()).limit(6).all()
        
        # Calculate average days from period start to ovulation
        ovulation_offsets = []
        
        for ovulation in ovulations:
            # Find the corresponding period for this ovulation
            for period in periods:
                if period.start_date <= ovulation.ovulation_date:
                    offset = (ovulation.ovulation_date - period.start_date).days
                    if 0 <= offset <= 21:  # Reasonable range for ovulation
                        ovulation_offsets.append(offset)
                    break
        
        # Use average offset if we have data, otherwise use standard 14 days
        if ovulation_offsets:
            avg_offset = statistics.mean(ovulation_offsets)
            confidence = 'high' if len(ovulation_offsets) >= 3 else 'medium'
        else:
            avg_offset = 14  # Standard ovulation day
            confidence = 'low'
        
        # Predict ovulation date based on last period
        predicted_ovulation = last_period.start_date + timedelta(days=int(avg_offset))
        
        # If the predicted date is in the past, predict for next cycle
        today = datetime.now().date()
        if predicted_ovulation < today:
            # Get predicted next period and calculate ovulation from that
            periods_for_cycle = Period.query.filter_by(user_id=current_user_id).order_by(Period.start_date.desc()).limit(6).all()
            
            if len(periods_for_cycle) >= 2:
                cycle_lengths = []
                for i in range(len(periods_for_cycle) - 1):
                    current_period = periods_for_cycle[i]
                    previous_period = periods_for_cycle[i + 1]
                    cycle_length = (current_period.start_date - previous_period.start_date).days
                    cycle_lengths.append(cycle_length)
                
                avg_cycle_length = statistics.mean(cycle_lengths)
                next_period_date = last_period.start_date + timedelta(days=int(avg_cycle_length))
                predicted_ovulation = next_period_date + timedelta(days=int(avg_offset))
        
        return jsonify({
            'predicted_date': predicted_ovulation.isoformat(),
            'average_ovulation_day': round(avg_offset, 1),
            'confidence': confidence,
            'ovulation_records_analyzed': len(ovulation_offsets)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/cycle-stats', methods=['GET'])
@jwt_required()
def get_cycle_stats():
    try:
        current_user_id = get_jwt_identity()
        
        # Get periods and ovulations
        periods = Period.query.filter_by(user_id=current_user_id).order_by(Period.start_date.desc()).all()
        ovulations = Ovulation.query.filter_by(user_id=current_user_id).order_by(Ovulation.ovulation_date.desc()).all()
        
        stats = {
            'total_periods': len(periods),
            'total_ovulations': len(ovulations),
            'average_cycle_length': None,
            'cycle_regularity': None,
            'average_period_length': None
        }
        
        if len(periods) >= 2:
            # Calculate cycle lengths
            cycle_lengths = []
            for i in range(len(periods) - 1):
                current_period = periods[i]
                previous_period = periods[i + 1]
                cycle_length = (current_period.start_date - previous_period.start_date).days
                cycle_lengths.append(cycle_length)
            
            stats['average_cycle_length'] = round(statistics.mean(cycle_lengths), 1)
            
            if len(cycle_lengths) >= 3:
                std_dev = statistics.stdev(cycle_lengths)
                if std_dev <= 2:
                    stats['cycle_regularity'] = 'very regular'
                elif std_dev <= 5:
                    stats['cycle_regularity'] = 'regular'
                else:
                    stats['cycle_regularity'] = 'irregular'
        
        # Calculate average period length
        period_lengths = []
        for period in periods:
            if period.end_date:
                length = (period.end_date - period.start_date).days + 1
                period_lengths.append(length)
        
        if period_lengths:
            stats['average_period_length'] = round(statistics.mean(period_lengths), 1)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

