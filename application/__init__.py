import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from application.views import (auth_bp, home_bp, travel_bp, daily_bp)

# CSRF保護
csrf = CSRFProtect()

# Firebase Admin SDK 初期化（認証情報の設定）
cred = credentials.Certificate("application/config/serviceAccountKey.json")
firebase_admin_app = initialize_app(cred)

# Firestore クライアント取得
firestore_db = firestore.client()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Flask の設定ファイル読み込み
    app.config.from_object('application.config.config')

    # CSRF 初期化
    csrf.init_app(app)

    # Blueprint 登録
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(home_bp, url_prefix='/home')
    app.register_blueprint(travel_bp, url_prefix='/travel')
    app.register_blueprint(daily_bp, url_prefix='/daily')

    return app