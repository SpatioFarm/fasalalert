"""
src/utils/helpers.py
────────────────────
Utility functions for FasalAlert pipeline.

Functions
---------
get_anomalies()       — Compute delta (observed − normal) for temp, rain, humidity
generate_advisory()   — Human-readable advisory string with dominant stress driver
export_csv()          — Export list of district result dicts to a CSV file
rate_limit_handler()  — Throttled wrapper for bulk OpenWeatherMap API calls

CSS Scale (from stress.py)
--------------------------
  +7 to +10  →  Extreme Stress   🔴
  +4 to +7   →  High Stress      🟠
  +1 to +4   →  Moderate Stress  🟡
  −1 to +1   →  Near Normal      🟢
  −4 to −1   →  Favorable        🔵
 −10 to −4   →  Very Favorable   💙
"""

import csv
import time
import requests
from datetime import datetime


# ─────────────────────────────────────────────
# 1. GET ANOMALIES
#    Computes delta = observed − historical normal
#    Returns a dict so callers have named fields (no positional confusion)
# ─────────────────────────────────────────────
def get_anomalies(obs_temp, obs_rain, obs_humidity,
                  normal_temp, normal_rain, normal_humidity):
    """
    Calculate weather anomalies (deviations from historical normals).

    Parameters
    ----------
    obs_temp       : float  — live observed temperature (°C)
    obs_rain       : float  — live observed rainfall (mm)
    obs_humidity   : float  — live observed humidity (%)
    normal_temp    : float  — IMD historical normal temperature (°C)
    normal_rain    : float  — IMD historical normal rainfall (mm)
    normal_humidity: float  — IMD historical normal humidity (%)

    Returns
    -------
    dict with keys:
        delta_temp     : float  — positive → hotter than normal
        delta_rain     : float  — positive → wetter than normal
        delta_humidity : float  — positive → more humid than normal
        obs_temp       : float  — raw observed temp (passed through for display)
        obs_rain       : float  — raw observed rain
        obs_humidity   : float  — raw observed humidity
    """
    return {
        "delta_temp":      round(obs_temp     - normal_temp,     2),
        "delta_rain":      round(obs_rain     - normal_rain,     2),
        "delta_humidity":  round(obs_humidity - normal_humidity, 2),
        # Raw observed values passed through so callers don't need to re-pass them
        "obs_temp":        obs_temp,
        "obs_rain":        obs_rain,
        "obs_humidity":    obs_humidity,
    }


# ─────────────────────────────────────────────
# 2. GENERATE ADVISORY
#    Produces a plain-English advisory identifying the dominant driver.
#    Handles both positive (stress) and negative (favorable) CSS correctly.
#    Relies on classify_css() from stress.py — import lazily to avoid
#    circular imports if stress.py ever imports from helpers.
# ─────────────────────────────────────────────
def generate_advisory(css, crop, delta_temp, delta_rain, delta_humidity):
    """
    Generate a human-readable advisory string.

    Parameters
    ----------
    css            : float  — Crop Stress Score in [−10, +10]
    crop           : str    — crop name (e.g. "wheat")
    delta_temp     : float  — ΔTemp from get_anomalies()
    delta_rain     : float  — ΔRainfall from get_anomalies()
    delta_humidity : float  — ΔHumidity from get_anomalies()

    Returns
    -------
    str — formatted advisory message
    """
    # Lazy import avoids circular dependency
    from src.logic.stress import classify_css

    info    = classify_css(css)
    level   = info["level"]
    emoji   = info["emoji"]
    message = info["message"]

    # ── Identify which parameters are driving the result ──
    # Threshold for "significant" anomaly: 1 unit in any parameter
    drivers = []

    if abs(delta_temp) >= 1:
        direction = "above" if delta_temp > 0 else "below"
        drivers.append(
            f"temperature is {abs(delta_temp):.1f}°C {direction} normal"
        )

    if abs(delta_rain) >= 1:
        direction = "above" if delta_rain > 0 else "below"
        drivers.append(
            f"rainfall is {abs(delta_rain):.1f} mm {direction} normal"
        )

    if abs(delta_humidity) >= 1:
        direction = "above" if delta_humidity > 0 else "below"
        drivers.append(
            f"humidity is {abs(delta_humidity):.1f}% {direction} normal"
        )

    # ── Compose reason string ──
    if drivers:
        reason = "; ".join(drivers).capitalize() + "."
    else:
        reason = "All parameters are within normal range."

    # ── Crop-specific action recommendations ──
    action = _get_action_recommendation(css, crop, delta_temp, delta_rain, delta_humidity)

    return (
        f"{emoji} [{level}] for {crop.title()} | "
        f"{reason} | "
        f"{message}"
        + (f" → {action}" if action else "")
    )


