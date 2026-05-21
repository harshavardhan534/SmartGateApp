from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "database/data.json"

users = []

# -----------------------------
# LOAD DATA
# -----------------------------
def load_data():

    with open(DATA_FILE, "r") as file:
        return json.load(file)

# -----------------------------
# SAVE DATA
# -----------------------------
def save_data(data):

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():

    data = load_data()

    return render_template(
        "index.html",
        status=data["status"],
        waiting=data["waiting_users"],
        updated=data["last_updated"]
    )

# -----------------------------
# RECEIVE LOCATION
# -----------------------------
@app.route("/location", methods=["POST"])
def location():

    data = load_data()

    user = request.json

    users.append(user)

    waiting_users = 0

    for u in users:

        if u["speed"] < 2:
            waiting_users += 1

    data["waiting_users"] = waiting_users
    data["last_updated"] = datetime.now().strftime("%I:%M:%S %p")

    # Logic
    if waiting_users >= 3:
        data["status"] = "CLOSED"
    else:
        data["status"] = "OPEN"

    save_data(data)

    return jsonify({
        "message": "Location received",
        "status": data["status"]
    })

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":

    import os

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )