import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add project root to path so internal imports work
sys.path.append(os.path.abspath("."))

from src.utils.weather_api import get_weather_batch
from src.logic.spatial import (
    load_districts,
    get_centroid,
    join_weather_to_districts,
    build_choropleth_map
)
from src.logic.stress  import load_thresholds, calculate_css, classify_css
from src.utils.helpers import get_anomalies, generate_advisory

# ---------------------------
# PAGE SETUP
# ---------------------------
st.set_page_config(page_title="FasalAlert", layout="wide")
st.title("🌾 FasalAlert — Crop Stress & Weather Advisory")

# ---------------------------
# LOAD STATIC DATA (cached)
# ---------------------------
@st.cache_data
def load_geo():
    return load_districts("data/india_districts.geojson")

@st.cache_data
def load_normals():
    df = pd.read_csv("data/imd_district_normals.csv")
    df.columns = df.columns.str.lower().str.strip()
    return df

gdf        = load_geo()
normals_df = load_normals()
thresholds = load_thresholds()
states     = sorted(gdf["NAME_1"].unique())

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("🔍 User Inputs")

selected_state = st.sidebar.selectbox("Select State", states)

districts_in_state = sorted(
    gdf[gdf["NAME_1"] == selected_state]["NAME_2"].unique()
)

selected_districts = st.sidebar.multiselect(
    "Select Districts (1–20)",
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

    # STEP 1 — GET COORDINATES FROM GEOJSON
    district_coords = []
    for d in selected_districts:
        lat, lon = get_centroid(d, selected_state, gdf)
        if lat is not None:
            district_coords.append({"district": d, "lat": lat, "lon": lon})

    if not district_coords:
        st.error("Could not find coordinates for selected districts. "
                 "Check district names match the GeoJSON file.")
        st.stop()

    district_df = pd.DataFrame(district_coords)

    # STEP 2 — FETCH LIVE WEATHER FROM API
    with st.spinner("Fetching live weather data..."):
        weather_df = get_weather_batch(district_df)

    if weather_df.empty:
        st.error("No weather data received. Check API key or internet connection.")
        st.stop()

    # STEP 3 — COMPUTE ANOMALIES, CSS, AND ADVISORY PER DISTRICT
    results = []
    for _, row in weather_df.iterrows():
        district = row["district"]

        # Get IMD historical normals for this district and month
        normal_row = normals_df[
            (normals_df["district"].str.lower() == district.lower()) &
            (normals_df["month"] == month)
        ]

        if not normal_row.empty:
            n_temp = float(normal_row["normal_temp_c"].values[0])
            n_rain = float(normal_row["normal_rainfall_mm"].values[0])
            n_hum  = float(normal_row["normal_humidity_pct"].values[0])
        else:
            # Fallback defaults if district not found in IMD normals
            n_temp, n_rain, n_hum = 30.0, 50.0, 70.0

        # Compute anomalies (observed minus historical normal)
        anomalies = get_anomalies(
            row["temperature"], row["rainfall"], row["humidity"],
            n_temp, n_rain, n_hum
        )

        # Compute CSS using sign-aware delta formula
        css_score = calculate_css(
            anomalies["delta_temp"],
            anomalies["delta_rain"],
            anomalies["delta_humidity"],
            crop,
            stage,
            thresholds
        )

        category = classify_css(css_score)
        advisory = generate_advisory(css_score, crop.capitalize(), anomalies)

        results.append({
            "District":      district,
            "State":         selected_state,
            "Crop":          crop.capitalize(),
            "Stage":         stage.replace("_", "-").capitalize(),
            "Temp (°C)":     row["temperature"],
            "ΔTemp":         round(anomalies["delta_temp"],     2),
            "Rainfall (mm)": row["rainfall"],
            "ΔRainfall":     round(anomalies["delta_rain"],     2),
            "Humidity (%)":  row["humidity"],
            "ΔRHI":          round(anomalies["delta_humidity"], 2),
            "CSS":           css_score,
            "Category":      category,
            "Advisory":      advisory
        })

    results_df = pd.DataFrame(results)

    # ---------------------------
    # OUTPUT 1 — 4 SUMMARY METRIC CARDS
    # ---------------------------
    st.subheader("📊 Summary")

    avg_css       = round(results_df["CSS"].mean(), 2)
    hottest       = results_df.loc[results_df["Temp (°C)"].idxmax(),    "District"]
    wettest       = results_df.loc[results_df["Rainfall (mm)"].idxmax(),"District"]
    most_stressed = results_df.loc[results_df["CSS"].idxmax(),          "District"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ Avg Stress Score (CSS)", avg_css)
    c2.metric("🔥 Hottest District",        hottest)
    c3.metric("🌧️ Wettest District",        wettest)
    c4.metric("⚠️ Most Stressed",           most_stressed)

    st.divider()

    # ---------------------------
    # OUTPUT 2 — DISTRICT DETAIL TABLE + CSV DOWNLOAD
    # ---------------------------
    st.subheader("📋 District Details")
    st.dataframe(results_df, use_container_width=True)

    csv = results_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv,
        file_name="fasalalert_report.csv",
        mime="text/csv"
    )

    st.divider()

    # ---------------------------
    # OUTPUT 3 — CHOROPLETH MAP
    # ---------------------------
    st.subheader("🗺️ Stress Map")

    map_input = results_df.rename(columns={
        "District": "district",
        "State":    "state"
    })
    merged = join_weather_to_districts(gdf, map_input)

    if not merged.empty:
        map_obj = build_choropleth_map(merged)
        st.components.v1.html(map_obj._repr_html_(), height=600)
    else:
        st.warning("Map could not render — district names may not match GeoJSON. "
                   "Results table above is still valid.")

    st.divider()

    # ---------------------------
    # OUTPUT 4 — HIGH STRESS ADVISORY PANELS
    # ---------------------------
    high_stress = results_df[results_df["CSS"] >= 6]

    if not high_stress.empty:
        st.subheader("🚨 High Stress Advisories")
        for _, row in high_stress.iterrows():
            st.error(
                f"**{row['District']}, {row['State']}**  |  "
                f"Crop: {row['Crop']}  |  "
                f"Stage: {row['Stage']}  |  "
                f"CSS: {row['CSS']}  |  "
                f"⚠️ {row['Advisory']}"
            )
    else:
        st.success("✅ No high-stress districts detected in your selection.")

else:
    st.info("👈 Select your parameters in the sidebar and click "
            "**Fetch & Analyse** to begin.")
