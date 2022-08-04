import os
from unittest import TestCase

from models import db, User

os.environ['DATABASE_URL'] = "postgresql:///zelda_tracker_test"

from app import app

db.create_all()

class UserModelTest(TestCase):
    """Tests for User Model"""

    def setUp(self):
        """Create a test user, and test client"""
        db.drop_all()
        db.create_all()

        user = User.signup("James Dean", "jimmydean", "test@imagine.com", "password")

        db.session.add(user)
        db.session.commit()
        
        self.user = user
        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Test Model Basics"""

        user2 = User(
            full_name="Link",
            username="legend",
            email="link@legend.com",
            password="excuseMe",
        )

        db.session.add(user2)
        db.session.commit()

        self.assertEqual(user2.username, "legend")
        self.assertEqual(len(user2.playing), 0)
        self.assertEqual(len(user2.wishlist), 0)

    def test_user_signup(self):
        """New user via signup method"""
        
        user2 = User.signup(
            full_name="Link",
            username="legend",
            email="link@legend.com",
            password="excuseMe",
        )

        user2.id = 99999

        db.session.add(user2)
        db.session.commit()

        test_u = User.query.get(99999)

        self.assertIsInstance(test_u, User)
        self.assertEqual(test_u.full_name, "Link")
        self.assertEqual(test_u.email, "link@legend.com")


    def test_authenticate(self):
        """Test authentication works"""
        
        user = User.authenticate("jimmydean", "password")
        
        self.assertIsNotNone(user)
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, self.user.id)


    def test_invalid_auth(self):
        """Test authentication fails if credentials incorrect"""

        attempt1 = User.authenticate("jimmydean", "iamnotapass")
        attempt2 = User.authenticate("doesntexist", "password")
        self.assertFalse(attempt1)
        self.assertFalse(attempt2)