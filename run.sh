#!/bin/bash

cd /home/ubuntu/ai-stock-bot

source venv/bin/activate

python -m ml.build_dataset || exit 1
python -m ml.train_model || exit 1
python -m ml.scan_stocks_model || exit 1
python main.py || exit 1
