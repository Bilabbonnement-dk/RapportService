import requests
from flask import jsonify
import sqlite3
import datetime
import os

######### url for Lejeaftale Service #########
LEJEAFTALE_SERVICE_URL = "http://localhost:5003"

# Database path
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '../Database/rapport.db')

# Fetches the list of rented cars by communicating with the Lejeaftale microservice.
def fetch_rented_cars():

    # Fetch lejeaftale data
    lejeaftale_response = requests.get(f"{LEJEAFTALE_SERVICE_URL}/lejeaftale")
    if lejeaftale_response.status_code != 200:
        return {"error": "Failed to fetch data from Lejeaftale microservice"}, 500

    lejeaftale_data = lejeaftale_response.json()

    # Filter rented cars
    rented_cars = []
    for car in lejeaftale_data:
        bil_id = car['BilID']
        kunde_id = car['KundeID']

        status_response = requests.get(f"{LEJEAFTALE_SERVICE_URL}/status/{bil_id}")
        if status_response.status_code == 200 and status_response.json().get('status') == 'Aktiv':
            rented_cars.append({
                "bil_id": bil_id,
                "kunde_id": kunde_id,
            })

    return {
        "msg": "Rented cars retrieved successfully",
        "rented_cars": rented_cars
    }, 200


# Fetch rented cars and total price
def fetch_rented_cars_and_price():

    # Fetch lease agreements
    lejeaftale_response = requests.get(f"{LEJEAFTALE_SERVICE_URL}/lejeaftale")
    if lejeaftale_response.status_code != 200:
        return None, "Failed to fetch data from Lejeaftale microservice"

    lejeaftale_data = lejeaftale_response.json()
    
    # Initialize lists and totals
    rented_cars = []
    total_price_sum = 0

    # Process each lease agreement
    for car in lejeaftale_data:
        bil_id = car['BilID']
        kunde_id = car['KundeID']
        total_price = car['AbonnementsVarighed'] * car['PrisPrMåned']
        
        # Check the car status
        status_response = requests.get(f"{LEJEAFTALE_SERVICE_URL}/status/{bil_id}")
        if status_response.status_code == 200 and status_response.json().get('status') == 'Aktiv':
            rented_cars.append({
                "bil_id": bil_id,
                "kunde_id": kunde_id,
                "total_price": total_price
            })
            total_price_sum += total_price

    return rented_cars, total_price_sum



