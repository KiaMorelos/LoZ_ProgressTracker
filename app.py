from json import load
from pydoc import render_doc
import requests

from flask import Flask, jsonify, session, g, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import SignUpForm, LoginForm, NoteForm, HiddenDetailsForm, HiddenUrlForm
from models import db, connect_db, User, Wishlist, Playing, Note

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

    try:
        resp = requests.get(f"{ZELDA_API_URL}/games", params={"limit": 50})

        games = resp.json()
    
    except:
        error = "No results found"
        flash('I AM ERROR. - Sorry something went wrong while retrieving the games list. Please try again later.', 'warning')
        return render_template('index.html', error=error)


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

    try:
        resp = requests.get(f"{ZELDA_API_URL}/games/{game_id}")
        game_dict = resp.json()
        game = game_dict['data']

        form = HiddenDetailsForm()
        form.game_id.data = game['id']
        form.game_title.data = game['name']
    except:
        error = "No results found"
        flash('I AM ERROR. - Sorry something went wrong while retrieving the details for that. Please try again later', 'warning')
        return render_template("games/game-details.html", error=error)

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

@app.route('/games/<category>')
@login_required
def show_category_list(category):
    """Show General List of Chosen Category"""
    
    if request.args.get('page'):
        page_num = int(request.args.get('page'))
    else:
        page_num = 0

    try:
        resp = requests.get(f"{ZELDA_API_URL}/{category}", params={"limit": 20, "page": page_num })
        cat_data = resp.json()
    
    except:
        error = "No results found"
        flash(f'I AM ERROR. - Sorry something went wrong while retrieving a list for {category}. Please try again later', 'warning')
        return render_template('games/categories/category.html', error=error)

    return render_template('games/categories/category.html', category=category, cat_data=cat_data, page_num=page_num)

@app.route('/search/<category>')
@login_required
def search_category_list(category):
    """Search for something in a category general list - bosses, dungeons, items, places"""

    search = request.args.get('q')
    
    if request.args.get('page'):
        page_num = int(request.args.get('page'))
    else:
        page_num = 0
    
    try:
        resp = requests.get(f"{ZELDA_API_URL}/{category}", params={"limit": 20, "name": f"{search.title()}", "page": page_num })
        
        cat_data = resp.json()

    except:
        
        error = "No results found"
        flash(f'I AM ERROR. - Sorry something went wrong while retrieving a search for {search}. Please try again later', 'warning')
        return redirect(f'/games/{category}', error=error)


    return render_template('games/categories/category.html', category=category, cat_data=cat_data, search=search, page_num=page_num)


@app.route('/games/<category>/details/<item_id>')
@login_required
def show_item_details(category, item_id):
    """Show details for chosen item in category list"""
    
    try:
        resp = requests.get(f"{ZELDA_API_URL}/{category}/{item_id}")
        r = resp.json()
        item = r['data']

    except:
        error = "No results found"
        flash(f'I AM ERROR. - Sorry something went wrong while retrieving the details for that. Please try again later', 'warning')
        
        return render_template('games/categories/details.html', error=error)
    

    return render_template('games/categories/details.html', item=item)


###Video Content Routes ###
@app.route('/playing/find-a-game-guide/<int:playing_id>')
@login_required
def show_youtube_game_guides(playing_id):
    """Show Video Walkthrough Guides for specific game"""

    playing = Playing.query.get_or_404(playing_id)
    g_title = playing.game_title

    try:
        resp = requests.get(f"{YOUTUBE_API_URL}", params={"part": "snippet", "maxResults": 10, "q": f"{g_title} walkthrough", "type" : "video", "videoEmbeddable": "true"})
        guides_raw = resp.json()

        guides = guides_raw['items']
    
    except:

        error = "Couldn't retrieve video results from YouTube. Please try again later. You can still add and update your gaming journals, but may not be able to add or switch guides for the journals at this time."

        flash('I AM ERROR. - Sorry! It looks like something may have went wrong with our YouTube connection', 'warning')

        return render_template('video-content/guides.html', error=error)


    return render_template('video-content/guides.html', guides=guides, YOUTUBE_EMBED_URL=YOUTUBE_EMBED_URL, playing=playing)

@app.route('/find-guide-to/<item_name>')
@login_required
def show_youtube_guide_misc(item_name):
    """Show guides for a chosen item - bosses, dungeons, items, places"""

    try:

        resp = requests.get(f"{YOUTUBE_API_URL}", params={"part": "snippet", "maxResults": 10, "q": f"{item_name} walkthrough", "type" : "video", "videoEmbeddable": "true"})
        guides_raw = resp.json()

        guides = guides_raw['items']

    except:

        error = "Couldn't retrieve video results from YouTube. Please try again later. You can still add and update your gaming journals, but may not be able to add or switch guides for the journals at this time."

        flash('I AM ERROR. - Sorry! It looks like something may have went wrong with our YouTube connection', 'warning')

        return render_template('video-content/misc-guides.html', error=error)

    return render_template('video-content/misc-guides.html', guides=guides, YOUTUBE_EMBED_URL=YOUTUBE_EMBED_URL, item_name=item_name)


@app.route('/add-guide-to-journal', methods=['POST'])
@login_required 
def add_guide_to_journal():
    """Add a game guide to a corresponding journal"""
    playing_id = request.form['playing_id']
    p = Playing.query.get_or_404(playing_id)
    
    p.game_guide = request.form['game_guide']
    db.session.add(p)
    db.session.commit()

    return redirect(f'/playing/{playing_id}')

@app.route('/games/find-a-game-theory/<item_name>')
@login_required
def find_game_theory(item_name):
    """Try to find a game theory about a game, boss, item, dungeon or place"""

    try:
        resp = requests.get(f"{YOUTUBE_API_URL}", params={"part": "snippet", "maxResults": 10, "q": f"{item_name} zelda theory", "type" : "video", "videoEmbeddable": "true"})
        theories_raw = resp.json()

        theories = theories_raw['items']


    except:
        error = "Couldn't retrieve video results from YouTube. Please try again later. You can still add and update your gaming journals, but may not be able to add or switch guides for the journals at this time or view game theory videos."

        flash('I AM ERROR. - Sorry! It looks like something may have went wrong with our YouTube connection', 'warning')

        return render_template('video-content/theory-videos.html', error=error)

    return render_template('video-content/theory-videos.html', theories=theories, YOUTUBE_EMBED_URL=YOUTUBE_EMBED_URL, item_name=item_name)


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


#### Utitlity Function and Route ###
def serialize(playing):
    """Serialize a playing SQLAlchemy obj to dictionary."""
    
    return {
        "id": playing.id,
        "user_id": playing.user_id,
        "game_id": playing.game_id,
        "game_title": playing.game_title,
        "game_guide": playing.game_guide,
        }

@app.route('/api/playing')
@login_required
def get_currently_playing_list():
    """Get JSONIFIED playing list of the current user's games"""

    user_id = current_user.id
    playing_list = Playing.query.filter_by(user_id=user_id).all()

    serialized = [serialize(playing) for playing in playing_list]

    return jsonify(serialized)