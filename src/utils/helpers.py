# helpers.py
# Member 4 support file
# This file contains helper functions used across the whole project:
# 1. Anomaly calculator (observed - historical normal)
# 2. Advisory text generator
# 3. CSV export function

import pandas as pd

# ─────────────────────────────────────────
# FUNCTION 1 — Calculate weather anomalies
# ─────────────────────────────────────────
def calculate_anomaly(observed_temp, normal_temp,
                      observed_rain, normal_rain,
                      observed_humidity, normal_humidity):
    # Anomaly = observed value minus historical normal value
    delta_temp = observed_temp - normal_temp
    delta_rain = observed_rain - normal_rain
    delta_humidity = observed_humidity - normal_humidity

    return delta_temp, delta_rain, delta_humidity


# ─────────────────────────────────────────
# FUNCTION 2 — Generate advisory text
# ─────────────────────────────────────────
def generate_advisory(css_score, crop, delta_temp,
                      delta_rain, delta_humidity):
    # Low stress — no action needed
    if css_score <= 3:
        advisory = "No immediate action needed. Conditions are normal."

    # Moderate stress — watch advisory
    elif css_score <= 6:
        advisory = "Watch advisory issued. Monitor conditions closely."

        # Add specific reason based on which anomaly is highest
        if abs(delta_temp) >= abs(delta_rain) and abs(delta_temp) >= abs(delta_humidity):
            advisory += f" Temperature deviation detected for {crop}."
        elif abs(delta_rain) >= abs(delta_humidity):
            advisory += f" Rainfall deviation detected for {crop}."
        else:
            advisory += f" Humidity deviation detected for {crop}."

    # High stress — immediate action
    else:
        if delta_temp > 0:
            advisory = f"URGENT: Heat stress detected for {crop}. Irrigate within 48 hours."
        elif delta_rain > 0:
            advisory = f"URGENT: Excess rainfall detected for {crop}. Check drainage immediately."
        elif delta_humidity > 0:
            advisory = f"URGENT: High humidity for {crop}. Apply fungicide to prevent disease."
        else:
            advisory = f"URGENT: Severe stress detected for {crop}. Contact local agriculture officer."

    return advisory


# ─────────────────────────────────────────
# FUNCTION 3 — Export results to CSV
# ─────────────────────────────────────────
def export_to_csv(results_list):
    # results_list is a list of dictionaries
    # Each dictionary has one district's full results
    results_df = pd.DataFrame(results_list)

    # Convert DataFrame to CSV string for Streamlit download
    csv_string = results_df.to_csv(index=False)

    return csv_string