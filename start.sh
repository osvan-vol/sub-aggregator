#!/bin/bash
set -e

# 把用户安装的包加入路径
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$HOME/.local/lib/python3.10/site-packages:$PYTHONPATH"

PORT="${PORT:-5000}"
echo "[sub-aggregator] starting on 0.0.0.0:${PORT}" | tee /tmp/bot.log

# 前台运行，日志同时写入平台在读的文件
exec python -u app.py 2>&1 | tee -a /tmp/bot.log
