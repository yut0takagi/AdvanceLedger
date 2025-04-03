from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.forms import CreateGroupForm
from application.extensions import firestore_db, login_required
from utils import generate_id, get_user_doc_id_by_email
import json
import uuid

friend_bp = Blueprint("friend", __name__, url_prefix="/friend")


@friend_bp.route('/<user_id>', methods=['GET'])
@login_required
def add_friend(user_id):
    doc_ref = firestore_db.collection('groups').document(user_id)
    doc = doc_ref.get()
    return "友達追加！！"

@friend_bp.route("/friend/<user_id>/detail", methods=["GET", "POST"])
@login_required
def friend_detail(user_id):
    #^ ログイン状態の確認
    user = session.get('user')
    #^ friendsのリストを定義
    friends = []
    #^ debug
    print("debugFRIEND:",friends)
    groups=[{"name": "旅行グループ","docID":"1"}, {"name": "飲み会メンバー", "docID":"bbbb"}]
    return render_template("friend_detail.html", friends=friends, groups=groups)

