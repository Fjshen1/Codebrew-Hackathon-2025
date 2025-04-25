from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy database handle
# In your application factory or main file, make sure to call db.init_app(app)
db = SQLAlchemy()

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
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
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

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # Automatically set to the current timestamp on creation
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
