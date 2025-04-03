# application/extensions.py

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("application/config/serviceAccountKey.json")
firebase_admin_app = firebase_admin.initialize_app(cred)

# Firestore client
firestore_db = firestore.client()