import os
from unittest import TestCase

from models import db, User, Playing, Note

os.environ['DATABASE_URL'] = "postgresql:///zelda_tracker_test"

from app import app

db.create_all()

class NoteModelTest(TestCase):
    """Tests for Note Model"""

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

    def test_add_note(self):
        """Test adding a note"""
        
        note = Note(
        note = "Finished Ikana Canyon",
        user_id = 900,
        playing_id = self.game.id,
        )
        note.id = 777
        
        db.session.add(note)
        db.session.commit()

        n = Note.query.get(777)

        self.assertIsInstance(n, Note)
        self.assertEqual(n.note, "Finished Ikana Canyon")
        self.assertEqual(n.user_id, 900)
        self.assertEqual(n.playing_id, self.game.id)