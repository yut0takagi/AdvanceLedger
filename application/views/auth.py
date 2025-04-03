from flask import Flask, redirect, url_for, session, request, Blueprint, flash, render_template
import pyrebase
from datetime import datetime
from application.forms import LoginForm, SignupForm
from application.extensions import firestore_db
from utils import generate_id, get_user_doc_id_by_email
import json

with open('application/config/firebaseConfig.json') as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config)
firebase_auth = firebase.auth()


#^ auth/ 
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

#^ ログイン画面(auth/login)
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
        try:
            email = request.form['email']
            password = request.form['password']
            """firebaseへの認証を送信"""
            user = firebase_auth.sign_in_with_email_and_password(email, password)
            #~ デバック print(user)
            docID = get_user_doc_id_by_email(email)
            session['user'] = {
                'docID': docID,
                'email': user['email'],
                'idToken': user['idToken'],
                'refreshToken': user['refreshToken'],
            }
            print("ログイン成功しました！")
            return redirect(url_for(f"dashboard.dashboard", user_id=docID))
        except Exception as e:
            error_message = str(e)
            print(f"ログインに失敗しました: {error_message}")
            
            return redirect(url_for('auth.login'))
    else:
        """GETリクエストの場合の処理"""
        return render_template('login.html', form=form)

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
            created_at = datetime.now()
            print("debug point111")
            user=  firestore_db.collection("users").add({
                        "username": request.form['name'],
                        "email": email,
                        "friends":[], #~ 友達のdocID
                        "joining":[], #~ 所属GroupのdocID
                        "created_at": created_at,
                    })
            return redirect(url_for('auth.login'))
        except Exception as e:
            #TODO: Error画面の作成
            error_message = str(e)
            print(f"ユーザー登録に失敗しました: {error_message}")
            return 'ユーザー登録に失敗しました'
    """utils.make_dictを参照"""
    return render_template('signup.html', form=form)

#^ ログアウト処理
@auth_bp.route("/logout")
def logout():
    session.pop("logged_in", None)
    session["logged_in"] = False
    return redirect(url_for("home.home"))