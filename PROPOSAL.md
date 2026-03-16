# PROPOSAL.md

**Group Name:** SpatioFarm

**Members:** Swathi A Patil, K. Yaswanthi , Sathvik , Himanshu

**Project Working Title:** FasalAlert: Real-Time Crop Stress & Weather Risk Advisory Dashboard

---

## 1. Problem Statement

### What is the "Spatial Problem"?
Unseasonal rainfall, among other meteorological extremes, pose a serious threat to Indian agriculture.
Despite heat waves, cold waves, and droughts, the majority of farmers and district-level agricultural
Officers lack a single instrument that integrates geographical and real-time weather intelligence crop calendars to instantly identify areas of concern.

Current options are either too generic (national weather apps without agricultural context) or too technical (raw IMD data portals). There is a definite need for a **A crop calendar-driven advice dashboard with spatial awareness** that:

- The OpenWeatherMap API is used to retrieve **live weather data** (temperature, humidity, rainfall, wind) for every Indian
  district based on its geographic coordinates.
- Overlays fetched conditions against **crop-specific stress thresholds** (for example, rice is flood-stressed when rainfall
  exceeds 150 mm/week, and wheat is heat-stressed above 35°C during grain-filling).
- Combines temperature anomaly, humidity, and rainfall deviation to calculate a **Crop Stress Score (CSS)** for each
  district that is searched.
- Using GeoPandas and Folium, an interactive pan-India choropleth map is created, color-coding all district-level results
  according to the degree of stress.Agricultural officials can monitor an entire state at once by enabling bulk querying of
  **multiple districts simultaneously**.

### Target User
- **District Agricultural Officers (DAOs)** : They are responsible for keeping an eye on various blocks' seasonal
  agricultural conditions.
- **State agriculture authorities**: Before issuing advisories, they require a quick spatial picture of meteorological
  stress.
- **Agritech researchers and students**: A lightweight crop-weather correlation tool is needed for them. 
- **Farmers' cooperatives and FPOs**:They are interested in real-time risk indicators for insurance and procurement choices.

Although the architecture supports pan-India districts, 
the prototype will be demonstrated using selected agricultural regions for efficient analysis.

---

## 2. Technical Stack & Libraries

### GUI Framework
- **Streamlit**: It was selected due to its zero-boilerplate online user interface, integrated sidebar widgets, interactive
  map embedding using `st.components.v1.html()`, and integration with Folium and `st.map()`. Perfect for a novice team that
  wants to finish the project on schedule and produce a clean, demo-ready dashboard.


### Core Geospatial Logic
- **GeoPandas**: It is used to load the GeoJSON/Shapefile of the pan-India district boundaries, calculate district centroids
  (which are used as coordinates for API queries), execute spatial joins, and construct the Folium choropleth layer.
- **Folium** : An interactive Leaflet.js choropleth map showing district-level Crop Stress Scores embedded within Streamlit
  can be rendered.
- **Shapely** : It is included in GeoPandas package, for centroid extraction and point-in-polygon verification.

### The "Advanced" Component

**Web & API Track (Primary):**
- **Requests** library to call the **OpenWeatherMap Current Weather API**
  (free tier, 60 calls/min) using district centroid latitude/longitude.
- Fetched fields: `temp`, `humidity`, `rainfall (1h)`, `wind_speed`, `weather_id`.
- **IMD Open Data (static CSV)** — historical normal rainfall and temperature
  normals per district used as baseline for anomaly calculation.
- Stress thresholds are defined per crop per growth stage in a
  `crop_thresholds.json` config file, making the logic data-driven and
  easily extensible.

**Spatial Modeling Component (Secondary):**
- **GeoPandas spatial joins** — joining fetched weather point data back to
  district polygons for choropleth rendering.
- **Pandas** — for tabular aggregation, anomaly computation
  (observed − normal), and CSS formula application.

### Crop Stress Score (CSS) Formula
```
CSS = w1 × (ΔTemp / threshold_temp)
    + w2 × (ΔRainfall / threshold_rain)
    + w3 × (Humidity_deviation / threshold_humidity)

Where:
  Δ = observed − historical normal
  w1, w2, w3 = crop-specific weights (defined in crop_thresholds.json)
  CSS range: 0 (no stress) → 10 (extreme stress)
```

### Data Sources
1. **OpenWeatherMap Current Weather API** — free-tier key, queried by
   district centroid coordinates.
   URL: `https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}`
