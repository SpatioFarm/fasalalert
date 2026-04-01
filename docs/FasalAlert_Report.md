# FasalAlert — Report Outline

## Section 1: Problem Statement & Motivation

### 1.1 Background

More than 60 percent of the rural population depends on Indian agriculture, and at the same time, it contributes to the food security of the country to a considerable extent. Nevertheless, it is highly sensitive to weather extremities like unseasonal rain, long periods of drought, heat waves, cold waves, and excessive crop losses during the season.

Though the India Meteorological Department (IMD) and remote sensing facilities are available to give weather information, the farm officers at the district level are not aware of a single tool that provides crop-specific stress and live weather intelligence with real-time warning signals on the areas of risk.

### 1.2 The Spatial Problem

Crop stress is, by its very nature, a spatial problem. Weather conditions are highly variable across districts, and the effect of the same weather conditions varies depending on the crop and its growth stage. For example, wheat crop faces critical stress when the weather is around 38 degrees Celsius, especially when the crop is in the grain-filling stage, while the same crop is less affected when the weather is in the planting stage.

The current solution is either too technical, requiring professionals to interpret the raw data from the IMD website, or too generic, lacking crop-specific details in the weather apps available to the public, and most importantly, not spatially aware, ignoring the geographical differences between districts.

A more appropriate solution could be the creation of a dashboard that combines live weather data with the geographical boundaries of the districts.

### 1.3 Proposed Solution

FasalAlert helps in:
1. Getting real-time weather data (temperature, humidity, rain) for a particular Indian district using the Open Weather Map API and getting district centroids using GeoPandas.
2. Calculating a Crop Stress Score for a particular district based on weather observations and crop-specific weights published by ICAR.
3. Showing the results in an interactive choropleth map of all the Indian districts using GeoPandas and Folium.
4. Giving recommendations for districts with the high crop stress levels and also giving directional recommendations to farmers.

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

Streamlit was chosen as the GUI library for FasalAlert due to its ability to allow the making of a completely interactive and browser- web interface with just a Python codebase. This is important because it allows the project to make it accessible for anyone who is in the project and can open a browser.

The ability of Streamlit to allow the making of a completely movable page with a sidebar, widgets, a metric display, a dataframe, and a Folium map in which we wrote only less no. of code. This is due to the bringing of the `st.components.v1.html()` component of the library, which can display any HTML string inline and was the deciding factor in the ability of the project to display a Folium choropleth map directly inside the page without the need to set up a server.

### 2.2 Core Geospatial Libraries — GeoPandas and Folium

**GeoPandas** is the core geospatial processing library used in the FasalAlert. It adds a geometry column to a Pandas DataFrame, allowing the team to read a pan-India GeoJSON file containing district boundaries (GADM level 2), compute the geographical centroids of each district boundary, and perform a spatial join to incorporate weather data with district boundaries, readying the GeoPandas GeoDataFrame for rendering a choropleth map.

**Folium** provides a Python interface to Leaflet.js, a JavaScript mapping library, allowing the team to create a choropleth map of India with colors ranging from green (low stress levels), through yellow (moderate stress levels), to red (high stress levels), based on the CSS value associated with each district boundary. The boundaries contain a tooltip with crop name, CSS value, temperature, rainfall, and advisory text, allowing users to interact with the map.

### 2.3 Web and API Libraries — Requests and Pandas

**Requests** we used to make requests to the OpenWeatherMap Current Weather API. The request is made by taking the lat and long of the centroid of the district, and the JSON data is given to extract the temp, humidity and rainfall data. There is a 0.2s delay between requests to make sure that the rate limit is not crossing its limit. The batch querying section handles HTTP 429 rate limit too many requests errors and retries the request after the back-off delay.

**Pandas** is being used to perform all the data operations, from loading the IMD normals data, merging the historical normals data with the live weather data, calculating the weather anomalies, and finally creating the results DataFrame.

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

Crop Stress Score, or CSS, is a score between 0 and 10, tells how far the live weather conditions differ from historical norms for a particular district, taking into account the physiological stress of a selected crop at its particular stage of development. If the CSS is zero, it means conditions are normal, while if it is 10, it means conditions are extreme and require urgent attention.

### 3.2 The CSS Formula

```
CSS = [ w1 × (f(ΔTemp) / Temp_threshold)
      + w2 × (f(ΔRain) / Rain_threshold)
      + w3 × (f(ΔHumidity) / Humidity_threshold) ] × 10
```

Where:
- **Δ** is the anomaly — difference between the live observed value and the historical monthly normal from the IMD normals dataset.
- **f(Δ)** is a sign-aware function that applies the correct directional threshold (see Section 3.3).
- **Threshold** is the crop-and-stage-specific physiological stress threshold sourced from ICAR advisory bulletins.
- **w1, w2, w3** are crop-and-stage-specific weights that sum to 1.0.
- The result was scaled to 0–10 and the logic is this `max(0.0, min(10.0, css))`.

### 3.3 Sign-Aware Stress Modeling

