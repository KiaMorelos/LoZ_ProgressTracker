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

            note = Note(
                note = "Started a playthrough",
                user_id = 900,
                playing_id = 800,
            )

            note.id = 700

            wish = Wishlist(
                user_id= 900,
                game_id = "200", 
                game_title = "Ocarina of Time",

            )

            wish.id = 600

            db.session.add(user)
            db.session.add(game)
            db.session.add(note)
            db.session.add(wish)


            
            db.session.commit()
        
        self.user = user
        self.game = game
        self.note = note
        self.wish = wish



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
            self.assertFalse(current_user.is_authenticated)

    def test_wishlist_view(self):
        """Test Wishlist View as logged in user"""
       
        user = User.query.get(900)
        
        with app.test_client(user=user) as client:
            resp = client.get("/wishlist")
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn("Ocarina of Time", content)

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
                self.assertIn('Started a playthrough', content)

    def test_game_details_view_fail(self):
        """Test game details view - invalid"""

        with self.public_client as c:
                resp = c.get(f"/games/game-details/100", follow_redirects=True)
                content = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn('No results found', content)

    def test_game_details_view_success(self):
        """Test game details view - valid id in zelda api"""

        with self.public_client as c:
                resp = c.get(f"/games/game-details/5f6ce9d805615a85623ec2b8", follow_redirects=True)
                content = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn('The Legend of Zelda', content)


    def test_add_game_to_playing_list(self):
        """Test adding game to playing now list"""
        
        user = User.query.get(900)
        with app.test_client(user=user) as client:

                resp = client.post(f"/add-to-playing-list", data={"user_id": "900", "game_id": "5f6ce9d805615a85623ec2b8", "game_title":"The Legend of Zelda: A Link to the Past" }, follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn('A Link to the Past', content)

    def test_add_guide_to_journal(self):
        "Test add a game guide"
        
        user = User.query.get(900)
        with app.test_client(user=user) as client:
            resp = client.post("/add-guide-to-journal", data={"game_guide": "https://text-guide.com", "playing_id": "800"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertIn('https://text-guide.com', content)
            self.assertIn('Switch to New Video Guide', content)


    def test_add_game_to_wishlist(self):
        """Test adding game to wishlist"""
        
        user = User.query.get(900)
        with app.test_client(user=user) as client:

                resp = client.post(f"/add-to-wishlist", data={"user_id": "900", "game_id": "5f6ce9d805615a85623ec2b8", "game_title":"The Legend of Zelda: A Link to the Past" }, follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn('A Link to the Past', content)

    def test_delete_wishlist_item(self):
        """Delete game from wishlist"""

        user = User.query.get(900)
        with app.test_client(user=user) as client:

            resp = client.post(f"/wishlist/600/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertNotIn('Ocarina of Time', content)
            self.assertIn('No games currently on wishlist', content)

    def test_finish_game(self):
        """Test mark game as finished"""
        
        user = User.query.get(900)
        with app.test_client(user=user) as client:

                resp = client.post(f"/finished-game/800", data={"completed": "True" }, follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn('The Legend of Zelda', content)
                self.assertIn('Finished!', content)


    def test_delete_game(self):
        """Test delete game from playing list"""
        
        user = User.query.get(900)
        with app.test_client(user=user) as client:

                resp = client.post(f"/playing/800/delete", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn('No games currently in play', content)

    def test_add_note(self):
        """Test add note to game journal"""
        user = User.query.get(900)
        with app.test_client(user=user) as client:

                resp = client.post(f"/playing/800",data={"note": "finished level 1" }, follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn('finished level 1', content)

    def test_edit_note(self):
        """Test edit note"""
        user = User.query.get(900)
        with app.test_client(user=user) as client:

                resp = client.post(f"/playing/800/700/edit",data={"note": "finished level 7" }, follow_redirects=True)
                self.assertEqual(resp.status_code, 200)
                content = resp.get_data(as_text=True)
                self.assertIn('finished level 7', content)
    
    def test_delete_note(self):
        """Test delete note"""

        user = User.query.get(900)
        with app.test_client(user=user) as client:

            resp = client.post(f"/playing/800/700/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            content = resp.get_data(as_text=True)
            self.assertNotIn('finished level 1', content)


                
                
        

