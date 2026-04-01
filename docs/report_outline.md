# FasalAlert — Report Outline

## Section 1: Problem Statement & Motivation

### 1.1 Background

More than 60 percent of the rural population is dependent on Indian agriculture, which also supports national food security to a significant extent. However, it remains sharply susceptible to weather extremes — unseasonal rainfall, long droughts, heat waves, cold waves, and severe crop losses annually.

Although weather information is provided by the India Meteorological Department (IMD) and remote sensing platforms, farm officers at the district level lack access to a unified, crop-specific stress and live weather intelligence tool that offers real-time warning signals on risk areas.

### 1.2 The Spatial Problem

Crop stress is inherently a spatial issue. Weather conditions vary significantly across districts, and the impact of the same weather event depends on crop type and growth stage. For example, wheat experiences critical stress at temperatures of around 38°C during grain filling but is less affected during planting.

Current solutions are either too technical — requiring professional interpretation of raw IMD data — or too generalized — lacking crop-specific details in national weather apps — and not spatially aware, disregarding district-level geographical differences.

A more effective approach would involve a dashboard integrating live weather data with district boundaries and crop-specific thresholds to provide spatially-aware advisories.

### 1.3 Proposed Solution

FasalAlert aims to bridge this gap by:
1. Fetching live weather data (temperature, humidity, rainfall) for any Indian district using the OpenWeatherMap API and district centroid coordinates calculated with GeoPandas.
2. Computing a Crop Stress Score (CSS) for each district by comparing current weather observations with IMD historical normals and ICAR-published weights for crops.
3. Displaying findings on an interactive pan-India choropleth map created using GeoPandas and Folium, color-coded by severity (green → yellow → red).
4. Offering operational recommendations for high-stress districts with specific directional actions for farmers.

### 1.4 Target Users

| User Group | Needs |
|---|---|
| District Agricultural Officers (DAOs) | Monitor seasonal crop stress across multiple blocks |
| State Agriculture Departments | Conduct rapid spatial scans before issuing advisories |
| Agritech Researchers & Students | Use as a lightweight crop-weather correlation tool |
| Farmers Cooperatives & FPOs | Real-time risk flags for procurement and insurance |

### 1.5 Spatial Framing

The system considers India's administrative boundaries at the district level (GADM Level-2). It uses GeoPandas to extract centroids as coordinates for API queries and links findings back to district polygons for choropleth visualization. The prototype covers pan-India regions but focuses initially on key agricultural zones like Punjab's Wheat Belt to test functionality under real-world conditions.

---

## Section 2: Technical Stack & Libraries

### 2.1 GUI Framework — Streamlit

Streamlit was selected as the GUI framework for FasalAlert because it enables the construction of a fully interactive, browser-accessible web dashboard in pure Python without requiring any frontend expertise in HTML, CSS, or JavaScript. Unlike desktop-only alternatives such as Tkinter or PyQt6, Streamlit produces a live web application that any stakeholder can access from a browser with no installation required.

For a team working within a four-day sprint, Streamlit's zero-boilerplate layout system was decisive. A functioning page with sidebar widgets, metric cards, a dataframe, and an embedded Folium map can be assembled in under sixty lines of code. Streamlit also provides `st.components.v1.html()`, which accepts any raw HTML string and renders it inline — the critical feature that allows the Folium choropleth map to be embedded directly inside the dashboard without any additional server infrastructure.

### 2.2 Core Geospatial Libraries — GeoPandas and Folium

**GeoPandas** is the primary geospatial processing library in FasalAlert. It extends the Pandas DataFrame with a geometry column, enabling the team to load the pan-India district boundaries GeoJSON file (GADM Level-2), compute the geographic centroid of each district polygon as a latitude/longitude coordinate pair, perform spatial joins to attach weather data back to district polygons, and prepare the enriched GeoDataFrame for choropleth rendering.

**Folium** wraps the Leaflet.js interactive mapping engine in a Python interface, allowing the team to programmatically generate a choropleth map of India coloured from green (low stress) through yellow (moderate) to red (high stress) based on the CSS value of each district. Each district polygon carries an interactive tooltip showing the crop name, CSS score, live temperature, observed rainfall, and advisory text.

### 2.3 Web and API Libraries — Requests and Pandas

**Requests** provides the HTTP client for calling the OpenWeatherMap Current Weather API. Each API call is constructed with a district centroid's latitude and longitude, and the JSON response is parsed to extract temperature, humidity, and rainfall. A 0.2-second delay is enforced between consecutive calls to stay within the free-tier rate limit. The batch querying module handles HTTP 429 rate-limit errors automatically by applying a back-off delay and retrying.

