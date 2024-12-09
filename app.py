"""
    Rapport Service:
    Håndterer...
"""

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import requests
import os
from datetime import timedelta
from Database.user import users
from Services.auth import authenticate_user, get_logged_in_user
from Services.cars import fetch_rented_cars

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.getenv('KEY')
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
#app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

jwt = JWTManager(app)

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'Database/rapport.db')

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'msg': 'Missing JSON payload'}), 400

    # Authenticate user
    result, status_code = authenticate_user(data)

    # If login is successful, set JWT cookies
    if status_code == 200:
        response = jsonify(result)
        set_access_cookies(response, result['access_token'])
        return response, 200

    # Return error if authentication fails
    return jsonify(result), status_code

# Protected resource
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    result, status_code = get_logged_in_user()
    return jsonify(result), status_code

# Fetch rented cars
@app.route('/udlejedeBiler', methods=['GET'])
@jwt_required()
def udlejede_biler():
    result, status_code = fetch_rented_cars()
    return jsonify(result), status_code

app.run(debug=True, host='0.0.0.0', port=5003)