import requests
import time
import pandas as pd

API_KEY = "7076e29b9130852efc173cb259a75417"

def get_weather(lat, lon, district):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code == 429:
            print(f"Rate limit hit! Waiting 30 seconds...")
            time.sleep(30)
            response = requests.get(url)  # retry once

        if response.status_code != 200:
            print(f"API Error for {district}: {response.text}")
            return None

        data = response.json()
        return {
            "district": district,
            "temperature": round(data["main"]["temp"], 2),
            "humidity": data["main"]["humidity"],
            "rainfall": data.get("rain", {}).get("1h", 0)
        }
    except Exception as e:
        print(f"Error in {district}: {e}")
        return None


def get_weather_batch(district_df):
    """Query up to 20 districts with a 0.2s delay between calls"""
    results = []
    for _, row in district_df.iterrows():
        weather = get_weather(row["lat"], row["lon"], row["district"])
        if weather:
            results.append(weather)
        time.sleep(0.2)  # avoid API rate limit
    return pd.DataFrame(results)
