import pandas as pd

# -----------------------------
# ANOMALY CALCULATION
# -----------------------------
def calculate_anomaly(current, normal):
    return current - normal


# -----------------------------
# FULL ANOMALY FUNCTION
# -----------------------------
def get_anomalies(temp, rain, humidity, normal_temp, normal_rain, normal_humidity):

    delta_temp     = calculate_anomaly(temp, normal_temp)
    delta_rain     = calculate_anomaly(rain, normal_rain)
    delta_humidity = calculate_anomaly(humidity, normal_humidity)

    return {
        "delta_temp":     delta_temp,
        "delta_rain":     delta_rain,
        "delta_humidity": delta_humidity
    }


# -----------------------------
# ADVISORY GENERATOR (improved: crop-specific + reason included)
# -----------------------------
def generate_advisory(css, crop, delta_temp=None, delta_rain=None, delta_humidity=None):

    crop = crop.capitalize()

    if css < 3:
        return f"{crop}: No stress detected. Conditions are within normal range."

    elif css < 6:
        reason = ""
        if delta_temp is not None and delta_temp > 2:
            reason = f" Temperature is {delta_temp}°C above normal — monitor field moisture."
        elif delta_rain is not None and delta_rain < -10:
            reason = f" Rainfall is {abs(delta_rain)} mm below normal — consider light irrigation."
        elif delta_humidity is not None and delta_humidity > 10:
            reason = f" Humidity is {delta_humidity}% above normal — watch for fungal risk."
        return f"{crop}: Moderate stress — Watch advisory issued.{reason}"

    else:
        reason = ""
        if delta_temp is not None and delta_temp > 5:
            reason = f" Temperature {delta_temp}°C above normal — irrigate within 48 hours to cool root zone."
        elif delta_rain is not None and delta_rain < -20:
            reason = f" Severe rainfall deficit ({abs(delta_rain)} mm below normal) — immediate irrigation required."
        elif delta_humidity is not None and delta_humidity > 15:
            reason = f" Very high humidity (+{delta_humidity}%) — apply fungicide immediately."
        else:
            reason = " Take immediate field action (irrigation / crop protection spray)."
        return f"{crop}: HIGH STRESS — Immediate action advisory!{reason}"


# -----------------------------
# CSV EXPORT
# -----------------------------
def export_to_csv(data, filename="output.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data exported to {filename}")


if __name__ == "__main__":

    temp, rain, humidity             = 36, 70, 80
    normal_temp, normal_rain, normal_humidity = 30, 50, 70

    anomalies = get_anomalies(temp, rain, humidity, normal_temp, normal_rain, normal_humidity)
    print("Anomalies:", anomalies)

    css = 7.5
    advisory = generate_advisory(css, "wheat",
                                  delta_temp=anomalies["delta_temp"],
                                  delta_rain=anomalies["delta_rain"],
                                  delta_humidity=anomalies["delta_humidity"])
    print(advisory)

    export_to_csv([anomalies])
