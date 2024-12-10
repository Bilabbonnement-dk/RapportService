"""
    Rapport Service:
    Håndterer...
"""

from flask import Flask, jsonify
import requests
import os
import sqlite3

app = Flask(__name__)

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'Database/rapport.db')

rented_cars = []


@app.route('/udlejedeBiler', methods=['GET'])
def udlejedeBiler():
    global rented_cars
    lejeaftale_response = requests.get("http://localhost:5002/lejeaftale")
    if lejeaftale_response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from Lejeaftale microservice"}), 500
    
    lejeaftale_data = lejeaftale_response.json()

    rented_cars= []
    for car in lejeaftale_data:
        bil_id = car['BilID']
        kunde_id = car['KundeID']
        
        status_response = requests.get(f"http://localhost:5002/status/{bil_id}")
        if status_response.status_code == 200 and status_response.json().get('status') == 'Aktiv':
                rented_cars.append({
                    "bil_id": bil_id,
                    "kunde_id": kunde_id,
                })
    
    return jsonify({"rented_cars": rented_cars}), 201

@app.route('/gemUdlejedeBiler', methods=['POST'])
def gemUdlejedeBiler():
    global rented_cars
    if len(rented_cars) == 0:
        return jsonify({"error": "No rented cars to save"}), 400

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO Rapport (Antal_Udlejede_Biler) VALUES (?)", (len(rented_cars),))
    
    conn.commit()
    conn.close()

    rented_cars = []
    return jsonify({"message": "Rented cars saved"}), 201

app.run(debug=True, host='0.0.0.0', port=5001)