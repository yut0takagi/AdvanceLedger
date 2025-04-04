# application/extensions.py

import firebase_admin
from firebase_admin import credentials, firestore, auth
from functools import wraps
from ortools.sat.python import cp_model
from typing import List, Tuple

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
    for payer, payee, amount in transactions:
        balance[idx[payer]] -= amount
        balance[idx[payee]] += amount

    model = cp_model.CpModel()
    max_amount = sum(abs(b) for b in balance)

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
                        result.append((people[i], people[j], amount))
    return result