from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # Validate required fields
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # print("Login attempt",{'data': request.json})
        # if not request.json:
        #     return jsonify({'error': 'Request body is required'}), 400
        data = request.json
        # print(data.get('username'), data.get('password'))
        
        # Validate required fields
        if not data or not data.get('username') or not data.get('password'):
            # print(data)
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        # print(user)
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create access token
        # access_token = create_access_token(identity=user.id)
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @auth_bp.route('/profile', methods=['GET'])
# @jwt_required()
# def get_profile():
#     try:
#         print("Get profile attempt", {'user_id': get_jwt_identity()})
#         current_user_id = get_jwt_identity()
#         print("Current user ID", {'current_user_id': current_user_id})
#         if not current_user_id:
#             return jsonify({'error': 'User not authenticated'}), 401
#         print("Fetching user from database")
#         # Fetch user from database
#         user = User.query.get(current_user_id)
#         print("User found", {'user': user})
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         return jsonify(user.to_dict()), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500



@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        # print("DEBUG: Get profile attempt initiated.")
        current_user_id = get_jwt_identity()
        # print(f"DEBUG: Value from get_jwt_identity(): {current_user_id}, Type: {type(current_user_id)}")

        if current_user_id is None:
            # print("DEBUG: get_jwt_identity() returned None. This indicates an issue with the JWT or its identity claim.")
            return jsonify({'error': 'User not authenticated or JWT identity missing'}), 401

        # Attempt to convert current_user_id to an integer.
        # Flask-JWT-Extended stores the identity as whatever you pass to create_access_token.
        # If user.id is an integer, ensure it remains an integer here.
        # If your user IDs are strings (e.g., UUIDs), remove the int() conversion.
        try:
            # Assuming user.id (which you used for create_access_token(identity=user.id)) is an integer
            processed_user_id = int(current_user_id)
            # print(f"DEBUG: Converted user ID for query: {processed_user_id}, Type: {type(processed_user_id)}")
        except ValueError:
            # print(f"DEBUG: Failed to convert identity '{current_user_id}' to an integer. This might be the cause of the 422.")
            return jsonify({'error': 'Invalid user ID format in token payload'}), 422 # Or 401 if it's considered unauthenticatable

        # print(f"DEBUG: Attempting to fetch user from database with ID: {processed_user_id}")
        # Fetch user from database
        user = User.query.get(processed_user_id)
        # print(f"DEBUG: User object retrieved: {user}")

        if not user:
            # print(f"DEBUG: User with ID {processed_user_id} not found in database. This might indicate a stale token or deleted user.")
            return jsonify({'error': 'User not found'}), 404

        # print("DEBUG: User found. Returning user data.")
        return jsonify(user.to_dict()), 200

    except Exception as e:
        import traceback
        # print(f"ERROR: An unexpected exception occurred in get_profile: {e}")
        traceback.print_exc() # This will print the full traceback to your console
        return jsonify({'error': str(e)}), 500
