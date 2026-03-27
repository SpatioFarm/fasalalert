import streamlit as st
import pandas as pd

st.set_page_config(page_title="FasalAlert", layout="wide")
st.title("🌾 FasalAlert — Crop Stress & Weather Advisory")

# ============================================================
# DUMMY DATA (will be replaced by real API data later)
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
# TASK 1 — SIDEBAR
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
# TASK 2 — SUMMARY METRIC CARDS
# ============================================================
if fetch:
    # Filter dummy data to selected districts
    filtered = dummy_data[dummy_data["District"].isin(selected_districts)]

    if filtered.empty:
        st.warning("No data found for selected districts. Please select at least one district.")
    else:
        st.subheader("📊 Summary")

        avg_css = round(filtered["CSS"].mean(), 2)
        hottest = filtered.loc[filtered["Temp (°C)"].idxmax(), "District"]
        wettest = filtered.loc[filtered["Rainfall (mm)"].idxmax(), "District"]
        most_stressed = filtered.loc[filtered["CSS"].idxmax(), "District"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ Avg Stress Score (CSS)", avg_css)
        col2.metric("🔥 Hottest District", hottest)
        col3.metric("🌧️ Wettest District", wettest)
        col4.metric("⚠️ Most Stressed", most_stressed)

        st.divider()

        # ============================================================
        # TASK 3 — DISTRICT DETAIL TABLE + CSV DOWNLOAD
        # ============================================================
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

        # ============================================================
        # TASK 4 — ADVISORY PANELS FOR HIGH STRESS DISTRICTS
        # ============================================================
        high_stress = filtered[filtered["CSS"] >= 6]

        if not high_stress.empty:
            st.subheader("🚨 High Stress Advisories")
            for _, row in high_stress.iterrows():
                st.error(
                    f"**{row['District']}, {row['State']}** | "
                    f"Crop: {row['Crop']} | "
                    f"CSS: {row['CSS']} | "
                    f"⚠️ {row['Advisory']}"
                )
        else:
            st.success("✅ No high-stress districts in your selection.")

else:
    st.info("👈 Select your parameters in the sidebar and click **Fetch & Analyse** to begin.")