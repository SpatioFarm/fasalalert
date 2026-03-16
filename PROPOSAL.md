# PROPOSAL.md

**Group Name:** SpatioFarm

**Members:** Swathi A Patil, K. Yaswanthi , Sathvik , Himanshu

**Project Working Title:** FasalAlert: Real-Time Crop Stress & Weather Risk Advisory Dashboard

---

## 1. Problem Statement

### What is the "Spatial Problem"?
Indian agriculture is acutely vulnerable to weather extremes — unseasonal rainfall,
drought, heatwaves, and cold waves — yet most farmers and district-level agricultural
officers have no single tool that combines live weather intelligence with spatial
crop calendars to flag stress zones in real time.

Existing solutions are either too technical (raw IMD data portals) or too generic
(national weather apps with no crop context). There is a clear gap for a
**spatially-aware, crop-calendar-driven advisory dashboard** that:

- Fetches **live weather data** (temperature, humidity, rainfall, wind) for any
  Indian district using its geographic coordinates via the OpenWeatherMap API.
- Overlays fetched conditions against **crop-specific stress thresholds**
  (e.g., wheat is heat-stressed above 35°C during grain-filling; rice is
  flood-stressed when rainfall exceeds 150mm/week).
- Computes a **Crop Stress Score (CSS)** for each queried district combining
  temperature anomaly, humidity, and rainfall deviation.
- Renders all district-level results on an **interactive pan-India choropleth map**
  built with GeoPandas and Folium, colour-coded by stress severity.
- Allows bulk querying of **multiple districts simultaneously** so agricultural
  officers can monitor an entire state at once.

### Target User
- **District Agricultural Officers (DAOs)** monitoring seasonal crop conditions
  across multiple blocks.
- **State agriculture departments** needing a quick spatial overview of weather
  stress before issuing advisories.
- **Agritech researchers and students** requiring a lightweight crop-weather
  correlation tool.
- **Farmers' cooperatives and FPOs** wanting real-time risk flags for
  procurement and insurance decisions.

---

## 2. Technical Stack & Libraries

### GUI Framework
- **Streamlit** — chosen for its zero-boilerplate web UI, built-in sidebar
  widgets, interactive map embedding via `st.components.v1.html()`, and
  `st.map()` / Folium integration. Ideal for a beginner team producing a
  polished, demo-ready dashboard within the project timeline.

### Core Geospatial Logic
- **GeoPandas** — for loading the pan-India district boundary GeoJSON/Shapefile,
  computing district centroids (used as API query coordinates), performing
  spatial joins, and building the Folium choropleth layer.
- **Folium** — for rendering an interactive Leaflet.js choropleth map of
  district-level Crop Stress Scores embedded inside Streamlit.
- **Shapely** (bundled with GeoPandas) — for point-in-polygon checks and
  centroid extraction.

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
| **Swati Patil** | `src/utils/weather_api.py` — OpenWeatherMap API integration, batch querying, rate-limit handling, response parsing | `data/imd_district_normals.csv` — data collection and cleaning |
| **K. Yaswanthi** | `src/logic/spatial.py` — GeoPandas district GeoJSON loading, centroid extraction, Folium choropleth builder | Git lead: repo setup, `README.md`, `requirements.txt`, `main.py`, final module integration |

---
*Proposal submitted by: SpatioFarm | Date: March 16, 2026*

