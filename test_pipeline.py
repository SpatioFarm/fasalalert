import sys
import os

# Ensure the project root is in the Python path to avoid 'ModuleNotFoundError'
# This assumes test_pipeline.py is located in the root 'fasalalert' folder.
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.logic.stress import load_thresholds, calculate_css, classify_css
from src.utils.helpers import get_anomalies, generate_advisory

# Load thresholds
thresholds = load_thresholds()

# Sample observed weather
temp, rain, humidity = 36, 70, 80

# Historical normal values for this district/month
normal_temp, normal_rain, normal_humidity = 28, 50, 65

# Step 1: Calculate anomalies (delta = observed - normal)
anomalies = get_anomalies(temp, rain, humidity, normal_temp, normal_rain, normal_humidity)

# Step 2: CSS uses anomalies, not raw values
css = calculate_css(
    anomalies["delta_temp"],
    anomalies["delta_rain"],
    anomalies["delta_humidity"],
    "wheat", "grain_filling", thresholds
)

# Step 3: Classification
category = classify_css(css)

# Step 4: Advisory with reason
advisory = generate_advisory(css, "wheat",
                              delta_temp=anomalies["delta_temp"],
                              delta_rain=anomalies["delta_rain"],
                              delta_humidity=anomalies["delta_humidity"])

print("=" * 50)
print("Anomalies :", anomalies)
print("CSS       :", css, "(range: 0-10)")
print("Category  :", category)
print("Advisory  :", advisory)
print("=" * 50)
