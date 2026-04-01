import json

# -----------------------------
# LOAD JSON FILE
# -----------------------------
def load_thresholds(path="data/crop_thresholds.json"):
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# CALCULATE CSS — SIGN-AWARE
# Uses direction of delta to apply correct threshold:
#   Temperature  → heat threshold vs cold threshold
#   Rainfall     → excess threshold vs deficit threshold
#   Humidity     → high threshold vs low threshold
# Cold/deficit/low thresholds default to 50% of the heat threshold
# if not separately defined in crop_thresholds.json
# -----------------------------
def calculate_css(delta_temp, delta_rain, delta_humidity, crop, stage, thresholds):

    crop_data = thresholds[crop][stage]
    weights   = crop_data["weights"]

    # --- TEMPERATURE ---
    if delta_temp > 0:
        # Heat stress
        temp_score = delta_temp / crop_data["temp_threshold"]
    else:
        # Cold stress — use separate cold threshold if available, else 50% of heat
        cold_thresh = crop_data.get("temp_threshold_cold",
                                    crop_data["temp_threshold"] * 0.5)
        temp_score  = abs(delta_temp) / cold_thresh

    # --- RAINFALL ---
    if delta_rain >= 0:
        # Excess rainfall / waterlogging
        rain_score = delta_rain / crop_data["rain_threshold"]
    else:
        # Drought / deficit
        deficit_thresh = crop_data.get("rain_threshold_deficit",
                                       crop_data["rain_threshold"] * 0.5)
        rain_score     = abs(delta_rain) / deficit_thresh

    # --- HUMIDITY ---
    if delta_humidity >= 0:
        # High humidity — fungal risk
        hum_score = delta_humidity / crop_data["humidity_threshold"]
    else:
        # Low humidity — dry stress
        low_thresh = crop_data.get("humidity_threshold_low",
                                   crop_data["humidity_threshold"] * 0.5)
        hum_score  = abs(delta_humidity) / low_thresh

    # --- CSS FORMULA ---
    css = (
        weights["temp"]     * temp_score +
        weights["rain"]     * rain_score +
        weights["humidity"] * hum_score
    ) * 10

    # Clamp to valid 0–10 range
    return round(max(0.0, min(10.0, css)), 2)


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

    # Test 1: Heat stress
    css1 = calculate_css(6, -30, 10, "wheat", "grain_filling", thresholds)
    print(f"Heat + Drought stress  → CSS: {css1} | {classify_css(css1)}")

    # Test 2: Cold stress
    css2 = calculate_css(-4, 5, -8, "wheat", "sowing", thresholds)
    print(f"Cold stress            → CSS: {css2} | {classify_css(css2)}")

    # Test 3: Normal conditions
    css3 = calculate_css(0.5, 1.0, -0.5, "rice", "vegetative", thresholds)
    print(f"Near-normal conditions → CSS: {css3} | {classify_css(css3)}")
