from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.forms import add_group_form_in_dashboard, add_friend_form_in_dashboard
from application.extensions import firestore_db
from utils import generate_id
import json

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route('/', methods=['GET', "POST"])
def dashboard():
    if request.method == "POST":
        # Handle POST request
        print("POSTリクエスト")
        # Add your logic here for handling the POST request
    else:
        # Handle GET request
        friends = [
            {
                "name": "たろう",
                "user_id": "u12345",
                "email": "taro@example.com",
                "is_registered": True
            },
            {
                "name": "はなこ",
                "user_id": "u67890",
                "email": "hanako@example.com",
                "is_registered": False
            }
        ]
        groups=[{"name": "旅行グループ"}, {"name": "飲み会メンバー"}]

        return render_template("dashboard.html", friends=friends, groups=groups)
    

