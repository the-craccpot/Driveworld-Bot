import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

# URLs
WEBSITE_URL = "https://sites.google.com/view/drive-world-values/values-list"
GITHUB_RAW_CSV_URL = "https://raw.githubusercontent.com/the-craccpot/Driveworld-Bot/main/values.csv"
CSV_FILE = "values.csv"

# Step 1: Fetch and Process Car Data from Website
def fetch_car_data_from_site():
    response = requests.get(WEBSITE_URL)
    if response.status_code != 200:
        print("⚠️ ERROR: Failed to fetch website data.")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    spans = [span.text.strip() for span in soup.find_all("span", class_="C9DxTc") if span.text.strip()]
    
    car_list = []
    current_car = {}
    last_key = None  

    i = 0
    while i < len(spans):
        text = spans[i].strip()

        if "Price:" in text:
            price_parts = [text.replace("Price:", "").strip()]
            i += 1
            while i < len(spans) and any(char.isdigit() for char in spans[i]):
                price_parts.append(spans[i])
                i += 1
            price = " ".join(price_parts).strip()
            
            if "-" not in price and any(char.isdigit() for char in price):
                try:
                    price_value = float(price.replace("M", "").replace("B", "").strip())
                    min_price = round(price_value * 0.67, 2)
                    max_price = round(price_value * 1.33, 2)
                    price = f"{min_price}-{max_price}M"
                except ValueError:
                    price = "N/A"
            
            current_car["Price"] = price
            continue

        elif text in ["Market Find:", "Market Sale:", "Demand:", "Inspired by:"]:
            last_key = text.replace(":", "").strip()
        
        elif last_key:
            current_car[last_key] = text.strip()
            last_key = None
        
        elif text and "$" not in text and ":" not in text and len(text) < 40:
            if "Name" in current_car:
                car_list.append(current_car)
                current_car = {}
            current_car["Name"] = text.strip()
        
        i += 1

    if current_car:
        car_list.append(current_car)

    return car_list

# Step 2: Save Car Data to CSV
def save_to_csv(car_data):
    headers = ["Name", "Price", "Market Find", "Market Sale", "Demand", "Inspired by"]
    
    df = pd.DataFrame(car_data)
    df.to_csv(CSV_FILE, index=False)
    print(f"✅ Data saved to {CSV_FILE}")

# Step 3: Fetch Car Data from GitHub CSV
def fetch_car_data_from_github():
    try:
        response = requests.get(GITHUB_RAW_CSV_URL)
        response.raise_for_status()  # Raise an error for failed requests

        # Load CSV data into a pandas DataFrame
        df = pd.read_csv(io.StringIO(response.text))
        car_list = df.to_dict(orient="records")  # Convert to list of dictionaries

        print(f"✅ Loaded {len(car_list)} cars from values.csv (GitHub).")
        return car_list
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return []

# Main Execution
print("🔄 Fetching car data from website...")
car_data = fetch_car_data_from_site()

if car_data:
    print(f"✅ {len(car_data)} cars found. Saving to CSV...")
    save_to_csv(car_data)
    print("📤 Upload `values.csv` to GitHub manually!")

# Fetching from GitHub
fetch_car_data_from_github()
