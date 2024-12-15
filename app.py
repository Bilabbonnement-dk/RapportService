"""
    Rapport Service:
    Håndterer...
"""

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import requests
import csv
import io
from flask import Response
import os
from datetime import timedelta
from Database.user import users
from Services.auth import authenticate_user, get_logged_in_user
from Services.cars import fetch_rented_cars
from Services.damages import fetch_damaged_cars
from Services.generateCSV import generate_csv
from Services.generateCSV import get_damaged_car_data

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

# Fetch damage niveau
@app.route('/process-skade-niveau/', methods=['GET'])  # No damage_niveau, get all data
@app.route('/process-skade-niveau/<int:damage_niveau>', methods=['GET'])  # With damage_niveau, get specific data
@jwt_required()
def process_niveau(damage_niveau=None):  # Make damage_niveau optional
    report_data, report_status_code = fetch_damaged_cars(damage_niveau)

    if report_status_code != 200:
        return jsonify(report_data), report_status_code

    return jsonify({"Damage_data": report_data}), 200



@app.route('/export-skadet-biler', methods=['GET'])
@jwt_required()
def export_damaged_cars():
    try:
        # Fetch damaged car data
        data = get_damaged_car_data()
        report_data = data.get("report_data", [])
        losses = data.get("losses", [])

        # Generate the CSV content
        csv_content = generate_csv(report_data, losses)

        # Return the CSV as a downloadable file
        response = Response(
            csv_content,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment; filename=damage_loss.csv"}
        )
        return response

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500





app.run(debug=True, host='0.0.0.0', port=5003)