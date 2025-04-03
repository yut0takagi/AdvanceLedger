from firebase_admin import firestore
from application.extensions import firestore_db

def get_user_doc_id_by_email(email):
    users_ref = firestore_db.collection('users')
    query = users_ref.where('email', '==', email).limit(1).stream()
    for doc in query:
        return doc.id  # ドキュメントIDを返す
    return None  # 該当なし