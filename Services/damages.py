import requests
from flask import jsonify


######### url for Skades Service #########
SKADES_SERVICE_URL = "http://localhost:5002"

####### url for Lejeaftale Service #######
LEJEAFTALE_SERVICE_URL = "http://localhost:5003"


DAMAGE_NIVEAU_TO_MONTHS = {
    1: 1,   # Minor damage, car is out of service for 1 month
    2: 3,   # Moderate damage, car is out of service for 3 months
    3: 6,   # Significant damage, car is out of service for 6 months
    4: 12   # Severe damage, car is out of service for 12 months
}

# Calculate financial losses for damaged cars.
def calculate_loss(damaged_cars, car_prices, damage_niveau_to_months):

    losses = []

    report_data = damaged_cars.get('Damage_data', {}).get('report_data', [])
    print( report_data)
    for car in report_data:

        if not isinstance(car, dict): 
            print(f"Skipping invalid entry in damaged_cars: {car}")
            continue

        bil_id = car.get("bil_id")
        damage_niveau = car.get("skade_niveau")

        # Skip entries with missing car_id or invalid SkadeNiveau
        if bil_id is None or damage_niveau is None:
            print(f"Skipping car with missing BilID or SkadeNiveau: {car}")
            continue

        # If SkadeNiveau is None, you can set a default value or skip
        if damage_niveau is None:
            print(f"Skipping car with null SkadeNiveau: {car}")
            continue  # Skip the car with no damage level (if that's what you want)

        # Determine the months out of service for the damage level
        months_out_of_service = damage_niveau_to_months.get(damage_niveau, 0)

        # Fetch the car's monthly price
        monthly_price = car_prices.get(str(bil_id), 0)  # Ensure car_id matches key type in car_prices

        # Calculate the total loss
        loss = months_out_of_service * monthly_price

        # Add the result to the list
        losses.append({"BilID": bil_id, "SkadeNiveau": damage_niveau, "Loss": loss})

    return losses



def fetch_damaged_cars(damage_niveau=None):
    # Fetch damage data from Skades Service
    try:
        if damage_niveau is None:
            url = f"{SKADES_SERVICE_URL}/send-skade-data"
        else:
            url = f"{SKADES_SERVICE_URL}/send-skade-data/{damage_niveau}"
        
        damage_response = requests.get(url)

        if damage_response.status_code == 404:
            return {"error": "The requested resource was not found in Skades Service."}, 404

        damaged_cars = damage_response.json()
    except (requests.RequestException, ValueError) as e:
        return {"error": f"Error while fetching Skades data: {e}"}, 500

    # Fetch price data from Lejeaftale Service
    try:
        price_response = requests.get(f"{LEJEAFTALE_SERVICE_URL}/process-pris-data")
        print("Raw price response:", price_response.status_code, price_response.json())  # Debugging
        
        if price_response.status_code not in [200, 201]:
            return {"error": f"Failed to fetch data from Lejeaftale Service. Status code: {price_response.status_code}"}, 500

        # Extract the price data
        price_data = price_response.json().get("price_data", [])
        print("Extracted price data:", price_data)  # Debugging

        # Convert price data to a dictionary
        car_prices = {str(item["bil_id"]): item["pris_pr_måned"] for item in price_data if "bil_id" in item}
        print("Car Prices Dictionary:", car_prices)  # Debugging

    except (requests.RequestException, ValueError) as e:
        return {"error": f"Error while fetching Lejeaftale data: {e}"}, 500

    if not car_prices:
        return {"error": "No price data retrieved from Lejeaftale Service"}, 404

    # Calculate losses for all damaged cars
    losses = calculate_loss(damaged_cars, car_prices, DAMAGE_NIVEAU_TO_MONTHS)

    return {
        "damaged_cars": damaged_cars,
        "car_prices": car_prices,
        "losses": losses
    }, 200
