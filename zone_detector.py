import requests
import math

# --------------------------------------------------
# DISTANCE CALCULATION
# --------------------------------------------------

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# --------------------------------------------------
# FETCH REAL NEARBY ZONES
# --------------------------------------------------

def fetch_nearby_places(lat, lon):

    query = f"""
    [out:json];

    (
      node["amenity"="school"](around:500,{lat},{lon});
      node["amenity"="hospital"](around:500,{lat},{lon});
      node["amenity"="college"](around:500,{lat},{lon});
    );

    out body;
    """

    response = requests.get(
        "https://overpass-api.de/api/interpreter",
        params={"data": query},
        headers={
            "User-Agent": "SmartHelmetProject/1.0"
        },
        timeout=20
    )

    print(response.status_code)
    print(response.text[:200])

    return response.json()


# --------------------------------------------------
# DETECT ZONES
# --------------------------------------------------

def detect_zone(current_lat, current_lon):

    data = fetch_nearby_places(current_lat, current_lon)

    elements = data.get("elements", [])

    if not elements:
        print("\n✅ Normal Area")
        return None

    nearest_zone = None
    nearest_distance = 999

    for place in elements:

        lat = place["lat"]
        lon = place["lon"]

        tags = place.get("tags", {})

        name = tags.get("name", "Unknown Zone")

        amenity = tags.get("amenity", "zone")

        distance = calculate_distance(
            current_lat,
            current_lon,
            lat,
            lon
        )

        if distance < nearest_distance:

            nearest_distance = distance

            nearest_zone = {
                "name": name,
                "type": amenity,
                "distance": round(distance, 2)
            }

    print("\n⚠ REAL ZONE DETECTED")
    print(f"Name: {nearest_zone['name']}")
    print(f"Type: {nearest_zone['type']}")
    print(f"Distance: {nearest_zone['distance']} km")

    return nearest_zone


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    detect_zone(
        12.9716,
        77.5946
    )