from unittest import TestCase

from models import db, User, Wishlist

from app import app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///zelda_tracker_test'


db.create_all()

class WishlistModelTest(TestCase):
    """Tests for Wishlist Model"""

    def setUp(self):
        """Create a test user, and test client"""
        db.drop_all()
        db.create_all()

        user = User.signup("James Dean", "jimmydean", "test@imagine.com", "password")
        user.id = 900

        game = Wishlist(
            user_id= 900,
            game_id = "100", 
            game_title = "Majora's Mask",
            )

        db.session.add(user)
        db.session.add(game)

        db.session.commit()
        
        self.user = user
        self.game = game

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()


    def test_wishlist_new_game(self):
        """Test adding game to wishlist works"""

        new_game = Wishlist(
            user_id= self.user.id,
            game_id = "5f6ce9d805615a85623ec2c5", 
            game_title = "The Legend of Zelda: Spirit Tracks",
            )
        
        db.session.add(new_game)
        db.session.commit()

        self.assertIsNotNone(new_game)
        self.assertEqual(new_game.game_id, "5f6ce9d805615a85623ec2c5")
        self.assertEqual(new_game.game_title, "The Legend of Zelda: Spirit Tracks")
        self.assertEqual(len(self.user.wishlist), 2)
