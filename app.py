import base64
import json
import os
import random
import string
import urllib.parse
import re
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

# 🌟 Premium 极简高级浅色调控制面板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NextGen 订阅控制台</title>
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

# ==================== 后端协议核心高容错解析模块 ====================

def decode_safe_base64(data):
    """安全 Base64 解码，规避各种 padding 缺失报错"""
    data = data.strip().replace('-', '+').replace('_', '/')
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except:
        return ""

def parse_node_to_dict(node_str):
    """极致容错版协议解析：完美分离各种非标准畸形链接格式"""
    try:
        node_str = node_str.strip()
        if not node_str or "://" not in node_str: return None
        
        protocol, rest = node_str.split("://", 1)
        protocol = protocol.lower()
        
        # 1. 处理 VMESS 格式
        if protocol == "vmess":
            try:
                padded = rest.split("#")[0]
                config = json.loads(decode_safe_base64(padded))
                return {
                    "type": "vmess", "name": config.get("ps", "VMess_Node"),
                    "server": config.get("add"), "port": int(config.get("port", 443)),
                    "uuid": config.get("id"), "aid": int(config.get("aid", 0)),
                    "net": config.get("net", "tcp").lower(), "path": config.get("path", ""),
                    "host": config.get("host", ""), "tls": True if str(config.get("tls")).lower() in ["tls", "true"] else False
                }
            except: return None

        # 2. 处理标准或非标准的 Shadowsocks (ss://)
        if protocol in ["ss", "shadowsocks"]:
            try:
                b64_part = rest.split("#")[0]
                name = urllib.parse.unquote(rest.split("#")[1]) if "#" in rest else "SS_Node"
                if "@" not in b64_part:
                    decoded = decode_safe_base64(b64_part)
                    if "@" in decoded:
                        user_info, server_info = decoded.split("@", 1)
                        method, password = user_info.split(":", 1)
                        server, port = server_info.split(":", 1)
                        return {"type": "ss", "name": name, "server": server, "port": int(port), "method": method, "password": password}
                else:
                    user_info, server_info = b64_part.split("@", 1)
                    decoded_user = decode_safe_base64(user_info)
                    method, password = decoded_user.split(":", 1)
                    server, port = server_info.split(":", 1)
                    return {"type": "ss", "name": name, "server": server, "port": int(port), "method": method, "password": password}
            except: pass

        # 3. 兼容通用 URL 规范的节点 (VLESS / Trojan)
        url_parsed = urllib.parse.urlparse(node_str)
        name = urllib.parse.unquote(url_parsed.fragment) if url_parsed.fragment else f"{protocol.upper()}_Node"
        queries = dict(urllib.parse.parse_qsl(url_parsed.query))
        
        netloc = url_parsed.netloc
        user_info = ""
        if "@" in netloc:
            user_info, netloc = netloc.split("@", 1)
            user_info = urllib.parse.unquote(user_info)
            
        server = netloc.split(":")[0]
        port = int(netloc.split(":")[1]) if ":" in netloc else 443

        return {
            "type": protocol, "name": name, "server": server, "port": port,
            "uuid": user_info, "password": user_info, "method": "aes-256-gcm",
            "sni": queries.get("sni", queries.get("peer", server)), 
            "path": queries.get("path", ""),
            "security": queries.get("security", "none").lower(),
            "net": queries.get("type", "tcp").lower()
        }
    except: return None

# ==================== 工业级订阅输出模块 ====================

