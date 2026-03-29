import streamlit as st
import pandas as pd
from src.logic.spatial import load_districts, build_choropleth_map

st.set_page_config(page_title="FasalAlert", layout="wide")
st.title("🌾 FasalAlert — Crop Stress & Weather Advisory")

# ============================================================
# DUMMY DATA (will be replaced later)
# ============================================================
dummy_data = pd.DataFrame({
    "District": ["Ludhiana", "Amritsar", "Karnal", "Hisar", "Jaipur"],
    "State": ["Punjab", "Punjab", "Haryana", "Haryana", "Rajasthan"],
    "Crop": ["Wheat", "Wheat", "Rice", "Cotton", "Maize"],
    "Stage": ["Grain-filling", "Flowering", "Vegetative", "Sowing", "Harvest"],
    "Temp (°C)": [38.2, 35.0, 32.5, 41.0, 29.0],
    "ΔTemp": [5.2, 2.0, -0.5, 8.0, -1.0],
    "Rainfall (mm)": [2.0, 15.0, 80.0, 0.0, 10.0],
    "ΔRainfall": [-10.0, 3.0, 68.0, -5.0, -2.0],
    "Humidity (%)": [85, 60, 90, 30, 55],
    "CSS": [8.5, 4.2, 3.1, 7.8, 1.5],
    "Advisory": [
        "Irrigate within 48 hours — heat stress critical",
        "Monitor closely — moderate stress detected",
        "No action needed — conditions normal",
        "Apply irrigation — severe drought stress",
        "No action needed — low stress"
    ]
})

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("🔍 Select Parameters")

    states = ["-- Select State --", "Punjab", "Haryana", "Rajasthan",
              "Uttar Pradesh", "Maharashtra", "Madhya Pradesh"]
    selected_state = st.selectbox("State", states)

    districts = ["Ludhiana", "Amritsar", "Karnal", "Hisar", "Jaipur"]
    selected_districts = st.multiselect(
        "Districts (select 1–20)",
        districts,
        default=["Ludhiana", "Amritsar", "Hisar"]
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

    # Filter data
    filtered = dummy_data[dummy_data["District"].isin(selected_districts)]

    if filtered.empty:
        st.warning("No data found. Select districts.")

    else:
        # ================= SUMMARY =================
        st.subheader("📊 Summary")

        avg_css = round(filtered["CSS"].mean(), 2)
        hottest = filtered.loc[filtered["Temp (°C)"].idxmax(), "District"]
        wettest = filtered.loc[filtered["Rainfall (mm)"].idxmax(), "District"]
        most_stressed = filtered.loc[filtered["CSS"].idxmax(), "District"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ Avg Stress Score", avg_css)
        col2.metric("🔥 Hottest", hottest)
        col3.metric("🌧️ Wettest", wettest)
        col4.metric("⚠️ Most Stressed", most_stressed)

        st.divider()

        # ================= TABLE =================
        st.subheader("📋 District Details")
        st.dataframe(filtered, use_container_width=True)

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="fasalalert_results.csv",
            mime="text/csv"
        )

        st.divider()

        # ================= ADVISORY =================
        high_stress = filtered[filtered["CSS"] >= 6]

        if not high_stress.empty:
            st.subheader("🚨 High Stress Advisories")
            for _, row in high_stress.iterrows():
                st.error(
                    f"{row['District']}, {row['State']} | "
                    f"CSS: {row['CSS']} | {row['Advisory']}"
                )
        else:
            st.success("✅ No high stress districts")

        st.divider()

        # ================= MAP =================
        st.subheader("🗺️ Crop Stress Map")

        gdf = load_districts("data/india_districts.geojson")

        map_data = filtered.copy()
        map_data.rename(columns={
            "District": "district",
            "State": "state",
            "CSS": "css_score",
            "Advisory": "advisory"
        }, inplace=True)

        merged = gdf.merge(
            map_data,
            left_on=["NAME_2", "NAME_1"],
            right_on=["district", "state"],
            how="inner"
        )

        map_obj = build_choropleth_map(merged)

        st.components.v1.html(map_obj._repr_html_(), height=600)

else:
    st.info("👈 Select parameters and click Fetch & Analyse")