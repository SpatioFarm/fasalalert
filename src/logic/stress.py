import json

# -----------------------------
# LOAD JSON FILE
# -----------------------------
def load_thresholds(path="data/crop_thresholds.json"):
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# CALCULATE CSS
# FIX: Takes delta (anomaly) values, NOT raw values
# Formula: CSS = w1*(ΔTemp/thr_T) + w2*(ΔRain/thr_R) + w3*(ΔHum/thr_H)  scaled to 0-10
# -----------------------------
def calculate_css(delta_temp, delta_rain, delta_humidity, crop, stage, thresholds):

    crop_data = thresholds[crop][stage]

    temp_threshold   = crop_data["temp_threshold"]
    rain_threshold   = crop_data["rain_threshold"]
    humidity_threshold = crop_data["humidity_threshold"]
    weights          = crop_data["weights"]

    # Normalized anomaly scores
    temp_score     = delta_temp     / temp_threshold
    rain_score     = delta_rain     / rain_threshold
    humidity_score = delta_humidity / humidity_threshold

    # Weighted sum then scale to 0-10 and clamp
    css = (weights["temp"] * temp_score +
           weights["rain"] * rain_score +
           weights["humidity"] * humidity_score) * 10

    css = max(0.0, min(10.0, css))   # clamp to valid range
    return round(css, 2)


# -----------------------------
# CLASSIFY CSS
# -----------------------------
def classify_css(css):
    if css < 3:
        return "Low"
    elif css < 6:
        return "Moderate"
    else:
        return "High"


# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":

    thresholds = load_thresholds()

    temp, rain, humidity             = 36, 70, 80
    normal_temp, normal_rain, normal_humidity = 28, 50, 65

    delta_temp     = temp - normal_temp
    delta_rain     = rain - normal_rain
    delta_humidity = humidity - normal_humidity

    crop, stage = "wheat", "grain_filling"

    css = calculate_css(delta_temp, delta_rain, delta_humidity, crop, stage, thresholds)
    category = classify_css(css)

    print("Anomaly   | ΔTemp:", delta_temp, " ΔRain:", delta_rain, " ΔHumidity:", delta_humidity)
    print("CSS:", css, "| Stress Level:", category)
