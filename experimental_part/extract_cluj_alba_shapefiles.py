import geopandas as gpd

# Load the counties layer
counties = gpd.read_file("datasets/county_data/gadm41_ROU_1.shp")

# Inspect the attribute table to identify the relevant column for filtering
print(counties.columns)
print(counties.head())

# Filter for Cluj and Alba
cluj_alba = counties[counties['NAME_1'].isin(['Cluj', 'Alba'])]

# Save to a new file
cluj_alba.to_file("cluj_alba.gpkg", driver="GPKG")  # Save as GeoPackage
# Or, save as shapefile if necessary
cluj_alba.to_file("cluj_alba.shp")