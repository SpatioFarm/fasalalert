# FasalAlert — Report Outline

## Section 1: Problem Statement & Motivation

### 1.1 Background
More than 60 percent of the rural population is dependent on Indian agriculture, which also supports national food security to a significant extent. However, it remains sharply susceptible to weather extremes—unseasonal rainfall, long droughts, heat waves, cold waves, and severe crop losses annually.

Although weather information is provided by the India Meteorological Department (IMD) and remote sensing platforms, farm officers at the district level lack access to a unified, crop-specific stress and live weather intelligence tool that offers real-time warning signals on risk areas.

### 1.2 The Spatial Problem
Crop stress is inherently a spatial issue. Weather conditions vary significantly across districts, and the impact of the same weather event depends on crop type and growth stage. For example, wheat experiences critical stress at temperatures of around 38°C during grain filling but is less affected during planting.

Current solutions are either too technical—requiring professional interpretation of raw IMD data—or too generalized—lacking crop-specific details in national weather apps—and not spatially aware, disregarding district-level geographical differences.

A more effective approach would involve a dashboard integrating live weather data with district boundaries and crop-specific thresholds to provide spatially-aware advisories.

### 1.3 Proposed Solution
FasalAlert aims to bridge this gap by:
1. Fetching live weather data (temperature, humidity, rainfall) for any Indian district using the OpenWeatherMap API and district centroid coordinates calculated with GeoPandas.
2. Computing a Crop Stress Score (CSS) for each district by comparing current weather observations with IMD historical normals and ICAR-published crossover weights for crops.
3. Displaying findings on an interactive pan-India choropleth map created using GeoPandas and Folium, color-coded by severity (green - yellow - red).
4. Offering operational recommendations for high-stress districts with specific actions for farmers.

### 1.4 Target Users
| User Group | Needs |
|--------------|--------|
| District Agricultural Officers (DAOs) | Survey seasonal crop stress across multiple blocks |
| State Agriculture Departments | Conduct rapid spatial scans before issuing advisories |
| Agritech Researchers & Students | Use as a lightweight crop-weather correlation tool |
| Farmers Cooperatives & FPOs | Real-time risk flags for procurement and insurance |

### 1.5 Spatial Framing
The system considers India's administrative boundaries at the district level (GADM Level-2). It uses GeoPandas to extract centroids as coordinates for API queries and links findings back to district polygons for choropleth visualization.

The prototype covers pan-India regions but focuses initially on key agricultural zones like Punjab's Wheat Belt (Ludhiana, Amritsar, Patiala, Sangrur, Moga) to test functionality under real-world conditions.

## Section 2: Technical Stack & Libraries
### 2.1 GUI Framework — Streamlit

Streamlit was selected as the GUI framework for FasalAlert because it enables the construction of a fully interactive, browser-accessible web dashboard in pure Python without requiring any frontend expertise in HTML, CSS, or JavaScript. Unlike desktop-only alternatives such as Tkinter or PyQt6, Streamlit produces a live web application that any stakeholder — a district agricultural officer, a researcher, or a cooperative member — can access from a browser with no installation required.

For a team working within a four-day sprint, Streamlit's zero-boilerplate layout system was decisive. A functioning page with sidebar widgets, metric cards, a dataframe, and an embedded Folium map can be assembled in under sixty lines of code. Streamlit also provides `st.components.v1.html()`, which accepts any raw HTML string and renders it inline — the critical feature that allows the Folium choropleth map to be embedded directly inside the dashboard without any additional server infrastructure.

### 2.2 Core Geospatial Libraries — GeoPandas and Folium

**GeoPandas** is the primary geospatial processing library in FasalAlert. It extends the Pandas DataFrame with a geometry column, enabling the team to load the pan-India district boundaries GeoJSON file (GADM Level-2), compute the geographic centroid of each district polygon as a latitude/longitude coordinate pair, perform spatial joins to attach weather data back to district polygons, and prepare the enriched GeoDataFrame for choropleth rendering. GeoPandas was chosen over raw Shapely processing because it preserves the tabular structure that Pandas needs for vectorised anomaly computation. The Shapely library, which is bundled with GeoPandas, handles lower-level geometric operations such as point-in-polygon checks and centroid extraction.

**Folium** wraps the Leaflet.js interactive mapping engine in a Python interface, allowing the team to programmatically generate a choropleth map of India coloured from green (low stress) through yellow (moderate) to red (high stress) based on the CSS value of each district. Folium generates a self-contained HTML string that is passed to `st.components.v1.html()` for rendering inside Streamlit. Each district polygon on the map carries an interactive tooltip showing the crop name, CSS score, live temperature, observed rainfall, and advisory text, so users can inspect any district without leaving the map view.

### 2.3 Web and API Libraries — Requests and Pandas

**Requests** provides the HTTP client for calling the OpenWeatherMap Current Weather API. Each API call is constructed with a district centroid's latitude and longitude, and the JSON response is parsed to extract four fields: `main.temp` (temperature in Kelvin, converted to Celsius), `main.humidity` (relative humidity as a percentage), `rain.1h` (rainfall in millimetres over the past hour), and `wind.speed`. A 0.2-second delay is enforced between consecutive calls to stay within the free-tier rate limit of 60 requests per minute. The batch querying module handles HTTP 429 rate-limit errors automatically by catching the exception, applying an exponential back-off delay, and retrying the failed call.

**Pandas** handles all tabular data operations in the project: loading the IMD district normals CSV, merging historical normals with live weather observations on the district key, computing weather anomalies (ΔTemp, ΔRainfall, ΔHumidity) as the difference between the observed value and the historical monthly normal, applying the CSS formula across all districts simultaneously using vectorised column operations, and assembling the final results DataFrame for display in the Streamlit table and export as a UTF-8 CSV file.

