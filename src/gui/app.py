import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath("."))

from src.utils.weather_api import get_weather_batch
from src.logic.spatial import load_districts, build_choropleth_map

st.set_page_config(page_title="FasalAlert", layout="wide")
st.title("🌾 FasalAlert — Crop Stress & Weather Advisory")

# ============================================================
# ALL DISTRICTS WITH REAL COORDINATES
# ============================================================
@st.cache_data
def load_district_data():
    data = [
        # Andhra Pradesh
        {"district": "Kadapa",          "lat": 14.47, "lon": 78.82, "state": "Andhra Pradesh"},
        {"district": "Visakhapatnam",   "lat": 17.68, "lon": 83.21, "state": "Andhra Pradesh"},
        {"district": "Vijayawada",      "lat": 16.51, "lon": 80.64, "state": "Andhra Pradesh"},
        {"district": "Nellore",         "lat": 14.43, "lon": 79.98, "state": "Andhra Pradesh"},
        {"district": "Kurnool",         "lat": 15.83, "lon": 78.04, "state": "Andhra Pradesh"},
        {"district": "Guntur",          "lat": 16.30, "lon": 80.43, "state": "Andhra Pradesh"},
        {"district": "Tirupati",        "lat": 13.63, "lon": 79.41, "state": "Andhra Pradesh"},
        {"district": "Anantapur",       "lat": 14.68, "lon": 77.60, "state": "Andhra Pradesh"},
        {"district": "Srikakulam",      "lat": 18.29, "lon": 83.89, "state": "Andhra Pradesh"},
        # Telangana
        {"district": "Hyderabad",       "lat": 17.38, "lon": 78.49, "state": "Telangana"},
        {"district": "Warangal",        "lat": 17.97, "lon": 79.59, "state": "Telangana"},
        {"district": "Nizamabad",       "lat": 18.67, "lon": 78.09, "state": "Telangana"},
        {"district": "Karimnagar",      "lat": 18.43, "lon": 79.13, "state": "Telangana"},
        {"district": "Khammam",         "lat": 17.25, "lon": 80.15, "state": "Telangana"},
        # Punjab
        {"district": "Ludhiana",        "lat": 30.90, "lon": 75.85, "state": "Punjab"},
        {"district": "Amritsar",        "lat": 31.63, "lon": 74.87, "state": "Punjab"},
        {"district": "Patiala",         "lat": 30.33, "lon": 76.40, "state": "Punjab"},
        {"district": "Jalandhar",       "lat": 31.33, "lon": 75.57, "state": "Punjab"},
        {"district": "Bathinda",        "lat": 30.21, "lon": 74.94, "state": "Punjab"},
        # Haryana
        {"district": "Karnal",          "lat": 29.68, "lon": 76.99, "state": "Haryana"},
        {"district": "Hisar",           "lat": 29.15, "lon": 75.72, "state": "Haryana"},
        {"district": "Rohtak",          "lat": 28.89, "lon": 76.60, "state": "Haryana"},
        {"district": "Panipat",         "lat": 29.39, "lon": 76.97, "state": "Haryana"},
        {"district": "Ambala",          "lat": 30.37, "lon": 76.78, "state": "Haryana"},
        # Rajasthan
        {"district": "Jaipur",          "lat": 26.91, "lon": 75.79, "state": "Rajasthan"},
        {"district": "Jodhpur",         "lat": 26.29, "lon": 73.02, "state": "Rajasthan"},
        {"district": "Kota",            "lat": 25.18, "lon": 75.83, "state": "Rajasthan"},
        {"district": "Bikaner",         "lat": 28.02, "lon": 73.31, "state": "Rajasthan"},
        {"district": "Ajmer",           "lat": 26.45, "lon": 74.64, "state": "Rajasthan"},
        # Uttar Pradesh
        {"district": "Agra",            "lat": 27.18, "lon": 78.01, "state": "Uttar Pradesh"},
        {"district": "Varanasi",        "lat": 25.32, "lon": 83.01, "state": "Uttar Pradesh"},
        {"district": "Lucknow",         "lat": 26.85, "lon": 80.95, "state": "Uttar Pradesh"},
        {"district": "Kanpur",          "lat": 26.46, "lon": 80.33, "state": "Uttar Pradesh"},
        {"district": "Allahabad",       "lat": 25.44, "lon": 81.84, "state": "Uttar Pradesh"},
        {"district": "Meerut",          "lat": 28.98, "lon": 77.70, "state": "Uttar Pradesh"},
        # Maharashtra
        {"district": "Nagpur",          "lat": 21.15, "lon": 79.09, "state": "Maharashtra"},
        {"district": "Pune",            "lat": 18.52, "lon": 73.86, "state": "Maharashtra"},
        {"district": "Nashik",          "lat": 19.99, "lon": 73.79, "state": "Maharashtra"},
        {"district": "Aurangabad",      "lat": 19.88, "lon": 75.32, "state": "Maharashtra"},
        {"district": "Solapur",         "lat": 17.68, "lon": 75.90, "state": "Maharashtra"},
        {"district": "Kolhapur",        "lat": 16.70, "lon": 74.24, "state": "Maharashtra"},
        # Madhya Pradesh
        {"district": "Bhopal",          "lat": 23.25, "lon": 77.40, "state": "Madhya Pradesh"},
        {"district": "Indore",          "lat": 22.72, "lon": 75.86, "state": "Madhya Pradesh"},
        {"district": "Gwalior",         "lat": 26.22, "lon": 78.18, "state": "Madhya Pradesh"},
        {"district": "Jabalpur",        "lat": 23.18, "lon": 79.99, "state": "Madhya Pradesh"},
        {"district": "Ujjain",          "lat": 23.18, "lon": 75.78, "state": "Madhya Pradesh"},
        # Karnataka
        {"district": "Bengaluru",       "lat": 12.97, "lon": 77.59, "state": "Karnataka"},
        {"district": "Mysuru",          "lat": 12.29, "lon": 76.63, "state": "Karnataka"},
        {"district": "Hubli",           "lat": 15.36, "lon": 75.12, "state": "Karnataka"},
        {"district": "Mangaluru",       "lat": 12.91, "lon": 74.85, "state": "Karnataka"},
        {"district": "Belagavi",        "lat": 15.85, "lon": 74.50, "state": "Karnataka"},
        # Tamil Nadu
        {"district": "Chennai",         "lat": 13.08, "lon": 80.27, "state": "Tamil Nadu"},
        {"district": "Coimbatore",      "lat": 11.01, "lon": 76.97, "state": "Tamil Nadu"},
        {"district": "Madurai",         "lat":  9.92, "lon": 78.12, "state": "Tamil Nadu"},
        {"district": "Salem",           "lat": 11.65, "lon": 78.16, "state": "Tamil Nadu"},
        {"district": "Tiruchirappalli", "lat": 10.79, "lon": 78.70, "state": "Tamil Nadu"},
        # Gujarat
        {"district": "Ahmedabad",       "lat": 23.02, "lon": 72.57, "state": "Gujarat"},
        {"district": "Surat",           "lat": 21.17, "lon": 72.83, "state": "Gujarat"},
        {"district": "Vadodara",        "lat": 22.30, "lon": 73.19, "state": "Gujarat"},
        {"district": "Rajkot",          "lat": 22.30, "lon": 70.80, "state": "Gujarat"},
        # West Bengal
        {"district": "Kolkata",         "lat": 22.57, "lon": 88.36, "state": "West Bengal"},
        {"district": "Asansol",         "lat": 23.68, "lon": 86.98, "state": "West Bengal"},
        {"district": "Siliguri",        "lat": 26.72, "lon": 88.43, "state": "West Bengal"},
        # Bihar
        {"district": "Patna",           "lat": 25.59, "lon": 85.13, "state": "Bihar"},
        {"district": "Gaya",            "lat": 24.79, "lon": 85.00, "state": "Bihar"},
        {"district": "Muzaffarpur",     "lat": 26.12, "lon": 85.39, "state": "Bihar"},
        # Odisha
        {"district": "Bhubaneswar",     "lat": 20.29, "lon": 85.82, "state": "Odisha"},
        {"district": "Cuttack",         "lat": 20.46, "lon": 85.88, "state": "Odisha"},
        {"district": "Sambalpur",       "lat": 21.46, "lon": 83.97, "state": "Odisha"},
    ]
    return pd.DataFrame(data)