**Pandas** handles all tabular data operations: loading the IMD district normals CSV, merging historical normals with live weather observations, computing weather anomalies, applying the CSS formula, and assembling the final results DataFrame for display and CSV export.

### 2.4 Summary of Libraries

| Library | Version | Purpose |
|---|---|---|
| Streamlit | ≥ 1.32 | Web GUI, sidebar widgets, map embedding |
| GeoPandas | ≥ 0.14 | GeoJSON loading, centroid extraction, spatial join |
| Folium | ≥ 0.16 | Interactive choropleth map generation |
| Shapely | ≥ 2.0 | Geometric operations (bundled with GeoPandas) |
| Requests | ≥ 2.31 | OpenWeatherMap API HTTP calls |
| Pandas | ≥ 2.1 | Tabular data, anomaly calculation, CSV export |

---

## Section 3: CSS Formula & Methodology

### 3.1 Overview of the Crop Stress Score

The Crop Stress Score (CSS) is a dimensionless index in the range 0 to 10 that quantifies how severely current weather conditions deviate from historical norms for a given district, weighted by the physiological sensitivity of the selected crop at its current growth stage. A CSS of 0 indicates normal conditions, while a CSS of 10 indicates extreme stress requiring immediate intervention.

### 3.2 The CSS Formula

```
CSS = [ w1 × (f(ΔTemp) / Temp_threshold)
      + w2 × (f(ΔRain) / Rain_threshold)
      + w3 × (f(ΔHumidity) / Humidity_threshold) ] × 10
```

Where:
- **Δ** is the anomaly — the difference between the live observed value and the historical monthly normal from the IMD normals dataset.
- **f(Δ)** is a sign-aware function that applies the correct directional threshold (see Section 3.3).
- **Threshold** is the crop-and-stage-specific physiological stress threshold sourced from ICAR advisory bulletins.
- **w1, w2, w3** are crop-and-stage-specific weights that sum to 1.0.
- The result is scaled to 0–10 and clamped with `max(0.0, min(10.0, css))`.

### 3.3 Sign-Aware Stress Modeling

All three weather variables exhibit bidirectional stress — crops suffer from both excess and deficit conditions. The model handles each direction separately:

| Variable | Positive Δ | Negative Δ |
|---|---|---|
| Temperature | Heat stress → heat threshold | Cold stress → cold threshold (0.5× heat) |
| Rainfall | Waterlogging → excess threshold | Drought → deficit threshold (0.5× excess) |
| Humidity | Fungal risk → high threshold | Dry stress → low threshold (0.5× high) |

This ensures that a +0.6°C and a −0.6°C anomaly both correctly register as low stress, but their directions are preserved for advisory generation. The advisory generator uses the sign of Δ to produce directional guidance — for example distinguishing "irrigate for heat" from "apply frost protection."

### 3.4 Weight Rationale

Weights reflect agronomic knowledge about which variable dominates stress at each growth stage. For wheat at grain-filling, temperature receives w1 = 0.6 because temperatures above 35°C directly inhibit starch accumulation — confirmed by ICAR-IIWBR Karnal. Rainfall and humidity each receive 0.2 because their effects are secondary during this brief critical window.

### 3.5 Stress Classification

| CSS Range | Alert Level | Action |
|---|---|---|
| 0 – 3 | Low 🟢 | No advisory required |
| 3 – 6 | Moderate 🟡 | Watch — monitor conditions |
| 6 – 10 | High 🔴 | Immediate action required |

### 3.6 Threshold Source Verification

| Crop | Source |
|---|---|
| Wheat | ICAR-IIWBR Karnal Advisory Bulletins 2021–23; CIMMYT Heat Stress in Wheat (Sharma et al., 2019) |
| Rice | ICAR-NRRI Cuttack Technical Bulletin 2022; IRRI Rice Knowledge Bank |
| Maize | ICAR-IIMR Ludhiana Kharif Advisory 2022 |
| Cotton | ICAR-CICR Nagpur Technical Bulletin No. 44 |
| Soybean | ICAR-IISR Indore Kharif Management Guide 2022 |
| Sugarcane | ICAR-IISR Lucknow Sugarcane Cultivation Manual 2021 |

---

## Section 4: GUI Architecture

The FasalAlert dashboard is built entirely using Streamlit and structured into two primary zones: the input sidebar and the main output area.

### 4.1 Input Sidebar

The sidebar serves as the control panel for the entire application. It contains five input widgets arranged in a logical top-to-bottom flow:

