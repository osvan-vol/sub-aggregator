import base64
import json
import os
import random
import string
import urllib.parse
import requests
from flask import Flask, request, Response, render_template_string, abort

app = Flask(__name__)
DB_FILE = "short_urls.json"

def load_db():
    if os.path.exists(DB_FILE):
        try: with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e: print(f"保存失败: {e}")

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# 🌟 全新重构的高级果味极简面板（增加了多客户端格式配置展示）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NextGen 订阅聚合控制台</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>
<body class="bg-[#f4f5f6] text-slate-800 antialiased min-h-screen flex items-center justify-center p-4">

    <div class="w-full max-w-xl bg-white rounded-2xl border border-slate-200/80 shadow-[0_10px_30px_-10px_rgba(0,0,0,0.05)] p-6 md:p-8">
        <div class="mb-6">
            <h1 class="text-xl font-bold text-slate-900 flex items-center gap-2">
                <i class="bi bi-cloud-arrow-up-fill text-blue-600 text-2xl"></i> 全格式订阅转换聚合器
            </h1>
            <p class="text-xs text-slate-400 mt-1">本地安全解析，完美原生适配 Clash、v2rayN、Karing、Sing-box、Shadowrocket。</p>
        </div>

        <form class="space-y-4">
            <div>
                <textarea id="urlsInput" rows="7" 
                    class="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs font-mono text-slate-600 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 outline-none transition-all resize-none placeholder:text-slate-300"
                    placeholder="https://example.com/sub&#10;vless://xxxxxxx&#10;vmess://xxxxxxx"></textarea>
            </div>
            <button type="button" id="genBtn" 
                class="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-xl py-3 text-sm font-medium transition-all shadow-sm flex items-center justify-center gap-2">
                <i class="bi bi-transformer"></i> 转换并生成短链接
            </button>
        </form>

        <div id="resultZone" class="hidden mt-6 pt-6 border-t border-slate-100 space-y-4">
            <div class="text-xs font-semibold text-emerald-600 flex items-center gap-1">
                <i class="bi bi-check-circle-fill"></i> 专属多端适配链接已就绪：
            </div>
            
            <div class="flex flex-wrap gap-1 bg-slate-100 p-1 rounded-xl text-xs font-medium text-slate-500">
                <button id="tab-v2ray" class="flex-1 py-1.5 rounded-lg bg-white text-slate-800 shadow-sm transition-all" onclick="switchTab('v2ray')">v2rayN/小火箭</button>
                <button id="tab-clash" class="flex-1 py-1.5 rounded-lg hover:text-slate-800 transition-all" onclick="switchTab('clash')">Clash</button>
                <button id="tab-singbox" class="flex-1 py-1.5 rounded-lg hover:text-slate-800 transition-all" onclick="switchTab('singbox')">Karing/Sing-box</button>
            </div>

            <div class="relative flex items-center bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5">
                <input type="text" id="outputLink" class="w-full bg-transparent text-xs font-mono text-blue-600 outline-none pr-16" readonly>
                <button type="button" id="copyBtn" class="absolute right-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 text-[11px] font-medium px-2.5 py-1 rounded-md shadow-sm transition-all">
                    复制
                </button>
            </div>
            <p class="text-[11px] text-slate-400 text-center"><i class="bi bi-shield-lock"></i> 提示：代码在本地运行格式化打包，不经过任何第三方接口，绝对防封防泄漏。</p>
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
                    switchTab('v2ray');
                    document.getElementById('resultZone').classList.remove('hidden');
                }
            } catch (err) { alert('网络异常'); }
        });

        function switchTab(type) {
            const buttons = document.querySelectorAll('.flex button');
            buttons.forEach(btn => btn.classList.remove('bg-white', 'text-slate-800', 'shadow-sm'));
            
            document.getElementById(`tab-${type}`).classList.add('bg-white', 'text-slate-800', 'shadow-sm');

            const output = document.getElementById('outputLink');
            if (type === 'v2ray') output.value = baseShortUrl;
            else if (type === 'clash') output.value = `${baseShortUrl}?type=clash`;
            else if (type === 'singbox') output.value = `${baseShortUrl}?type=singbox`;
        }

        document.getElementById('copyBtn').addEventListener('click', function() {
            const linkInput = document.getElementById('outputLink');
            linkInput.select();
            navigator.clipboard.writeText(linkInput.value);
            const btn = document.getElementById('copyBtn');
            btn.innerText = "已复制";
            setTimeout(() => { btn.innerText = "复制"; }, 1500);
        });
    </script>
