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

@app.route('/udlejedeBiler', methods=['GET'])
def udlejedeBiler():
    response = requests.get("http://localhost:5002/lejeaftale")
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from Lejeaftale microservice"}), 500
    
    lejeaftale_data = response.json()
    
    available_cars = []
    for car in lejeaftale_data:
        bil_id = car['BilID']
        pris_pr_måned = car['PrisPrMåned']
        status_response = requests.get(f"http://localhost:5002/status/{bil_id}")
        if status_response.status_code == 200 and status_response.json().get('status') == 'Aktiv':
            available_cars.append({"bil_id": bil_id, "pris_pr_måned": pris_pr_måned})
    
    return jsonify({"available_cars": available_cars}), 201

app.run(debug=True, host='0.0.0.0', port=5003)