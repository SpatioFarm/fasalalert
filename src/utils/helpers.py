import pandas as pd

# -----------------------------
# ANOMALY CALCULATION
# -----------------------------
def calculate_anomaly(current, normal):
    return current - normal


# -----------------------------
# FULL ANOMALY FUNCTION
# Returns delta for all three variables
# -----------------------------
def get_anomalies(temp, rain, humidity, normal_temp, normal_rain, normal_humidity):

    return {
        "delta_temp":     calculate_anomaly(temp,     normal_temp),
        "delta_rain":     calculate_anomaly(rain,     normal_rain),
        "delta_humidity": calculate_anomaly(humidity, normal_humidity)
    }


# -----------------------------
# DIRECTION-AWARE ADVISORY GENERATOR
# Sign of delta determines stress type:
#   ΔTemp > 0  → heat stress     | ΔTemp < 0  → cold stress
#   ΔRain < 0  → drought         | ΔRain > 0  → waterlogging
#   ΔHum > 0   → fungal risk     | ΔHum < 0   → dry stress
# -----------------------------
def generate_advisory(css, crop, anomalies=None):

    if css < 3:
        return f"{crop}: No stress. Conditions are normal."

    elif css < 6:
        if anomalies:
            dt = anomalies["delta_temp"]
            dr = anomalies["delta_rain"]
            dh = anomalies["delta_humidity"]
            hints = []
            if dt > 2:
                hints.append("above-normal temperature — monitor for heat stress")
            elif dt < -2:
                hints.append("below-normal temperature — watch for cold damage")
            if dr < -10:
                hints.append("rainfall deficit — consider supplemental irrigation")
            elif dr > 10:
                hints.append("excess rainfall — check field drainage")
            if dh > 10:
                hints.append("high humidity — watch for fungal disease")
            elif dh < -10:
                hints.append("low humidity — increase irrigation frequency")
            if hints:
                return f"{crop}: Moderate stress. {'; '.join(hints).capitalize()}."
        return f"{crop}: Moderate stress. Monitor field conditions closely."

    else:
        # High stress — direction-specific urgent advisory
        if anomalies:
            dt = anomalies["delta_temp"]
            dr = anomalies["delta_rain"]
            dh = anomalies["delta_humidity"]

            # Find dominant driver
            temp_contrib = abs(dt)
            rain_contrib = abs(dr)
            hum_contrib  = abs(dh)

            dominant = max(
                ("temp", temp_contrib),
                ("rain", rain_contrib),
                ("hum",  hum_contrib),
                key=lambda x: x[1]
            )[0]

            if dominant == "temp":
                if dt > 0:
                    return (f"{crop}: HIGH heat stress "
                            f"(+{dt:.1f}°C above normal). "
                            f"Irrigate within 48 hours to cool root zone.")
                else:
                    return (f"{crop}: HIGH cold stress "
                            f"({dt:.1f}°C below normal). "
                            f"Apply frost protection immediately.")

            elif dominant == "rain":
                if dr < 0:
                    return (f"{crop}: HIGH drought stress "
                            f"({dr:.1f}mm rainfall deficit). "
                            f"Irrigate immediately — crop water demand critical.")
                else:
                    return (f"{crop}: HIGH waterlogging risk "
                            f"(+{dr:.1f}mm excess rainfall). "
                            f"Ensure drainage channels are clear.")

            else:  # humidity dominant
                if dh > 0:
                    return (f"{crop}: HIGH humidity stress "
                            f"(+{dh:.1f}% above normal). "
                            f"Apply fungicide — disease outbreak risk.")
                else:
                    return (f"{crop}: HIGH dry stress "
                            f"({dh:.1f}% below normal humidity). "
                            f"Increase irrigation frequency.")

        return f"{crop}: HIGH stress! Take immediate action (irrigation/spray)."


# -----------------------------
# CSV EXPORT
# -----------------------------
def export_to_csv(data, filename="output.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data exported to {filename}")


# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":

    anomalies = get_anomalies(38, 5, 85, 29, 50, 68)
    print("Anomalies:", anomalies)

    print(generate_advisory(8.5, "Wheat", anomalies))
    print(generate_advisory(4.2, "Rice",  anomalies))
    print(generate_advisory(1.5, "Maize", anomalies))
