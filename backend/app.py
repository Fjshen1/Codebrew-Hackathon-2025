from flask import Flask, jsonify, request
from flask_cors import CORS
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
CORS(app)

# In-memory storage of professionals
professionals = []
_next_id = 1

def haversine(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two lat/lng points."""
    R = 6371  # Earth radius in km
    φ1, φ2 = radians(lat1), radians(lat2)
    Δφ = radians(lat2 - lat1)
    Δλ = radians(lon2 - lon1)

    a = sin(Δφ/2)**2 + cos(φ1) * cos(φ2) * sin(Δλ/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

@app.route("/api/greet")
def greet():
    return jsonify(message="Hello from Flask!")

@app.route("/api/professionals", methods=["POST"])
def register_professional():
    """
    Body JSON: { name, profession, lat, lng }
    Returns: { id }
    """
    global _next_id
    data = request.get_json()
    prof = {
        "id":         _next_id,
        "name":       data["name"],
        "profession": data["profession"],
        "lat":        data["lat"],
        "lng":        data["lng"],
    }
    professionals.append(prof)
    _next_id += 1
    return jsonify(id=prof["id"]), 201

@app.route("/api/search", methods=["POST"])
def search_professionals():
    """
    Body JSON: { profession, lat, lng }
    Returns: [ { id, name, profession, distance_km }, … ]
    """
    data = request.get_json()
    target_prof = data["profession"]
    user_lat, user_lng = data["lat"], data["lng"]

    # filter by profession
    matches = [
        {
            "id":          p["id"],
            "name":        p["name"],
            "profession":  p["profession"],
            "distance_km": round(haversine(user_lat, user_lng, p["lat"], p["lng"]), 2)
        }
        for p in professionals
        if p["profession"] == target_prof
    ]

    # sort nearest first
    matches.sort(key=lambda x: x["distance_km"])
    return jsonify(matches)

if __name__ == "__main__":
    app.run()