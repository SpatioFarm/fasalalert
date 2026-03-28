import json

# -----------------------------
# LOAD JSON FILE
# -----------------------------
def load_thresholds(path="data/crop_thresholds.json"):
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# CALCULATE CSS
# -----------------------------
def calculate_css(temp, rain, humidity, crop, stage, thresholds):
    
    crop_data = thresholds[crop][stage]

    temp_threshold = crop_data["temp_threshold"]
    rain_threshold = crop_data["rain_threshold"]
    humidity_threshold = crop_data["humidity_threshold"]

    weights = crop_data["weights"]

    # Normalized scores
    temp_score = temp / temp_threshold
    rain_score = rain / rain_threshold
    humidity_score = humidity / humidity_threshold

    # CSS formula
    css = (
        weights["temp"] * temp_score +
        weights["rain"] * rain_score +
        weights["humidity"] * humidity_score
    )

    # Scale to 0–10
    css = css * 10

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
# TEST RUN (VERY IMPORTANT)
# -----------------------------
if __name__ == "__main__":

    thresholds = load_thresholds()

    # Dummy values (you can change these)
    temp = 36
    rain = 70
    humidity = 80

    crop = "wheat"
    stage = "grain_filling"

    css = calculate_css(temp, rain, humidity, crop, stage, thresholds)

    category = classify_css(css)

    print("Temperature:", temp)
    print("Rainfall:", rain)
    print("Humidity:", humidity)
    print("Crop:", crop)
    print("Stage:", stage)
    print("CSS:", css)
    print("Stress Level:", category)