import streamlit as st

st.set_page_config(page_title="FasalAlert", layout="wide")

st.title("🌾 FasalAlert — Crop Stress & Weather Advisory")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Select Parameters")
    st.selectbox("State", ["-- Select State --"])
    st.multiselect("Districts", [])
    st.selectbox("Crop", ["Wheat", "Rice", "Maize", "Cotton", "Soybean", "Sugarcane"])
    st.radio("Growth Stage", ["Sowing", "Vegetative", "Flowering", "Grain-filling", "Harvest"])
    st.button("Fetch & Analyse")

# --- MAIN AREA ---
st.subheader("Summary")
st.info("Results will appear here after you click Fetch & Analyse.")

st.subheader("Map")
st.info("Choropleth map will appear here.")

st.subheader("District Details")
st.info("Data table will appear here.")