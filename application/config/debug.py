import os
from pathlib import Path

DEBUG = True

# シークレットキーの設定
SECRET_KEY = os.urandom(24).hex()