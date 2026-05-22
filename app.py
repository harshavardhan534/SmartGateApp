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

    global users

    user = request.json

    users.append(user)

    # Limit memory
    if len(users) > 100:

        users = users[-100:]

    gate_results = []

    # -----------------------------------
    # CHECK EACH GATE
    # -----------------------------------

    for gate in gates:

        nearby_users = 0
        waiting_users = 0

        for u in users:

            distance = calculate_distance(

                u["lat"],
                u["lon"],

                gate["lat"],
                gate["lon"]

            )

            # Nearby user
            if distance < 100:

                nearby_users += 1

                speed = u.get("speed")

                if speed is None or speed < 2:

                    waiting_users += 1

        # -----------------------------------
        # GATE STATUS
        # -----------------------------------

        if nearby_users == 0:

            status = "UNKNOWN"

        elif waiting_users >= 3:

            status = "CLOSED"

        else:

            status = "OPEN"

        # Current user's distance
        current_distance = calculate_distance(

            user["lat"],
            user["lon"],

            gate["lat"],
            gate["lon"]

        )

        gate_results.append({

            "name": gate["name"],

            "status": status,

            "waiting_users": waiting_users,

            "nearby_users": nearby_users,

            "distance": round(current_distance, 2),

            "updated": datetime.now().strftime(
                "%I:%M:%S %p"
            )

        })

    return jsonify(gate_results)

# -----------------------------------
# RUN APP
# -----------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
