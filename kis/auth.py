import json
import os
from datetime import datetime, timedelta

import requests

from kis_config import KIS_APP_KEY, KIS_APP_SECRET, KIS_BASE_URL


TOKEN_PATH = "kis/token.json"


def validate_config():
    required_values = {
        "KIS_APP_KEY": KIS_APP_KEY,
        "KIS_APP_SECRET": KIS_APP_SECRET,
        "KIS_BASE_URL": KIS_BASE_URL,
    }

    missing_keys = [
        key
        for key, value in required_values.items()
        if not value
    ]

    if missing_keys:
        missing_text = ", ".join(missing_keys)

        raise ValueError(
            f"필수 환경변수가 없습니다: {missing_text}\n"
            ".env 파일을 확인하세요."
        )


def load_saved_token():
    if not os.path.exists(TOKEN_PATH):
        return None

    try:
        with open(TOKEN_PATH, "r", encoding="utf-8") as file:
            token_data = json.load(file)

        access_token = token_data.get("access_token")
        expires_at_text = token_data.get("expires_at")

        if not access_token or not expires_at_text:
            return None

        expires_at = datetime.fromisoformat(expires_at_text)

        if datetime.now() < expires_at:
            return access_token

    except (
        json.JSONDecodeError,
        ValueError,
        KeyError,
        TypeError,
    ):
        return None

    return None


def save_token(access_token):
    os.makedirs(
        os.path.dirname(TOKEN_PATH),
        exist_ok=True,
    )

    token_data = {
        "access_token": access_token,
        "expires_at": (
            datetime.now() + timedelta(hours=23)
        ).isoformat(),
    }

    with open(
        TOKEN_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            token_data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def get_access_token():
    validate_config()

    saved_token = load_saved_token()

    if saved_token:
        return saved_token

    url = f"{KIS_BASE_URL}/oauth2/tokenP"

    headers = {
        "content-type": "application/json",
    }

    body = {
        "grant_type": "client_credentials",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=15,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        response_text = ""

        if getattr(error, "response", None) is not None:
            response_text = error.response.text

        raise RuntimeError(
            "KIS 토큰 발급 실패\n"
            f"오류: {error}\n"
            f"응답: {response_text}"
        ) from error

    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        raise RuntimeError(
            f"KIS 응답에 access_token이 없습니다: {data}"
        )

    save_token(access_token)

    return access_token


if __name__ == "__main__":
    token = get_access_token()

    print("토큰 발급 성공")
    print(token[:20] + "...")