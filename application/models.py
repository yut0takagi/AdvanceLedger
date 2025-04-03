# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class User(db.Model):
    """
    id: ユーザーID
    username: ユーザー名
    email: メールアドレス
    created_at: 登録日時(db.Datetime)
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Trip(db.Model):
    trip_id = db.Column(db.String(20), nullable=False, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Member(db.Model):
    member_id = db.Column(db.String(20), nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    trip_id = db.Column(db.String(10), db.ForeignKey('trip.trip_id'), nullable=False)

class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(10), nullable=False)
    uploaded_by = db.Column(db.String(50), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class liabilities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(10), nullable=False)
    from_ = db.Column(db.Integer(),db.ForeignKey('Users.id'), nullable=False)
    to_ = db.Column(db.Integer(),db.ForeignKey('Users.id'), nullable=False)
    amount = db.Column(db.Integer(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)