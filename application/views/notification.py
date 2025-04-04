from flask import Blueprint, render_template, session, redirect, url_for, flash
from application.extensions import firestore_db
from datetime import datetime

notification_bp = Blueprint("notification", __name__, url_prefix="/notification")

@notification_bp.route("/view")
def view():
    user = session.get("user")
    if not user:
        flash("ログインしてください", "warning")
        return redirect(url_for("auth.login"))

    user_id = user["docID"]
    notifications_ref = firestore_db.collection("notifications")\
        .where("user_id", "==", user_id)\
        .order_by("created_at", direction="DESCENDING")

    docs = notifications_ref.stream()
    notifications = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = data.get("created_at").strftime("%Y-%m-%d %H:%M") if data.get("created_at") else "不明"
        notifications.append(data)

        # 🔔 未読なら既読にする
        if not data.get("is_read", False):
            doc.reference.update({"is_read": True})

    return render_template("notification_view.html", notifications=notifications)