### 2.4 Summary of Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| Streamlit | ≥ 1.32 | Web GUI, sidebar widgets, map embedding |
| GeoPandas | ≥ 0.14 | GeoJSON loading, centroid extraction, spatial join |
| Folium | ≥ 0.16 | Interactive choropleth map generation |
| Shapely | ≥ 2.0 | Geometric operations (bundled with GeoPandas) |
| Requests | ≥ 2.31 | OpenWeatherMap API HTTP calls |
| Pandas | ≥ 2.1 | Tabular data, anomaly calculation, CSV export |

---
## Section 3: CSS Formula & Methodology
Owner: Swathi | Target: ~400 words

## Section 4: GUI Architecture

The FasalAlert dashboard is built entirely using Streamlit, a Python-based 
web framework that enables rapid construction of interactive data applications 
without requiring any frontend expertise. The GUI is structured into two 
primary zones: the input sidebar and the main output area.

### 4.1 Input Sidebar

The sidebar serves as the control panel for the entire application. It 
contains four input widgets arranged in a logical top-to-bottom flow:

- **State Selector (`st.selectbox`):** Allows the user to select an Indian 
  state, which filters the available district list contextually.
- **District Multi-Selector (`st.multiselect`):** Enables bulk selection of 
  up to 20 districts simultaneously, supporting state-wide monitoring by 
  agricultural officers.
- **Crop Selector (`st.selectbox`):** Lets the user specify the active crop 
  from six supported options — Wheat, Rice, Maize, Cotton, Soybean, and 
  Sugarcane — ensuring crop-specific stress thresholds are applied.
- **Growth Stage Selector (`st.radio`):** Allows selection of the current 
  phenological stage (Sowing, Vegetative, Flowering, Grain-filling, Harvest), 
  which determines the CSS weight configuration loaded from 
  `crop_thresholds.json`.
- **Fetch & Analyse Button:** Triggers the full data pipeline — API calls, 
  anomaly computation, CSS scoring, and output rendering — in a single click.

### 4.2 Summary Metric Cards

Upon clicking Fetch & Analyse, four `st.metric` cards are rendered at the 
top of the main area, providing an at-a-glance overview of the selected 
districts. These cards display the average Crop Stress Score (CSS), the 
hottest district by temperature, the wettest district by rainfall, and the 
most stressed district by CSS value.

### 4.3 District Detail Table

A full `st.dataframe` table displays all queried districts with columns 
including District, State, Crop, Growth Stage, Temperature, ΔTemp, Rainfall, 
ΔRainfall, Humidity, CSS score, and Advisory text. A `st.download_button` 
below the table allows users to export the results as a UTF-8 encoded CSV 
file for offline field use.

### 4.4 Advisory Panels

For any district with a CSS value of 6 or above (High stress threshold), 
a prominent `st.error()` panel is automatically rendered. Each panel 
displays the district name, state, crop, CSS score, and a specific 
recommended farmer action such as "Irrigate within 48 hours" or 
"Apply fungicide — high humidity risk." This ensures critical alerts 
are immediately visible without requiring the user to scan the full table.


The FasalAlert dashboard is built entirely using Streamlit, a Python-based 
web framework that enables rapid construction of interactive data applications 
without requiring any frontend expertise. The GUI is structured into two 
primary zones: the input sidebar and the main output area.

### 4.1 Input Sidebar

The sidebar serves as the control panel for the entire application. It 
contains four input widgets arranged in a logical top-to-bottom flow:

- **State Selector (`st.selectbox`):** Allows the user to select an Indian 
  state, which filters the available district list contextually.
- **District Multi-Selector (`st.multiselect`):** Enables bulk selection of 
  up to 20 districts simultaneously, supporting state-wide monitoring by 
  agricultural officers.
- **Crop Selector (`st.selectbox`):** Lets the user specify the active crop 
  from six supported options — Wheat, Rice, Maize, Cotton, Soybean, and 
  Sugarcane — ensuring crop-specific stress thresholds are applied.
- **Growth Stage Selector (`st.radio`):** Allows selection of the current 
  phenological stage (Sowing, Vegetative, Flowering, Grain-filling, Harvest), 
  which determines the CSS weight configuration loaded from 
  `crop_thresholds.json`.
- **Fetch & Analyse Button:** Triggers the full data pipeline — API calls, 
  anomaly computation, CSS scoring, and output rendering — in a single click.

### 4.2 Summary Metric Cards

Upon clicking Fetch & Analyse, four `st.metric` cards are rendered at the 
top of the main area, providing an at-a-glance overview of the selected 
districts. These cards display the average Crop Stress Score (CSS), the 
hottest district by temperature, the wettest district by rainfall, and the 
most stressed district by CSS value.

### 4.3 District Detail Table

A full `st.dataframe` table displays all queried districts with columns 
including District, State, Crop, Growth Stage, Temperature, ΔTemp, Rainfall, 
ΔRainfall, Humidity, CSS score, and Advisory text. A `st.download_button` 
below the table allows users to export the results as a UTF-8 encoded CSV 
file for offline field use.

### 4.4 Advisory Panels

For any district with a CSS value of 6 or above (High stress threshold), 
a prominent `st.error()` panel is automatically rendered. Each panel 
displays the district name, state, crop, CSS score, and a specific 
recommended farmer action such as "Irrigate within 48 hours" or 
"Apply fungicide — high humidity risk." This ensures critical alerts 
are immediately visible without requiring the user to scan the full table.

## Section 5: Results
Owner: K. Yaswanthi and Sathvik | Target: ~400 words
