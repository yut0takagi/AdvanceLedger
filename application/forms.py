from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField, SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange

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


class CreateGroupForm(FlaskForm):
    group_name = StringField(
        'グループ名',
        validators=[DataRequired(message="グループ名は必須です"), Length(max=50)]
    )
    
    member_names = TextAreaField(
        'メンバー名（1行に1人ずつ）',
        validators=[DataRequired(message="メンバー名を入力してください")]
    )
    
    submit = SubmitField('グループを作成')
    
class PaymentForm(FlaskForm):
    payer = SelectField("支払者", validators=[DataRequired()])
    amount = DecimalField("金額", validators=[DataRequired(), NumberRange(min=1)])
    memo = StringField("メモ")
    payees = SelectMultipleField(
        "支払い対象者",
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False),
        coerce=str  # user_idなど文字列で受け取る場合
    )