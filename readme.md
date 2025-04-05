# 💸 ペイとも - Flaskで作る「立て替え管理」アプリケーション

**ペイとも**は、グループ旅行や日常の割り勝で「誰がいくら払って、誰にいくら請求すべきか？」を分かりやすく整理・共有するアプリです。  
学習用にも最適な、Flask + Firebase をベースにしたWebアプリケーションです。
以下のサイトより、ご利用いただければと思います。

```Python
https://paytomo.onrender.com/home/
```

---

## 📌 主な機能

- ✅ Firebase Authによるログイン/サインアップ
- 🧑‍🤝‍🧑 グループ作成・参加・ニックネーム選択
- 💸 立て替え情報の登録・最適化表示
- 📬 フォロー機能・フレンド検索（リアルタイム）
- 🔔 通知（精算済み処理など）
- 📱 スマホ対応のUI（TailwindCSS）
- 🛰 エラーハンドリング・CSRF対応・ログ記録

---

## 🛠️ 使用技術

| 分類        | 技術 |
|-------------|------|
| フレームワーク | Flask 3.x |
| UI/CSS      | Tailwind CSS |
| データベース | Firebase Firestore |
| 認証        | Firebase Authentication |
| デプロイ    | Render⢸️Gunicorn + WSGI）|
| その他      | Jinja2, WTForms, CSRF, Python logging, Pyrebase4 |

---

## 📂 ディレクトリ構成

```Python

.
├── Pipfile
├── Pipfile.lock
├── application
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-313.pyc
│   │   ├── forms.cpython-313.pyc
│   │   └── models.cpython-313.pyc
│   ├── config
│   │   ├── __pycache__
│   │   │   └── config.cpython-313.pyc
│   │   ├── config.py
│   │   ├── firebaseConfig.json
│   │   └── serviceAccountKey.json
│   ├── extensions.py
│   ├── forms.py
│   ├── templates
│   │   ├── choose_nickname.html
│   │   ├── create_group.html
│   │   ├── dashboard.html
│   │   ├── errors
│   │   │   ├── 401.html
│   │   │   ├── 403.html
│   │   │   ├── 404.html
│   │   │   ├── 405.html
│   │   │   └── 500.html
│   │   ├── friend_detail.html
│   │   ├── friend_search.html
│   │   ├── group.html
│   │   ├── home.html
│   │   ├── layout
│   │   │   └── layout1.html
│   │   ├── login.html
│   │   ├── make-project.html
│   │   ├── notification_view.html
│   │   └── signup.html
│   └── views
│       ├── __init__.py
│       ├── __pycache__
│       │   ├── __init__.cpython-313.pyc
│       │   ├── auth.cpython-313.pyc
│       │   ├── daily.cpython-313.pyc
│       │   ├── home.cpython-313.pyc
│       │   └── travel.cpython-313.pyc
│       ├── auth.py
│       ├── daily.py
│       ├── dashboard.py
│       ├── friend.py
│       ├── group.py
│       ├── home.py
│       └── notification.py
├── db.ipynb
├── error.log
├── image.png
├── readme.md
├── requirements.txt
├── utils
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-313.pyc
│   │   └── id.cpython-313.pyc
│   ├── id.py
│   └── manage_firestore.py
└── wsgi.py

```

---

## 🚀 ローカル実行手順

```bash
# 仮想環境を作成
$ pipenv install
$ pipenv shell

# Firebase設定ファイルを配置
- application/config/firebaseConfig.json
- application/config/serviceAccountKey.json

# 起動
$ flask run
# or
$ python wsgi.py
```

---

## 🌍 Render でのデプロイ

1. Render で GitHub リポジトリを連携
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `gunicorn wsgi:app`
4. 環境変数に以下を登録:

| Key | Value |
|-----|-------|
| `FIREBASE_CONFIG_JSON` | `firebaseConfig.json`の中身をjsonテキストにして入力 |
| `SECRET_KEY` | Flaskアプリのシークレット |
| `FLASK_DEBUG` | `False` (本番環境) |


---

## 🔐 セキュリティとベストプラクティス

- `.env` を使った設定切り替え
- CSRF対策として Flask-WTF を利用
- Python logging + `error.log`による日記
- Firestore のルール設定 (別途必要)

---

## 🎓 Flask学習ポイント

- FlaskのBlueprint構成
- Firebase との連携 (Firestore / Auth)
- WTForms + CSRF の実装
- TailwindCSS を使ったレスポンシブルUI
- Jinja2 のテンプレート統合
- Renderでのデプロイ手順

---

## 📄 ライセンス

MIT License  
学習や内部サービスのプロトタイプにも自由にご利用ください

---

## 📷 広告PR

![pr](https://github.com/yut0takagi/AdvanceLedger/blob/develop/image.png)

---

## 🙌 作者

- 作成・運用：[@yut0takagi](https://github.com/yut0takagi)  
- 設計やPRも歓迎です！