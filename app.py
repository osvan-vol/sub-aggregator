import base64
import json
import os
import random
import string
import requests
from flask import Flask, request, Response, render_template_string, redirect, abort

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

# ✨ 现代化炫酷深色流光主题前端 UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NextGen 订阅聚合控制台</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: rgba(22, 29, 49, 0.7);
            --accent-color: #6366f1;
            --accent-gradient: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        body {
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.15) 0px, transparent 50%);
            color: var(--text-main);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            min-height: 100vh;
        }
        .container { max-width: 850px; padding-top: 60px; padding-bottom: 60px; }
        .card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        .main-title {
            font-weight: 800;
            background: linear-gradient(to right, #ffffff, #93c5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }
        .form-control, .form-control:focus {
            background-color: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #ffffff;
            border-radius: 14px;
            padding: 14px;
            transition: all 0.2s ease;
        }
        .form-control:focus {
            border-color: #06b6d4;
            box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.2);
        }
        textarea.form-control { font-family: 'Fira Code', Consolas, monospace; font-size: 13px; }
        .btn-gradient {
            background: var(--accent-gradient);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 14px;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .btn-gradient:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
            color: white;
        }
        .btn-gradient:active { transform: translateY(0); }
        .result-box {
            display: none;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 16px;
            padding: 24px;
            margin-top: 30px;
            animation: fadeIn 0.4s ease-out forwards;
        }
        .format-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .format-title { font-size: 14px; font-weight: 600; color: #38bdf8; margin-bottom: 8px; }
        .copy-input-group { display: flex; gap: 8px; }
        .btn-copy {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-main);
            border-radius: 8px;
            padding: 6px 16px;
        }
        .btn-copy:hover { background: rgba(255, 255, 255, 0.15); color: #ffffff; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="card p-4 p-md-5">
            <div class="text-center mb-4">
                <div class="display-5 mb-2"><i class="bi bi-clouds-fill" style="background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"></i></div>
                <h2 class="main-title text-center">NextGen 订阅聚合控制台</h2>
                <p class="text-muted">安全、精简、全平台兼容的节点聚合与转换服务</p>
            </div>
            
            <form id="aggregatorForm">
                <div class="mb-4">
                    <label for="urlsInput" class="form-label fw-semibold"><i class="bi bi-box-seam me-2"></i>原始数据导入：</label>
                    <textarea class="form-control" id="urlsInput" rows="8" placeholder="https://example.com/sub1  (支持订阅URL，一行一个)&#10;vless://xxxxxxx            (支持明文节点，一行一个)&#10;vmess://xxxxxxx"></textarea>
                </div>
                <div class="d-grid">
                    <button type="button" id="submitBtn" class="btn btn-gradient btn-lg"><i class="bi bi-lightning-charge-fill me-2"></i>一键分析并生成短链接</button>
                </div>
            </form>

            <div id="resultContainer" class="result-box">
                <h5 class="fw-bold text-info mb-4"><i class="bi bi-check-circle-fill me-2"></i>专属订阅短链接已就绪：</h5>
                
                <div class="format-card">
                    <div class="format-title"><i class="bi bi-file-earmark-code me-2"></i>通用 Base64 订阅（适合 Shadowrocket / v2rayN）</div>
                    <div class="copy-input-group">
                        <input type="text" id="urlBase64" class="form-control form-control-sm text-muted" readonly>
                        <button class="btn btn-copy btn-sm" onclick="copyText('urlBase64')">复制</button>
                    </div>
                </div>

                <div class="format-card">
                    <div class="format-title"><i class="bi bi-shield-shaded me-2"></i>Clash 专属订阅配置（由通用后端提供托管转换）</div>
                    <div class="copy-input-group">
                        <input type="text" id="urlClash" class="form-control form-control-sm text-muted" readonly>
                        <button class="btn btn-copy btn-sm" onclick="copyText('urlClash')">复制</button>
                    </div>
                </div>

                <div class="format-card">
                    <div class="format-title"><i class="bi bi-box me-2"></i>Sing-Box 专属订阅配置</div>
                    <div class="copy-input-group">
                        <input type="text" id="urlSingbox" class="form-control form-control-sm text-muted" readonly>
                        <button class="btn btn-copy btn-sm" onclick="copyText('urlSingbox')">复制</button>
                    </div>
                </div>
                
                <div class="text-center mt-3">
                    <small class="text-muted"><i class="bi bi-info-circle me-1"></i>提示：链接已进行全隐私混淆防护，可直接在各客户端中直接更新拉取。</small>
                </div>
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
            
            try {
                const response = await fetch('/create_short', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ urls: lines })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const shortUrl = data.short_url;
                    
                    // 构造各大软件的专属一键转换链接
                    document.getElementById('urlBase64').value = shortUrl;
                    document.getElementById('urlClash').value = `https://url.v1.mk/sub?target=clash&url=${encodeURIComponent(shortUrl)}&insert=false`;
                    document.getElementById('urlSingbox').value = `https://url.v1.mk/sub?target=singbox&url=${encodeURIComponent(shortUrl)}&insert=false`;
                    
                    document.getElementById('resultContainer').style.display = 'block';
                    document.getElementById('resultContainer').scrollIntoView({ behavior: 'smooth' });
                } else {
                    alert('后端处理失败，请检查输入格式。');
                }
            } catch (err) {
                alert('网络异常，无法连接到云服务器。');
            }
        });

        function copyText(id) {
            const copyText = document.getElementById(id);
            copyText.select();
            navigator.clipboard.writeText(copyText.value);
            alert('复制成功！可以直接粘贴到软件中使用。');
        }
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
