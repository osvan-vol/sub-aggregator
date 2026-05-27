import base64
import json
import os
import random
import string
import requests
from flask import Flask, request, Response, render_template_string, redirect, abort

app = Flask(__name__)

# 短链接映射数据保存路径（本地 JSON 文件）
DB_FILE = "short_urls.json"

def load_db():
    """读取短链接数据库"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(data):
    """保存短链接数据库"""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存短链接数据库失败: {e}")

def generate_short_code(length=6):
    """生成 6 位随机字母数字组合作为短链接后缀"""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# 🎨 升级后的前端界面（修复了短链接逻辑）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>高级节点订阅聚合 & 短网址生成器</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .container { max-width: 800px; margin-top: 50px; }
        .card { border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-radius: 12px; }
        .btn-primary { background-color: #4f46e5; border-color: #4f46e5; }
        .btn-primary:hover { background-color: #4338ca; border-color: #4338ca; }
        textarea { font-family: monospace; font-size: 14px; }
        .result-box { display: none; background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 15px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card p-4 p-md-5">
            <h2 class="text-center mb-4" style="color: #1e293b; font-weight: 700;">🌐 订阅聚合 & 短链接生成器</h2>
            <p class="text-muted text-center mb-4">粘贴你的原始订阅链接（一行一个），或直接粘贴 vless://, vmess:// 等节点，一键生成精简防封的短链接。</p>
            
            <form id="aggregatorForm">
                <div class="mb-4">
                    <label for="urlsInput" class="form-label fw-bold">输入数据（支持订阅 URL 或节点明文）：</label>
                    <textarea class="form-control" id="urlsInput" rows="8" placeholder="https://example.com/sub1&#10;https://example.com/sub2&#10;vless://xxxxxxx&#10;vmess://xxxxxxx"></textarea>
                </div>
                <div class="d-grid">
                    <button type="button" id="submitBtn" class="btn btn-primary btn-lg fw-bold">🚀 生成精简短链接</button>
                </div>
            </form>

            <div id="resultContainer" class="result-box">
                <h5 class="fw-bold text-success mb-3">🎉 您的专属订阅短链接：</h5>
                <div class="input-group mb-3">
                    <input type="text" id="generatedUrl" class="form-control" readonly>
                    <button class="btn btn-outline-secondary" type="button" id="copyBtn">复制短链接</button>
                </div>
                <small class="text-muted">提示：短链接已安全隐藏您的原始凭证。直接复制此短链接粘贴到代理软件（Clash, Shadowrocket 等）中即可。</small>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('submitBtn').addEventListener('click', async function() {
            const rawInput = document.getElementById('urlsInput').value.trim();
            if (!rawInput) {
                alert('请先输入订阅链接或节点信息！');
                return;
            }

            const lines = rawInput.split('\\n').map(line => line.trim()).filter(line => line !== "");
            
            // 请求后端生成短链接
            try {
                const response = await fetch('/create_short', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ urls: lines })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('generatedUrl').value = data.short_url;
                    document.getElementById('resultContainer').style.display = 'block';
                } else {
                    alert('后端生成短链接失败，请重试');
                }
            } catch (err) {
                alert('网络错误，无法连接到服务器');
            }
        });

        document.getElementById('copyBtn').addEventListener('click', function() {
            const copyText = document.getElementById('generatedUrl');
            copyText.select();
            navigator.clipboard.writeText(copyText.value);
            alert('短链接已成功复制！');
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
    """主页"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/create_short', methods=['POST'])
def create_short():
    """接收前端数据，生成短网址映射"""
    data = request.json
    if not data or 'urls' not in data:
        return {"error": "Invalid data"}, 400
    
    urls_list = data['urls']
    
    # 读取现有数据库
    db = load_db()
    
    # 检查这个配置组合是否已经生成过短链接，避免重复创建
    urls_key = ",".join(urls_list)
    for code, stored_urls in db.items():
        if stored_urls == urls_key:
            return {"short_url": f"{request.host_url}s/{code}"}
    
    # 生成独一无二的短代码
    while True:
        code = generate_short_code()
        if code not in db:
            break
            
    # 存入数据库并保存
    db[code] = urls_key
    save_db(db)
    
    return {"short_url": f"{request.host_url}s/{code}"}

@app.route('/s/<code>', methods=['GET'])
def redirect_short(code):
    """短链接核心解析路由：访问 /s/AbCd12 时触发"""
    db = load_db()
    if code not in db:
        abort(404)
        
    # 提取出原本长串的节点/链接列表
    original_urls = db[code].split(',')
    
    # 执行聚合逻辑
    result = fetch_and_aggregate(original_urls)
    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
