"""Provides all routes for the Social Insecurity application.

This file contains the routes for the application. It is imported by the social_insecurity package.
It also contains the SQL queries used for communicating with the database.
"""

import sqlite3
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
from pathlib import Path
# import os
# from dotenv import load_dotenv
from flask import current_app as app
from flask import flash, redirect, render_template, send_from_directory, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user, login_required, login_user, logout_user

from social_insecurity import sqlite
from social_insecurity.config import *
from social_insecurity.database import User
from social_insecurity.forms import CommentsForm, FriendsForm, IndexForm, PostForm, ProfileForm
from social_insecurity.utils import *
from . import bcrypt

# load_dotenv()

limiter = Limiter(get_remote_address, app=app)

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@limiter.limit("1000 per day")
def index():
    """Provides the index page for the application.

    It reads the composite IndexForm and based on which form was submitted,
    it either logs the user in or registers a new user.

    If no form was submitted, it simply renders the index page.
    """
    index_form = IndexForm()
    login_form = index_form.login
    register_form = index_form.register

    if login_form.is_submitted() and login_form.submit.data:
        get_user = "SELECT * FROM Users WHERE username = ?;"
        user = sqlite.query(get_user, login_form.username.data, one=True)

        if user is None:
            flash("Invalid username or password!", category="warning")
        else:
            user_data = User(
                id = user["id"],
                username = user["username"],
                password = user["password"]
            )

            if not bcrypt.check_password_hash(user_data.password, login_form.password.data):
                flash("Sorry, wrong username or password !", category="warning")
            else:
                login_user(user_data, remember=login_form.remember_me.data)
                return redirect(url_for("stream"))

    elif register_form.is_submitted() and register_form.submit.data:
        password_hashed = bcrypt.generate_password_hash(register_form.password.data).decode("utf-8")
        check_user = """
            SELECT id FROM Users WHERE username = ?;
        """
        existing_user = sqlite.query(
            check_user,
            register_form.username.data
        )

        if existing_user:
            flash("Username already taken. Please choose a different username.", category="warning")
        else:
            insert_user = """
                INSERT INTO Users (username, first_name, last_name, password)
                VALUES (?, ?, ?, ?);
            """
            sqlite.query(
                insert_user,
                register_form.username.data,
                register_form.first_name.data,
                register_form.last_name.data,
                password_hashed,
            )
            flash("User successfully created!", category="success")
            return redirect(url_for("index"))

    return render_template("index.html.j2", title="Welcome", form=index_form)


@app.route("/stream", methods=["GET", "POST"])
@login_required
def stream():
    """Provides the stream page for the application.

    If a form was submitted, it reads the form data and inserts a new post into the database.

    Otherwise, it reads the username from the URL and displays all posts from the user and their friends.
    """
    username = current_user.username
    get_user = "SELECT * FROM Users WHERE username = ?;"
    user = sqlite.query(get_user, username, one=True)

    if not user:
        flash("User not found", category="warning")
        return redirect(url_for('index'))
    
    post_form = PostForm()
    get_user = "SELECT * FROM Users WHERE username = ?;"
    user = sqlite.query(get_user, username, one=True)

    if post_form.is_submitted():
        image_filename = None
        if post_form.image.data:
            file = post_form.image.data
            filename = file.filename
            if allowed_file(filename) and allowed_mime_type(file.stream):
                unique_filename = f"{uuid.uuid4().hex}_{secure_filename(filename)}"
                upload_path = Path(app.instance_path) / app.config["UPLOADS_FOLDER_PATH"] / unique_filename

                file.save(upload_path)

                image_filename = unique_filename
            else:
                flash("Invalid file type or format!", category="warning")
                return redirect(url_for("stream"))

        insert_post = """
            INSERT INTO Posts (u_id, content, image, creation_time)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP);
        """
        sqlite.query(insert_post, user["id"], post_form.content.data, image_filename)
        return redirect(url_for("stream"))

    get_posts = """
        SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id = p.id) AS cc
        FROM Posts AS p JOIN Users AS u ON u.id = p.u_id
        WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id = ?)
           OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id = ?)
           OR p.u_id = ?
        ORDER BY p.creation_time DESC;
    """
    posts = sqlite.query(get_posts, user["id"], user["id"], user["id"])
    return render_template("stream.html.j2", title="Stream", username=username, form=post_form, posts=posts)


