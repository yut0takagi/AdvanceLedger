# application/__init__.py

import os
from flask import Flask, session, redirect, url_for, request
from flask_wtf.csrf import CSRFProtect
from application.views import (auth_bp, home_bp, travel_bp, daily_bp, dashboard_bp, group_bp)
from application.extensions import firestore_db

from firebase_admin import auth

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('application.config.config')
    csrf.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(home_bp, url_prefix='/home')
    app.register_blueprint(travel_bp, url_prefix='/travel')
    app.register_blueprint(daily_bp, url_prefix='/daily')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(group_bp, url_prefix='/group')
    return app

