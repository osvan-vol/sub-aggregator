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

# 🌟 重新设计的 Apple/GitHub Premium 极简高级质感 UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>聚合面板</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>
<body class="bg-[#f4f5f6] text-slate-800 antialiased min-h-screen flex items-center justify-center p-4">

    <div class="w-full max-w-xl bg-white rounded-2xl border border-slate-200/80 shadow-[0_10px_30px_-10px_rgba(0,0,0,0.05)] p-6 md:p-8 transition-all">
        <div class="mb-6">
            <h1 class="text-xl font-bold text-slate-900 flex items-center gap-2">
                <i class="bi bi-link-45deg text-blue-600 text-2xl"></i> 节点订阅聚合器
            </h1>
            <p class="text-xs text-slate-400 mt-1">输入多个订阅链接或明文节点，一行一个。自动清洗重复项，一键生成专属短链接。</p>
        </div>

        <form class="space-y-4">
            <div>
                <textarea id="urlsInput" rows="7" 
                    class="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs font-mono text-slate-600 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 outline-none transition-all resize-none placeholder:text-slate-300"
                    placeholder="https://example.com/sub&#10;vless://xxxxxxx&#10;vmess://xxxxxxx"></textarea>
            </div>
            
            <button type="button" id="genBtn" 
                class="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-xl py-3 text-sm font-medium transition-all shadow-sm flex items-center justify-center gap-2">
                <i class="bi bi-lightning-charge"></i> 生成聚合短链接
            </button>
        </form>

        <div id="resultZone" class="hidden mt-6 pt-6 border-t border-slate-100 space-y-4">
            <div class="text-xs font-semibold text-emerald-600 flex items-center gap-1">
                <i class="bi bi-check-circle-fill"></i> 聚合短链接已就绪
            </div>
            
            <div class="space-y-2">
                <div class="flex gap-2 bg-slate-100 p-1 rounded-lg text-xs font-medium text-slate-500">
                    <button class="flex-1 py-1.5 rounded-md bg-white text-slate-800 shadow-sm transition-all" onclick="switchTab('general')">通用格式</button>
                    <button class="flex-1 py-1.5 rounded-md hover:text-slate-800 transition-all" onclick="switchTab('clash')">Clash 参数</button>
                    <button class="flex-1 py-1.5 rounded-md hover:text-slate-800 transition-all" onclick="switchTab('singbox')">Sing-Box 参数</button>
                </div>

                <div class="relative flex items-center mt-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5">
                    <input type="text" id="outputLink" class="w-full bg-transparent text-xs font-mono text-blue-600 outline-none pr-16" readonly>
                    <button type="button" id="copyBtn" class="absolute right-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 text-[11px] font-medium px-2.5 py-1 rounded-md shadow-sm transition-all">
                        复制
                    </button>
                </div>
            </div>
            <p class="text-[11px] text-slate-400 text-center"><i class="bi bi-info-circle"></i> 提示：复制对应格式的链接，直接粘贴到代理软件中更新即可。</p>
        </div>
    </div>

    <script>
        let baseShortUrl = "";

        document.getElementById('genBtn').addEventListener('click', async function() {
            const rawInput = document.getElementById('urlsInput').value.trim();
            if (!rawInput) return;

            const lines = rawInput.split('\\n').map(line => line.trim()).filter(line => line !== "");
            
            try {
                const response = await fetch('/create_short', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ urls: lines })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    baseShortUrl = data.short_url;
                    
                    // 默认显示通用 Tab
                    switchTab('general');
                    document.getElementById('resultZone').classList.remove('hidden');
                }
            } catch (err) {
                alert('网络异常');
            }
        });

        function switchTab(type) {
            const tabs = document.querySelectorAll('nav button, div button');
            // 更新 Tab 按钮样式
            const buttons = document.querySelectorAll('.flex.gap-2 button');
            buttons.forEach(btn => {
                btn.classList.remove('bg-white', 'text-slate-800', 'shadow-sm');
                btn.classList.add('hover:text-slate-800');
            });
            
            const event = window.event;
            if(event) {
                event.target.classList.add('bg-white', 'text-slate-800', 'shadow-sm');
                event.target.classList.remove('hover:text-slate-800');
            }

            // 更新链接格式内容
            const output = document.getElementById('outputLink');
            if (type === 'general') {
                output.value = baseShortUrl;
            } else if (type === 'clash') {
                output.value = `${baseShortUrl}?flag=clash`;
            } else if (type === 'singbox') {
                output.value = `${baseShortUrl}?flag=singbox`;
            }
        }

        document.getElementById('copyBtn').addEventListener('click', function() {
            const linkInput = document.getElementById('outputLink');
            linkInput.select();
            navigator.clipboard.writeText(linkInput.value);
            
            const btn = document.getElementById('copyBtn');
            btn.innerText = "已复制";
            btn.classList.add('bg-emerald-50', 'text-emerald-600', 'border-emerald-200');
            setTimeout(() => {
                btn.innerText = "复制";
                btn.classList.remove('bg-emerald-50', 'text-emerald-600', 'border-emerald-200');
            }, 1500);
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
    
    # 💡 核心后端逻辑：识别客户端发出的请求标识或者链接自带的 flag 参数
    user_agent = request.headers.get('User-Agent', '').lower()
    flag = request.args.get('flag', '').lower()
    
    # 如果用户使用 Clash 客户端请求，或者链接带了 ?flag=clash
    if 'clash' in user_agent or flag == 'clash':
        # 这里你可以自由定制返回符合 Clash Profile 格式的 YAML 文本
        # 为了保证稳定性和纯净度，目前直接下发纯文本节点数据（绝大部分主流现代 Clash/Clash Meta 内核支持直接拉取通用 Base64 并自动解析为节点）
        pass

    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
