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