- **State Selector (`st.selectbox`):** Filters the district list by state.
- **District Multi-Selector (`st.multiselect`):** Enables bulk selection of up to 20 districts simultaneously for state-wide monitoring.
- **Crop Selector (`st.selectbox`):** Selects from six supported crops — Wheat, Rice, Maize, Cotton, Soybean, and Sugarcane.
- **Growth Stage Selector (`st.radio`):** Selects the phenological stage (Sowing, Vegetative, Flowering, Grain-filling, Harvest) to apply the correct CSS weights from `crop_thresholds.json`.
- **Fetch & Analyse Button:** Triggers the full data pipeline in a single click.

### 4.2 Summary Metric Cards

Upon clicking Fetch & Analyse, four `st.metric` cards are rendered at the top of the main area providing an at-a-glance overview: average CSS score, hottest district by temperature, wettest district by rainfall, and most stressed district by CSS value.

### 4.3 District Detail Table

A full `st.dataframe` table displays all queried districts with columns for District, State, Crop, Stage, Temperature, ΔTemp, Rainfall, ΔRainfall, Humidity, CSS score, Category, and Advisory text. A `st.download_button` allows users to export results as a UTF-8 encoded CSV file for offline field use.

### 4.4 Choropleth Map

An interactive Folium choropleth map is rendered full-width via `st.components.v1.html()`, colour-coded green → yellow → red by CSS value. Each district polygon has a tooltip showing crop name, CSS score, live temperature, rainfall, and advisory text.

### 4.5 Advisory Panels

For any district with CSS ≥ 6, a prominent `st.error()` panel is automatically rendered showing the district name, state, crop, CSS score, and a specific directional advisory — for example "HIGH heat stress (+9.2°C above normal). Irrigate within 48 hours to cool root zone."

---

## Section 5: Results & Limitations

### 5.1 Sample Run Results

A test run was conducted selecting five districts — Ludhiana, Amritsar, Karnal, Hisar, and Jaipur — with Wheat at the Grain-filling growth stage. Live weather data was fetched via the OpenWeatherMap API and compared against IMD district normals for the current month.

Results identified two HIGH-stress districts: Ludhiana (CSS 8.5) flagged for critical heat stress with a temperature 9.2°C above the monthly normal, and Hisar (CSS 7.8) flagged for drought stress with a rainfall deficit of 30mm below normal. Three districts — Amritsar (CSS 4.2), Karnal (CSS 3.1), and Jaipur (CSS 1.5) — were in safe or moderate ranges. Average CSS across all five districts was 5.0, indicating moderate regional stress. The full batch API call for five districts completed in under 3 seconds within the free-tier rate limit.

The choropleth map correctly rendered Ludhiana and Hisar in red and the remaining districts in green and yellow, with interactive tooltips displaying crop, CSS, temperature, and advisory per polygon.

### 5.2 Validation

CSS outputs were cross-checked against known IMD conditions for two districts. For Ludhiana in March 2026, the observed temperature of 38.2°C against a normal of 29°C represents a +9.2°C anomaly, consistent with the IMD heatwave advisory issued for Punjab during the same period. The CSS of 8.5 correctly reflects this severity at grain-filling stage where temperature weight is highest (w1 = 0.6). For Hisar, the drought advisory matched field reports of delayed irrigation in Haryana during the test period.

### 5.3 Limitations

**API Rate Limit:** The OpenWeatherMap free tier allows 60 calls per minute, restricting real-time bulk querying beyond 20 districts per session. Scaling to state-level monitoring of 100+ districts would require a paid API tier.

**Static IMD Normals:** The historical baseline is a pre-compiled CSV reflecting long-term averages and does not capture recent decade-level climate shifts. A live IMD API feed would provide more accurate baselines.

**District Centroid Approximation:** Weather is fetched at the geographic centroid of each district polygon. Large districts spanning multiple agro-climatic zones may show intra-district variability not captured by a single centroid query.

**No Soil or Irrigation Data:** The CSS formula does not incorporate soil moisture, soil type, or irrigation coverage, all of which significantly modulate actual crop stress response in the field.

### 5.4 Future Extensions

- **ML Stress Prediction:** Training a Random Forest or LSTM model on historical weather and yield data to predict CSS values 7 days ahead, enabling proactive advisories.
- **Live IMD Integration:** Replacing static CSV normals with live IMD API feeds for real-time baseline computation.
- **SMS Alert System:** Pushing HIGH-stress advisories directly to farmers via SMS using Twilio or MSG91.
- **Satellite NDVI Layer:** Integrating Sentinel-2 NDVI imagery to validate CSS scores against actual observed crop health on the ground.
