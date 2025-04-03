from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.forms import CreateGroupForm, PaymentForm
from application.extensions import firestore_db, login_required
from utils import generate_id, get_user_doc_id_by_email
import json
import uuid

group_bp = Blueprint("group", __name__, url_prefix="/group")

@group_bp.route('/<group_id>', methods=['GET', 'POST'])
@login_required
def group(group_id):
    form = PaymentForm()

    # グループ情報の取得
    doc = firestore_db.collection('groups').document(group_id).get()
    if not doc.exists:
        flash("指定されたグループが存在しません。", "error")
        return redirect(url_for('auth.login'))

    group = doc.to_dict()

    # メンバー情報の取得
    members = []
    try:
        member_docs = firestore_db.collection('user2group').where('docID', '==', group_id).stream()
        for user_doc in member_docs:
            user_info = user_doc.to_dict()
            nickname = user_info.get('name', '未設定')
            user_id = user_info.get('user_id')

            if user_id:
                user_detail_doc = firestore_db.collection('users').document(user_id).get()
                if user_detail_doc.exists:
                    user_details = user_detail_doc.to_dict()
                    username = user_details.get('username', '未設定')
                    is_registered = True
                else:
                    username = "不明"
                    is_registered = False
            else:
                user_id = "----"
                username = "----"
                is_registered = False

            members.append({
                "user_id": user_id,
                "nickname": nickname,
                "username": username,
                "is_registered": is_registered
            })
    except Exception as e:
        print(f"[ERROR] メンバー取得エラー: {e}")
        flash("メンバー情報の取得に失敗しました。", "error")
        return redirect(url_for("auth.login"))

    # フォーム選択肢設定（POST処理前に必ず行う）
    form.payer.choices = [(m["nickname"], m["nickname"]) for m in members]
    form.payees.choices = [(m["nickname"], m["nickname"]) for m in members]

    # POST処理
    if form.validate_on_submit() and request.method == "POST":
        try:
            payer = form.payer.data
            payees = form.payees.data
            amount = form.amount.data
            memo = form.memo.data

            payment_data = {
                "groupID": group_id,
                "from_": payer,
                "to_": payees,
                "amount": int(amount),
                "memo": memo,
                "Created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Created_by": session["user"]["docID"]
            }

            firestore_db.collection('liabilitiesForGroups').add(payment_data)
            flash("支払いを追加しました！", "success")
            print("支払いを追加しました！")
        except Exception as e:
            print("[ERROR] 支払い登録エラー:", e)
            flash("支払いの登録に失敗しました。", "error")
        return redirect(url_for("group.group", group_id=group_id))

    # GET処理・テンプレート描画
    return render_template(
        "group.html",
        payment_form=form,
        group={
            "docID": group_id,
            "groupname": group.get("groupname", "未設定"),
            "created_at": group.get("created_at", "不明")
        },
        members=members,
        raw_payments=[
            {
                "payer": "たかぎ",
                "payees": ["やまだ", "すずき"],
                "amount": 3000,
                "memo": "夕食代"
            },
        ],
        optimized_transactions=[
            {
                "from": "やまだ",
                "to": "たかぎ",
                "amount": 1500
            },
            {
                "from": "すずき",
                "to": "たかぎ",
                "amount": 1500
            },
        ],
    )

@group_bp.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    
    if form.validate_on_submit() and request.method == 'POST':
        #^ 作成者のユーザIDを取得
        user = session.get('user')
        
        #^ フォームから抽出
        group_name = form.group_name.data
        member_names = request.form.getlist("member_names")
        member_names = [name.strip() for name in member_names if name.strip()]
        #~Debug
        print("member_names:",member_names)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        group_data = {
            "created_at": created_at,
            "groupname": group_name,
            "created_by":user["docID"]
        }
        doc_ref = firestore_db.collection("groups").add(group_data)
        docID = doc_ref[1].id
        for name in member_names:
            user_data2group = {
                "docID": docID,
                "name": name,
                "user_id": None
            }
            firestore_db.collection("user2group").add(user_data2group)
        
        flash(f"グループ「{group_name}」を作成しました！", "success")
        return redirect(url_for('group.group', group_id=docID))
    return render_template('create_group.html', form=form)