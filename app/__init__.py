"""
Created on <DateTime>

@uthor: $ujay $imha
"""

from flask import Flask
from config import DevelopmentConfig
from .exts import db, migrate, login_manager
from .main import index
from .auth import auth
from .models import *

def register_blueprints(app):
    app.register_blueprint(index)
    app.register_blueprint(auth)

def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login" #pyright:ignore

def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    register_blueprints(app)
    register_extensions(app)

    return app
