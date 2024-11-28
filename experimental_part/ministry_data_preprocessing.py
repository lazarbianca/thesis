import math
import re
import ee
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Authenticate and initialize Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-biancalazar1403')

# Load Romania boundary from GEE
# Load Romania boundary from GEE
dataset = ee.FeatureCollection("FAO/GAUL/2015/level0")
romania = dataset.filter(ee.Filter.eq('ADM0_NAME', 'Romania'))

# Export to GeoJSON
romania_geojson = romania.getInfo()  # Get GeoJSON-like dictionary
romania_gdf = gpd.GeoDataFrame.from_features(romania_geojson['features'])

# Explicitly set CRS to EPSG:4326 since this is the CRS used in the GEE dataset
romania_gdf = romania_gdf.set_crs('EPSG:4326', allow_override=True)

# Now you can reproject to the same CRS (it will already be in EPSG:4326)
# romania_gdf = romania_gdf.to_crs(epsg=4326)  # This is unnecessary because it's already in EPSG:4326

# Load the forest data and process it as previously
file_path = './datasets/2016-12-07_catalog_paduri_virgine_si_cvasivirgine.xlsx'
df_paduri_virgine = pd.read_excel(file_path, sheet_name='PADURI VIRGINE', engine='openpyxl')
df_paduri_cvasivirigine = pd.read_excel(file_path, sheet_name='PADURI CVASIVIRGINE', engine='openpyxl')

# Remove the last row (total) from each DataFrame
df_paduri_virgine = df_paduri_virgine[:-1]
df_paduri_cvasivirigine = df_paduri_cvasivirigine[:-1]

# Concatenate both DataFrames into a single DataFrame
df = pd.concat([df_paduri_virgine, df_paduri_cvasivirigine], ignore_index=True)

# Clean up the data (Remove non-data rows)
df = df[df['Nr. crt.'].notnull()]
df = df.reset_index(drop=True)

# Function to split coordinates
def split_coordinates(coord):
    coord = coord.strip()
    pattern = re.compile(r"(\d+)[°º](\d+)[\'′](\d+[\.\d]*)[\"″]?")
    match = pattern.match(coord)
    if not match:
        raise ValueError("Invalid coordinate format")
    degrees = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    return degrees, minutes, seconds

# Function to convert DMS to Decimal Degrees
def dms_to_dd(degrees, minutes, seconds):
    return degrees + minutes / 60 + seconds / 3600

# Apply the conversion to Latitude and Longitude
df['Latitude DMS'] = df['Latitude N'].apply(split_coordinates)
df['Longitude DMS'] = df['Longitude E'].apply(split_coordinates)
df['Latitude'] = df['Latitude DMS'].apply(lambda x: dms_to_dd(*x))
df['Longitude'] = df['Longitude DMS'].apply(lambda x: dms_to_dd(*x))

# Drop the original DMS columns if no longer needed
df = df.drop(columns=['Latitude N', 'Longitude E', 'Latitude DMS', 'Longitude DMS'])

# Convert columns to numeric where applicable (e.g., S (ha), Altitudine)
df['Altitudine min'] = pd.to_numeric(df['Altitudine min'], errors='coerce')
df['Altitudine max'] = pd.to_numeric(df['Altitudine max'], errors='coerce')
df['S (ha)'] = pd.to_numeric(df['S (ha)'], errors='coerce')

# Create the geometry for each point (latitude, longitude)
geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
geo_df = gpd.GeoDataFrame(df, geometry=geometry)

# Ensure the CRS for geo_df is the same as the Romania boundary (EPSG:4326)
geo_df = geo_df.set_crs('EPSG:4326')

# Plot the map of Romania and the circles representing the forests
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plot Romania boundary and forest locations on the same axes
romania_gdf.plot(ax=ax, color='white', edgecolor='black')  # Plot Romania boundary
geo_df.plot(ax=ax, color='blue', markersize=10, alpha=0.5)  # Plot forest points

# Add title and labels
plt.title('Virgin and Quasi-Virgin Forests of Romania')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Show the plot
plt.show()
