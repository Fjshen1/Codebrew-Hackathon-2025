"""
Setup script for user data storage system.
This file initializes the database and provides functions to interact with user data.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a minimal Flask app
app = Flask(__name__)

# Configure the SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)  # 'client' or 'pro'
    # One-to-one relationship: each user has one profile
    profile = db.relationship('Profile', uselist=False, backref='user')

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    bio = db.Column(db.Text)
    location = db.Column(db.String)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    is_available = db.Column(db.Boolean, default=True)
    is_advertiser = db.Column(db.Boolean, default=False)  # Added field: True if advertising, False if looking
    # Many-to-many relationship: a profile can list multiple professions
    professions = db.relationship(
        'Profession',
        secondary='profile_professions',
        backref='profiles'
    )

class Profession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class ProfileProfessions(db.Model):
    __tablename__ = 'profile_professions'
    profile_id = db.Column(
        db.Integer, db.ForeignKey('profile.id'), primary_key=True
    )
    profession_id = db.Column(
        db.Integer, db.ForeignKey('profession.id'), primary_key=True
    )

# User data management functions
def initialize_database():
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully.")

def add_user(email, password, name, role, is_advertiser=False, professions=None, 
             bio='', location='', lat=None, lng=None):
    """
    Add a new user to the database
    
    Args:
        email (str): User's email
        password (str): User's password (will be hashed)
        name (str): User's name
        role (str): User's role ('client' or 'pro')
        is_advertiser (bool): True if user is advertising services, False if looking
        professions (list): List of profession names
        bio (str): User bio/description
        location (str): Text description of location
        lat (float): Latitude coordinate
        lng (float): Longitude coordinate
        
    Returns:
        int: ID of the created user
    """
    with app.app_context():
        # Create user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        # Create profile
        profile = Profile(
            name=name,
            bio=bio,
            location=location,
            lat=lat,
            lng=lng,
            is_advertiser=is_advertiser
        )
        
        user.profile = profile
        
        # Add professions if provided
        if professions:
            for prof_name in professions:
                # Get or create profession
                profession = Profession.query.filter_by(name=prof_name).first()
                if not profession:
                    profession = Profession(name=prof_name)
                    db.session.add(profession)
                
                profile.professions.append(profession)
        
        db.session.add(user)
        db.session.commit()
        
        return user.id

def get_user(user_id):
    """
    Get user by ID
    
    Args:
        user_id (int): User ID
    
    Returns:
        dict: User data including profile
    """
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return None
        
        profile = user.profile
        professions = [p.name for p in profile.professions] if profile.professions else []
        
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "profile": {
                "name": profile.name,
                "bio": profile.bio,
                "location": profile.location,
                "lat": profile.lat,
                "lng": profile.lng,
                "is_available": profile.is_available,
                "is_advertiser": profile.is_advertiser,
                "professions": professions
            }
        }

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
        
        profile = user.profile
        
        # Update user fields
        if 'email' in data:
            user.email = data['email']
        
        # Update profile fields
        if 'name' in data:
            profile.name = data['name']
        if 'bio' in data:
            profile.bio = data['bio']
        if 'location' in data:
            profile.location = data['location']
        if 'lat' in data:
            profile.lat = data['lat']
        if 'lng' in data:
            profile.lng = data['lng']
        if 'is_available' in data:
            profile.is_available = data['is_available']
        if 'is_advertiser' in data:
            profile.is_advertiser = data['is_advertiser']
        
        # Update professions
        if 'professions' in data:
            # Clear existing professions
            profile.professions = []
            
            # Add new professions
            for prof_name in data['professions']:
                profession = Profession.query.filter_by(name=prof_name).first()
                if not profession:
                    profession = Profession(name=prof_name)
                    db.session.add(profession)
                
                profile.professions.append(profession)
        
        db.session.commit()
        return True

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