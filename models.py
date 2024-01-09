from flask_sqlalchemy import SQLAlchemy
import time


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    token = db.Column(db.String)
    password = db.Column(db.String)
    pumps = db.relationship('Pump', backref='user')


class Pump(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    level = db.Column(db.Integer)
    current = db.Column(db.Float)
    volt = db.Column(db.Integer)
    state_one = db.Column(db.Integer)
    state_two = db.Column(db.Integer)
    latest_modified = db.Column(db.Integer, default=time.time())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))