from flask import Flask, render_template, request, jsonify
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import os

app = Flask(__name__)

# -----------------------------------
# STORE USERS
# -----------------------------------

users = []

# -----------------------------------
# RAILWAY GATES
# -----------------------------------

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

# -----------------------------------
# DISTANCE CALCULATION
# -----------------------------------

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

# -----------------------------------
# HOME PAGE
# -----------------------------------

@app.route("/")
def home():

    return render_template("index.html")

# -----------------------------------
# RECEIVE LOCATION
# -----------------------------------

@app.route("/location", methods=["POST"])
def location():

    data = load_data()

    user = request.json

    user_id = user.get("user_id")

    user_lat = user["latitude"]
    user_lon = user["longitude"]

    speed = user.get("speed", 0)

    # Store active users
    active_users = {}

    active_users[user_id] = {
        "lat": user_lat,
        "lon": user_lon,
        "speed": speed
    }

    # CHECK EACH GATE

    for gate_id, gate in GATES.items():

        nearby_users = 0
        waiting_users = 0

        gate_lat = gate["lat"]
        gate_lon = gate["lon"]

        user_distance = calculate_distance(
            user_lat,
            user_lon,
            gate_lat,
            gate_lon
        )

        # Check active users

        for uid, u in active_users.items():

            distance = calculate_distance(
                u["lat"],
                u["lon"],
                gate_lat,
                gate_lon
            )

            # Nearby within 100m

            if distance <= 100:

                nearby_users += 1

                # Waiting if speed slow

                if u["speed"] < 2:
                    waiting_users += 1

        # STATUS

        if nearby_users == 0:

            status = "NO DATA"

        elif waiting_users >= 1:

            status = "CLOSED"

        else:

            status = "OPEN"

        # SAVE

        data[gate_id] = {

            "status": status,

            "waiting_users": waiting_users,

            "nearby_users": nearby_users,

            "distance": round(user_distance, 1),

            "last_updated": datetime.now().strftime(
                "%I:%M:%S %p"
            )

        }

    save_data(data)

    return jsonify({
        "message": "Location updated"
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
