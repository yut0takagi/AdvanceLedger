import string
import random
import uuid
import firebase_admin
from firebase_admin import credentials, storage
from flask import Flask, render_template, request, redirect, url_for,  session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import pyrebase
from application.models import db
from application.config.config import firebase_config


firebase = pyrebase.initialize_app(firebase_config)
firebase_auth = firebase.auth()

#^ Migrate Object
migrate = Migrate()

#^ CSRF対策
csrf = CSRFProtect()

#^BP関連
from application.views import (auth_bp, home_bp, travel_bp, daily_bp)

def create_app():
    app = Flask(__name__)
    
    app.config.from_object('application.config.Config')
    
    #^ 初期化
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)    
    
    #^ Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(home_bp, url_prefix='/home')
    app.register_blueprint(travel_bp, url_prefix='/travel')
    app.register_blueprint(daily_bp, url_prefix='/daily')
    
    return app

def load_user(user_id):
    """ログイン中のユーザーを取得"""
    from application.models import User  # ここでインポートして循環インポートを回避
    return User.query.get(int(user_id))






