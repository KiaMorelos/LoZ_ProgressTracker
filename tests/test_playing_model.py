import os
from unittest import TestCase

from models import db, User, Playing, Note

os.environ['DATABASE_URL'] = "postgresql:///zelda_tracker_test"

from app import app

db.create_all()

class PlayingModelTest(TestCase):
    """Tests for Playing Model"""

    def setUp(self):
        """Create a test user, and test client"""
        db.drop_all()
        db.create_all()

        user = User.signup("James Dean", "jimmydean", "test@imagine.com", "password")
        user.id = 900

        game = Playing(
            user_id= 900,
            game_id = "100", 
            game_title = "Majora's Mask",
            game_guide = "https://www.youtube.com/watch?v=9FigC7REkco",
            completed = True
            )

        db.session.add(user)
        db.session.add(game)

        db.session.commit()
        
        self.user = user
        self.game = game

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()


    def test_playing_new_game(self):
        """Test adding new game works"""

        new_game = Playing(
            user_id= self.user.id,
            game_id = "5f6ce9d805615a85623ec2c5", 
            game_title = "The Legend of Zelda: Spirit Tracks",
            )
        
        db.session.add(new_game)
        db.session.commit()

        self.assertIsNotNone(new_game)
        self.assertIsNone(new_game.game_guide) ## is allowed to be empty
        self.assertFalse(new_game.completed) ## should default to false
        self.assertEqual(new_game.game_id, "5f6ce9d805615a85623ec2c5")
        self.assertEqual(new_game.game_title, "The Legend of Zelda: Spirit Tracks")

    def test_playing_notes(self):
        """Test Playing obj can access notes"""
        
        ### add a test note
        n = Note(
        note = "Finished Ikana Canyon",
        user_id = 900,
        playing_id = self.game.id,
        )
        
        db.session.add(n)
        db.session.commit()

        self.assertEqual(len(self.game.notes), 1)
        self.assertEqual(self.game.notes[0].note, "Finished Ikana Canyon")