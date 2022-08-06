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

class CategoryViewsTest(TestCase):
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

            db.session.add(user)
            
            db.session.commit()
        
        self.user = user


    def tearDown(self):
        db.session.rollback()


    def test_category_list_view(self):
        """Test Category View as logged in user"""
       
        user = User.query.get(900)
        
        with app.test_client(user=user) as client:
            resp = client.get("games/bosses")
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("Bosses List", content)
            self.assertIn("View Details", content)
            self.assertIn("Search Bosses List", content)


    def test_category_view_unauthorized(self):
        """Test Category View as not logged in user"""
       
        with self.public_client as c:            
            resp = c.get("games/bosses", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertNotIn("Bosses List", content)
            self.assertNotIn("View Details", content)
            self.assertFalse(current_user.is_authenticated)
            self.assertIn("Please log in to access this page.", content)

    def test_category_detail_view(self):
        """Test Category item details View as logged in user"""
       
        user = User.query.get(900)
        
        with app.test_client(user=user) as client:
            resp = client.get("/games/bosses/details/5f6e93a7cbf4202fbde225c0")
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("Ganon", content)
            self.assertIn("Find a Guide", content)
            self.assertIn("Find a Game Theory", content)

    def test_category_detail_view_failed(self):
        """Test Category item details failed View as logged in user"""
       
        user = User.query.get(900)
        
        with app.test_client(user=user) as client:
            resp = client.get("/games/bosses/details/100")
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("I AM ERROR", content)
            self.assertIn("No results", content)
           




