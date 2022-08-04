"""SQLAlchemy models for Legend of Zelda Progress Tracker."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


bcrypt = Bcrypt()
db = SQLAlchemy()


class User(UserMixin, db.Model):
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

    password = db.Column(db.Text, nullable=False)

    wishlist = db.relationship('Wishlist', backref="User", cascade="all, delete-orphan")
    playing = db.relationship('Playing', backref="User", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User -- {self.id}: {self.username}, {self.full_name}, {self.email}>"

    @classmethod
    def signup(cls, full_name, username, email, password):
        """User Sign Up and Hash Password"""

        hashed_pass = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            full_name=full_name,
            username=username,
            email=email,
            password=hashed_pass,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with given username and password, otherwise return False."""

        user = cls.query.filter_by(username=username).first()

        if user:
            authorized = bcrypt.check_password_hash(user.password, password)
            if authorized:
                return user

        return False


class Playing(db.Model):
    """Games the User is currently playing"""

    __tablename__ = 'playing'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ## game id and title info will come from the Zelda API
    game_id = db.Column(db.Text, nullable=False)
    game_title = db.Column(db.Text, nullable=False)
    game_guide = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    notes = db.relationship('Note', backref="Playing", cascade="all, delete-orphan")

class Note(db.Model):
    """Notes model"""

    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    playing_id = db.Column(db.Integer, db.ForeignKey('playing.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow()
)

class Wishlist(db.Model):
    """Games the user wants to play, but is not actively playing"""

    __tablename__ = 'wishlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ## game id and title info will come from the Zelda API
    game_id = db.Column(db.Text, nullable=False)
    game_title = db.Column(db.Text, nullable=False)


def connect_db(app):
    """Connect this database to Flask app."""

    db.app = app
    db.init_app(app)
