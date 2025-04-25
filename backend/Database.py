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
# Use Heroku DATABASE_URL if present, otherwise fall back to local SQLite
db_url = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
# SQLAlchemy expects the postgresql:// scheme
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)  # 'client' or 'pro'
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

def delete_user(user_id):
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
