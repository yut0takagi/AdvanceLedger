from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.forms import LeaveGroupForm 
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
    form = LeaveGroupForm()
    doc = firestore_db.collection('users').document(user_id).get().to_dict()

    if doc is None:
        return redirect(url_for('auth.login'))

    # グループ情報取得
    groups = []
    for group_docID in doc.get("joining", []):
        group_ref = firestore_db.collection('groups').document(group_docID)
        group_doc = group_ref.get().to_dict()
        if group_doc:
            groups.append({
                "name": group_doc['groupname'],
                "docID": group_docID,
            })

    # 友達リスト取得 + 支払額と受取額を取得
    friends = []
    for friend_docID in doc.get("friends", []):
        user_ref = firestore_db.collection('users').document(friend_docID)
        friend_doc = user_ref.get().to_dict()
        if not friend_doc:
            continue

        # 初期値
        to_pay = 0
        to_receive = 0

        # liabilities の中から直接やり取り（groupID=None または "__direct__"）だけ見る
        liabilities_ref = firestore_db.collection("liabilities")
        for liab_doc in liabilities_ref.stream():
            liab = liab_doc.to_dict()
            if liab.get("groupID") not in [None, "__direct__"]:
                continue

            if liab.get("from_") == user_id and liab.get("to_") == friend_docID:
                to_pay += liab.get("amount", 0)
            elif liab.get("from_") == friend_docID and liab.get("to_") == user_id:
                to_receive += liab.get("amount", 0)

        friends.append({
            "name": friend_doc.get('username'),
            "user_id": friend_docID,
            "to_pay": to_pay,
            "to_receive": to_receive,
        })
    visible_friends = [
        f for f in friends if f.get("to_pay", 0) != 0 or f.get("to_receive", 0) != 0
    ]
    return render_template("dashboard.html", friends=friends, groups=groups, user_id=user_id, leave_form=form,
                           visible_friends = [
                                f for f in friends if f.get("to_pay", 0) != 0 or f.get("to_receive", 0) != 0
                            ]
                           )



@dashboard_bp.route('/<user_id>/settle/<friend_id>', methods=['POST'])
@login_required
def settle_with_friend(user_id, friend_id):
    """ 1:1のやり取り（liabilities）を精算済みにする(削除する) """
    liabilities_ref = firestore_db.collection("liabilities")
    docs = liabilities_ref.stream()

    deleted_count = 0
    for doc in docs:
        data = doc.to_dict()
        if data.get("groupID") in [None, "__direct__"]:
            # 双方向に対象が含まれる場合は削除
            if (data.get("from_") == user_id and data.get("to_") == friend_id) or \
               (data.get("from_") == friend_id and data.get("to_") == user_id):
                doc.reference.delete()
                deleted_count += 1

    flash(f"{deleted_count} 件のやり取りを精算済みにしました", "success")
    return redirect(url_for('dashboard.dashboard', user_id=user_id))