from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.forms import add_group_form_in_dashboard, add_friend_form_in_dashboard
from application.extensions import firestore_db, login_required
from utils import generate_id
import json

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route('/<user_id>', methods=['GET', 'POST'])
@login_required
def dashboard(user_id):
    #^ ログインしているユーザーのみアクセス可能とする
    """
    * dashboardページ
    [リダイレクト関連]
        - groupページ(group/group_id)
        - group作成ページ(group/new)
        - friendページ(friend/user_id)
        - friend作成ページ(friend/new)
    [GET]
        - グループ情報を取得
        - 友達情報を取得
    """
    #^ ログイン状態の確認
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    else:
        doc_ref = firestore_db.collection('users').document(user_id)
        doc = doc_ref.get().to_dict()
        
        #^ friendsのリストを定義
        friends = []
        if doc is None:
            return redirect(url_for('auth.login'))
        else:
            for friend_docID in doc["friends"]:
                users_ref = firestore_db.collection('users').document(friend_docID)
                friend_doc = users_ref.get().to_dict()
                friends.append(
                    {
                        "name": friend_doc['username'],
                        "user_id": friend_docID,
                    }
                )
        #^ debug
        print("debugFRIEND:",friends)
        groups=[{"name": "旅行グループ","docID":"1"}, {"name": "飲み会メンバー", "docID":"bbbb"}]
        return render_template("dashboard.html", friends=friends, groups=groups)


