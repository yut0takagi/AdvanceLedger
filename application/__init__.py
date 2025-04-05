# application/__init__.py

import os
from flask import Flask, session, redirect, url_for, request
from flask_wtf.csrf import CSRFProtect
from application.views import *
from application.extensions import firestore_db, log_error_to_firestore_global

from firebase_admin import auth
import logging
import sys
from dotenv import load_dotenv

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('application.config.config.Config')
    csrf.init_app(app)
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(home_bp, url_prefix='/home')
    app.register_blueprint(friend_bp, url_prefix='/friend')
    app.register_blueprint(daily_bp, url_prefix='/daily')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(group_bp, url_prefix='/group')
    app.register_blueprint(notification_bp, url_prefix='/notification')
    
    # 🔥 グローバルエラーハンドラの登録（すべてのエラーをキャッチ）
    app.register_error_handler(Exception, log_error_to_firestore_global)
    
    # ログ設定：stdout へ出力（Renderで確認可）
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout),                     # Renderログ
            logging.FileHandler("error.log", encoding="utf-8"),   # ローカル用
        ],
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_template("errors/401.html"), 401

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_template("errors/405.html"), 405

    @app.errorhandler(500)
    def server_error(e):
        logging.exception("500 Internal Server Error")
        return render_template("errors/500.html"), 500

    # 共通のエラーハンドラ（予期しない例外をログに記録）
    @app.errorhandler(Exception)
    def handle_exception(e):
        logging.exception("❗️ 未処理の例外が発生しました")
        return render_template("errors/500.html"), 500
    
    # 🔔 通知件数を全テンプレートに渡す
    @app.context_processor
    def inject_unread_notifications():
        if "user" in session:
            user_id = session["user"]["docID"]
            try:
                docs = (
                    firestore_db.collection("notifications")
                    .where("user_id", "==", user_id)  # ← 安定して動作する書き方
                    .where("is_read", "==", False)
                    .stream()
                )
                count = sum(1 for _ in docs)
                return dict(unread_notifications_count=count)
            except Exception as e:
                print("通知取得中にエラー:", e)
        return dict(unread_notifications_count=0)
    
    
    return app

