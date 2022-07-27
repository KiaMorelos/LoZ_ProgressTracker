"""Forms for Legend of Zelda - Progress Tracker & Gaming Reference App"""
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import InputRequired, Length, Email
from flask_wtf import FlaskForm

class SignUpForm(FlaskForm):
    """Form for signing up a user"""

    full_name = StringField("Full Name", validators=[InputRequired(message="Name field cannot be blank")])
    username = StringField("username", validators=[InputRequired(message="Please enter a username")])
    email = EmailField("Email", validators=[InputRequired(message="The email field cannot be empty"), Email()])
    password = PasswordField("Enter a password to use", validators=[Length(min=8)])

class LoginForm(FlaskForm):
    """Form for signing up a user"""

    username = StringField("username", validators=[InputRequired(message="Please enter a username")])
    password = PasswordField("Enter your password", validators=[Length(min=8)])

