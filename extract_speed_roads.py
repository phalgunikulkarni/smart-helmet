import requests
import pandas as pd

# --------------------------------------------------
# OVERPASS QUERY
# --------------------------------------------------

query = """
[out:json][timeout:25];

(
  way["highway"]["maxspeed"]
  (12.80,77.45,13.15,77.80);
);

out tags center;
"""

# --------------------------------------------------
# FETCH DATA
# --------------------------------------------------

print("\n📡 Fetching Bengaluru speed-limit roads...")

response = requests.get(
    "https://lz4.overpass-api.de/api/interpreter",
    params={"data": query},
    headers={
        "User-Agent": "SmartHelmetProject/1.0"
    },
    timeout=30
)

print("Status Code:", response.status_code)

data = response.json()

# --------------------------------------------------
# EXTRACT DATA
# --------------------------------------------------

roads = []

for element in data["elements"]:

    tags = element.get("tags", {})

    road_name = tags.get("name", "Unnamed Road")

    road_type = tags.get("highway", "unknown")

    maxspeed = tags.get("maxspeed", "Unknown")

    lat = element.get("center", {}).get("lat", None)

    lon = element.get("center", {}).get("lon", None)

    roads.append({
        "Road Name": road_name,
        "Road Type": road_type,
        "Latitude": lat,
        "Longitude": lon,
        "Speed Limit": maxspeed
    })

# --------------------------------------------------
# CREATE DATAFRAME
# --------------------------------------------------

df = pd.DataFrame(roads)

# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

df.to_csv("bengaluru_speed_roads.csv", index=False)

print("\n✅ SPEED ROAD DATASET CREATED")

print(df.head())