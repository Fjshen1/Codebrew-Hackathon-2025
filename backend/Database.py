"""
Setup script for user data storage system.
This file initializes the database and provides functions to interact with user data.
Modified to properly work with web browsers and server-side storage.
"""
import os
import json
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # For handling cross-origin requests
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from sqlalchemy import func, or_

# Load environment variables
load_dotenv()

# Create a minimal Flask app
app = Flask(__name__)

# Enable CORS to allow browser requests from different origins
CORS(app, supports_credentials=True)

# Configure the SQLAlchemy database

# Use Heroku DATABASE_URL if present, otherwise fall back to local SQLite
db_url = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
# SQLAlchemy expects the postgresql:// scheme
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

# Ensure we handle Heroku's PostgreSQL URL format correctly
db_url = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
# Fix for Heroku PostgreSQL URL format
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)


app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set secret key for sessions
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')  # Change in production!

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)  # 'client' or 'pro'

    profile = db.relationship('Profile', uselist=False, backref='user')

    # One-to-one relationship: each user has one profile
    profile = db.relationship('Profile', uselist=False, backref='user', cascade='all, delete-orphan')


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    bio = db.Column(db.Text)
    location = db.Column(db.String)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    is_available = db.Column(db.Boolean, default=True)
    is_advertiser = db.Column(db.Boolean, default=False)
    professions = db.relationship(
        'Profession', secondary='profile_professions', backref='profiles'
    )

class Profession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class ProfileProfessions(db.Model):
    __tablename__ = 'profile_professions'
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), primary_key=True)

# User data management functions
def initialize_database():
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully.")

# ... other helper functions (add_user, get_user, etc.) ...

def add_user(email, password, name, role, is_advertiser=False, professions=None,
             bio='', location='', lat=None, lng=None):
    with app.app_context():
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        profile = Profile(
            name=name,
            bio=bio,
            location=location,
            lat=lat,
            lng=lng,
            is_advertiser=is_advertiser
        )
        user.profile = profile
        if professions:
            for prof_name in professions:
                profession = Profession.query.filter_by(name=prof_name).first()
                if not profession:
                    profession = Profession(name=prof_name)
                    db.session.add(profession)
                profile.professions.append(profession)
        db.session.add(user)
        db.session.commit()
        return user.id

# ... other CRUD functions ...


def get_user_by_email(email):
    """
    Get user by email
    
    Args:
        email (str): User email
    
    Returns:
        User: User object or None
    """
    with app.app_context():
        return User.query.filter_by(email=email).first()

def find_users_by_profession(profession_name, advertiser_only=False):
    """
    Find users by profession
    
    Args:
        profession_name (str): Name of profession to search for
        advertiser_only (bool): If True, only return users with is_advertiser=True
    
    Returns:
        list: List of user profiles matching the criteria
    """
    with app.app_context():
        query = Profile.query.join(Profile.professions).filter(Profession.name == profession_name)
        
        if advertiser_only:
            query = query.filter(Profile.is_available == True)
            if advertiser_only:
                query = query.filter(Profile.is_advertiser == True)
        
        profiles = query.all()
        
        result = []
        for profile in profiles:
            result.append({
                "user_id": profile.user_id,
                "name": profile.name,
                "location": profile.location,
                "lat": profile.lat,
                "lng": profile.lng,
                "is_advertiser": profile.is_advertiser
            })
            
        return result

def find_matching_professionals(needed_services, location=None, distance=50):
    """
    Find professionals who offer the needed services
    
    Args:
        needed_services (list): List of service names to match
        location (str): Location to search near (optional)
        distance (int): Max distance in miles/km (for future geospatial search)
        
    Returns:
        list: List of matching professionals
    """
    with app.app_context():
        # Start with professionals who are available
        query = db.session.query(User, Profile).join(Profile).filter(
            User.role == 'pro',
            Profile.is_available == True,
            Profile.is_advertiser == True
        )
        
        # Filter by matching professions if services specified
        if needed_services:
            query = query.join(Profile.professions).filter(
                Profession.name.in_(needed_services)
            ).group_by(User.id, Profile.id).having(
                func.count(Profession.id) > 0  # At least one matching profession
            )
        
        # Filter by location if specified
        if location:
            query = query.filter(Profile.location.ilike(f"%{location}%"))
        
        # Execute query and format results
        results = []
        for user, profile in query.all():
            results.append({
                'id': user.id,
                'name': profile.name,
                'location': profile.location,
                'bio': profile.bio,
                'professions': [p.name for p in profile.professions]
            })
        
        return results

def update_user(user_id, data):
    """
    Update user information
    
    Args:
        user_id (int): User ID
        data (dict): Fields to update
    
    Returns:
        bool: True if successful
    """

    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return False
        db.session.delete(user)
        db.session.commit()
        return True


# Allow the script to be run directly to initialize the database
if __name__ == '__main__':
    initialize_database()

def delete_user(user_id):
    """
    Delete a user and their profile
    
    Args:
        user_id (int): User ID
    
    Returns:
        bool: True if successful
    """
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return False
        
        db.session.delete(user)
        db.session.commit()
        return True

# Web routes for browser integration
@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Get user
        user = get_user_by_email(email)
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Store user in session
        session['user_id'] = user.id
        session['role'] = user.role
        
        # Return user data
        profile = user.profile
        return jsonify({
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'profile': {
                'name': profile.name,
                'bio': profile.bio,
                'location': profile.location,
                'is_advertiser': profile.is_advertiser,
                'professions': [p.name for p in profile.professions]
            }
        })
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.json
        
        # Check if email already exists
        existing_user = get_user_by_email(data.get('email'))
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user_id = add_user(
            email=data.get('email'),
            password=data.get('password'),
            name=data.get('name', ''),
            role=data.get('role', 'client'),
            is_advertiser=data.get('is_advertiser', False),
            professions=data.get('professions', []),
            bio=data.get('bio', ''),
            location=data.get('location', ''),
            lat=data.get('lat'),
            lng=data.get('lng')
        )
        
        return jsonify({'success': True, 'user_id': user_id})
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get the current user's profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_data = get_user(session['user_id'])
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user_data)

@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """Update the current user's profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    success = update_user(session['user_id'], data)
    
    if not success:
        return jsonify({'error': 'Failed to update profile'}), 404
    
    return jsonify({'success': True})

@app.route('/api/match', methods=['GET'])
def find_matches():
    """Find matching users based on profession/services"""
    professions = request.args.getlist('professions[]')
    location = request.args.get('location')
    
    results = find_matching_professionals(professions, location)
    return jsonify(results)

# If this file is run directly, initialize the database
if __name__ == '__main__':
    # Check if running on Heroku
    if 'PORT' in os.environ:
        # Running on Heroku
        port = int(os.environ.get('PORT', 5000))
        # Initialize database
        initialize_database()
        # Run app
        app.run(host='0.0.0.0', port=port)
    else:
        # Local development
        initialize_database()
        app.run(debug=True)

