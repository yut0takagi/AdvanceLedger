from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.extensions import firestore_db, login_required
from utils import generate_id
import json

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route('/<user_id>', methods=['GET'])
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
    doc = firestore_db.collection('users').document(user_id).get().to_dict()
    print("#DEBUG: doc: ", doc)

    if doc is None:
        return redirect(url_for('auth.login'))
    else:
        #^ groupsのリストを定義
        groups=[]
        for group_docID in doc["joining"]:
            groups_ref = firestore_db.collection('groups').document(group_docID)
            group_doc = groups_ref.get().to_dict()
            groups.append(
                {
                    "name": group_doc['groupname'],
                    "docID": group_docID,
                }
            )
        #^ friendsのリストを定義
        friends = []
        for friend_docID in doc["friends"]:
            users_ref = firestore_db.collection('users').document(friend_docID)
            friend_doc = users_ref.get().to_dict()
            friends.append(
                {
                    "name": friend_doc['username'],
                    "user_id": friend_docID,
                }
            )
        return render_template("dashboard.html", friends=friends, groups=groups, user_id=user_id)


