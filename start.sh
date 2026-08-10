#!/bin/bash

export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$HOME/.local/lib/python3.10/site-packages:$PYTHONPATH"

# 平台如果注入了 PORT 就用平台的，否则 5000
export PORT="${PORT:-8080}"

echo "[sub-aggregator] HOME=$HOME PORT=$PORT" > /tmp/bot.log
echo "[sub-aggregator] PYTHONPATH=$PYTHONPATH" >> /tmp/bot.log

# 先验证 flask 能不能导入
python -u -c "import flask; print('[sub-aggregator] flask', flask.__version__)" >> /tmp/bot.log 2>&1

echo "[sub-aggregator] launching app.py ..." >> /tmp/bot.log

# 不要用 exec，不要用管道，让 python 做主进程
python -u app.py >> /tmp/bot.log 2>&1
