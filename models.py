from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    host_star = db.Column(db.String(100))
    discovery_year = db.Column(db.Integer)
    method = db.Column(db.String(100))
    radius_earth = db.Column(db.Float)
    mass_earth = db.Column(db.Float)
    orbital_period = db.Column(db.Float)
    temperature = db.Column(db.Float)
    distance_pc = db.Column(db.Float)
    habitability_score = db.Column(db.Float)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=False)
    note = db.Column(db.Text, default="")
    planet = db.relationship("Planet")
    __table_args__ = (db.UniqueConstraint("user_id", "planet_id"),)