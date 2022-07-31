"""Forms for Legend of Zelda - Progress Tracker & Gaming Reference App"""
from tokenize import String
from flask import Flask
from wtforms import StringField, EmailField, PasswordField, TextAreaField, HiddenField, BooleanField
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

class NoteForm(FlaskForm):
    """Add a gaming journal note"""

    note = TextAreaField("Add a Note", validators=[InputRequired(message='Note field cannot be blank')])

class HiddenDetailsForm(FlaskForm):
    """Hidden Form Fields for Game Details page to add games to play or wish list"""

    game_id = HiddenField("game id")
    game_title = HiddenField("game title")

class HiddenUrlForm(FlaskForm):
    """Hidden Fields for adding a guide to the journal"""

    game_guide = HiddenField("game guide")

