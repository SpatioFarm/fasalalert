from src.logic.stress import load_thresholds, calculate_css, classify_css
from src.utils.helpers import get_anomalies, generate_advisory

# Load thresholds
thresholds = load_thresholds()

# Sample weather data
temp = 36
rain = 70
humidity = 80

# Normal values
normal_temp = 30
normal_rain = 50
normal_humidity = 70

# Step 1: Anomaly
anomalies = get_anomalies(temp, rain, humidity, normal_temp, normal_rain, normal_humidity)

# Step 2: CSS
css = calculate_css(temp, rain, humidity, "wheat", "grain_filling", thresholds)

# Step 3: Classification
category = classify_css(css)

# Step 4: Advisory
advisory = generate_advisory(css, "wheat")

print("Anomalies:", anomalies)
print("CSS:", css)
print("Category:", category)
print("Advisory:", advisory)