@app.route("/comments/<int:post_id>", methods=["GET", "POST"])
@login_required
def comments(post_id: int):
    username = current_user.username
    if not username:
        return redirect(url_for('index'))
    
    """Provides the comments page for the application.

    If a form was submitted, it reads the form data and inserts a new comment into the database.

    Otherwise, it reads the username and post id from the URL and displays all comments for the post.
    """
    comments_form = CommentsForm()
    get_user = "SELECT * FROM Users WHERE username = ?;"
    user = sqlite.query(get_user, username, one=True)

    if comments_form.is_submitted():
        insert_comment = """
            INSERT INTO Comments (p_id, u_id, comment, creation_time)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP);
        """
        sqlite.query(insert_comment, post_id, user["id"], comments_form.comment.data)

    get_post = """
        SELECT *
        FROM Posts AS p JOIN Users AS u ON p.u_id = u.id
        WHERE p.id = ?;
    """
    get_comments = """
        SELECT DISTINCT *
        FROM Comments AS c JOIN Users AS u ON c.u_id = u.id
        WHERE c.p_id = ?
        ORDER BY c.creation_time DESC;
    """
    post = sqlite.query(get_post, post_id, one=True)
    comments = sqlite.query(get_comments, post_id)
    return render_template(
        "comments.html.j2", title="Comments", username=username, form=comments_form, post=post, comments=comments
    )


@app.route("/friends", methods=["GET", "POST"])
@login_required
def friends():
    username = current_user.username
    if not username:
        return redirect(url_for('index'))
    """Provides the friends page for the application.

    If a form was submitted, it reads the form data and inserts a new friend into the database.

    Otherwise, it reads the username from the URL and displays all friends of the user.
    """
    friends_form = FriendsForm()
    get_user = "SELECT * FROM Users WHERE username = ?;"
    user = sqlite.query(get_user, username, one=True)

    if friends_form.is_submitted():
        get_friend = "SELECT * FROM Users WHERE username = ?;"
        friend = sqlite.query(get_friend, friends_form.username.data, one=True)
        get_friends = "SELECT f_id FROM Friends WHERE u_id = ?;"
        friends = sqlite.query(get_friends, user["id"])

        if friend is None:
            flash("User does not exist!", category="warning")
        elif friend["id"] == user["id"]:
            flash("You cannot be friends with yourself!", category="warning")
        elif friend["id"] in [friend["f_id"] for friend in friends]:
            flash("You are already friends with this user!", category="warning")
        else:
            insert_friend = "INSERT INTO Friends (u_id, f_id) VALUES (?, ?);"
            sqlite.query(insert_friend, user["id"], friend["id"])
            flash("Friend successfully added!", category="success")

    get_friends = """
        SELECT *
        FROM Friends AS f JOIN Users as u ON f.f_id = u.id
        WHERE f.u_id = ? AND f.f_id != ?;
    """
    friends = sqlite.query(get_friends, user["id"], user["id"])
    return render_template("friends.html.j2", title="Friends", username=username, friends=friends, form=friends_form)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    username = current_user.username
    if not username:
        return redirect(url_for('index'))
    """Provides the profile page for the application.

    If a form was submitted, it reads the form data and updates the user's profile in the database.

    Otherwise, it reads the username from the URL and displays the user's profile.
    """
    profile_form = ProfileForm()
    get_user = "SELECT * FROM Users WHERE username = ?;"
    user = sqlite.query(get_user, username, one=True)

    if profile_form.is_submitted():
        update_profile = """
            UPDATE Users
            SET education = ?, employment = ?, music = ?, movie = ?, nationality = ?, birthday = ?
            WHERE username = ?;
        """
        sqlite.query(
            update_profile,
            profile_form.education.data,
            profile_form.employment.data,
            profile_form.music.data,
            profile_form.movie.data,
            profile_form.nationality.data,
            profile_form.birthday.data,
            username,
        )
        flash("Profile updated successfully!", category="success")
        return redirect(url_for("profile"))
    
    return render_template("profile.html.j2", title="Profile", username=username, user=user, form=profile_form)




@app.route("/uploads/<string:filename>")
@login_required
def uploads(filename):
    """Provides an endpoint for serving uploaded files."""
    return send_from_directory(Path(app.instance_path) / app.config["UPLOADS_FOLDER_PATH"], filename)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    #session.clear()
    return redirect(url_for('index'))

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html.j2"), 429

@app.errorhandler(413)
def ratelimit_handler(e):
    flash("File size exceeds the maximum allowed limit of 5 MB.", category="warning")
    return redirect(url_for("stream"))