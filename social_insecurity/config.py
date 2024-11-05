"""Provides the configuration for the Social Insecurity application.

This file is used to set the configuration for the application.

Example:
    from flask import Flask
    from social_insecurity.config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    # Use the configuration
    secret_key = app.config["SECRET_KEY"]
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") # TODO: Use this with wtforms
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application. Did you forget to add it to .env?")
    print(f"SECRET_KEY is loaded: {SECRET_KEY}")
    #print(SECRET_KEY)
    SQLITE3_DATABASE_PATH = "sqlite3.db"  # Path relative to the Flask instance folder
    UPLOADS_FOLDER_PATH = "uploads"  # Path relative to the Flask instance folder
    ALLOWED_EXTENSIONS = {}  # TODO: Might use this at some point, probably don't want people to upload any file type
    WTF_CSRF_ENABLED = True  # TODO: I should probably implement this wtforms feature, but it's not a priority
    REMEMBER_COOKIE_DURATION = timedelta(days=2)
