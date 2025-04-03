from flask import render_template, request, redirect, url_for, Blueprint

home_bp = Blueprint('home', __name__)

@home_bp.route('/', methods=['GET'])
def home():
    return render_template('home.html')