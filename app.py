from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import os

app = Flask(__name__)

DATA_FILE = "database/data.json"

users = []

# ---------------------------------
# MULTIPLE GATES
# ---------------------------------

gates = [

    {
        "name": "Gate A",
        "lat": 15.1514586,
        "lon": 76.8938312
    },

    {
        "name": "Gate B",
        "lat": 15.1445935,
        "lon": 76.9047562
    }

]

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
# DISTANCE CALCULATION
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
# FIND NEAREST GATE
# ---------------------------------

def find_nearest_gate(user_lat, user_lon):

    nearest_gate = None
    min_distance = 999999

    for gate in gates:

        distance = calculate_distance(
            user_lat,
            user_lon,
            gate["lat"],
            gate["lon"]
        )

        if distance < min_distance:

            min_distance = distance
            nearest_gate = gate

    return nearest_gate, min_distance

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

    nearest_gate, current_distance = find_nearest_gate(
        user["lat"],
        user["lon"]
    )

    waiting_users = 0

    for u in users:

        gate, distance = find_nearest_gate(
            u["lat"],
            u["lon"]
        )

        if distance < 100:

            speed = u.get("speed")

            if speed is None or speed < 2:

                waiting_users += 1

    data["waiting_users"] = waiting_users
    data["last_updated"] = datetime.now().strftime("%I:%M:%S %p")

    # Gate logic
    if waiting_users >= 3:
        data["status"] = "CLOSED"
    else:
        data["status"] = "OPEN"

    save_data(data)

    return jsonify({

        "message": "Location received",

        "status": data["status"],

        "distance": round(current_distance, 2),

        "gate": nearest_gate["name"]

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