2. **India District Boundaries GeoJSON** — GADM India Level-2 or
   Datameet India Maps (open license).
   Source: `https://github.com/datameet/maps`
3. **IMD District-Level Climate Normals (CSV)** — historical average
   temperature and rainfall per district per month, sourced from IMD's
   open data portal or pre-compiled from published IMD reports.
   Source: `https://imdpune.gov.in`
4. **Crop Calendar Reference (JSON)** — manually compiled from ICAR's
   published crop-wise sowing/harvesting calendar for Indian states,
   stored as `data/crop_calendar.json`.

---

## 3. Proposed GUI Architecture

### Input Section (Streamlit Sidebar)
- **State Selector:** `st.selectbox` — filters the district list by state.
- **District Multi-Selector:** `st.multiselect` — allows selecting 1–20
  districts for simultaneous querying (bulk mode).
- **Crop Selector:** `st.selectbox` — choose the active crop
  (Wheat / Rice / Maize / Cotton / Soybean / Sugarcane).
- **Growth Stage Selector:** `st.radio` — select current growth stage
  (Sowing / Vegetative / Flowering / Grain-filling / Harvest) to apply
  the correct stress thresholds from `crop_thresholds.json`.
- **"Fetch & Analyse" Button:** Triggers the full API + computation pipeline.

### Processing Section
When **"Fetch & Analyse"** is clicked:
1. GeoPandas loads `india_districts.geojson` and extracts centroid
   coordinates for all selected districts.
2. Requests calls OpenWeatherMap API for each district centroid
   (batched with a short delay to respect rate limits).
3. Fetched weather values are compared against IMD normals to compute
   anomalies (ΔTemp, ΔRainfall, ΔHumidity).
4. CSS is computed per district using crop- and stage-specific weights
   from `crop_thresholds.json`.
5. CSS values are classified into three alert levels:
   - 🟢 **Low (0–3):** No advisory needed
   - 🟡 **Moderate (3–6):** Watch advisory issued
   - 🔴 **High (6–10):** Immediate action advisory issued
6. Results are joined back to the district GeoDataFrame for map rendering.

### Output / Visualization
- **Top Summary Bar:** `st.metric` cards showing average CSS, hottest
  district, wettest district, and most stressed district for the selected
  set.
- **Interactive Choropleth Map:** Full-width Folium map colour-coded by CSS
  (green → yellow → red), with district tooltips showing crop name, CSS
  value, live temperature, rainfall, and advisory text. Embedded via
  `st.components.v1.html()`.
- **District Detail Table:** `st.dataframe` showing all queried districts
  with columns: District, State, Crop, Stage, Temp (°C), ΔTemp, Rainfall
  (mm), ΔRainfall, Humidity (%), CSS, Advisory.
- **Advisory Panel:** For each HIGH-stress district, a prominent
  `st.error()` card is shown with the specific stress reason and a
  recommended farmer action (e.g., "Irrigate within 48 hours",
  "Apply fungicide — high humidity risk").
- **Download Button:** `st.download_button` to export the results table
  as a CSV for offline field use.

---

## 4. GitHub Repository Setup

**Repo URL:** `https://github.com/spatiofarm/fasalalert` *(to be created)*

**Initial Folder Structure:**
```
fasalalert/
├── data/
├── docs/
├── src/
│   ├── gui/
│   ├── logic/
│   └── utils/
└── PROPOSAL.md
```

---

## 5. Preliminary Task Distribution

| Member Name | Primary Responsibility | Secondary Responsibility |
|-------------|------------------------|--------------------------|
| **Himanshu** | `src/logic/stress.py` — CSS formula, crop threshold JSON loader, stress classification logic | `data/` — Compile `crop_thresholds.json` and `crop_calendar.json` from ICAR sources |
| **Sathvik** | `src/gui/app.py` — Streamlit sidebar widgets, metric cards, dataframe display, advisory panels, download button | UI/UX testing across districts and crops; writeup Section 3 (GUI description) |
| **Swathi A Patil** | `src/utils/weather_api.py` — OpenWeatherMap API integration, batch querying, rate-limit handling, response parsing | `data/imd_district_normals.csv` — data collection and cleaning |
| **K. Yaswanthi** | `src/logic/spatial.py` — GeoPandas district GeoJSON loading, centroid extraction, Folium choropleth builder | Git lead: repo setup, `README.md`, `requirements.txt`, `main.py`, final module integration |

---
*Proposal submitted by: SpatioFarm | Date: March 16, 2026*

