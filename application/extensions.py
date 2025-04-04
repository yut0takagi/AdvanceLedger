# application/extensions.py

import firebase_admin
from firebase_admin import credentials, firestore, auth
from functools import wraps

from flask import session, redirect, url_for, request

cred = credentials.Certificate("application/config/serviceAccountKey.json")
firebase_admin_app = firebase_admin.initialize_app(cred)

# Firestore client
firestore_db = firestore.client()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        id_token = session.get('user', {}).get('idToken')
        if not id_token:
            return redirect(url_for('auth.login'))
        try:
            # IDトークンの検証
            decoded_token = auth.verify_id_token(id_token)
            request.user = decoded_token
        except Exception as e:
            print("Token verification failed:", e)
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

