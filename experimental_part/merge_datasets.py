import rasterio
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from rasterio.plot import show

# Load the Ministry data CSV into a DataFrame
ministry_data = pd.read_csv('./datasets/cleaned_2016-12-07_catalog_paduri_virgine_si_cvasivirgine.csv')
ministry_data = ministry_data[ministry_data['Localizare administrativa Judet'].isin(['Caras Severin', 'Hunedoara'])]
print(ministry_data)
geometry = [Point(xy) for xy in zip(ministry_data['Longitude'], ministry_data['Latitude'])]
ministry_gdf = gpd.GeoDataFrame(ministry_data, geometry=geometry)

# Set the CRS to match the raster data's CRS (usually WGS84)
ministry_gdf.set_crs('EPSG:4326', inplace=True)

# Reproject GeoDataFrame to match raster CRS
with rasterio.open('./datasets/treecover_carasSeverin_hunedoara.tif') as src:
    raster_crs = src.crs
    if ministry_gdf.crs != raster_crs:
        ministry_gdf = ministry_gdf.to_crs(raster_crs)

# Sample raster values
def sample_raster(raster_path, points):
    with rasterio.open(raster_path) as src:
        values = []
        for point in points:
            try:
                value = list(src.sample([point.coords[0]]))[0][0]
                values.append(value)
            except IndexError:
                values.append(None)  # Handle points outside the raster bounds
        return values

# Extract tree cover and loss year values for each point
treecover_values = sample_raster('./datasets/treecover_carasSeverin_hunedoara.tif', ministry_gdf.geometry)
lossyear_values = sample_raster('./datasets/lossyear_carasSeverin_hunedoara_2015_2020.tif', ministry_gdf.geometry)

# Add extracted values as columns in the GeoDataFrame
ministry_gdf['tree_cover'] = treecover_values
ministry_gdf['loss_year'] = lossyear_values

# Save the updated ministry data with additional columns
ministry_gdf.to_csv('ministry_forest_with_gfc_data.csv', index=False)

# Plot the data on the map
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the TIFF file as a background layer
with rasterio.open('./datasets/treecover_carasSeverin_hunedoara.tif') as src:
    show(src, ax=ax, cmap='Greens', alpha=0.5)

# Plot the points with varying sizes based on surface area
surface_area = ministry_gdf['S (ha)']
min_size = 20
max_size = 200
sizes = ((surface_area - surface_area.min()) / (surface_area.max() - surface_area.min()) * (max_size - min_size)) + min_size

ministry_gdf.plot(ax=ax, markersize=sizes, color='red', alpha=0.5, label='Ministry Forest Sections')

# Add labels and legend
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Tree Cover and Loss Year for Ministry Forest Sections')
plt.legend()
plt.show()
