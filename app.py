import requests

from flask import Flask, session, g, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import SignUpForm, LoginForm
from models import db, connect_db, User, Wishlist

from decouple import config

YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')
APP_SECRET_KEY = config('APP_SECRET_KEY')

YOUTUBE_API_URL = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}"

ZELDA_API_URL = "https://zelda.fanapis.com/api"

app = Flask(__name__)
app.config['SECRET_KEY'] = f"{APP_SECRET_KEY}"
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///zelda_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    """Root Route"""
    return redirect('/games')

@app.route('/games')
def games_list_view():
    """Home Page - Show list of Games"""

    resp = requests.get(f"{ZELDA_API_URL}/games", params={"limit": 50})

    games = resp.json()

    return render_template('index.html', games=games)

@app.route('/signup', methods=['GET', 'POST'])
def signup_new_user():
    """Sign Up New User - Page View"""

    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                full_name = form.full_name.data,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            db.session.commit()

        except:
            flash("Something went wrong", 'danger')
            return render_template('signup.html', form=form)
        login_user(user)
        return redirect("/")

    return render_template('signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Login User"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            login_user(user)
            return redirect("/")

        flash("Login Failed", 'danger')

    return render_template('login.html', form=form)

@login_required
@app.route('/logout')
def logout():
    """Logout User"""
    logout_user()
    flash("You are now logged out", "success")
    return redirect('/login')

@app.route('/games/game-details/<game_id>')
def game_details(game_id):
    """Show Details About Specific Game From Zelda API"""

    resp = requests.get(f"{ZELDA_API_URL}/games/{game_id}")
    game_dict = resp.json()
    
    game = game_dict['data']

    return render_template("games/game-details.html", game=game)

@login_required
@app.route('/wishlist')
def show_wishlist():
    """Show Game Wishlist"""
    
    return render_template('games/wishlist.html')

@login_required
@app.route('/wishlist/<game_id>',  methods=['GET', 'POST'])
def add_game_to_wishlist():
    """Add Game to wishlist"""

    return