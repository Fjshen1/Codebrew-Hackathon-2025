import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# Initialize Flask with static folder pointing to React's build output
global_app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '../frontend/build'),
    static_url_path='/'
)
app = global_app
CORS(app)

# Database Configuration
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

global_app.config['SQLALCHEMY_DATABASE_URI'] = db_url
global_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(global_app)

# Database Model
class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Utility function
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
    data = request.get_json()
    prof = Professional(
        name=data["name"],
        profession=data["profession"],
        lat=data["lat"],
        lng=data["lng"]
    )
    db.session.add(prof)
    db.session.commit()
    return jsonify(id=prof.id), 201

@app.route("/api/search", methods=["POST"])
def search_professionals():
    data = request.get_json()
    target_prof = data["profession"]
    user_lat, user_lng = data["lat"], data["lng"]

    matches = []
    pros = Professional.query.filter_by(profession=target_prof).all()
    for p in pros:
        dist = round(haversine(user_lat, user_lng, p.lat, p.lng), 2)
        matches.append({
            "id": p.id,
            "name": p.name,
            "profession": p.profession,
            "distance_km": dist,
            "created_at": p.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

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