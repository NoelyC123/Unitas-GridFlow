import geopandas as gpd
from shapely.geometry import Point
import os
import zipfile

# Match the mock_survey.csv ids (1–5)
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Pole A', 'Pole B', 'Pole C', 'Pole D', 'Pole E'],
    'geometry': [
        Point(10.0, 50.0),
        Point(10.1, 50.1),
        Point(10.2, 50.2),
        Point(10.3, 50.3),
        Point(10.4, 50.4)
    ]
}

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

# Create output folder
output_folder = "mock_shapefile"
os.makedirs(output_folder, exist_ok=True)

# Save Shapefile components
shapefile_path = os.path.join(output_folder, "poles.shp")
gdf.to_file(shapefile_path)

# Zip Shapefile files
zip_path = "mock_shapefile.zip"
with zipfile.ZipFile(zip_path, "w") as zipf:
    for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
        file_path = os.path.join(output_folder, f"poles{ext}")
        if os.path.exists(file_path):
            zipf.write(file_path, arcname=f"poles{ext}")

print(f"✅ Shapefile written to {zip_path}")