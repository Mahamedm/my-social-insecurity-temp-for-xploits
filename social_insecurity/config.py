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
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") 
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application. Did you forget to add it to .env?")
    print(f"SECRET_KEY is loaded: {SECRET_KEY}")
    #print(SECRET_KEY)
    SQLITE3_DATABASE_PATH = "sqlite3.db"  # Path relative to the Flask instance folder
    UPLOADS_FOLDER_PATH = "uploads"  # Path relative to the Flask instance folder
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    WTF_CSRF_ENABLED = True  
    REMEMBER_COOKIE_DURATION = timedelta(days=2)
