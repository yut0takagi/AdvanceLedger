from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.forms import add_group_form_in_dashboard, add_friend_form_in_dashboard
from application.extensions import firestore_db, login_required
from utils import generate_id, get_user_doc_id_by_email
import json

group_bp = Blueprint("group", __name__, url_prefix="/group")


@group_bp.route('/<group_id>', methods=['GET'])
@login_required
def group(group_id):
    doc_ref = firestore_db.collection('groups').document(group_id)
    doc = doc_ref.get()
    if doc.exists:
        group = doc.to_dict()
    else:
        group = None  # or エラー処理など
    #^membersの定義
    if group is None:
        return redirect(url_for('auth.login'))
    member_ids= group['members']
    members = []
    for member_id in member_ids:
        try:
            member = firestore_db.collection('users').document(member_id).to_dict()
            members.append({
                "name": member['username'],
                "user_id": member_id,
                "email": member['email'],
                "is_registered": member[""]
            })
        except Exception as e:
            print(f"Error fetching member data: {e}")
            member=None

    return render_template(
            "group.html",
            group={
                "docID": group_id,
                "groupname": group['groupname'],
                "created_at": group["created_at"]
            },
            members=[
                {
                    "name": "たかぎ",
                    "user_id": "user_001",
                    "email": "takagi@example.com",
                    "is_registered": True
                },
            ],
            balances=[
                {
                    "name": "たかぎ",
                    "to_pay": 1000,
                    "to_receive": 0
                },
            ]
        )

@group_bp.route('/create', methods=['GET', 'POST'])
def create_group():
    if request.method == "POST":

        # 共有用URLにリダイレクト
        return redirect(url_for('trip_room', trip_id=trip_id))
    else:
        
        return render_template("group_create.html")
