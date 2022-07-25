"""SQLAlchemy models for Legend of Zelda Progress Tracker."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User Model."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    full_name = db.Column(db.String(20), nullable=False)

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    credentials_id = db.Column(
        db.Integer,
        nullable=False,
    )

    def __repr__(self):
        return f"<User -- {self.id}: {self.username}, {self.full_name}, {self.email}>"


class Credential(db.Model):
    """Credentials Model for users"""
    
    __tablename__ = 'credentials'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    password = db.Column(db.Text, nullable=False)

class Note(db.Model):
    """Notes model"""

    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey('users.username'))
    playing_id = db.Column(db.Integer, db.ForeignKey('playing.id'))
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow()
)

class Playing(db.Model):
    """Games the User is currently playing"""

    __tablename__ = 'playing'

class Wishlist(db.Model):
    """Games the user wants to play, but is not actively playing"""

    __tablename__ = 'wishlists'

class Played(db.Model):
    """Has the user played this game before?"""

    __tablename__ = 'played'

class ItemToFind(db.Model):
    """Items the User Needs to Find or has Found"""

    __tablename__ = 'items_to_find'

class DungeonToComplete(db.Model):
    """Dungeons the User needs to complete or has completed"""

    __tablename__ = 'dungeons_to_complete'




def connect_db(app):
    """Connect this database to Flask app."""

    db.app = app
    db.init_app(app)
