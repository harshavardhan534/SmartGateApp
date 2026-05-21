from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import os

app = Flask(__name__)

DATA_FILE = "database/data.json"

users = []

# ---------------------------------
# RAILWAY GATE COORDINATES
# Replace with your real gate coords
# ---------------------------------

GATE_LAT = 15.1514586
GATE_LON = 76.8938312

# ---------------------------------
# LOAD DATA
# ---------------------------------

def load_data():

    with open(DATA_FILE, "r") as file:
        return json.load(file)

# ---------------------------------
# SAVE DATA
# ---------------------------------

def save_data(data):

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# ---------------------------------
# CALCULATE DISTANCE
# ---------------------------------

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2)**2 + \
        cos(radians(lat1)) * \
        cos(radians(lat2)) * \
        sin(dlon / 2)**2

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 1000

# ---------------------------------
# HOME PAGE
# ---------------------------------

@app.route("/")
def home():

    data = load_data()

    return render_template(
        "index.html",
        status=data["status"],
        waiting=data["waiting_users"],
        updated=data["last_updated"]
    )

# ---------------------------------
# RECEIVE LOCATION
# ---------------------------------

@app.route("/location", methods=["POST"])
def location():

    data = load_data()

    user = request.json

    users.append(user)

    waiting_users = 0

    for u in users:

        # Distance from railway gate
        distance = calculate_distance(
            u["lat"],
            u["lon"],
            GATE_LAT,
            GATE_LON
        )

        # User near gate
        if distance < 100:

            # User moving slowly
            if u["speed"] < 2:

                waiting_users += 1

    data["waiting_users"] = waiting_users
    data["last_updated"] = datetime.now().strftime("%I:%M:%S %p")

    # Gate Logic
    if waiting_users >= 3:
        data["status"] = "CLOSED"
    else:
        data["status"] = "OPEN"

save_data(data)

# Distance of current user from gate

current_distance = calculate_distance(
    user["lat"],
    user["lon"],
    GATE_LAT,
    GATE_LON
)

return jsonify({

    "message": "Location received",

    "status": data["status"],

    "distance": round(current_distance, 2)

})

# ---------------------------------
# RUN APP
# ---------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
