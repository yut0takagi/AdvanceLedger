from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.forms import LoginForm, SignupForm
from application.models import User, db
from application import firebase_auth
from utils import generate_id
#^ auth/ 
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    ログイン認証時の処理
    - 関連Class
    ```Python
    class Users(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), nullable=False)
        email = db.Column(db.String(100), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ```
    """
    form = LoginForm()
    if request.method == 'POST':
        """ログイフォームを送信された時(POSTリクエスト)の処理"""
        print("POSTリクエスト")
        user = User()
        # データの格納
        try:
            email = request.form['email']
            password = request.form['password']
            """firebaseへの認証を送信"""
            user = firebase_auth.sign_in_with_email_and_password(email, password)
            #~ デバック print(user)
            existing_user = User.query.filter_by(email=email).first()
            
            session['user'] = {
                'email': user['email'],
                'idToken': user['idToken'],
                'refreshToken': user['refreshToken'],
                'user_type': existing_user.user_type
            }
            print(existing_user.user_type)
            print("ログイン成功しました！")
            return redirect(url_for(f"home.home"))
        except Exception as e:
            error_message = str(e)
            flash(f"ログインに失敗しました: {error_message}", "danger")
            print(f"ログインに失敗しました: {error_message}")
            return redirect(url_for('auth.login'))
    else:
        """GETリクエストの場合の処理"""
        return render_template('login.html')

#^ 新規登録画面(auth/signup)
#~ 完成版のため、変更時注意
"""
新規ユーザ登録画面(auth/signup)の処理
[GET]:
    新規登録画面を表示
[POST]:
    新規登録要件をFirebaseへ送信し、確認後ログイン画面(auth/login)へ遷移する。
"""
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        """新規登録フォームを送信された時(POSTリクエスト)の処理"""
        email = request.form['email']
        password = request.form['password']
        print("debug point:",email,password)
        try:
            firebase_auth.create_user_with_email_and_password(email, password)
            name = request.form['name']
            created_at = datetime.now()
            print("debug point111")
            user = User(id=generate_id(length=10, table=User), username=name, email=email, created_at=created_at)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        except:
            #TODO: Error画面の作成
            return 'ユーザー登録に失敗しました'
    #TODO: make_dictの引数については後日再確認
    """utils.make_dictを参照"""
    return render_template('signup.html')


@auth_bp.route("/logout")
def logout():
    session.pop("logged_in", None)
    session["logged_in"] = False
    return redirect(url_for("home.home"))