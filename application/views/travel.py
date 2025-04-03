from flask import Blueprint, request, render_template, redirect, url_for
from application.models import Trip, Member, db
from utils import generate_id
import uuid
from firebase_admin import storage

travel_bp = Blueprint("travel", __name__, url_prefix="/travel")

@travel_bp.route("/group/create", methods=["GET", "POST"])
def create_group():
    if request.method == "POST":
        title = request.form.get("trip_title")
        members = [m for m in request.form.getlist("members") if m.strip()]
        trip_id = generate_id(length=10, table=Trip)  # Trip ID生成
        # Trip保存
        trip = Trip(trip_id=trip_id, title=title)
        db.session.add(trip)
        db.session.flush()  # trip_idを参照する前にflush
        # メンバー保存
        for name in members:
            db.session.add(Member(name=name.strip(), trip_id=trip_id))
        db.session.commit()

        # 共有用URLにリダイレクト
        return redirect(url_for('trip_room', trip_id=trip_id))

    return render_template("group_create.html")

@travel_bp.route("/trip/<trip_id>")
def trip_room(trip_id):
    trip = Trip.query.filter_by(trip_id=trip_id).first_or_404()
    members = Member.query.filter_by(trip_id=trip_id).all()
    return render_template("trip_room.html", trip=trip, members=members)

@travel_bp.route("/upload_receipt", methods=["POST"])
def upload_receipt():
    file = request.files['receipt']
    filename = f"receipts/{uuid.uuid4()}.jpg"
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_file(file, content_type=file.content_type)
    blob.make_public()  # 必要に応じて公開設定

    file_url = blob.public_url
    # DBに保存するなど
    return {"url": file_url}