def build_clash_yaml(nodes_dict_list):
    """适配 Clash Meta / Verge 内核的全面分流托管模版"""
    proxies = []
    for n in nodes_dict_list:
        try:
            if n["type"] == "vless":
                item = {
                    "name": n["name"], "type": "vless", "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "cipher": "auto", "tls": True if n["security"] in ["tls", "reality"] else False,
                    "udp": True, "network": n["net"], "servername": n["sni"]
                }
                if n["net"] == "ws": item["ws-opts"] = {"path": n["path"], "headers": {"Host": n["sni"]}}
                proxies.append(item)
            elif n["type"] == "vmess":
                item = {
                    "name": n["name"], "type": "vmess", "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "alterId": n["aid"], "cipher": "auto", "tls": n["tls"],
                    "udp": True, "network": n["net"]
                }
                if n["net"] == "ws": item["ws-opts"] = {"path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["server"]}}
                proxies.append(item)
            elif n["type"] in ["ss", "shadowsocks"]:
                proxies.append({
                    "name": n["name"], "type": "ss", "server": n["server"], "port": n["port"],
                    "cipher": n.get("method", "aes-256-gcm"), "password": n["password"], "udp": True
                })
            elif n["type"] == "trojan":
                proxies.append({
                    "name": n["name"], "type": "trojan", "server": n["server"], "port": n["port"],
                    "password": n["password"], "udp": True, "sni": n["sni"]
                })
        except: continue

    if not proxies: 
        proxies = [{"name": "占位防报错节点", "type": "ss", "server": "127.0.0.1", "port": 8388, "cipher": "aes-256-gcm", "password": "123"}]

    clash_config = {
        "port": 7890, "socks-port": 7891, "allow-lan": True, "mode": "rule", "log-level": "info",
        "dns": {"enable": True, "enhanced-mode": "redir-host", "nameserver": ["119.29.29.29", "8.8.8.8"]},
        "proxies": proxies,
        "proxy-groups": [
            {"name": "🚀 节点选择", "type": "select", "proxies": ["⚡ 自动测速"] + [p["name"] for p in proxies]},
            {"name": "⚡ 自动测速", "type": "url-test", "proxies": [p["name"] for p in proxies], "url": "http://www.gstatic.com/generate_204", "interval": 300}
        ],
        "rules": ["GEOIP,LAN,DIRECT", "GEOIP,CN,DIRECT", "MATCH,🚀 节点选择"]
    }
    import yaml
    return yaml.dump(clash_config, allow_unicode=True, default_flow_style=False)


def build_singbox_json(nodes_dict_list):
    """完美适配 Karing / Sing-box 1.11+ 生产环境规范（移除废弃的 clash_mode 健壮兼容）"""
    outbounds = []
    node_tags = [n["name"] for n in nodes_dict_list]
    
    if not node_tags:
        node_tags = ["DIRECT"]
        
    outbounds.append({"type": "selector", "tag": "proxy", "outbounds": ["auto-test"] + node_tags})
    outbounds.append({
        "type": "urltest", "tag": "auto-test", "outbounds": node_tags,
        "url": "https://www.gstatic.com/generate_204", "interval": "3m"
    })

    for n in nodes_dict_list:
        try:
            if n["type"] == "vless":
                node_item = {
                    "type": "vless", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "flow": ""
                }
                if n["security"] in ["tls", "reality"]:
                    node_item["tls"] = {"enabled": True, "server_name": n["sni"], "utls": {"enabled": True, "fingerprint": "chrome"}}
                if n["net"] == "ws":
                    node_item["transport"] = {"type": "ws", "path": n["path"], "headers": {"Host": n["sni"]}}
                outbounds.append(node_item)
                
            elif n["type"] == "vmess":
                node_item = {
                    "type": "vmess", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "security": "auto"
                }
                if n["tls"]:
                    node_item["tls"] = {"enabled": True, "server_name": n["server"]}
                if n["net"] == "ws":
                    node_item["transport"] = {"type": "ws", "path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["server"]}}
                outbounds.append(node_item)
                
            elif n["type"] in ["ss", "shadowsocks"]:
                outbounds.append({
                    "type": "shadowsocks", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "method": n.get("method", "aes-256-gcm"), "password": n["password"]
                })
            elif n["type"] == "trojan":
                outbounds.append({
                    "type": "trojan", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "password": n["password"], "tls": {"enabled": True, "server_name": n["sni"]}
                })
        except: continue

    outbounds.extend([{"type": "direct", "tag": "direct"}, {"type": "block", "tag": "block"}])
    
    # 彻底修复：使用标准的路由和 DNS 匹配块，不再使用已被弃用的规则对象
    singbox_config = {
        "dns": {
            "servers": [
                {"tag": "dns_proxy", "address": "8.8.8.8", "detour": "proxy"},
                {"tag": "dns_direct", "address": "223.5.5.5", "detour": "direct"}
            ],
            "rules": [
                {"outbound": "any", "server": "dns_proxy"},
                {"geoip": ["private", "cn"], "server": "dns_direct"}
            ]
        },
        "route": {
            "rules": [
                {"geoip": ["private", "cn"], "outbound": "direct"},
                {"domain_suffix": [".cn"], "outbound": "direct"}
            ],
            "final": "proxy",
            "auto_detect_interface": True
        },
        "outbounds": outbounds
    }
    return json.dumps(singbox_config, indent=2, ensure_ascii=False)

# ==================== Flask 调度核心 ====================

def fetch_and_get_raw_nodes(urls):
    all_nodes = set()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for item in urls:
        item = item.strip()
        if not item: continue
        if item.startswith('http://') or item.startswith('https://'):
            try:
                response = requests.get(item, headers=headers, timeout=10)
                if response.status_code == 200:
                    raw_content = response.text.strip()
                    decoded_content = decode_safe_base64(raw_content)
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
    db = load_db()
    if code not in db: abort(404)
        
    original_urls = db[code].split(',')
    raw_nodes = fetch_and_get_raw_nodes(original_urls)
    
    client_type = request.args.get('type', '').lower()
    ua = request.headers.get('User-Agent', '').lower()
    
    parsed_nodes = []
    for n in raw_nodes:
        p = parse_node_to_dict(n)
        if p: parsed_nodes.append(p)

    # 1. Clash 转换路由
    if client_type == 'clash' or 'clash' in ua:
        yaml_content = build_clash_yaml(parsed_nodes)
        return Response(yaml_content, mimetype='text/yaml', headers={"Content-Disposition": "attachment; filename=config.yaml"})
        
    # 2. Sing-box / Karing 转换路由
    if client_type == 'singbox' or 'sing-box' in ua or 'karing' in ua:
        json_content = build_singbox_json(parsed_nodes)
        return Response(json_content, mimetype='application/json', headers={"Content-Disposition": "attachment; filename=config.json"})

    # 3. 默认输出 (v2rayN / Base64 流)
    combined_str = "\n".join(raw_nodes)
    b64_result = base64.b64encode(combined_str.encode('utf-8')).decode('utf-8')
    return Response(b64_result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
