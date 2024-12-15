import requests
from flask import jsonify

######### url for Lejeaftale Service #########
LEJEAFTALE_SERVICE_URL = "http://localhost:5002"

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
