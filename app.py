from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import os

app = Flask(__name__)

DATA_FILE = "database/data.json"

# Store active users
users = []

# ------------------------------------------------
# RAILWAY GATES
# Replace with real coordinates
# ------------------------------------------------

gates = [

    {
        "name": "Cantonment Gate",
        "lat": 15.1514586,
        "lon": 76.8938312
    },

    {
        "name": "Radio Park Gate",
        "lat": 15.1445935,
        "lon": 76.9047562
    }

]

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

def load_data():

    with open(DATA_FILE, "r") as file:
        return json.load(file)

# ------------------------------------------------
# SAVE DATA
# ------------------------------------------------

def save_data(data):

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# ------------------------------------------------
# DISTANCE CALCULATION
# ------------------------------------------------

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + \
        cos(radians(lat1)) * \
        cos(radians(lat2)) * \
        sin(dlon / 2) ** 2

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 1000

# ------------------------------------------------
# FIND NEAREST GATE
# ------------------------------------------------

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

# ------------------------------------------------
# HOME PAGE
# ------------------------------------------------

@app.route("/")
def home():

    data = load_data()

    return render_template(
        "index.html",
        status=data["status"],
        waiting=data["waiting_users"],
        updated=data["last_updated"]
    )

# ------------------------------------------------
# RECEIVE LOCATION
# ------------------------------------------------

@app.route("/location", methods=["POST"])
def location():

    global users

    data = load_data()

    user = request.json

    users.append(user)

    # Prevent huge memory usage
    if len(users) > 100:
        users = users[-100:]

    # Current user nearest gate
    nearest_gate, current_distance = find_nearest_gate(
        user["lat"],
        user["lon"]
    )

    waiting_users = 0
    nearby_users = 0

    # Check all users
    for u in users:

        gate, distance = find_nearest_gate(
            u["lat"],
            u["lon"]
        )

        # Only nearby users
        if distance < 100:

            nearby_users += 1

            speed = u.get("speed")

            # Some phones return None speed
            if speed is None or speed < 2:

                waiting_users += 1

    # Save values
    data["waiting_users"] = waiting_users

    data["last_updated"] = datetime.now().strftime(
        "%I:%M:%S %p"
    )

    # ------------------------------------------------
    # SMART STATUS LOGIC
    # ------------------------------------------------

    if nearby_users == 0:

        data["status"] = "UNKNOWN"

    elif waiting_users >= 3:

        data["status"] = "CLOSED"

    else:

        data["status"] = "OPEN"

    save_data(data)

    # ------------------------------------------------
    # RESPONSE
    # ------------------------------------------------

    return jsonify({

        "status": data["status"],

        "waiting_users": waiting_users,

        "distance": round(current_distance, 2),

        "nearest_gate": nearest_gate["name"],

        "updated": data["last_updated"]

    })

# ------------------------------------------------
# RUN APP
# ------------------------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
