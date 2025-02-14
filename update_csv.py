import requests
from bs4 import BeautifulSoup
import csv

# URL of the website containing the values
URL = "https://sites.google.com/view/drive-world-values/values-list"
CSV_FILE = "values.csv"

# Function to fetch and process car data
def fetch_car_data():
    response = requests.get(URL)
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

# Function to write data to CSV
def write_to_csv(car_data):
    headers = ["Name", "Price", "Market Find", "Market Sale", "Demand", "Inspired by"]
    
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        
        for car in car_data:
            writer.writerow({
                "Name": car.get("Name", "N/A"),
                "Price": car.get("Price", "N/A"),
                "Market Find": car.get("Market Find", "N/A"),
                "Market Sale": car.get("Market Sale", "N/A"),
                "Demand": car.get("Demand", "N/A"),
                "Inspired by": car.get("Inspired by", "N/A")
            })

# Main execution
print("🔄 Fetching car data...")
car_data = fetch_car_data()

if car_data:
    print(f"✅ {len(car_data)} cars found. Writing to CSV...")
    write_to_csv(car_data)
    print(f"📁 Data saved to {CSV_FILE}")
else:
    print("⚠️ No data extracted.")
