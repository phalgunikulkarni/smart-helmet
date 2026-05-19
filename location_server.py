import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

# --------------------------------------------------
# IMPORT ZONE DETECTOR
# --------------------------------------------------

from zone_detector import detect_zone

# --------------------------------------------------
# FLASK SETUP
# --------------------------------------------------

app = Flask(__name__)

CORS(app)

# ════════════════════════════════════════════════
# LOAD DATASETS
# ════════════════════════════════════════════════

geometry_df = pd.read_csv(
    "bengaluru_geometry_roads.csv"
)

print("\n✅ Geometry roads loaded")

speed_df = pd.read_csv(
    "bengaluru_speed_roads.csv"
)

print("\n✅ Speed roads loaded")

print("\n✅ Bengaluru road dataset loaded")

print(speed_df.head())

# ════════════════════════════════════════════════
# LIVE RIDER STATE
# ════════════════════════════════════════════════

live_rider_data = {

    "lat": 12.9716,
    "lon": 77.5946,
    "speed": 0,
    "road": "Unknown",
    "limit": 0,
    "status": "safe"

}

# ════════════════════════════════════════════════
# BENGALURU BOUNDARIES
# ════════════════════════════════════════════════

MIN_LAT = 12.80
MAX_LAT = 13.15

MIN_LON = 77.45
MAX_LON = 77.80

# ════════════════════════════════════════════════
# RECEIVE LIVE LOCATION
# ════════════════════════════════════════════════

@app.route("/location", methods=["POST"])
def receive_location():

    global live_rider_data

    data = request.json

    latitude = data.get("lat")
    longitude = data.get("lon")
    speed = data.get("speed", 0)

    road_name = data.get(
        "road",
        "Unknown Road"
    )

    speed_limit = data.get(
        "limit",
        0
    )

    # --------------------------------------------------
    # AREA CHECK
    # --------------------------------------------------

    inside_area = (

        MIN_LAT <= latitude <= MAX_LAT

        and

        MIN_LON <= longitude <= MAX_LON

    )

    if not inside_area:

        print(
            "❌ Outside Bengaluru Area"
        )

        return jsonify({

            "status": "outside_area"

        })

    print("\n📍 LIVE LOCATION RECEIVED")

    print(f"Latitude : {latitude}")

    print(f"Longitude: {longitude}")

    print(f"Road     : {road_name}")

    print(f"Speed    : {speed}")

    print(f"Limit    : {speed_limit}")

    # --------------------------------------------------
    # CHECK ZONE
    # --------------------------------------------------

    zone = detect_zone(
        latitude,
        longitude
    )

    # --------------------------------------------------
    # DEFAULT STATUS
    # --------------------------------------------------

    status = "safe"

    # --------------------------------------------------
    # SPEED CHECK
    # --------------------------------------------------

    if speed_limit > 0:

        if speed > speed_limit:

            status = "warning"

    
    # --------------------------------------------------
    # UPDATE LIVE RIDER
    # --------------------------------------------------

    live_rider_data = {

        "lat": latitude,
        "lon": longitude,
        "speed": speed,
        "road": road_name,
        "limit": speed_limit,
        "status": status

    }

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return jsonify({

        "status": status,
        "road": road_name,
        "speed": speed,
        "limit": speed_limit

    })

# ════════════════════════════════════════════════
# SEND GEOMETRY ROADS
# ════════════════════════════════════════════════

@app.route(
    "/geometry_roads",
    methods=["GET"]
)

def get_geometry_roads():

    return jsonify(

        geometry_df.to_dict(
            orient="records"
        )

    )

# ════════════════════════════════════════════════
# SEND SPEED ROADS
# ════════════════════════════════════════════════

@app.route(
    "/speed_roads",
    methods=["GET"]
)

def get_speed_roads():

    return jsonify(

        speed_df.to_dict(
            orient="records"
        )

    )

# ════════════════════════════════════════════════
# LIVE RIDER API
# ════════════════════════════════════════════════

@app.route(
    "/live_rider",
    methods=["GET"]
)

def live_rider():

    return jsonify(
        live_rider_data
    )

# ════════════════════════════════════════════════
# START SERVER
# ════════════════════════════════════════════════

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",
        port=5050,
        debug=True

    )