district_df = load_district_data()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("🔍 Select Parameters")

    all_states = ["-- Select State --"] + sorted(district_df["state"].unique().tolist())
    selected_state = st.selectbox("State", all_states)

    if selected_state == "-- Select State --":
        available_districts = sorted(district_df["district"].tolist())
    else:
        available_districts = sorted(
            district_df[district_df["state"] == selected_state]["district"].tolist()
        )

    selected_districts = st.multiselect(
        "Districts (select 1–20)",
        available_districts,
        default=available_districts[:3] if len(available_districts) >= 3 else available_districts
    )

    selected_crop = st.selectbox(
        "Crop",
        ["Wheat", "Rice", "Maize", "Cotton", "Soybean", "Sugarcane"]
    )

    selected_stage = st.radio(
        "Growth Stage",
        ["Sowing", "Vegetative", "Flowering", "Grain-filling", "Harvest"]
    )

    fetch = st.button("🚀 Fetch & Analyse")

# ============================================================
# MAIN LOGIC
# ============================================================
if fetch:

    if not selected_districts:
        st.warning("Please select at least one district.")

    else:
        # ===== FETCH REAL WEATHER DATA =====
        with st.spinner("Fetching live weather data... please wait ⏳"):
            selected_rows = district_df[district_df["district"].isin(selected_districts)].copy()
            weather_df = get_weather_batch(selected_rows)

        # Add state, crop, stage columns
        state_map = dict(zip(district_df["district"], district_df["state"]))
        weather_df["State"] = weather_df["district"].map(state_map)
        weather_df["Crop"]  = selected_crop
        weather_df["Stage"] = selected_stage

        # Rename columns for display
        weather_df.rename(columns={
            "district":    "District",
            "temperature": "Temp (°C)",
            "humidity":    "Humidity (%)",
            "rainfall":    "Rainfall (mm)"
        }, inplace=True)

        # Simple CSS score based on temperature
        weather_df["CSS"] = weather_df["Temp (°C)"].apply(
            lambda t: round(min((t - 20) / 2, 10), 1) if t > 20 else 0
        )

        # Advisory based on CSS
        weather_df["Advisory"] = weather_df["CSS"].apply(
            lambda c: "🔴 Irrigate immediately — heat stress critical" if c >= 7
            else ("🟡 Monitor closely — moderate stress detected" if c >= 4
            else "🟢 No action needed — conditions normal")
        )

        filtered = weather_df

        # ===== SUMMARY CARDS =====
        st.subheader("📊 Summary")

        avg_css       = round(filtered["CSS"].mean(), 2)
        hottest       = filtered.loc[filtered["Temp (°C)"].idxmax(),    "District"]
        wettest       = filtered.loc[filtered["Rainfall (mm)"].idxmax(), "District"]
        most_stressed = filtered.loc[filtered["CSS"].idxmax(),           "District"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ Avg Stress Score", avg_css)
        col2.metric("🔥 Hottest District",  hottest)
        col3.metric("🌧️ Wettest District",  wettest)
        col4.metric("⚠️ Most Stressed",     most_stressed)

        st.divider()

        # ===== DISTRICT TABLE + CSV DOWNLOAD =====
        st.subheader("📋 District Details")
        st.dataframe(filtered, use_container_width=True)

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv,
            file_name="fasalalert_results.csv",
            mime="text/csv"
        )

        st.divider()

        # ===== HIGH STRESS ADVISORIES =====
        high_stress = filtered[filtered["CSS"] >= 7]

        if not high_stress.empty:
            st.subheader("🚨 High Stress Advisories")
            for _, row in high_stress.iterrows():
                st.error(
                    f"**{row['District']}, {row['State']}** | "
                    f"Crop: {row['Crop']} | Stage: {row['Stage']} | "
                    f"CSS: {row['CSS']} | {row['Advisory']}"
                )
        else:
            st.success("✅ No high stress districts in your selection.")

        st.divider()

        # ===== MAP =====
        st.subheader("🗺️ Crop Stress Map")
        try:
            gdf = load_districts("data/india_districts.geojson")

            map_data = filtered.copy()
            map_data.rename(columns={
                "District":     "district",
                "State":        "state",
                "CSS":          "css_score",
                "Advisory":     "advisory"
            }, inplace=True)

            merged = gdf.merge(
                map_data,
                left_on=["NAME_2", "NAME_1"],
                right_on=["district", "state"],
                how="inner"
            )

            map_obj = build_choropleth_map(merged)
            st.components.v1.html(map_obj._repr_html_(), height=600)

        except Exception as e:
            st.warning(f"Map could not load: {e}")

else:
    st.info("👈 Select parameters and click Fetch & Analyse to begin.")
