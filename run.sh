#!/bin/bash

set -euo pipefail

PROJECT_DIR="$(
    cd "$(
        dirname "$0"
    )"
    pwd
)"

cd "$PROJECT_DIR"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Python 가상환경을 찾을 수 없습니다."
    echo "확인 경로:"
    echo "  $PROJECT_DIR/venv/bin/activate"
    echo "  $PROJECT_DIR/.venv/bin/activate"
    exit 1
fi

echo "============================================================"
echo "AI 주식 자동매매 파이프라인 시작"
echo "프로젝트 경로: $PROJECT_DIR"
echo "시작 시각: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

echo
echo "[1/3] ML 자동 재학습"
python -m ml.auto_retrain

echo
echo "[2/3] AI 종목 스캔"
python -m ml.scan_stocks_model

echo
echo "[3/3] 메인 자동매매 실행"
python main.py

echo
echo "============================================================"
echo "AI 주식 자동매매 파이프라인 완료"
echo "완료 시각: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
