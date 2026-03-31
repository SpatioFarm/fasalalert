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
    
    delta_temp = calculate_anomaly(temp, normal_temp)
    delta_rain = calculate_anomaly(rain, normal_rain)
    delta_humidity = calculate_anomaly(humidity, normal_humidity)

    return {
        "delta_temp": delta_temp,
        "delta_rain": delta_rain,
        "delta_humidity": delta_humidity
    }


# -----------------------------
# ADVISORY GENERATOR
# -----------------------------
def generate_advisory(css, crop):

    if css < 3:
        return f"{crop}: No stress. Conditions are normal."

    elif css < 6:
        return f"{crop}: Moderate stress. Monitor field conditions."

    else:
        return f"{crop}: High stress! Take immediate action (irrigation/spray)."


# -----------------------------
# CSV EXPORT
# -----------------------------
def export_to_csv(data, filename="output.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data exported to {filename}")

if __name__ == "__main__":

    # Sample values
    temp = 36
    rain = 70
    humidity = 80

    normal_temp = 30
    normal_rain = 50
    normal_humidity = 70

    anomalies = get_anomalies(temp, rain, humidity, normal_temp, normal_rain, normal_humidity)

    print("Anomalies:", anomalies)

    # Test advisory
    css = 7.5
    print(generate_advisory(css, "wheat"))

    # Test CSV
    data = [anomalies]
    export_to_csv(data)
