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
import sqlite3
import datetime
from flasgger import Swagger, swag_from
from swagger.config import swagger_config
from datetime import timedelta
from Database.user import users
from Services.auth import authenticate_user, get_logged_in_user
from Services.cars import fetch_rented_cars
from Services.damages import fetch_damaged_cars
from Services.generateCSV import generate_csv
from Services.generateCSV import get_damaged_car_data
from Services.cars import fetch_rented_cars_and_price

app = Flask(__name__)
swagger = Swagger(app, config=swagger_config)

app.config['JWT_SECRET_KEY'] = os.getenv('KEY')
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
#app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

jwt = JWTManager(app)

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'Database/rapport.db')

rented_cars = []
total_price = 0

lejeaftale_url = os.getenv("LEJEAFTALE_SERVICE_URL", "http://localhost:5002")

@app.route('/')
@swag_from('swagger/home.yaml')
def home():
    return jsonify({
        "service": "API Gateway",
        "available_endpoints": [
            {
                "path": "/udlejedeBiler",
                "method": "GET",
                "description": "Get a list of rented cars and the total price sum"
            },
            {
                "path": "/gemUdlejedeBiler",
                "method": "POST",
                "description": "Save the count of rented cars and the total price sum"
            }
        ]
    })

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

# Fetch rented cars and total price
@app.route('/udlejedeBiler', methods=['GET'])
@swag_from('swagger/udlejedeBiler.yaml')
def udlejedeBiler():

    rented_cars, error_message = fetch_rented_cars_and_price()

    if error_message:
        return jsonify({"error": error_message}), 500

    total_price_sum = sum(car['total_price'] for car in rented_cars)
    
    return jsonify({"rented_cars": rented_cars, "total_price_sum": total_price_sum}), 200



@app.route('/gemUdlejedeBiler', methods=['POST'])
@swag_from('swagger/gemUdlejedeBiler.yaml')
def gemUdlejedeBiler():
    global rented_cars
    global total_price
    if len(rented_cars) == 0:
        return jsonify({"error": "No rented cars to save"}), 400
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO Rapport (Antal_Udlejede_Biler, RapportDato, Sammenlagt_Pris) VALUES (?, ?, ?)", (len(rented_cars), current_date, total_price))
    
    conn.commit()
    conn.close()

    rented_cars = []
    return jsonify({"message": "Rented cars saved"}), 201

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

app.run(debug=True, host='0.0.0.0', port=5001)