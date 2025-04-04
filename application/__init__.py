# application/__init__.py

import os
from flask import Flask, session, redirect, url_for, request
from flask_wtf.csrf import CSRFProtect
from application.views import *
from application.extensions import firestore_db

from firebase_admin import auth

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('application.config.config')
    csrf.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(home_bp, url_prefix='/home')
    app.register_blueprint(friend_bp, url_prefix='/friend')
    app.register_blueprint(daily_bp, url_prefix='/daily')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(group_bp, url_prefix='/group')
    app.register_blueprint(notification_bp, url_prefix='/notification')
    
    # 🔔 通知件数を全テンプレートに渡す
    @app.context_processor
    def inject_unread_notifications():
        if "user" in session:
            user_id = session["user"]["docID"]
            unread_docs = (
                firestore_db.collection("notifications")
                .where("user_id", "==", user_id)
                .where("is_read", "==", False)
                .get()
            )
            return {"unread_notifications_count": len(unread_docs)}
        return {"unread_notifications_count": 0}

    return app

