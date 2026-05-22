from flask import Flask, render_template, request, jsonify
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import json
import os

app = Flask(__name__)

# -----------------------------------
# DATABASE FILE
# -----------------------------------

DATA_FILE = "database/data.json"

# -----------------------------------
# GATE LOCATIONS
# -----------------------------------

GATES = {
    "gate1": {
        "name": "Gate 1",
        "lat": 12.9716,
        "lon": 77.5946
    },

    "gate2": {
        "name": "Gate 2",
        "lat": 12.9750,
        "lon": 77.5990
    }
}

# -----------------------------------
# CREATE DATABASE IF NOT EXISTS
# -----------------------------------

if not os.path.exists("database"):
    os.makedirs("database")

if not os.path.exists(DATA_FILE):

    default_data = {

        "gate1": {
            "status": "NO DATA",
            "waiting_users": 0,
            "nearby_users": 0,
            "distance": 0,
            "last_updated": "--"
        },

        "gate2": {
            "status": "NO DATA",
            "waiting_users": 0,
            "nearby_users": 0,
            "distance": 0,
            "last_updated": "--"
        }

    }

    with open(DATA_FILE, "w") as file:
        json.dump(default_data, file, indent=4)

# -----------------------------------
# LOAD DATA
# -----------------------------------

def load_data():

    with open(DATA_FILE, "r") as file:
        return json.load(file)

# -----------------------------------
# SAVE DATA
# -----------------------------------

def save_data(data):

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# -----------------------------------
# DISTANCE FUNCTION
# -----------------------------------

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 1000

# -----------------------------------
# HOME PAGE
# -----------------------------------

@app.route("/")
def home():

    return render_template("index.html")

# -----------------------------------
# SEND DATA TO WEBSITE
# -----------------------------------

@app.route("/data")
def data():

    data = load_data()

    return jsonify(data)

# -----------------------------------
# RECEIVE LOCATION
# -----------------------------------

@app.route("/location", methods=["POST"])
def location():

    data = load_data()

    user = request.json

    user_lat = user["latitude"]
    user_lon = user["longitude"]

    speed = user.get("speed", 0)

    # -----------------------------------
    # CHECK EACH GATE
    # -----------------------------------

    for gate_id, gate in GATES.items():

        gate_lat = gate["lat"]
        gate_lon = gate["lon"]

        distance = calculate_distance(
            user_lat,
            user_lon,
            gate_lat,
            gate_lon
        )

        nearby_users = 0
        waiting_users = 0

        # Nearby if within 100m
        if distance <= 100:

            nearby_users = 1

            # Waiting if slow
            if speed < 2:
                waiting_users = 1

        # -----------------------------------
        # STATUS LOGIC
        # -----------------------------------

        if nearby_users == 0:

            status = "NO DATA"

        elif waiting_users >= 1:

            status = "CLOSED"

        else:

            status = "OPEN"

        # -----------------------------------
        # SAVE GATE DATA
        # -----------------------------------

        data[gate_id] = {

            "status": status,

            "waiting_users": waiting_users,

            "nearby_users": nearby_users,

            "distance": round(distance, 1),

            "last_updated": datetime.now().strftime(
                "%I:%M:%S %p"
            )

        }

    save_data(data)

    return jsonify({
        "message": "Location received"
    })

# -----------------------------------
# RUN APP
# -----------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
