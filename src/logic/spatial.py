# spatial.py
# Member 4 — Himanshu
# This file handles all spatial operations:
# 1. Loading India district GeoJSON
# 2. Extracting district centroids (lat/lon for API calls)
# 3. Spatial join of weather results to district polygons
# 4. Building the Folium choropleth map

import geopandas as gpd
import folium
import pandas as pd

# ─────────────────────────────────────────
# FUNCTION 1 — Load district GeoJSON file
# ─────────────────────────────────────────
def load_districts(geojson_path):
    # Read the GeoJSON file into a GeoDataFrame
    gdf = gpd.read_file(geojson_path)

    # Make sure coordinate system is WGS84 (standard lat/lon)
    gdf = gdf.to_crs(epsg=4326)

    return gdf


# ─────────────────────────────────────────
# FUNCTION 2 — Get centroid of one district
# ─────────────────────────────────────────
def get_centroid(district_name, state_name, gdf):
    # Filter the GeoDataFrame to find the matching district
    match = gdf[
        (gdf["NAME_2"].str.lower() == district_name.lower()) &
        (gdf["NAME_1"].str.lower() == state_name.lower())
    ]

    # If no match found, return None
    if match.empty:
        return None, None

    # Extract the centroid point of the district polygon
    centroid = match.geometry.centroid.iloc[0]

    # Return latitude and longitude separately
    latitude = centroid.y
    longitude = centroid.x

    return latitude, longitude


# ─────────────────────────────────────────
# FUNCTION 3 — Join weather results to GDF
# ─────────────────────────────────────────
def join_weather_to_districts(gdf, results_df):
    # results_df must have columns: district, state, css_score
    # Merge on district + state name
    merged = gdf.merge(
        results_df,
        left_on=["NAME_2", "NAME_1"],
        right_on=["district", "state"],
        how="inner"
    )

    return merged


# ─────────────────────────────────────────
# FUNCTION 4 — Build Folium choropleth map
# ─────────────────────────────────────────
def build_choropleth_map(merged_gdf):
    # Start map centered on India
    india_map = folium.Map(
        location=[22.5, 82.0],
        zoom_start=5
    )

    # Define colour steps for CSS score (0-10)
    # Green = low stress, Yellow = moderate, Red = high stress
    folium.Choropleth(
        geo_data=merged_gdf,
        data=merged_gdf,
        columns=["district", "css_score"],
        key_on="feature.properties.NAME_2",
        fill_color="RdYlGn_r",
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name="Crop Stress Score (0 = Low, 10 = High)",
        nan_fill_color="lightgrey"
    ).add_to(india_map)

    # Add tooltip to each district polygon
    folium.GeoJson(
        merged_gdf,
        tooltip=folium.GeoJsonTooltip(
            fields=["district", "state", "css_score", "advisory"],
            aliases=["District:", "State:", "Stress Score:", "Advisory:"],
            localize=True
        )
    ).add_to(india_map)

    # Return the map object
    return india_map