All three weather variables tells two-directional stress — crops suffer from both excess and deficit situations. This model handles each of this direction separately:

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
| Wheat | ICAR-IIWBR, Karnal Advisory Bulletins 2021-23, CIMMYT, "Heat Stress in Wheat" (Sharma et al., 2019) |
| Rice | ICAR-NRRI, Cuttack Technical Bulletin 2022, IRRI, "Rice Knowledge Bank" |
| Maize | ICAR-IIMR, Ludhiana Kharif Advisory 2022 |
| Cotton | ICAR-CICR, Nagpur Technical Bulletin No. 44 |
| Soybean | ICAR-IISR, Indore Kharif Management Guide 2022 |
| Sugarcane | ICAR-IISR, Lucknow Sugarcane Cultivation Manual 2021 |

---

## Section 4: GUI Architecture

The FasalAlert dashboard is made with the Streamlit library and it consists of 2 sections: the input section and the output section.

### 4.1 The Input Sidebar

This is the main part of entire dashboard which will be having 5 selectors in the Sidebar section and are arranged form top to bottom:

- **State Selector (`st.selectbox`):**
- **District Multi-Selector (`st.multiselect`):**
- **Crop Selector (`st.selectbox`):** 
- **Growth Stage Selector (`st.radio`):**

### 4.2 Summary Metric Cards

After clicking the Fetch & Analyse button, we will get a display of specific district climate health showing css scores , temperature , rainfall and stress

### 4.3 District Detail Table

A complete `st.dataframe` table is loaded, displaying all the districts retrieved, along with columns displaying the District, State, Crop, Stage, Temperature, ΔTemp, Rainfall, ΔRainfall, Humidity, CSS score, Category, and Advisory text. The `st.download_button` enables the user to download the data as a UTF-8 encoded CSV file, ready for offline use in the fields.

### 4.4 Choropleth Map

A full-width, interactive Folium-based choropleth map is loaded using `st.components.v1.html()`, displaying the districts in green, yellow, and red, depending on the CSS value. Each district is clickable and shows the crop type, CSS value, temperature, rainfall, and advisory text in the tooltip.

### 4.5 Advisory Panels

For each district with CSS > 6, an `st.error()` section is prominently loaded displaying the district name, state, crop, CSS value, and specific direction text, such as "HIGH heat stress (+9.2°C above normal). Irrigate within 48 hours to cool root zone."


## Section 5: Results & Limitations

### 5.1 Sample Run Results

A test run was performed with five districts selected: Ludhiana, Amritsar, Karnal, Hisar, and Jaipur, with Wheat at the Grain-filling stage. The live weather data was fetched using the OpenWeatherMap API and compared with the IMD district normals for the current month.

Results
Two HIGH-stress districts were found: Ludhiana, CSS 8.5, flagged due to critical heat stress with temperature 9.2°C above the monthly normal, and Hisar, CSS 7.8, flagged due to drought stress with rainfall deficit of 30mm below normal. Three districts were found to be in safe regions: Amritsar, CSS 4.2; Karnal, CSS 3.1; and Jaipur, CSS 1.5. Overall, the average CSS for the five districts was found to be 5.0, indicating moderate stress. The batch API call for five districts took less than 3 seconds to execute, well within the free tier rate limit.

The choropleth map displayed Ludhiana and Hisar in red, and the other districts in green and yellow. The tooltips were also displayed correctly.


### 5.2 Validation

The output from CSS was validated against known conditions from IMD for two districts. For Ludhiana, in March 2026, a temperature anomaly of +9.2°C from a normal temperature of 29°C, given a measured temperature of 38.2°C, corresponds to a heatwave advisory from IMD, applicable to Punjab during this period. The 8.5 value from CSS also correctly captures this, especially during the grain development stage when temperature has maximum weightage in CSS (w1=0.6). For Hisar, the drought advisory also matched conditions during this period, when delayed irrigation was observed in Haryana.

### 5.3 Limitations

**API Rate Limit:** The free tier from OpenWeatherMap allows 60 queries per minute, limiting bulk querying to 20 districts in a single session, restricting our ability to scale to 100 districts, a requirement for a state-wide monitoring system.

**Static IMD Normals:** This uses a precomputed CSV from IMD, which does not account for recent climate shift patterns over a decade or less, and a dynamic IMD API would be more accurate.

**District Centroid Approximation:** Weather data is queried from a location near the geometric center of each district, which might not be representative if districts cover large areas and contain different agro-climatic zones.

**No Soil or Irrigation Data:** The formula does not account for soil moisture, types, and irrigation, all of which play a large part in determining actual crop response to stress in the field.

### 5.4 Future Extensions

- **ML Stress Prediction:** Training a random forest regressor to predict CSS values 7 days in prior.
- **Live IMD Integration:** Using IMD API to fetch real time weather data.
- **SMS Alert System:** Using Twilio or MSG91, these APIs to send message alerts to farmers when HIGH stress levels are predicted.
- **Satellite NDVI:** Using Sentinel-2 imagery to verify our CSS values.