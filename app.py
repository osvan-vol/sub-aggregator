import base64
import json
import os
import random
import string
import requests
from flask import Flask, request, Response, render_template_string, abort

app = Flask(__name__)
DB_FILE = "short_urls.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存失败: {e}")

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# 🤍 极简清爽风格 UI（白雪主题）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>订阅聚合器</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: #f6f8fa; color: #24292e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; padding: 40px 20px; }
        .wrapper { max-width: 650px; margin: 0 auto; background: #ffffff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
        h2 { font-size: 20px; font-weight: 600; margin-bottom: 8px; color: #000000; }
        p { font-size: 13px; color: #586069; margin-bottom: 24px; }
        label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
        textarea { w_idth: 100%; width: 100%; background-color: #fafbfc; border: 1px solid #e1e4e8; border-radius: 6px; padding: 12px; font-family: monospace; font-size: 13px; resize: vertical; min-height: 160px; margin-bottom: 20px; outline: none; }
        textarea:focus { background-color: #ffffff; border-color: #0366d6; box-shadow: 0 0 0 3px rgba(3,102,214,0.3); }
        button { background-color: #2ea44f; color: #ffffff; border: 1px solid rgba(27,31,35,0.15); border-radius: 6px; padding: 10px 20px; font-size: 14px; font-weight: 500; cursor: pointer; width: 100%; transition: background-color 0.1s; }
        button:hover { background-color: #2c974b; }
        .result-zone { display: none; margin-top: 28px; border-top: 1px solid #e1e4e8; padding-top: 24px; }
        .result-title { font-size: 14px; font-weight: 600; color: #28a745; margin-bottom: 10px; }
        .output-group { display: flex; gap: 8px; }
        .output-url { flex: 1; background: #f6f8fa; border: 1px solid #e1e4e8; padding: 8px 12px; font-size: 13px; font-family: monospace; border-radius: 6px; color: #0366d6; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .btn-copy { background: #fafbfc; color: #24292e; border: 1px solid #e1e4e8; width: auto; padding: 0 16px; font-size: 13px; }
        .btn-copy:hover { background: #f3f4f6; }
    </style>
</head>
<body>
    <div class="wrapper">
        <h2>订阅 & 节点聚合器</h2>
        <p>输入你的订阅链接或明文节点（一行一个），自动清洗重复项并生成精简短链接。</p>
        
        <form id="subForm">
            <label for="urlsInput">节点数据 / 订阅 URL</label>
            <textarea id="urlsInput" placeholder="https://example.com/sub&#10;vless://xxxxxxx&#10;vmess://xxxxxxx"></textarea>
            <button type="button" id="genBtn">生成聚合短链接</button>
        </form>

        <div id="resultZone" class="result-zone">
            <div class="result-title">✓ 聚合短链接已生成</div>
            <div class="output-group">
                <input type="text" id="outputLink" class="output-url" readonly>
                <button type="button" class="btn-copy" id="copyBtn">复制</button>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('genBtn').addEventListener('click', async function() {
            const rawInput = document.getElementById('urlsInput').value.trim();
            if (!rawInput) { return; }

            const lines = rawInput.split('\\n').map(line => line.trim()).filter(line => line !== "");
            
            try {
                const response = await fetch('/create_short', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ urls: lines })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('outputLink').value = data.short_url;
                    document.getElementById('resultZone').style.display = 'block';
                }
            } catch (err) {
                alert('网络异常');
            }
        });

        document.getElementById('copyBtn').addEventListener('click', function() {
            const linkInput = document.getElementById('outputLink');
            linkInput.select();
            document.execCommand('copy');
            alert('已复制');
        });
    </script>
</body>
</html>
"""

def decode_base64(data):
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(data).decode('utf-8')
    except Exception:
        return ""

def fetch_and_aggregate(urls):
    all_nodes = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for item in urls:
        item = item.strip()
        if not item:
            continue
        
        if item.startswith('http://') or item.startswith('https://'):
            try:
                response = requests.get(item, headers=headers, timeout=10)
                if response.status_code == 200:
                    raw_content = response.text.strip()
                    decoded_content = decode_base64(raw_content)
                    nodes = decoded_content.splitlines() if decoded_content else raw_content.splitlines()
                    for node in nodes:
                        node = node.strip()
                        if node and ('://' in node):
                            all_nodes.add(node)
            except Exception:
                continue
        elif '://' in item:
            all_nodes.add(item)

    combined_nodes = "\n".join(all_nodes)
    return base64.b64encode(combined_nodes.encode('utf-8')).decode('utf-8')

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/create_short', methods=['POST'])
def create_short():
    data = request.json
    if not data or 'urls' not in data:
        return {"error": "Invalid data"}, 400
    
    urls_list = data['urls']
    db = load_db()
    
    urls_key = ",".join(urls_list)
    for code, stored_urls in db.items():
        if stored_urls == urls_key:
            return {"short_url": f"{request.host_url}s/{code}"}
    
    while True:
        code = generate_short_code()
        if code not in db:
            break
            
    db[code] = urls_key
    save_db(db)
    
    return {"short_url": f"{request.host_url}s/{code}"}

@app.route('/s/<code>', methods=['GET'])
def redirect_short(code):
    db = load_db()
    if code not in db:
        abort(404)
        
    original_urls = db[code].split(',')
    result = fetch_and_aggregate(original_urls)
    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
