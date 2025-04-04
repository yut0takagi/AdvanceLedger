# application/extensions.py
#^--------------------------------------------------
#^ 完成したコードのため、注意
#^--------------------------------------------------
import firebase_admin
import traceback
import json
import os
from firebase_admin import credentials, firestore, auth, initialize_app
from functools import wraps
from ortools.sat.python import cp_model
from typing import List, Tuple

from flask import session, redirect, url_for, request


service_account = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
cred = credentials.Certificate(service_account)
firebase_admin.initialize_app(cred)

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


def or_tools_to_minimum_paying(
        people: List[str],
        transactions: List[Tuple[str, str, int]]
    ) -> List[Tuple[str, str, int]]:
    """
    Google OR-Tools を用いて、支払い関係を最小支払い回数で整理する。

    Parameters:
        people (List[str]): 関与するユーザーIDのリスト
        transactions (List[Tuple[str, str, int]]): 各支払い (支払者, 受取者, 金額)

    Returns:
        List[Tuple[str, str, int]]: 最小支払い構成 (支払者, 受取者, 金額)
                                    解が存在しない場合は空リスト
    """
    idx = {p: i for i, p in enumerate(people)}
    n = len(people)
    
    # 各人のネット収支を計算
    balance = [0] * n
    for receiver, payer, amount in transactions:
        balance[idx[payer]] -= amount
        balance[idx[receiver]] += amount

    model = cp_model.CpModel()
    max_amount = int(sum(abs(b) for b in balance))

    x = {}
    used = {}
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            x[i, j] = model.NewIntVar(0, max_amount, f'x_{i}_{j}')
            used[i, j] = model.NewBoolVar(f'u_{i}_{j}')
            model.Add(x[i, j] <= max_amount * used[i, j])

    for i in range(n):
        outflow = sum(x[i, j] for j in range(n) if i != j)
        inflow = sum(x[j, i] for j in range(n) if i != j)
        model.Add(inflow - outflow == balance[i])

    model.Minimize(sum(used[i, j] for i in range(n) for j in range(n) if i != j))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    result = []
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for i in range(n):
            for j in range(n):
                if i != j:
                    amount = solver.Value(x[i, j])
                    if amount > 0:
                        result.append({"from_":people[i], "to_":people[j],"amount": amount})
    return result

def convert_raw_to_transactions(raw_payments):
    """
    
    """
    transactions = []
    for payment in raw_payments:
        payer = payment["payer"]
        payees = payment["payees"]
        total_amount = payment["amount"]
        num_payees = len(payees)
        if num_payees == 0:
            continue  # 受取人がいない場合はスキップ
        share = int(total_amount) // int(num_payees)  # 割り切れなかった分は捨てる（必要に応じて調整）

        for payee in payees:
            if payer==payee:
                continue
            transactions.append((payer, payee, share))
    return transactions

def log_error_to_firestore_global(e):
    user = session.get("user", {})
    error_data = {
        "user_id": user.get("docID", "anonymous"),
        "path": request.path,
        "method": request.method,
        "error": str(e),
        "stacktrace": traceback.format_exc(),
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    try:
        firestore_db.collection("errors").add(error_data)
    except Exception as log_error:
        print("🔥 Firestoreエラー保存に失敗:", log_error)
    return "予期せぬエラーが発生しました", 500