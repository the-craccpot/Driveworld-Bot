import pandas as pd
import requests
import io

# GitHub Raw CSV URL (Replace with your actual URL)
CSV_URL = "https://raw.githubusercontent.com/the-craccpot/Driveworld-Bot/refs/heads/main/values.csv"

# Function to fetch CSV data from GitHub
def fetch_car_data():
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()  # Raise an error for failed requests

        # Load CSV data into a pandas DataFrame
        df = pd.read_csv(io.StringIO(response.text))
        car_list = df.to_dict(orient="records")  # Convert to list of dictionaries

        print(f"✅ Loaded {len(car_list)} cars from values.csv.")
        return car_list
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return []

# Run test
fetch_car_data()