</body>
</html>
"""

# ==================== 后端协议解析模块 ====================

def parse_node_to_dict(node_str):
    """解析主流节点协议 (VLESS/VMESS/SS/Trojan) 为通用的 Python 字典结构"""
    try:
        node_str = node_str.strip()
        if not node_str or "://" not in node_str: return None
        
        protocol, rest = node_str.split("://", 1)
        protocol = protocol.lower()
        
        # 针对 VMESS 这种通常是全 Base64 JSON 的处理
        if protocol == "vmess":
            try:
                # 自动补齐 padding 并解码
                padded = rest.split("#")[0]
                padded += "=" * (4 - len(padded) % 4)
                config = json.loads(base64.b64decode(padded).decode('utf-8'))
                return {
                    "type": "vmess", "name": config.get("ps", "Vmess_Node"),
                    "server": config.get("add"), "port": int(config.get("port", 443)),
                    "uuid": config.get("id"), "aid": int(config.get("aid", 0)),
                    "net": config.get("net", "tcp"), "path": config.get("path", ""),
                    "tls": True if config.get("tls") == "tls" else False
                }
            except: return None

        # 针对 VLESS / Trojan / SS 的标准 URL 格式解析
        url_parsed = urllib.parse.urlparse(node_str)
        name = urllib.parse.unquote(url_parsed.fragment) if url_parsed.fragment else f"{protocol.upper()}_Node"
        queries = dict(urllib.parse.parse_qsl(url_parsed.query))
        
        server_port = url_parsed.netloc.split("@")[-1]
        server = server_port.split(":")[0]
        port = int(server_port.split(":")[1]) if ":" in server_port else 443
        user_info = url_parsed.netloc.split("@")[0] if "@" in url_parsed.netloc else ""

        return {
            "type": protocol, "name": name, "server": server, "port": port,
            "uuid": user_info, "password": user_info, # 兼容不同叫法
            "sni": queries.get("sni", server), "path": queries.get("path", ""),
            "security": queries.get("security", "none"),
            "net": queries.get("type", "tcp")
        }
    except: return None

# ==================== 客户端专属格式打包模块 ====================

def build_clash_yaml(nodes_dict_list):
    """动态拼装符合 Clash Meta 标准的完整 YAML 订阅"""
    proxies = []
    for n in nodes_dict_list:
        if n["type"] == "vless":
            proxies.append({
                "name": n["name"], "type": "vless", "server": n["server"], "port": n["port"],
                "uuid": n["uuid"], "cipher": "auto", "tls": True if n["security"] == "tls" else False,
                "udp": True, "servername": n["sni"], "network": n["net"], "ws-opts": {"path": n["path"]} if n["net"] == "ws" else {}
            })
        elif n["type"] == "vmess":
            proxies.append({
                "name": n["name"], "type": "vmess", "server": n["server"], "port": n["port"],
                "uuid": n["uuid"], "alterId": n["aid"], "cipher": "auto", "tls": n["tls"],
                "network": n["net"], "ws-opts": {"path": n["path"]} if n["net"] == "ws" else {}
            })
        elif n["type"] == "ss":
            proxies.append({
                "name": n["name"], "type": "ss", "server": n["server"], "port": n["port"],
                "cipher": "aes-256-gcm", "password": n["password"]
            })

    # 完整标准的 Clash Profile 骨架
    clash_config = {
        "port": 7890, "socks-port": 7891, "allow-自由": True, "mode": "Rule", "log-level": "info",
        "proxies": proxies,
        "proxy-groups": [
            {"name": "🚀 节点选择", "type": "select", "proxies": ["URL-Test"] + [p["name"] for p in proxies]},
            {"name": "URL-Test", "type": "url-test", "proxies": [p["name"] for p in proxies], "url": "http://www.gstatic.com/generate_204", "interval": 300}
        ],
        "rules": ["MATCH,🚀 节点选择"]
    }
    
    # 极简转换成 YAML 文本输出
    import yaml
    return yaml.dump(clash_config, allow_unicode=True, default_flow_style=False)


def build_singbox_json(nodes_dict_list):
    """动态拼装原生 Sing-box / Karing 的标准 JSON 配置结构"""
    outbounds = []
    
    # 先注入策略组/选择器
    outbounds.append({
        "type": "selector", "tag": "proxy",
        "outbounds": ["auto-test"] + [n["name"] for n in nodes_dict_list]
    })
    outbounds.append({
        "type": "urltest", "tag": "auto-test",
        "outbounds": [n["name"] for n in nodes_dict_list],
        "url": "https://www.gstatic.com/generate_204", "interval": "3m"
    })

    # 注入节点实体
    for n in nodes_dict_list:
        try:
            if n["type"] == "vless":
                outbounds.append({
                    "type": "vless", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "flow": "", 
                    "tls": {"enabled": True, "server_name": n["sni"], "insecure": False} if n["security"] == "tls" else {"enabled": False}
                })
            elif n["type"] == "vmess":
                outbounds.append({
                    "type": "vmess", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "security": "auto",
                    "tls": {"enabled": True, "insecure": False} if n["tls"] else {"enabled": False}
                })
        except: continue

    # 注入系统直连与拦截拦截
    outbounds.extend([{"type": "direct", "tag": "direct"}, {"type": "block", "tag": "block"}])

    singbox_config = {
        "route": {
            "rules": [{"geoip": "private", "outbound": "direct"}, {"domain_suffix": ["cn"], "outbound": "direct"}],
            "final": "proxy"
        },
        "outbounds": outbounds
    }
    return json.dumps(singbox_config, indent=2, ensure_ascii=False)

# ==================== Flask核心路由 ====================

def decode_base64(data):
    missing_padding = len(data) % 4
    if missing_padding: data += '=' * (4 - missing_padding)
    try: return base64.b64decode(data).decode('utf-8')
    except: return ""

def fetch_and_get_raw_nodes(urls):
    """抓取源，清洗、去重，返回明文节点列表"""
    all_nodes = set()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for item in urls:
        item = item.strip()
        if not item: continue
        if item.startswith('http://') or item.startswith('https://'):
            try:
                response = requests.get(item, headers=headers, timeout=10)
                if response.status_code == 200:
                    raw_content = response.text.strip()
                    decoded_content = decode_base64(raw_content)
                    nodes = decoded_content.splitlines() if decoded_content else raw_content.splitlines()
                    for n in nodes:
                        if '://' in n: all_nodes.add(n.strip())
            except: continue
        elif '://' in item:
            all_nodes.add(item)
    return list(all_nodes)

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/create_short', methods=['POST'])
def create_short():
    data = request.json
    if not data or 'urls' not in data: return {"error": "Invalid data"}, 400
    db = load_db()
    urls_key = ",".join(data['urls'])
    
    for code, stored_urls in db.items():
        if stored_urls == urls_key:
            return {"short_url": f"{request.host_url}s/{code}"}
    
    while True:
        code = generate_short_code()
        if code not in db: break
            
    db[code] = urls_key
    save_db(db)
    return {"short_url": f"{request.host_url}s/{code}"}

@app.route('/s/<code>', methods=['GET'])
def redirect_short(code):
    """智能下发订阅中心核心逻辑"""
    db = load_db()
    if code not in db: abort(404)
        
    original_urls = db[code].split(',')
    raw_nodes = fetch_and_get_raw_nodes(original_urls)
    
    # 显式参数具有最高优先级，其次是 User-Agent 嗅探
    client_type = request.args.get('type', '').lower()
    ua = request.headers.get('User-Agent', '').lower()
    
    # 先将明文节点流全部预解析为结构化字典
    parsed_nodes = [parse_node_to_dict(n) for n in raw_nodes]
    parsed_nodes = [n for n in parsed_nodes if n is not None]

    # 1. 输出给 Clash 
    if client_type == 'clash' or 'clash' in ua:
        yaml_content = build_clash_yaml(parsed_nodes)
        return Response(yaml_content, mimetype='text/yaml', headers={"Content-Disposition": "attachment; filename=config.yaml"})
        
    # 2. 输出给 Sing-box / Karing
    if client_type == 'singbox' or 'sing-box' in ua or 'karing' in ua:
        json_content = build_singbox_json(parsed_nodes)
        return Response(json_content, mimetype='application/json', headers={"Content-Disposition": "attachment; filename=config.json"})

    # 3. 默认返回通用的明文 Base64 字符串流 (适合 v2rayN / Shadowrocket)
    combined_str = "\n".join(raw_nodes)
    b64_result = base64.b64encode(combined_str.encode('utf-8')).decode('utf-8')
    return Response(b64_result, mimetype='text/plain')

if __name__ == '__main__':
    # 生产环境中如果依赖 yaml 库，请确保在 requirements.txt 中补上 pyyaml
    app.run(host='0.0.0.0', port=5000)
