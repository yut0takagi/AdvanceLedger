# ペイとも - 立て替え管理アプリ

「ペイとも」は、友達やグループとの**立て替え支払いの管理と精算を簡単に行えるWebアプリケーション**です。  
個人間・グループ間でのやり取りをスムーズにし、支払いの見える化と最適化をサポートします。

---

## 🚀 特徴

- ✅ **ユーザー登録 / ログイン機能（Firebase Auth）**
- ✅ **グループ作成＆参加（招待リンクあり）**
- ✅ **立て替え記録の追加、リアルタイム集計**
- ✅ **支払い回数を最小化する最適化アルゴリズム（OR-Tools）**
- ✅ **1:1の直接やり取りにも対応**
- ✅ **友達検索・フォロー・精算済み機能**
- ✅ **スマホ・PC 両対応のUI（Tailwind CSS）**

---

## 🛠 技術スタック

| 項目         | 使用技術 |
|--------------|----------|
| フレームワーク | Flask (Python) |
| 認証         | Firebase Authentication |
| データベース | Firestore（NoSQL） |
| スタイリング | Tailwind CSS |
| 最適化       | Google OR-Tools |
| ログインセッション | Flask Session |
| デプロイ対応 | WSGI + Gunicorn など |

---

## 📦 インストール & 実行

### 1. 仮想環境の作成

```bash
python3 -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows