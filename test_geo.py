import geopandas as gpd

# Load the GeoJSON file
gdf = gpd.read_file("data/india_districts.geojson")

# Print basic info
print(gdf.head())
print("\nColumns:", gdf.columns)
print("\nTotal districts:", len(gdf))