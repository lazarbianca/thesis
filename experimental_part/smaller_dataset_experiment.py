import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.mask import mask
import numpy as np
from shapely.geometry import Point, Polygon

# Load county shapefiles
cluj_alba_shapefile = gpd.read_file("./datasets/cluj_alba_subset/cluj_alba.shp")
print(cluj_alba_shapefile.columns)
print(cluj_alba_shapefile.head())

# Ensure CRS is consistent
cluj_alba_shapefile = cluj_alba_shapefile.to_crs("EPSG:4326")


# Load GFC raster
gfc_raster = rasterio.open("path/to/gfc_tree_cover_loss.tif")

# Mask GFC raster to Cluj and Alba
cluj_alba_masked, cluj_alba_transform = mask(gfc_raster, cluj_alba_shapefile.geometry, crop=True)

# Extract years 2015-2020 from GFC raster bands
years = list(range(2015, 2021))
gfc_data = {year: cluj_alba_masked[year - 2000] for year in years}  # Adjust for band-year mapping
