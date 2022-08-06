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

class VideoViewsTest(TestCase):
    """Tests for Category Views Public/Private"""

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


    def tearDown(self):
        db.session.rollback()

    ###General full game guides
    def test_find_guide_view(self):
        """Test Find Guide View as logged in user"""
       
        user = User.query.get(900)
        
        with app.test_client(user=user) as client:
            resp = client.get("/playing/find-a-game-guide/800")
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("Guides from YouTube", content)


    def test_find_guide_view_logged_out(self):
        """Test Find guide view as public user"""

        with self.public_client as c:
            resp = c.get("/playing/find-a-game-guide/800", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("Please log in to access this page.", content)

### Item guides, video tests

    def test_find_item_guide_view(self):
            """Test Find specific Guide View as logged in user"""
        
            user = User.query.get(900)
            
            with app.test_client(user=user) as client:
                resp = client.get("/find-guide-to/woodfall")
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn("Add this guide to a gaming journal", content)


    def test_find_item_guide_view_logged_out(self):
            """Test Find specfic guide view as public user"""

            with self.public_client as c:
                resp = c.get("/find-guide-to/woodfall", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn("Please log in to access this page.", content)


  

  ##Game theory routes tests
    def test_find_theory_view(self):
            """Test Find theory View as logged in user"""
        
            user = User.query.get(900)
            
            with app.test_client(user=user) as client:
                resp = client.get("/games/find-a-game-theory/volvagia")
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn("Theories about volvagia", content)


    def test_find_theory_logged_out(self):
            """Test Find theory view as public user"""

            with self.public_client as c:
                resp = c.get("/games/find-a-game-theory/volvagia", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn("Please log in to access this page.", content)









