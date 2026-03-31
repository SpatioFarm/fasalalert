import json
import csv
import os

# -----------------------------
# LOAD THRESHOLDS
# Supports both JSON and CSV formats
# -----------------------------
def load_thresholds(path="data/crop_thresholds.json"):
    """
    Load crop stress thresholds from a JSON or CSV file.
    Returns a nested dict: thresholds[crop][stage] = { ... }
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".json":
        with open(path, "r") as f:
            return json.load(f)

    elif ext == ".csv":
        thresholds = {}
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                crop  = row["crop"].strip().lower()
                stage = row["stage"].strip().lower()

                thresholds.setdefault(crop, {})[stage] = {
                    "temp_threshold":     float(row["temp_threshold"]),
                    "rain_threshold":     float(row["rain_threshold"]),
                    "humidity_threshold": float(row["humidity_threshold"]),
                    "weights": {
                        "temp":     float(row["weight_temp"]),
                        "rain":     float(row["weight_rain"]),
                        "humidity": float(row["weight_humidity"]),
                    }
                }
        return thresholds

    else:
        raise ValueError(f"Unsupported threshold file format: {ext}. Use .json or .csv")


# -----------------------------
# CALCULATE CSS
#
# INPUT:  delta values (anomaly = observed − historical normal)
#         A POSITIVE delta means hotter / wetter / more humid than normal → STRESS
#         A NEGATIVE delta means cooler / drier / less humid than normal  → RELIEF / FAVORABLE
#
# FORMULA:
#   CSS = [w1*(ΔTemp/thr_T) + w2*(ΔRain/thr_R) + w3*(ΔHum/thr_H)] × 10
#
# RANGE:  −10 (most favorable) → 0 (baseline) → +10 (extreme stress)
#
# WHY NOT CLAMP TO 0?
#   The old code used max(0.0, css) which silently turned all negative
#   (favorable) conditions into 0, making it impossible to detect or
#   report below-normal weather conditions in the dashboard.
#   We now clamp to [−10, +10] so the full signal is preserved.
# -----------------------------
def calculate_css(delta_temp, delta_rain, delta_humidity, crop, stage, thresholds):
    """
    Calculate Crop Stress Score (CSS) in the range −10 to +10.

    Parameters
    ----------
    delta_temp     : float  — ΔTemp     = observed_temp − normal_temp
    delta_rain     : float  — ΔRainfall = observed_rain − normal_rain
    delta_humidity : float  — ΔHumidity = observed_hum  − normal_hum
    crop           : str    — crop name  (e.g. "wheat")
    stage          : str    — growth stage (e.g. "grain_filling")
    thresholds     : dict   — loaded via load_thresholds()

    Returns
    -------
    float in [−10.0, +10.0]
      Positive → stress above normal
      Zero     → exactly at baseline
      Negative → favorable / below-normal conditions
    """
    crop_key  = crop.strip().lower()
    stage_key = stage.strip().lower()

    if crop_key not in thresholds:
        raise KeyError(f"Crop '{crop}' not found in thresholds. "
                       f"Available: {list(thresholds.keys())}")
    if stage_key not in thresholds[crop_key]:
        raise KeyError(f"Stage '{stage}' not found for crop '{crop}'. "
                       f"Available stages: {list(thresholds[crop_key].keys())}")

    crop_data = thresholds[crop_key][stage_key]

    temp_threshold      = crop_data["temp_threshold"]
    rain_threshold      = crop_data["rain_threshold"]
    humidity_threshold  = crop_data["humidity_threshold"]
    weights             = crop_data["weights"]

    # Normalized anomaly scores (can be negative — that is intentional)
    temp_score     = delta_temp     / temp_threshold
    rain_score     = delta_rain     / rain_threshold
    humidity_score = delta_humidity / humidity_threshold

    # Weighted sum scaled to [−10, +10]
    # Positive → above-normal stress | Negative → below-normal (favorable)
    css = (weights["temp"]     * temp_score +
           weights["rain"]     * rain_score +
           weights["humidity"] * humidity_score) * 10

    # Clamp to [−10, +10] — preserves negative values unlike the old [0, 10] clamp
    css = max(-10.0, min(10.0, css))

    return round(css, 2)


# -----------------------------
# CLASSIFY CSS  (full −10 to +10 scale)
#
# Positive zone  → crop is under stress (heat / excess rain / excess humidity)
# Zero zone      → near-normal conditions
# Negative zone  → favorable / relief conditions (cooler / drier / lower humidity)
# -----------------------------
def classify_css(css):
    """
    Classify CSS into a human-readable stress level.

    Returns a dict with:
      - level   : short label (e.g. "High Stress")
      - emoji   : traffic-light icon for Streamlit display
      - color   : hex color for choropleth / metric coloring
      - message : one-line description for advisory
    """
    if css >= 7:
        return {
            "level":   "Extreme Stress",
            "emoji":   "🔴",
            "color":   "#cc0000",
            "message": "Immediate intervention required. Crop loss risk is very high."
        }
    elif css >= 4:
        return {
            "level":   "High Stress",
            "emoji":   "🟠",
            "color":   "#ff6600",
            "message": "High stress detected. Monitor closely and take corrective action."
        }
    elif css >= 1:
        return {
            "level":   "Moderate Stress",
            "emoji":   "🟡",
            "color":   "#ffcc00",
            "message": "Moderate stress. Watch advisory issued."
        }
    elif css >= -1:
        return {
            "level":   "Near Normal",
            "emoji":   "🟢",
            "color":   "#33cc33",
            "message": "Conditions are near normal. No advisory needed."
        }
    elif css >= -4:
        return {
            "level":   "Favorable",
            "emoji":   "🔵",
            "color":   "#3399ff",
            "message": "Conditions are below normal — cooler / drier than usual. Crops may benefit."
        }
    else:
        return {
            "level":   "Very Favorable",
            "emoji":   "💙",
            "color":   "#0055cc",
            "message": "Significantly below-normal conditions. Ideal growing environment."
        }


# -----------------------------
# GENERATE ADVISORY TEXT
# Explains WHICH factor is driving the stress (or relief)
# -----------------------------
def generate_advisory(css, crop, delta_temp, delta_rain, delta_humidity):
    """
    Returns a plain-English advisory string based on the dominant anomaly.
    Works for both positive (stress) and negative (favorable) CSS values.
    """
    classification = classify_css(css)
    level   = classification["level"]
    emoji   = classification["emoji"]

    drivers = []

    # Identify which deltas are significant (threshold: ±1 unit)
    if abs(delta_temp) >= 1:
        direction = "above" if delta_temp > 0 else "below"
        drivers.append(f"temperature is {abs(delta_temp):.1f}°C {direction} normal")

    if abs(delta_rain) >= 1:
        direction = "above" if delta_rain > 0 else "below"
        drivers.append(f"rainfall is {abs(delta_rain):.1f} mm {direction} normal")

    if abs(delta_humidity) >= 1:
        direction = "above" if delta_humidity > 0 else "below"
        drivers.append(f"humidity is {abs(delta_humidity):.1f}% {direction} normal")

    if drivers:
        reason = "; ".join(drivers).capitalize() + "."
    else:
        reason = "All parameters within normal range."

    return f"{emoji} [{level}] {reason} — {classification['message']}"


# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":

    # Try CSV first (matches your uploaded file), fall back to JSON
    try:
        thresholds = load_thresholds("data/crop_thresholds.csv")
        print("Loaded thresholds from CSV")
    except FileNotFoundError:
        thresholds = load_thresholds("data/crop_thresholds.json")
        print("Loaded thresholds from JSON")

    # ── TEST 1: Positive stress (old behaviour, should still work) ──
    print("\n" + "=" * 55)
    print("TEST 1 — Heat / rain stress (positive CSS)")
    temp, rain, humidity             = 36, 70, 80
    normal_temp, normal_rain, normal_hum = 28, 50, 65

    dt = temp - normal_temp          # +8
    dr = rain - normal_rain          # +20
    dh = humidity - normal_hum       # +15

    css = calculate_css(dt, dr, dh, "wheat", "grain_filling", thresholds)
    info = classify_css(css)
    adv  = generate_advisory(css, "wheat", dt, dr, dh)

    print(f"  ΔTemp={dt}  ΔRain={dr}  ΔHumidity={dh}")
    print(f"  CSS     : {css}  (range −10 to +10)")
    print(f"  Level   : {info['level']}  {info['emoji']}")
    print(f"  Advisory: {adv}")

    # ── TEST 2: Negative CSS (was silently zeroed out before — now visible) ──
    print("\n" + "=" * 55)
    print("TEST 2 — Cool / dry conditions (negative CSS, was broken before)")
    temp2, rain2, humidity2          = 22, 30, 50
    normal_temp, normal_rain, normal_hum = 28, 50, 65

    dt2 = temp2 - normal_temp        # −6
    dr2 = rain2 - normal_rain        # −20
    dh2 = humidity2 - normal_hum     # −15

    css2 = calculate_css(dt2, dr2, dh2, "wheat", "grain_filling", thresholds)
    info2 = classify_css(css2)
    adv2  = generate_advisory(css2, "wheat", dt2, dr2, dh2)

    print(f"  ΔTemp={dt2}  ΔRain={dr2}  ΔHumidity={dh2}")
    print(f"  CSS     : {css2}  (was showing 0 before the fix!)")
    print(f"  Level   : {info2['level']}  {info2['emoji']}")
    print(f"  Advisory: {adv2}")

    # ── TEST 3: Near-normal conditions ──
    print("\n" + "=" * 55)
    print("TEST 3 — Near-normal conditions")
    dt3, dr3, dh3 = 0.5, 1.0, -0.5
    css3 = calculate_css(dt3, dr3, dh3, "rice", "flowering", thresholds)
    info3 = classify_css(css3)
    print(f"  ΔTemp={dt3}  ΔRain={dr3}  ΔHumidity={dh3}")
    print(f"  CSS     : {css3}")
    print(f"  Level   : {info3['level']}  {info3['emoji']}")
    print("=" * 55)
