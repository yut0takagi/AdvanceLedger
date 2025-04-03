from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from application.extensions import firestore_db

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class SignupForm(FlaskForm):
    """
    username: ユーザ名
    email: メールアドレス
    password: パスワード
    confirm_password: パスワード確認
    submit: 登録ボタン
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        users_ref = firestore_db.collection("users")
        query = users_ref.where("email", "==", email.data)
        results = query.get()
        if len(results)>0:
            raise ValidationError('That email is already in use. Please choose a different one.')

class add_group_form_in_dashboard(FlaskForm):
    """
    group_name: 友達の名前
    submit: 追加ボタン
    """
    group_name = StringField('Group Name', validators=[DataRequired()])
    submit = SubmitField('Add Group')

class add_friend_form_in_dashboard(FlaskForm):
    """
    friend_name: 友達の名前
    submit: 追加ボタン
    """
    friend_email = StringField('Friend Email', validators=[DataRequired()])
    submit = SubmitField('Add Friend')

