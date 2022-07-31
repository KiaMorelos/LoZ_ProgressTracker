from json import load
from pydoc import render_doc
import requests

from flask import Flask, session, g, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import SignUpForm, LoginForm, NoteForm, HiddenDetailsForm, HiddenUrlForm
from models import db, connect_db, User, Wishlist, Playing, Note, Played

from decouple import config

YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')
APP_SECRET_KEY = config('APP_SECRET_KEY')

YOUTUBE_API_URL = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}"

ZELDA_API_URL = "https://zelda.fanapis.com/api"

YOUTUBE_EMBED_URL = "https://www.youtube.com/embed/"

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
    try: 
        return User.query.get(int(user_id))
    except:
        return None

### root routes ###
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

### Sign up, login, logout routes ###
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

@app.route('/logout')
@login_required
def logout():
    """Logout User"""
    logout_user()
    flash("You are now logged out", "success")
    return redirect('/login')

### Game Details, Wishlists, Play Lists, and Playing Routes ###
@app.route('/games/game-details/<game_id>')
def show_game_details(game_id):
    """Show Details About Specific Game From Zelda API"""

    resp = requests.get(f"{ZELDA_API_URL}/games/{game_id}")
    game_dict = resp.json()
    game = game_dict['data']

    form = HiddenDetailsForm()
    form.game_id.data = game['id']
    form.game_title.data = game['name']

    return render_template("games/game-details.html", game=game, form=form)

@app.route('/playing')
@login_required
def show_currently_playing_list():
    """Show Currently Playing Game List"""
   
    user_id = current_user.id
    playing_list = Playing.query.filter_by(user_id=user_id).all()
   
    return render_template('games/in-play/playing.html', playing_list=playing_list)

@app.route('/wishlist')
@login_required
def show_wishlist():
    """Show Game Wishlist"""

    user_id = current_user.id
    wishlist = Wishlist.query.filter_by(user_id=user_id).all()

    return render_template('games/wishlist.html', wishlist=wishlist)

@app.route('/add-to-playing-list', methods=['POST'])
@login_required
def add_to_playing_list():
    """Add game to playing list"""
    
    user_id = current_user.id

    form = HiddenDetailsForm()

    if form.validate_on_submit():
        new_game  = Playing(user_id=user_id,
                    game_id=form.game_id.data,
                    game_title=form.game_title.data)

    db.session.add(new_game)
    db.session.commit()

    return redirect('/playing')

@app.route('/add-to-wishlist',  methods=['POST'])
@login_required
def add_game_to_wishlist():
    """Add Game to wishlist"""
    
    user_id = current_user.id
    form = HiddenDetailsForm()

    if form.validate_on_submit():
        game_wish = Wishlist(user_id=user_id,
                    game_id=form.game_id.data,
                    game_title=form.game_title.data)

        db.session.add(game_wish)
        db.session.commit()

    return redirect('/wishlist')

@app.route('/playing/<int:playing_id>', methods=['GET', 'POST'])
@login_required
def show_playing_journal(playing_id):
    """Show Game Journal Notes for Game in progress, and allow for new notes to be added"""
    
    game_journal = Playing.query.get_or_404(playing_id)
    user_id = current_user.id

    form = NoteForm()

    if form.validate_on_submit():
        note = Note(note=form.note.data,
                    user_id=user_id,
                    playing_id=playing_id,)
        
        db.session.add(note)
        db.session.commit()
        redirect(f'/playing/{playing_id}')

    return render_template('/games/in-play/playing-journal.html', game_journal=game_journal, form=form)

### Category Views - Bosses, Dungeons, Items, Places ###

@app.route('/games/<category>/<int:page_num>')
@login_required
def show_category_list(category, page_num):
    """Show General List of Chosen Category"""

    resp = requests.get(f"{ZELDA_API_URL}/{category}", params={"limit": 50, "page": page_num})
    cat_data = resp.json()

    return render_template('games/categories/category.html', category=category, cat_data=cat_data)

@app.route('/games/<category>/details/<item_id>')
@login_required
def show_item_details(category, item_id):
    """Show details for chosen item in category list"""
    
    resp = requests.get(f"{ZELDA_API_URL}/{category}/{item_id}")
    r = resp.json()
    item = r['data']

    return render_template('games/categories/details.html', item=item)


###Video Content Routes ###
@app.route('/playing/find-a-game-guide/<int:playing_id>')
@login_required
def show_youtube_guides(playing_id):
    """Show Video Walkthrough Guides for specific game"""

    playing = Playing.query.get_or_404(playing_id)
    g_title = playing.game_title

    resp = requests.get(f"{YOUTUBE_API_URL}", params={"part": "snippet", "maxResults": 10, "q": f"{g_title} walkthrough", "type" : "video", "videoEmbeddable": "true"})
    guides_raw = resp.json()

    guides = guides_raw['items']

    return render_template('video-content/guides.html', guides=guides, YOUTUBE_EMBED_URL=YOUTUBE_EMBED_URL, playing=playing)

@app.route('/add-guide-to-journal/<int:playing_id>', methods=['POST'])
@login_required
def add_guide_to_journal(playing_id):
    """Add a game guide to a corresponding journal"""
    
    p = Playing.query.get_or_404(playing_id)
    
    p.game_guide = request.form['game_guide']
    db.session.add(p)
    db.session.commit()

    return redirect(f'/playing/{playing_id}')


###Delete and Edit Routes for Lists, Gaming Notes
@app.route('/playing/<int:playing_id>/delete', methods=['POST'])
@login_required
def delete_game_in_play(playing_id):
    """Delete Game from Playing List"""

    game_in_play = Playing.query.get_or_404(playing_id)
    db.session.delete(game_in_play)
    db.session.commit()

    return redirect('/playing')

@app.route('/playing/<int:playing_id>/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def update_note(playing_id, note_id):
    """Edit a Game Note"""
    
    n = Note.query.get_or_404(note_id)

    form = NoteForm(obj=n)
    if form.validate_on_submit():
        
        n.note = form.note.data
        db.session.add(n)
        db.session.commit()

        return redirect(f'/playing/{playing_id}')

    return render_template('games/in-play/edit-game-note.html', n=n, form=form)

@app.route('/playing/<int:playing_id>/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(playing_id, note_id):
    """Delete a Game Note"""

    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()

    return redirect(f'/playing/{playing_id}')

@app.route('/wishlist/<int:wishlist_id>/delete', methods=['POST'])
@login_required
def delete_game_wish(wishlist_id):
    """Delete Game from Wishlist"""

    game_wish = Wishlist.query.get_or_404(wishlist_id)
    db.session.delete(game_wish)
    db.session.commit()

    return redirect('/wishlist')