def _get_action_recommendation(css, crop, delta_temp, delta_rain, delta_humidity):
    """
    Internal helper: returns a short crop-specific action string
    based on which parameter is the dominant stressor.
    """
    if css < 1:
        # No stress or favorable — no action needed
        return ""

    crop = crop.lower()

    # Find dominant driver
    scores = {
        "temp":     abs(delta_temp),
        "rain":     abs(delta_rain),
        "humidity": abs(delta_humidity),
    }
    dominant = max(scores, key=scores.get)

    actions = {
        "wheat": {
            "temp":     "Consider irrigation and shade nets to reduce heat load.",
            "rain":     "Ensure proper drainage to prevent waterlogging.",
            "humidity": "Apply preventive fungicide; monitor for rust and blight.",
        },
        "rice": {
            "temp":     "Maintain adequate water depth to buffer against heat.",
            "rain":     "Check bund integrity; excess water may cause lodging.",
            "humidity": "Scout for blast and bacterial leaf blight infection.",
        },
        "maize": {
            "temp":     "Irrigate during silking stage to protect pollination.",
            "rain":     "Improve field drainage; monitor for stalk rot.",
            "humidity": "Apply fungicide to control ear rot and leaf blight.",
        },
        "cotton": {
            "temp":     "Apply potassium foliar spray to reduce heat stress.",
            "rain":     "Avoid water stagnation; check for boll rot.",
            "humidity": "Monitor for grey mildew and apply appropriate fungicide.",
        },
        "soybean": {
            "temp":     "Irrigate at flowering and pod-fill stages.",
            "rain":     "Ensure drainage; excess rain causes root rot.",
            "humidity": "Watch for stem canker and pod and stem blight.",
        },
        "sugarcane": {
            "temp":     "Increase irrigation frequency during peak heat.",
            "rain":     "Open drainage channels to prevent root asphyxiation.",
            "humidity": "Apply bio-agents for red rot management.",
        },
    }

    # Default fallback for unknown crops
    default_actions = {
        "temp":     "Provide supplementary irrigation to reduce heat stress.",
        "rain":     "Improve drainage; monitor for waterlogging symptoms.",
        "humidity": "Apply preventive fungicide treatment.",
    }

    return actions.get(crop, default_actions).get(dominant, "")


# ─────────────────────────────────────────────
# 3. EXPORT CSV
#    Saves a list of district result dicts to a CSV file.
#    Safe for Streamlit's st.download_button (returns bytes too).
# ─────────────────────────────────────────────
def export_csv(results, output_path=None):
    """
    Export district results to a CSV file.

    Parameters
    ----------
    results     : list of dict — each dict is one district's result row.
                  Expected keys (extras are written too):
                    district, state, crop, stage,
                    obs_temp, obs_rain, obs_humidity,
                    delta_temp, delta_rain, delta_humidity,
                    css, stress_level, advisory
    output_path : str or None — if None, returns CSV content as a string
                  (useful for st.download_button).
                  If a path is given, writes the file and returns the path.

    Returns
    -------
    str — CSV string (if output_path is None) or file path (if written to disk)
    """
    if not results:
        raise ValueError("No results to export.")

    # Preferred column order — any extra keys are appended after
    preferred_cols = [
        "district", "state", "crop", "stage",
        "obs_temp", "obs_rain", "obs_humidity",
        "delta_temp", "delta_rain", "delta_humidity",
        "css", "stress_level", "advisory",
        "timestamp",
    ]

    # Collect all actual keys from results (preserving preferred order)
    all_keys = list(results[0].keys())
    ordered_cols = [c for c in preferred_cols if c in all_keys] + \
                   [c for c in all_keys if c not in preferred_cols]

    # Add timestamp to each row if not already present
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    for row in results:
        row.setdefault("timestamp", ts)

    if output_path is None:
        # Return as string for st.download_button
        import io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=ordered_cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
        return buf.getvalue()
    else:
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=ordered_cols, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
        return output_path


