from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db

from decouple import config

YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')
APP_SECRET_KEY = config('APP_SECRET_KEY')

YOUTUBE_API_URL = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}"

ZELDA_API_URL = "https://zelda.fanapis.com/api"

app = Flask(__name__)
app.config['SECRET_KEY'] = f"{APP_SECRET_KEY}"
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///zelda_tracker_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

@app.route('/')
def home():
    """Home Page"""
    return render_template('index.html')

