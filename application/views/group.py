from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.forms import CreateGroupForm, PaymentForm, DeletePaymentForm, ChooseNicknameForm
from application.extensions import (firestore_db, login_required, or_tools_to_minimum_paying,
                                    convert_raw_to_transactions)
from utils import generate_id, get_user_doc_id_by_email
from google.cloud import firestore
import json
import uuid

group_bp = Blueprint("group", __name__, url_prefix="/group")

@group_bp.route('/<group_id>', methods=['GET', 'POST'])
@login_required
def group(group_id):
    form = PaymentForm()
    Form=DeletePaymentForm()
    # グループ情報の取得
    doc = firestore_db.collection('groups').document(group_id).get()
    if not doc.exists:
        flash("指定されたグループが存在しません。", "error")
        return redirect(url_for('auth.login'))
    group = doc.to_dict()
    #^ メンバー情報の取得----------------------------------------------------------------------
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
    #^ nickname_listの定義------------------------------------------------------------------------
        nickname_list = [member["nickname"] for member in members]
    except Exception as e:#^ エラー処理
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
    transactions=convert_raw_to_transactions(get_raw_payments_from_group(group_id=group_id))
    optimized_transactions=or_tools_to_minimum_paying(people=nickname_list,transactions=transactions)
    print("DEBUG: transactions:", transactions)
    print("DEBUG: optimized_transactions:", optimized_transactions)
    return render_template(
        "group.html",
        DeletePaymentForm_=Form,
        payment_form=form,
        group={
            "docID": group_id,
            "groupname": group.get("groupname", "未設定"),
            "created_at": group.get("created_at", "不明")
        },
        members=members,
        raw_payments=get_raw_payments_from_group(group_id=group_id),
        optimized_transactions=optimized_transactions
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
        print("member_names:", member_names)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self_name = request.form.get("self_name")
        group_data = {
            "created_at": created_at,
            "groupname": group_name,
            "created_by": user["docID"]
        }
        doc_ref = firestore_db.collection("groups").add(group_data)
        docID = doc_ref[1].id

        for name in member_names:
            if name == self_name:
                user_id = user["docID"]
            else:
                user_id = None
            user_data2group = {
                "docID": docID,
                "name": name,
                "user_id": user_id
            }
            firestore_db.collection("user2group").add(user_data2group)

        # ✅ 自分のusersドキュメントのjoiningにgroup_idを追加
        user_ref = firestore_db.collection("users").document(user["docID"])
        user_ref.update({
            "joining": firestore.ArrayUnion([docID])
        })

        flash(f"グループ「{group_name}」を作成しました！", "success")
        return redirect(url_for('group.group', group_id=docID))

    return render_template('create_group.html', form=form)

def get_raw_payments_from_group(group_id: str) -> list:
    """
    FirestoreのliabilitiesForGroupsから、指定したgroupIDに該当する支払い情報を
    raw_payments形式に変換して返す関数。

    Returns:
        List[Dict]: {
            "payer": str,
            "payees": List[str],
            "amount": int,
            "memo": str
        }
    """
    
    #^ オブジェクト定義
    raw_payments = []
    
    #^ groupID でフィルタリング
    docs = firestore_db.collection("liabilitiesForGroups").where("groupID", "==", group_id).stream()

    for doc in docs:
        data = doc.to_dict()
        payer = data.get("from_", "")
        payees = data.get("to_", [])
        amount = data.get("amount", 0)
        memo = data.get("memo", "")

        filtered_payees = [p for p in payees]
        
        form = DeletePaymentForm()
        form.doc_id.data = doc.id
        raw_payments.append({
            "payID": doc.id,
            "payer": payer,
            "payees": filtered_payees,
            "form": form,
            "amount": amount,
            "memo": memo
        })

    return raw_payments

@group_bp.route("/delete_payment/<group_id>", methods=["POST"])
def delete_payment(group_id):
    form = DeletePaymentForm()
    if form.validate_on_submit() and form.form_id.data == "delete_form":
        doc_id = form.doc_id.data
        print(doc_id)
        try:
            firestore_db.collection("liabilitiesForGroups").document(doc_id).delete()
            flash("削除に成功しました", "success")
            print("削除に成功しました")
        except Exception as e:
            flash(f"削除に失敗しました: {str(e)}", "error")
            print(f"削除に失敗しました: {str(e)}", "error")
    else:
        flash("不正な送信です", "error")
        print("不正な送信です", "error")
    print("FVoS:",form.validate_on_submit())
    print("form errors:", form.errors)
    print("request.form:", request.form)
    return redirect(url_for("group.group", group_id=group_id))

@group_bp.route("/leave_group/<group_id>", methods=["POST"])
def leave_group(group_id):
    user = session.get("user")  # または request.cookies / current_user など
    user_id = user["docID"] if user else None
    if not user_id:
        flash("ユーザー情報がありません", "error")
        return redirect(url_for("auth.login"))

    try:
        user_ref = firestore_db.collection("users").document(user_id)
        user_ref.update({
            "joining": firestore.ArrayRemove([group_id])
        })
        flash("グループから脱退しました", "success")
    except Exception as e:
        flash(f"脱退処理でエラーが発生しました: {e}", "error")

    return redirect(url_for("dashboard.dashboard", user_id=user_id))

@group_bp.route("/join/<group_id>")
def join_group(group_id):
    user = session.get("user")
    if not user:
        session["next_url"] = url_for("group.join_group", group_id=group_id)
        flash("ログインしてください。", "info")
        return redirect(url_for("auth.login"))

    # すでに所属していればグループページへ
    user2group_ref = firestore_db.collection("user2group")
    existing_query = user2group_ref.where("docID", "==", group_id).where("user_id", "==", user["docID"]).limit(1).stream()
    if any(existing_query):
        flash("すでにこのグループに参加しています", "info")
        return redirect(url_for("group.group", group_id=group_id))

    # 空き枠（user_id == None のすべて）を取得
    empty_slots_query = user2group_ref.where("docID", "==", group_id).where("user_id", "==", None).stream()
    empty_slots = [doc.to_dict() | {"doc_id": doc.id} for doc in empty_slots_query]

    if not empty_slots:
        flash("このグループには参加枠がありません", "error")
        return redirect(url_for("dashboard.dashboard", user_id=user["docID"]))

    # 空き枠を選択させる画面を表示
    form = ChooseNicknameForm()
    form.slot_doc_id.choices = [(slot["doc_id"], slot["name"]) for slot in empty_slots]

    return render_template("choose_nickname.html", group_id=group_id, form=form, empty_slots=empty_slots )

@group_bp.route("/group/confirm_join/<group_id>", methods=["POST"])
def confirm_join(group_id):
    user = session.get("user")
    if not user:
        flash("ログインしてください", "error")
        return redirect(url_for("auth.login"))

    slot_doc_id = request.form.get("slot_doc_id")
    if not slot_doc_id:
        flash("無効な操作です", "error")
        return redirect(url_for("group.join_group", group_id=group_id))

    slot_ref = firestore_db.collection("user2group").document(slot_doc_id)
    slot_doc = slot_ref.get()
    slot_data = slot_doc.to_dict()

    if not slot_doc.exists or slot_data.get("user_id") is not None:
        flash("このニックネームはすでに使用されています", "error")
        return redirect(url_for("group.join_group", group_id=group_id))

    # user_id を登録
    slot_ref.update({"user_id": user["docID"]})

    # ログイン中のユーザーIDと追加するグループID
    user_id = session["user"]["docID"]
    # ユーザードキュメント参照
    user_ref = firestore_db.collection("users").document(user_id)
    # joining フィールドに group_id を追加（重複しない）
    user_ref.update({
        "joining": firestore.ArrayUnion([group_id])
    })
    
    flash("グループに参加しました！", "success")
    return redirect(url_for("group.group", group_id=group_id))
