# FasalAlert — Crop Stress & Weather Risk Advisory Dashboard

**Group:** SpatioFarm  
**Members:** K. Yaswanthi, Swathi A Patil, Sathvik, Himanshu   
**Course:** MSc Agriculture Analytics — Python Project 2026  

---

## What is FasalAlert?

FasalAlert is a real-time crop stress advisory dashboard that:
- Fetches live weather data for any Indian district
- Computes a Crop Stress Score (CSS) based on weather anomalies
- Displays results on an interactive pan-India choropleth map
- Issues actionable advisories for stressed districts

---

## Tech Stack

- **GUI:** Streamlit
- **Geospatial:** GeoPandas, Folium, Shapely
- **API:** OpenWeatherMap (Requests)
- **Data:** IMD Climate Normals, ICAR Crop Calendar, GADM District Boundaries

---

## How to Run

### Step 1 — Clone the repo
```
git clone https://github.com/SpatioFarm/fasalalert.git
cd fasalalert
```

### Step 2 — Install dependencies
```
pip install -r requirements.txt
```

### Step 3 — Launch the app
```
python main.py
```

---

## Folder Structure
```
fasalalert/
├── data/                        # GeoJSON, CSV, JSON data files
├── docs/                        # Writeup and architecture diagram
├── src/
│   ├── gui/app.py               # Streamlit dashboard
│   ├── logic/stress.py          # CSS formula and classification
│   ├── logic/spatial.py         # GeoPandas and Folium map
│   └── utils/weather_api.py     # OpenWeatherMap API calls
│   └── utils/helpers.py         # Anomaly calculator and advisory
├── main.py                      # Entry point
└── requirements.txt             # Dependencies
```

---

## Team Contributions

| Member | Primary Role |
|--------|-------------|
| Swathi | stress.py, crop_thresholds.json, crop_calendar.json |
| Sathvik | app.py — Streamlit GUI |
| K. Yaswanthi | weather_api.py — OpenWeatherMap API |
| Himanshu | spatial.py, helpers.py, repo setup, README |

---

## Demo Region

System supports pan-India districts.  