# ─────────────────────────────────────────────
# 4. RATE LIMIT HANDLER
#    Wraps OpenWeatherMap API calls for bulk district queries.
#    Free tier: 60 calls/min → default delay = 1.1 s between calls.
# ─────────────────────────────────────────────
def rate_limit_handler(districts, api_key, delay_seconds=1.1):
    """
    Fetch live weather for a list of districts with rate-limit-safe pacing.

    Parameters
    ----------
    districts      : list of dict — each dict must have:
                       { "district": str, "state": str,
                         "lat": float, "lon": float }
    api_key        : str  — OpenWeatherMap API key
    delay_seconds  : float — pause between API calls (default 1.1 s for free tier)

    Returns
    -------
    list of dict — one entry per district:
        {
            "district"    : str,
            "state"       : str,
            "lat"         : float,
            "lon"         : float,
            "obs_temp"    : float,   # °C
            "obs_rain"    : float,   # mm (1-hour accumulation)
            "obs_humidity": float,   # %
            "wind_speed"  : float,   # m/s
            "weather_desc": str,
            "success"     : bool,
            "error"       : str or None
        }
    """
    BASE_URL = (
        "https://api.openweathermap.org/data/2.5/weather"
        "?lat={lat}&lon={lon}&appid={key}&units=metric"
    )

    results = []

    for i, district in enumerate(districts):
        lat = district["lat"]
        lon = district["lon"]
        url = BASE_URL.format(lat=lat, lon=lon, key=api_key)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            obs_temp     = data["main"]["temp"]
            obs_humidity = data["main"]["humidity"]
            # rain.1h may be absent on dry days
            obs_rain     = data.get("rain", {}).get("1h", 0.0)
            wind_speed   = data["wind"]["speed"]
            weather_desc = data["weather"][0]["description"]

            results.append({
                "district":     district["district"],
                "state":        district["state"],
                "lat":          lat,
                "lon":          lon,
                "obs_temp":     round(obs_temp, 2),
                "obs_rain":     round(obs_rain, 2),
                "obs_humidity": round(obs_humidity, 2),
                "wind_speed":   round(wind_speed, 2),
                "weather_desc": weather_desc,
                "success":      True,
                "error":        None,
            })

        except requests.exceptions.HTTPError as e:
            results.append({
                **district,
                "obs_temp": None, "obs_rain": None, "obs_humidity": None,
                "wind_speed": None, "weather_desc": None,
                "success": False,
                "error": f"HTTP {response.status_code}: {str(e)}",
            })
        except requests.exceptions.ConnectionError:
            results.append({
                **district,
                "obs_temp": None, "obs_rain": None, "obs_humidity": None,
                "wind_speed": None, "weather_desc": None,
                "success": False,
                "error": "Connection error — check internet / API endpoint.",
            })
        except requests.exceptions.Timeout:
            results.append({
                **district,
                "obs_temp": None, "obs_rain": None, "obs_humidity": None,
                "wind_speed": None, "weather_desc": None,
                "success": False,
                "error": "Request timed out.",
            })

        # Throttle — respect OWM free-tier rate limit
        if i < len(districts) - 1:   # no sleep after the last call
            time.sleep(delay_seconds)

    return results


# ─────────────────────────────────────────────
# QUICK SELF-TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":

    print("\n" + "=" * 55)
    print("helpers.py — self-test")
    print("=" * 55)

    # ── Test get_anomalies ──
    anomalies = get_anomalies(36, 70, 80, 28, 50, 65)
    print("\nget_anomalies() result:")
    for k, v in anomalies.items():
        print(f"  {k}: {v}")

    # ── Test generate_advisory (positive CSS) ──
    print("\ngenerate_advisory() — positive stress:")
    adv_pos = generate_advisory(
        css=6.5, crop="wheat",
        delta_temp=anomalies["delta_temp"],
        delta_rain=anomalies["delta_rain"],
        delta_humidity=anomalies["delta_humidity"]
    )
    print(" ", adv_pos)

    # ── Test generate_advisory (negative CSS — was broken before) ──
    print("\ngenerate_advisory() — favorable / negative CSS:")
    anomalies_neg = get_anomalies(22, 30, 50, 28, 50, 65)
    adv_neg = generate_advisory(
        css=-3.8, crop="rice",
        delta_temp=anomalies_neg["delta_temp"],
        delta_rain=anomalies_neg["delta_rain"],
        delta_humidity=anomalies_neg["delta_humidity"]
    )
    print(" ", adv_neg)

    # ── Test export_csv ──
    print("\nexport_csv() — returns CSV string:")
    sample_results = [
        {
            "district": "Lucknow", "state": "Uttar Pradesh",
            "crop": "wheat", "stage": "grain_filling",
            "obs_temp": 36, "obs_rain": 70, "obs_humidity": 80,
            "delta_temp": 8, "delta_rain": 20, "delta_humidity": 15,
            "css": 6.5, "stress_level": "High Stress",
            "advisory": adv_pos,
        },
        {
            "district": "Shimla", "state": "Himachal Pradesh",
            "crop": "rice", "stage": "flowering",
            "obs_temp": 22, "obs_rain": 30, "obs_humidity": 50,
            "delta_temp": -6, "delta_rain": -20, "delta_humidity": -15,
            "css": -3.8, "stress_level": "Favorable",
            "advisory": adv_neg,
        },
    ]
    csv_string = export_csv(sample_results)
    print(csv_string)

    print("=" * 55)
