import requests
from flask import jsonify
import io
import csv
from Services.damages import fetch_damaged_cars

######## Fetches and combin damaged car data and loss calculations. #########
def get_damaged_car_data():
    
    result, status = fetch_damaged_cars()

    if status != 200:
        raise ValueError(result.get("error", "Failed to fetch damaged car data"))

    # Extract relevant data
    report_data = result.get('damaged_cars', {}).get('Damage_data', {}).get('report_data', [])
    losses = result.get("losses", [])

    return {"report_data": report_data, "losses": losses}
    



######## Generate CSV content for the business developer to see damaged cars and losses. #########
def generate_csv(report_data, losses):

    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV headers
    writer.writerow(["BilID", "SkadeNiveau", "Loss"])

    # Write rows by combining report_data with losses
    for car in report_data:
        bil_id = car.get("bil_id")
        damage_level = car.get("skade_niveau")
        loss = next((l.get("Loss") for l in losses if l.get("BilID") == bil_id), 0)
        writer.writerow([bil_id, damage_level, loss])

    # Reset pointer and return CSV content
    output.seek(0)
    csv_content = output.getvalue()
    output.close()
    return csv_content
