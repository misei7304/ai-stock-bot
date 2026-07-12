import os

from dotenv import load_dotenv

load_dotenv()

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")

KIS_ACCOUNT_NO = os.getenv("KIS_ACCOUNT_NO")
KIS_ACCOUNT_PRODUCT_CODE = os.getenv("KIS_ACCOUNT_PRODUCT_CODE")

KIS_BASE_URL = os.getenv("KIS_BASE_URL")