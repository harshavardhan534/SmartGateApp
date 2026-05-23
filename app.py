from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

# =========================================
# GATE LOCATIONS
# =========================================

gates = [

    {
        "name": "Cantonment Gate",
        "lat": 15.1514586,
        "lng": 76.8938312
    },

    {
        "name": "Radio Park Gate",
        "lat": 15.1445935,
        "lng": 76.9047562
    }

]

# =========================================
# DISTANCE FUNCTION
# =========================================

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return round(R * c)

# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return render_template("index.html")

# =========================================
# LOCATION API
# =========================================

@app.route("/location", methods=["POST"])
def location():

    try:

        data = request.json

        lat = float(data["lat"])
        lng = float(data["lng"])
        speed = float(data["speed"])

        result = []

        for gate in gates:

            distance = calculate_distance(

                lat,
                lng,

                gate["lat"],
                gate["lng"]

            )

            # =========================================
            # GATE STATUS
            # =========================================

            if distance < 300:

                if speed < 3:

                    status = "CLOSED"
                    waiting = 1

                else:

                    status = "OPEN"
                    waiting = 0

            else:

                status = "UNKNOWN"
                waiting = 0

            result.append({

                "name": gate["name"],
                "distance": distance,
                "status": status,
                "waiting": waiting

            })

        return jsonify({

            "success": True,
            "gates": result

        })

    except Exception as e:

        print(e)

        return jsonify({

            "success": False

        })

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
