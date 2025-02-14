import requests
import pandas as pd
import io
import os
import json
from bs4 import BeautifulSoup

# GitHub Config
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "the-craccpot/Driveworld-Bot"  # Replace with your repo
GITHUB_FILE_PATH = "values.csv"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Website URL
WEBSITE_URL = "https://sites.google.com/view/drive-world-values/values-list"

# Step 1: Fetch Data from Website
def fetch_car_data():
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

# Step 2: Save Data to CSV
def save_to_csv(car_data):
    df = pd.DataFrame(car_data)
    df.to_csv(GITHUB_FILE_PATH, index=False)
    print(f"✅ Data saved to {GITHUB_FILE_PATH}")

# Step 3: Commit and Push CSV to GitHub
def upload_to_github():
    try:
        # Get the current file SHA
        response = requests.get(GITHUB_API_URL, headers=HEADERS)
        response_json = response.json()
        sha = response_json.get("sha", "")

        with open(GITHUB_FILE_PATH, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Upload new content
        payload = {
            "message": "🔄 Auto-update values.csv",
            "content": content.encode("utf-8").decode("latin-1"),  # Encode correctly for GitHub
            "sha": sha
        }

        update_response = requests.put(GITHUB_API_URL, headers=HEADERS, json=payload)

        if update_response.status_code == 200 or update_response.status_code == 201:
            print("✅ values.csv successfully updated on GitHub!")
        else:
            print(f"❌ Failed to update GitHub file: {update_response.text}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

# Main Execution
print("🔄 Fetching car data from website...")
car_data = fetch_car_data()

if car_data:
    print(f"✅ {len(car_data)} cars found. Saving to CSV...")
    save_to_csv(car_data)
    print("📤 Uploading values.csv to GitHub...")
    upload_to_github()
else:
    print("⚠️ No data extracted.")
