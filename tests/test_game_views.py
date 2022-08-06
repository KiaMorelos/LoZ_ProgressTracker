from unittest import TestCase
from flask_login import FlaskLoginClient
from flask_login import login_manager
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from models import db, User, Playing, Note, Wishlist

from app import app
app.test_client_class = FlaskLoginClient
login_manager.session_protection = None

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///zelda_tracker_test'


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

app.config["TESTING"] = True

class GameViewsTest(TestCase):
    """Tests for Game Views Public/Private"""

    def setUp(self):
        """Create a test user, and test client"""
        db.drop_all()
        db.create_all()

        self.public_client = app.test_client()
        self.request_ctx = app.test_request_context

        with self.request_ctx():
            user = User.signup("James Dean", "jimmydean", "test@imagine.com", "password")
            user.id = 900

            game = Playing(
                user_id= 900,
                game_id = "100", 
                game_title = "The Legend of Zelda",
                game_guide = "https://www.youtube.com/watch?v=9FigC7REkco",
                completed = True
                )
            
            game.id = 800

            db.session.add(user)
            db.session.add(game)
            
            db.session.commit()
        
        self.user = user
        self.game = game


    def tearDown(self):
        db.session.rollback()

    def test_game_view_logged_in(self):
        """Test Home Route as logged in user"""
       
        user = User.query.get(900)
        
        with app.test_client(user=user) as client:
            resp = client.get("/", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("jimmydean", content)
            self.assertIn("Logout", content)

    def test_game_view_logged_out(self):
        """Test Home Route as public user"""

        with self.public_client as c:
            resp = c.get("/", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("Keep track of your gaming progress!", content)
            self.assertNotIn("Click view details on any game to get started.", content)
            self.assertIn("Sign Up", content)

    def test_wishlist_view(self):
        """Test Wishlist View as logged in user"""
       
        user = User.query.get(900)
        
        with app.test_client(user=user) as client:
            resp = client.get("/wishlist")
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("No games currently on wishlist", content)

    def test_playing_list_view(self):
        """Test Playing List View as logged in user"""
       
        user = User.query.get(900)
        
        with app.test_client(user=user) as client:
            resp = client.get("/playing")
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("The Legend of Zelda", content)
            self.assertIn("Edit Game Journal", content)

    def test_playing_journal_view_unauthorized(self):
        """Test Playing/Game Journal View as not logged in user"""
       
        user = User.query.get(900)

        with self.public_client as c:
                resp = c.get(f"/playing/800", follow_redirects=True)
                content = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("Please log in to access this page.", content)


    def test_playing_journal_view(self):
        """Test Playing/Game Journal View as logged in user"""
       
        user = User.query.get(900)
        game = Playing.query.get(800)

        with app.test_client(user=user) as client:
                resp = client.get(f"/playing/{game.id}")
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn('Add a note to the journal', content)
                self.assertIn('Journal for: The Legend of Zelda', content)


