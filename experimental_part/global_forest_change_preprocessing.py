import numpy as np
import ee
import matplotlib.pyplot as plt

# Authenticate and initialize Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-biancalazar1403')

# Define the region of interest (Romania bounding box)
roi = ee.Geometry.Polygon(
    [[[22.5, 44.0], [26.5, 44.0], [26.5, 48.0], [22.5, 48.0]]], None, False
)

# Load the Hansen Global Forest Change dataset
dataset = ee.Image("UMD/hansen/global_forest_change_2023_v1_11")

# Get the band related to forest loss
loss = dataset.select('loss')

# Use 'datamask' for quality control (cloud corruption)
datamask = dataset.select('datamask')

# Apply the cloud corruption filter: only keep pixels with valid (non-cloud) data
clean_loss = loss.updateMask(datamask.eq(1))

# Clip the dataset to the area of interest (Romania)
clean_loss = clean_loss.clip(roi)

# Reduce the image to a grid for visualization
grid_size = 1024  # Number of pixels on each side
reduced_loss = clean_loss.reduceResolution(
    reducer=ee.Reducer.mean(),
    maxPixels=1024
).reproject(
    crs='EPSG:4326',
    scale=1000  # Adjust scale as needed
)

# Export data for visualization
loss_data = reduced_loss.sampleRectangle(region=roi).getInfo()

# Extract grid data from Earth Engine output
loss_array = np.array(loss_data['loss'])

# Plot the forest loss data
fig, ax = plt.subplots(figsize=(10, 10))
cax = ax.imshow(loss_array, cmap='Reds', interpolation='none', origin='upper')
fig.colorbar(cax, ax=ax, orientation='vertical')
ax.set_title('Forest Loss in Romania')
plt.show()
