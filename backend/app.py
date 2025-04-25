import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from math import radians, sin, cos, sqrt, atan2

# Initialize Flask with static folder pointing to React's build output
global_app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '../frontend/build'),
    static_url_path='/'  # serve static files at root
)
app = global_app
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

# --- API ROUTES ---

@app.route("/api/greet")
def greet():
    return jsonify(message="Hello from Flask!")

@app.route("/api/professionals", methods=["POST"])
def register_professional():
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
    data = request.get_json()
    target_prof = data["profession"]
    user_lat, user_lng = data["lat"], data["lng"]

    # filter by profession and compute distance
    matches = []
    for p in professionals:
        if p["profession"] == target_prof:
            dist = round(haversine(user_lat, user_lng, p["lat"], p["lng"]), 2)
            matches.append({
                "id": p["id"],
                "name": p["name"],
                "profession": p["profession"],
                "distance_km": dist
            })
    # sort nearest first
    matches.sort(key=lambda x: x["distance_km"])
    return jsonify(matches)

# --- REACT FRONTEND ROUTES ---

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    build_dir = app.static_folder
    file_path = os.path.join(build_dir, path)
    if path and os.path.exists(file_path):
        return send_from_directory(build_dir, path)
    return send_from_directory(build_dir, 'index.html')

if __name__ == "__main__":
    # Use PORT env provided by Heroku, default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
