from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from firebase_admin import firestore
from application.forms import CreateGroupForm, FollowForm, DirectPaymentForm
from application.extensions import firestore_db, login_required
from utils import generate_id, get_user_doc_id_by_email
from google.cloud.firestore_v1 import FieldFilter
import json
import uuid

friend_bp = Blueprint("friend", __name__, url_prefix="/friend")


#^ フレンド検索ページ
@friend_bp.route('/search', methods=['GET'])
@login_required
def search_friend_page():
    return render_template('friend_search.html')


#^ フレンド検索を高速実行させるためのAPI
@friend_bp.route('/search_api', methods=['GET'])
@login_required
def search_friend_api():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        users_ref = firestore_db.collection("users")
        docs = (
            users_ref
            .where(filter=FieldFilter("username", ">=", query))
            .where(filter=FieldFilter("username", "<=", query + "\uf8ff"))
            .limit(10)
            .stream()
        )
        for doc in docs:
            data = doc.to_dict()
            results.append({
                "id": doc.id,
                "username": data.get("username"),
                "email": data.get("email"),
            })

    return {"results": results}

#^ フレンド詳細ページ
@friend_bp.route('/detail/<user_id>')
@login_required
def friend_detail(user_id):
    current_user = session.get("user")
    if not current_user:
        flash("ログインしてください。", "error")
        return redirect(url_for("auth.login"))

    # 対象ユーザー情報を取得
    user_ref = firestore_db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        flash("ユーザーが見つかりませんでした。", "error")
        return redirect(url_for("friend.search_friend_page"))

    friend_data = user_doc.to_dict()
    friend_data["docID"] = user_doc.id

    # 支払い・受取予定を取得（例: liabilities コレクションから）
    liabilities_ref = firestore_db.collection("liabilities")
    to_pay = []
    to_receive = []

    for doc in liabilities_ref.stream():
        data = doc.to_dict()
        if data.get("from_") == current_user["docID"] and data.get("to_") == user_id:
            to_pay.append(data)
        elif data.get("from_") == user_id and data.get("to_") == current_user["docID"]:
            to_receive.append(data)

    # フォロー状態チェック
    current_user_doc = firestore_db.collection("users").document(current_user["docID"]).get()
    is_following = user_id in current_user_doc.to_dict().get("friends", [])

    follow_form = FollowForm()
    
    follow_form = FollowForm()
    direct_form = DirectPaymentForm()
    return render_template(
        "friend_detail.html",
        friend=friend_data,
        to_pay=to_pay,
        to_receive=to_receive,
        follow_form=follow_form,
        is_following=is_following,
        direct_form=direct_form,
    )

#^ フォローとフォロー解除を実施するAPI
@friend_bp.route('/toggle_follow/<user_id>', methods=['POST'])
@login_required
def toggle_follow(user_id):
    current_user = session.get("user")
    if not current_user:
        flash("ログインしてください。", "error")
        return redirect(url_for("auth.login"))

    current_user_id = current_user["docID"]
    # 自分と相手のユーザードキュメント参照
    user_ref = firestore_db.collection("users").document(current_user_id)
    target_ref = firestore_db.collection("users").document(user_id)

    user_doc = user_ref.get()
    target_doc = target_ref.get()

    if not user_doc.exists or not target_doc.exists:
        flash("ユーザー情報が見つかりません。", "error")
        return redirect(url_for("dashboard.dashboard", user_id=current_user_id))

    user_data = user_doc.to_dict()
    friends = user_data.get("friends", [])

    if user_id in friends:
        # フォロー解除（双方向から削除）
        user_ref.update({
            "friends": firestore.ArrayRemove([user_id])
        })
        target_ref.update({
            "friends": firestore.ArrayRemove([current_user_id])
        })
        flash("フォローを解除しました", "info")
    else:
        # フォロー追加（双方向に追加）
        user_ref.update({
            "friends": firestore.ArrayUnion([user_id])
        })
        target_ref.update({
            "friends": firestore.ArrayUnion([current_user_id])
        })
        flash("フォローしました", "success")

    return redirect(url_for("friend.friend_detail", user_id=user_id))

#^ 立て替え情報を追加するAPI
@friend_bp.route('/add_payment/<user_id>', methods=['POST'])
@login_required
def add_direct_payment(user_id):
    current_user = session.get("user")
    form = DirectPaymentForm()

    if not form.validate_on_submit():
        flash("入力内容に誤りがあります", "error")
        return redirect(url_for("friend.friend_detail", user_id=user_id))

    firestore_db.collection("liabilities").add({
        "from_": current_user["docID"],
        "to_": user_id,
        "amount": form.amount.data,
        "memo": form.memo.data,
        "groupID": "__direct__",
        "Created_by": current_user["docID"],
        "Created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    flash("やり取りを記録しました", "success")
    return redirect(url_for("friend.friend_detail", user_id=user_id))