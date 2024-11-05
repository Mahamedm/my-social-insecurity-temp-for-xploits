"""Provides all forms used in the Social Insecurity application.

This file is used to define all forms used in the application.
It is imported by the social_insecurity package.

Example:
    from flask import Flask
    from app.forms import LoginForm

    app = Flask(__name__)

    # Use the form
    form = LoginForm()
    if form.validate_on_submit() and form.login.submit.data:
        username = form.username.data
"""

from datetime import datetime
from typing import cast

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    FileField,
    FormField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, InputRequired, Length, Optional, Regexp

# Defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields

# TODO: Add validation, maybe use wtforms.validators??

# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it


class LoginForm(FlaskForm):
    """Provides the login form for the application."""

    username = StringField(label="Username", render_kw={"placeholder": "Username"}, validators=[DataRequired()])
    password = PasswordField(label="Password", render_kw={"placeholder": "Password"}, validators=[DataRequired()])
    remember_me = BooleanField(
        label="Remember me"
    )  # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField(label="Sign In")


class RegisterForm(FlaskForm):
    """Provides the registration form for the application."""

    first_name = StringField(label="First Name", render_kw={"placeholder": "First Name"}, validators=[InputRequired()])
    last_name = StringField(label="Last Name", render_kw={"placeholder": "Last Name"}, validators=[InputRequired()])
    username = StringField(label="Username", render_kw={"placeholder": "Username"}, validators=[InputRequired()])
    password = PasswordField(label="Password", render_kw={"placeholder": "Password"}, validators=[InputRequired(), 
                                                 Length(min=8, message="Password must be at least 8 characters"),
                                                 Regexp(r".*[A-Z].*", message="Password must contain at least one uppercase letter"),
                                                 Regexp(r".*\d.*", message="Password must contain at least one number"),
                                                 Regexp(r".*[!@#$%^&*()\-_=\+\\|[\]{};:/?.><].*", 
                                                        message="Password must contain at least one special character (e.g., ! @ # $ % ^ & * ( ) - _ = + \\ | [ ] { } ; : / ? . < >).")])
    confirm_password = PasswordField(label="Confirm Password", render_kw={"placeholder": "Confirm Password"}, validators=[InputRequired()])
    submit = SubmitField(label="Sign Up")


class IndexForm(FlaskForm):
    """Provides the composite form for the index page."""

    login = cast(LoginForm, FormField(LoginForm))
    register = cast(RegisterForm, FormField(RegisterForm))


class PostForm(FlaskForm):
    """Provides the post form for the application."""

    content = TextAreaField(label="New Post", render_kw={"placeholder": "What are you thinking about?"})
    image = FileField(label="Image")
    submit = SubmitField(label="Post")


class CommentsForm(FlaskForm):
    """Provides the comment form for the application."""

    comment = TextAreaField(label="New Comment", render_kw={"placeholder": "What do you have to say?"})
    submit = SubmitField(label="Comment")


class FriendsForm(FlaskForm):
    """Provides the friend form for the application."""

    username = StringField(label="Friend's username", render_kw={"placeholder": "Username"})
    submit = SubmitField(label="Add Friend")


class ProfileForm(FlaskForm):
    """Provides the profile form for the application."""

    education = StringField(label="Education", render_kw={"placeholder": "Highest education"}, validators=[Optional()])
    employment = StringField(label="Employment", render_kw={"placeholder": "Current employment"}, validators=[Optional()])
    music = StringField(label="Favorite song", render_kw={"placeholder": "Favorite song"}, validators=[Optional()])
    movie = StringField(label="Favorite movie", render_kw={"placeholder": "Favorite movie"}, validators=[Optional()])
    nationality = StringField(label="Nationality", render_kw={"placeholder": "Your nationality"}, validators=[Optional()])
    birthday = DateField(label="Birthday", default=datetime.now(), validators=[Optional()])
    submit = SubmitField(label="Update Profile")
