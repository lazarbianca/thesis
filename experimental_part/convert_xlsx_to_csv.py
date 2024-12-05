import math
import re
import pandas as pd
from shapely.geometry import Point

# Load the forest data from XLSX
filename = '2016-12-07_catalog_paduri_virgine_si_cvasivirgine'
file_path = f'./datasets/{filename}.xlsx'
df_paduri_virgine = pd.read_excel(file_path, sheet_name='PADURI VIRGINE', engine='openpyxl')
df_paduri_cvasivirigine = pd.read_excel(file_path, sheet_name='PADURI CVASIVIRGINE', engine='openpyxl')

# Remove the last row (total) from each DataFrame
df_paduri_virgine = df_paduri_virgine[:-1]
df_paduri_cvasivirigine = df_paduri_cvasivirigine[:-1]

df_paduri_virgine.columns = df_paduri_virgine.columns.str.strip()
df_paduri_cvasivirigine.columns = df_paduri_cvasivirigine.columns.str.strip()

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
        raise ValueError(f"Invalid coordinate format: {coord}")
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

print(df)

# Create a new DataFrame for export with cleaned and transformed data
export_df = df[['Nr. crt.', 'Numele padurii virgine si/sau cvasivirgine', 'Fundamentat in baza Amenaj silvic, editia',
                'Fundamentat in baza Studiu de fundam, editia', 'Tipul de proprietate', 'Latitude', 'Longitude',
                'Altitudine min', 'Altitudine max', 'Localizare administrativa Judet', 'Detinator Admin OS/OSP',
                 'UP', 'u.a.', 'TP', 'S (ha)', 'din care: suprafete care nu corespund criteriului de naturalitate u.a.',
                'din care: suprafete care nu corespund criteriului de naturalitate S (ha)']]

# Export to CSV
export_file_path = f'./datasets/cleaned_{filename}.csv'
export_df.to_csv(export_file_path, index=False)
print(f"Cleaned and transformed data exported to {export_file_path}")
