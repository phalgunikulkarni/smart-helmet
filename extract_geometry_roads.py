import requests
import pandas as pd

# --------------------------------------------------
# OVERPASS QUERY
# --------------------------------------------------

query = """
[out:json][timeout:25];

(
  way["highway"]
  (12.80,77.45,13.15,77.80);
);

out geom;
"""

# --------------------------------------------------
# FETCH DATA
# --------------------------------------------------

print("\n📡 Fetching Bengaluru_road data...")

response = requests.get(
    "https://lz4.overpass-api.de/api/interpreter",
    params={"data": query},
    headers={
        "User-Agent": "SmartHelmetProject/1.0"
    },
    timeout=30
)

# --------------------------------------------------
# CHECK RESPONSE
# --------------------------------------------------

print("Status Code:", response.status_code)

data = response.json()

# --------------------------------------------------
# EXTRACT ROAD DATA
# --------------------------------------------------

roads = []

for element in data["elements"]:

    tags = element.get("tags", {})

    road_name = tags.get("name", "Unnamed Road")

    road_type = tags.get("highway", "unknown")

    maxspeed = tags.get("maxspeed", "Not Available")
    print(road_name, maxspeed)

    geometry = element.get("geometry", [])

coordinates = []

for point in geometry:

    coordinates.append([
        point["lat"],
        point["lon"]
    ])

roads.append({
    "Road Name": road_name,
    "Road Type": road_type,
    "Speed Limit": maxspeed,
    "Coordinates": coordinates
})

# --------------------------------------------------
# CREATE DATAFRAME
# --------------------------------------------------

df = pd.DataFrame(roads)


# --------------------------------------------------
# KEEP ONLY ROADS WITH REAL SPEED LIMITS
# --------------------------------------------------

#df = df[df["Speed Limit"] != "Not Available"]

# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

df.to_csv("bengaluru_geometry_roads.csv", index=False)

print("\n✅ ROAD DATA EXTRACTION COMPLETE")
print("✅ CSV file created:")
print("bengaluru_roads.csv")

print("\n📋 SAMPLE DATA:\n")
print(df.head(20))