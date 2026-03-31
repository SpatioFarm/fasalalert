import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath("."))

# Internal Module Imports
from src.utils.weather_api import get_weather_batch
from src.logic.spatial import (
    load_districts,
    get_centroid,
    join_weather_to_districts,
    build_choropleth_map
)
from src.logic.stress import load_thresholds, calculate_css, classify_css
from src.utils.helpers import get_anomalies, generate_advisory

# ---------------------------
# PAGE SETUP
# ---------------------------
st.set_page_config(page_title="FasalAlert", layout="wide")
st.title("🌾 FasalAlert — Crop Stress & Weather Advisory")

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_geo():
    # Member 4's GeoJSON
    return load_districts("data/india_districts.geojson")

@st.cache_data
def load_normals():
    # IMD Normals provided by you
    df = pd.read_csv("data/imd_district_normals.csv")
    df.columns = df.columns.str.lower().str.strip()
    return df

gdf = load_geo()
normals_df = load_normals()
thresholds = load_thresholds()

states = sorted(gdf["NAME_1"].unique())

# ---------------------------
# SIDEBAR INPUT
# ---------------------------
st.sidebar.header("User Inputs")

selected_state = st.sidebar.selectbox("Select State", states)

districts_in_state = sorted(
    gdf[gdf["NAME_1"] == selected_state]["NAME_2"].unique()
)

selected_districts = st.sidebar.multiselect(
    "Select Districts",
    districts_in_state,
    default=districts_in_state[:3] if len(districts_in_state) >= 3 else districts_in_state
)

crop = st.sidebar.selectbox(
    "Select Crop",
    ["wheat", "rice", "maize", "cotton", "soybean", "sugarcane"]
)

stage = st.sidebar.radio(
    "Growth Stage",
    ["sowing", "vegetative", "flowering", "grain_filling", "harvest"]
)

fetch = st.sidebar.button("🚀 Fetch & Analyse")

# ---------------------------
# MAIN PIPELINE
# ---------------------------
if fetch:
    if not selected_districts:
        st.warning("Please select at least one district.")
        st.stop()

    month = datetime.now().month

    # STEP 1 — GET COORDINATES (Advanced Spatial Logic)
    district_coords = []
    for d in selected_districts:
        lat, lon = get_centroid(d, selected_state, gdf)
        if lat is not None:
            district_coords.append({"district": d, "lat": lat, "lon": lon})

    district_df = pd.DataFrame(district_coords)

    # STEP 2 — WEATHER API (Your Member 3 Code)
    with st.spinner("Fetching live weather..."):
        weather_df = get_weather_batch(district_df)

    if weather_df.empty:
        st.error("No weather data received. Check your API key or internet.")
        st.stop()

    # STEP 3 — PROCESS EACH DISTRICT
    results = []
    for _, row in weather_df.iterrows():
        district = row["district"]

        # GET NORMAL VALUES
        normal_row = normals_df[
            (normals_df["district"].str.lower() == district.lower()) &
            (normals_df["month"] == month)
        ]

        # Use defaults if IMD data is missing for a specific district
        if not normal_row.empty:
            n_temp = float(normal_row["normal_temp_c"].values[0])
            n_rain = float(normal_row["normal_rainfall_mm"].values[0])
            n_hum  = float(normal_row["normal_humidity_pct"].values[0])
        else:
            n_temp, n_rain, n_hum = 30.0, 50.0, 70.0

        # FIX: Calculate CSS using ACTUAL values (not deltas/differences)
        # This ensures the score is not 0
        css_score = calculate_css(
            row["temperature"],
            row["rainfall"],
            row["humidity"],
            crop,
            stage,
            thresholds
        )

        # Still calculate anomalies for the report/advisory
        anomalies = get_anomalies(
            row["temperature"], row["rainfall"], row["humidity"],
            n_temp, n_rain, n_hum
        )

        category = classify_css(css_score)
        
        # Detailed advisory
        advisory = generate_advisory(css_score, crop.capitalize())

        results.append({
            "district": district,
            "state": selected_state,
            "temperature": row["temperature"],
            "rainfall": row["rainfall"],
            "humidity": row["humidity"],
            "normal_temp": n_temp,
            "css_score": css_score,
            "category": category,
            "advisory": advisory
        })

    results_df = pd.DataFrame(results)

    # ---------------------------
    # DISPLAY OUTPUTS
    # ---------------------------
    st.subheader("📊 Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Stress Score", round(results_df["css_score"].mean(), 2))
    c2.metric("Max Temp", f"{results_df['temperature'].max()}°C")
    c3.metric("Most Stressed", results_df.sort_values("css_score", ascending=False)["district"].iloc[0])

    st.subheader("📋 Detailed Analysis")
    st.dataframe(results_df, use_container_width=True)

    # MAP (Member 4 Integration)
    st.subheader("🗺️ Stress Map")
    merged = join_weather_to_districts(gdf, results_df)
    if not merged.empty:
        map_obj = build_choropleth_map(merged)
        st.components.v1.html(map_obj._repr_html_(), height=600)
    else:
        st.error("Map could not sync with district names.")

    # DOWNLOAD
    csv = results_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV Report", csv, "fasalalert_report.csv", "text/csv")

else:
    st.info("👈 Select your parameters and click 'Fetch & Analyse' to start.")
