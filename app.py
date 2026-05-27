import base64
import json
import os
import random
import string
import urllib.parse
import requests
import yaml
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
        print(f"Database save error: {e}")

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# ==================== 融合版：顶级质感静态 UI 模板 ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Unified Subscription Compiler</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
    :root{
        --bg:#07090b;
        --panel:#0f1115;
        --panel-2:#12151a;
        --border:rgba(255,255,255,.06);
        --border-soft:rgba(255,255,255,.04);
        --text:#f5f7fa;
        --muted:#8b93a1;
        --muted-2:#5d6572;
    }
    *{ -webkit-tap-highlight-color:transparent; }
    html, body{ height:100%; }
    body{
        margin:0;
        background:
            radial-gradient(circle at top, rgba(255,255,255,.045), transparent 45%),
            #07090b;
        color:var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        overflow-x:hidden;
    }
    .noise{
        position:fixed;
        inset:0;
        pointer-events:none;
        opacity:.025;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140' viewBox='0 0 140 140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)' opacity='.9'/%3E%3C/svg%3E");
    }
    .shell{ position:relative; width:100%; max-width:780px; margin:auto; padding:72px 28px; }
    .panel{
        position:relative;
        overflow:hidden;
        border-radius:28px;
        background: linear-gradient(180deg, rgba(255,255,255,.025), rgba(255,255,255,.01));
        border:1px solid var(--border-soft);
        box-shadow: 0 0 0 1px rgba(255,255,255,.02), 0 30px 80px rgba(0,0,0,.45);
    }
    .panel::before{
        content:"";
        position:absolute;
        inset:0;
        background: radial-gradient(circle at top, rgba(255,255,255,.06), transparent 40%);
        pointer-events:none;
    }
    .hero{ padding:42px 42px 12px; }
    .brand{ display:flex; align-items:center; gap:14px; }
    .brand-icon{
        width:42px;
        height:42px;
        border-radius:14px;
        display:flex;
        align-items:center;
        justify-content:center;
        background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
        border:1px solid rgba(255,255,255,.06);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
    }
    .brand-icon::before{
        content:""; width:16px; height:16px; border-radius:5px;
        background: linear-gradient(135deg, rgba(255,255,255,.95), rgba(255,255,255,.4));
    }
    .eyebrow{ font-size:11px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted-2); }
    .title{ margin-top:6px; font-size:28px; line-height:1.1; font-weight:600; letter-spacing:-0.04em; color:white; }
    .subtitle{ margin-top:14px; max-width:540px; font-size:14px; line-height:1.7; color:var(--muted); }
    .content{ padding:28px 42px 42px; }
    .editor{ position:relative; }
    textarea{
        width:100%; min-height:210px; resize:none; border-radius:24px; padding:26px;
        border:1px solid rgba(255,255,255,.05);
        background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.015));
        color:#d8dee8; font-size:14px; line-height:1.8; outline:none;
        transition: border .25s ease, background .25s ease, transform .25s ease;
    }
    textarea::placeholder{ color:#5f6774; }
    textarea:focus{
        border-color:rgba(255,255,255,.12);
        background: linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.02));
    }
    .toolbar{ display:flex; align-items:center; justify-content:space-between; margin-top:20px; }
    .hint{ font-size:12px; color:#5f6774; letter-spacing:.01em; }
    .compile-btn{
        height:46px; padding:0 20px; border-radius:14px; border:1px solid rgba(255,255,255,.08);
        background: linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.04));
        color:white; font-size:13px; font-weight:500; letter-spacing:.01em; cursor:pointer;
        transition: background .2s ease, border .2s ease, transform .2s ease;
    }
    .compile-btn:hover{
        background: linear-gradient(180deg, rgba(255,255,255,.11), rgba(255,255,255,.06));
        border-color:rgba(255,255,255,.14);
    }
    .compile-btn:active{ transform:translateY(1px); }
    .result{
        margin-top:40px; padding-top:34px; border-top:1px solid rgba(255,255,255,.05);
        opacity:0; transform:translateY(12px); pointer-events:none;
        transition: opacity .45s ease, transform .45s ease;
    }
    .result.show{ opacity:1; transform:translateY(0); pointer-events:auto; }
    .result-top{ display:flex; align-items:center; justify-content:space-between; gap:20px; }
    .status{ display:flex; align-items:center; gap:10px; font-size:12px; color:#97a0ae; }
    .dot{ width:7px; height:7px; border-radius:999px; background:#8fffca; box-shadow: 0 0 12px rgba(143,255,202,.5); }
    .tabs{ display:flex; align-items:center; gap:24px; }
    .tab{ position:relative; background:none; border:none; color:#5f6774; font-size:13px; font-weight:500; cursor:pointer; transition:color .2s ease; }
    .tab::after{ content:""; position:absolute; left:0; bottom:-10px; width:0%; height:1px; background:white; transition:width .25s ease; }
    .tab.active{ color:white; }
    .tab.active::after{ width:100%; }
    .link-box{
        margin-top:34px; display:flex; align-items:center; gap:14px; padding:12px 14px; border-radius:18px;
        border:1px solid rgba(255,255,255,.05);
        background: linear-gradient(180deg, rgba(255,255,255,.025), rgba(255,255,255,.01));
    }
    .link-box input{
        flex:1; background:none; border:none; outline:none; color:#eef2f7; font-size:13px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }
    .copy-btn{
        height:38px; padding:0 14px; border-radius:12px; border:1px solid rgba(255,255,255,.06);
        background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
        color:#dce3eb; font-size:12px; font-weight:500; cursor:pointer; transition: background .2s ease, border .2s ease;
    }
    .copy-btn:hover{
        border-color:rgba(255,255,255,.1);
        background: linear-gradient(180deg, rgba(255,255,255,.1), rgba(255,255,255,.05));
    }
    .footer{ margin-top:20px; font-size:11px; line-height:1.7; color:#59616d; }
    @media (max-width:768px){
        .shell{ padding:22px; }
        .hero{ padding:28px 24px 0; }
        .content{ padding:22px 24px 28px; }
        .title{ font-size:22px; }
        .toolbar{ flex-direction:column; align-items:flex-start; gap:18px; }
        .compile-btn{ width:100%; }
        .result-top{ flex-direction:column; align-items:flex-start; gap:18px; }
        .tabs{ width:100%; justify-content:space-between; }
    }
</style>
</head>
<body>

<div class="noise"></div>
<div class="shell">
    <div class="panel">
        <div class="hero">
            <div class="brand">
                <div class="brand-icon"></div>
                <div>
                    <div class="eyebrow">Adaptive Runtime Pipeline</div>
                    <div class="title">Unified Subscription Compiler</div>
                </div>
            </div>
            <div class="subtitle">
                Compile heterogeneous proxy nodes into adaptive multi-client distributions for Clash Meta, Sing-box, Shadowrocket and modern Xray runtimes.
            </div>
        </div>

        <div class="content">
            <div class="editor">
                <textarea id="urlsInput" placeholder="Paste raw nodes or existing subscriptions...&#10;&#10;Supports:&#10;VLESS · VMess · Trojan · Shadowsocks · Hysteria2 · TUIC"></textarea>
            </div>

            <div class="toolbar">
                <div class="hint">Unified parsing · Local formatting · Zero third-party relay</div>
                <button class="compile-btn" id="compileBtn">Generate Distribution</button>
            </div>

            <div class="result" id="result">
                <div class="result-top">
                    <div class="status">
                        <div class="dot"></div>
                        Distribution pipeline compiled successfully
                    </div>
                    <div class="tabs">
                        <button class="tab active" data-type="universal">Universal</button>
                        <button class="tab" data-type="clash">Clash Meta</button>
                        <button class="tab" data-type="singbox">Sing-box</button>
                    </div>
                </div>

                <div class="link-box">
                    <input type="text" readonly id="output" value="" />
                    <button class="copy-btn" id="copyBtn">Copy</button>
                </div>

                <div class="footer">
                    Runtime distributions are generated locally within the current execution environment without external relay processing.
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    const result = document.getElementById('result');
    const compileBtn = document.getElementById('compileBtn');
    const output = document.getElementById('output');
    const tabs = document.querySelectorAll('.tab');
    const copyBtn = document.getElementById('copyBtn');
    let baseShortUrl = "";

    compileBtn.addEventListener('click', async () => {
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
                
                // 恢复你原本的默认选定 Universal 的切换逻辑
                updateTabDisplay('universal');
                result.classList.add('show');
            }
        } catch (err) {
            console.error('Network Error', err);
        }
    });

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const type = tab.dataset.type;
            updateTabDisplay(type);
        });
    });

    function updateTabDisplay(type) {
        tabs.forEach(t => {
            if(t.dataset.type === type) t.classList.add('active');
            else t.classList.remove('active');
        });

        if (!baseShortUrl) return;

        if(type === "universal"){
            output.value = baseShortUrl;
        }
        if(type === "clash"){
            output.value = `${baseShortUrl}?type=clash`;
        }
        if(type === "singbox"){
            output.value = `${baseShortUrl}?type=singbox`;
        }
    }

    copyBtn.addEventListener('click', async () => {
        if(!output.value) return;
        await navigator.clipboard.writeText(output.value);
        copyBtn.innerText = "Copied";
        setTimeout(() => {
            copyBtn.innerText = "Copy";
        }, 1400);
    });
</script>
</body>
</html>
"""

# ==================== 后端：全格式自适应解析引擎 ====================

def decode_safe_base64(data):
    data = data.strip().replace('-', '+').replace('_', '/')
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except:
        return ""

def parse_node_to_dict(node_str):
    try:
        node_str = node_str.strip()
        if not node_str or "://" not in node_str: return None
        
        protocol, rest = node_str.split("://", 1)
        protocol = protocol.lower()
        
        if protocol == "vmess":
            try:
                padded = rest.split("#")[0]
                config = json.loads(decode_safe_base64(padded))
                return {
                    "type": "vmess", "name": config.get("ps", "VMess_Node"),
                    "server": config.get("add"), "port": int(config.get("port", 443)),
                    "uuid": config.get("id"), "aid": int(config.get("aid", 0)),
                    "net": str(config.get("net", "tcp")).lower(), "path": config.get("path", ""),
                    "host": config.get("host", ""), "tls": True if str(config.get("tls")).lower() in ["tls", "true"] else False,
                    "sni": config.get("sni", ""), "flow": ""
                }
            except: return None

        url_parsed = urllib.parse.urlparse(node_str)
        name = urllib.parse.unquote(url_parsed.fragment) if url_parsed.fragment else f"{protocol.upper()}_Node"
        queries = dict(urllib.parse.parse_qsl(url_parsed.query))
        
        netloc = url_parsed.netloc
        user_info = ""
        if "@" in netloc:
            user_info, netloc = netloc.split("@", 1)
            user_info = urllib.parse.unquote(user_info)

        if "]" in netloc:
            server = netloc.split("]")[0] + "]"
            port_part = netloc.split("]")[-1]
            port = int(port_part.split(":")[1]) if ":" in port_part else 443
        else:
            server = netloc.split(":")[0]
            port = int(netloc.split(":")[1]) if ":" in netloc else 443

        res = {
            "type": protocol, "name": name, "server": server, "port": port,
            "uuid": user_info, "password": user_info, 
            "sni": queries.get("sni", queries.get("peer", server)),
            "path": queries.get("path", ""),
            "host": queries.get("host", ""),
            "security": queries.get("security", "none").lower(),
            "net": queries.get("type", queries.get("net", "tcp")).lower(),
            "flow": queries.get("flow", "").lower(),
            "fp": queries.get("fp", queries.get("browser", "chrome")),
            "pbk": queries.get("pbk", queries.get("publickey", "")),
            "sid": queries.get("sid", queries.get("shortid", "")),
            "alpn": queries.get("alpn", "")
        }

        if protocol == "tuic" and ":" in user_info:
            res["uuid"] = user_info.split(":")[0]
            res["password"] = user_info.split(":")[1]
        elif protocol in ["ss", "shadowsocks"] and ":" in user_info:
            res["method"] = user_info.split(":")[0]
            res["password"] = user_info.split(":")[1]

        return res
    except: return None

# ==================== 多端核心编译器（Clash / Sing-box） ====================

def build_clash_yaml(nodes_dict_list):
    proxies = []
    for n in nodes_dict_list:
        try:
            if n["type"] == "vless":
                item = {
                    "name": n["name"], "type": "vless", "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "cipher": "auto", "udp": True, "network": n["net"], "servername": n["sni"]
                }
                if n["security"] == "reality" or n["pbk"]:
                    item["tls"] = True
                    item["client-fingerprint"] = n["fp"]
                    item["reality-opts"] = {"public-key": n["pbk"], "short-id": n["sid"]}
                elif n["security"] == "tls":
                    item["tls"] = True
                if n["flow"]: item["flow"] = n["flow"]
                if n["net"] == "ws": item["ws-opts"] = {"path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["sni"]}}
                if n["net"] == "grpc": item["grpc-opts"] = {"grpc-service-name": n["path"]}
                proxies.append(item)
                
            elif n["type"] == "vmess":
                item = {
                    "name": n["name"], "type": "vmess", "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "alterId": n["aid"], "cipher": "auto", "tls": n["tls"] or (n["security"] == "tls"), "udp": True, "network": n["net"]
                }
                if n["net"] == "ws": item["ws-opts"] = {"path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["server"]}}
                if n["net"] == "grpc": item["grpc-opts"] = {"grpc-service-name": n["path"]}
                if n["sni"]: item["servername"] = n["sni"]
                proxies.append(item)
                
            elif n["type"] == "hysteria2":
                proxies.append({
                    "name": n["name"], "type": "hysteria2", "server": n["server"], "port": n["port"],
                    "password": n["password"], "ssl-verify": True, "sni": n["sni"]
                })
                
            elif n["type"] == "tuic":
                proxies.append({
                    "name": n["name"], "type": "tuic", "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "password": n["password"], "alpn": [n["alpn"]] if n["alpn"] else ["h3"],
                    "clash-mode": "bbr", "udp": True
                })
                
            elif n["type"] in ["ss", "shadowsocks", "trojan"]:
                p_type = "trojan" if n["type"] == "trojan" else "ss"
                item = {
                    "name": n["name"], "type": p_type, "server": n["server"], "port": n["port"],
                    "password": n["password"], "udp": True
                }
                if p_type == "ss": item["cipher"] = n.get("method", "aes-256-gcm")
                else: item["sni"] = n["sni"]
                proxies.append(item)
        except: continue

    if not proxies: 
        proxies = [{"name": "DIRECT_FALLBACK", "type": "ss", "server": "127.0.0.1", "port": 8388, "cipher": "aes-256-gcm", "password": "123"}]

    clash_config = {
        "port": 7890, "socks-port": 7891, "allow-lan": True, "mode": "rule", "log-level": "info",
        "dns": {"enable": True, "enhanced-mode": "redir-host", "nameserver": ["119.29.29.29", "8.8.8.8"]},
        "proxies": proxies,
        "proxy-groups": [
            {"name": "🚀 PROXY", "type": "select", "proxies": ["⚡ URL-TEST"] + [p["name"] for p in proxies]},
            {"name": "⚡ URL-TEST", "type": "url-test", "proxies": [p["name"] for p in proxies], "url": "http://www.gstatic.com/generate_204", "interval": 300}
        ],
        "rules": ["GEOIP,LAN,DIRECT", "GEOIP,CN,DIRECT", "MATCH,🚀 PROXY"]
    }
    return yaml.dump(clash_config, allow_unicode=True, default_flow_style=False)

def build_singbox_json(nodes_dict_list):
    outbounds = []
    node_tags = [n["name"] for n in nodes_dict_list]
    
    if not node_tags:
        node_tags = ["direct"]
        
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
                    "uuid": n["uuid"], "flow": n["flow"], "packet_encoding": "xray" if "vision" in n["flow"] else ""
                }
                if n["security"] == "reality" or n["pbk"]:
                    node_item["tls"] = {
                        "enabled": True, "server_name": n["sni"], "reality": {"enabled": True, "public_key": n["pbk"], "short_id": n["sid"]},
                        "utls": {"enabled": True, "fingerprint": n["fp"]}
                    }
                elif n["security"] == "tls":
                    node_item["tls"] = {"enabled": True, "server_name": n["sni"]}
                
                if n["net"] == "ws": node_item["transport"] = {"type": "ws", "path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["sni"]}}
                elif n["net"] == "grpc": node_item["transport"] = {"type": "grpc", "service_name": n["path"]}
                outbounds.append(node_item)
                
            elif n["type"] == "vmess":
                node_item = {
                    "type": "vmess", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "security": "auto", "packet_encoding": "xray"
                }
                if n["tls"] or (n["security"] == "tls"):
                    node_item["tls"] = {"enabled": True, "server_name": n["sni"] if n["sni"] else n["server"]}
                if n["net"] == "ws": node_item["transport"] = {"type": "ws", "path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["server"]}}
                elif n["net"] == "grpc": node_item["transport"] = {"type": "grpc", "service_name": n["path"]}
                outbounds.append(node_item)
                
            elif n["type"] == "hysteria2":
                outbounds.append({
                    "type": "hysteria2", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "password": n["password"], "tls": {"enabled": True, "server_name": n["sni"]}
                })
                
            elif n["type"] == "tuic":
                outbounds.append({
                    "type": "tuic", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "password": n["password"], "congestion_control": "bbr",
                    "tls": {"enabled": True, "server_name": n["sni"], "alpn": [n["alpn"]] if n["alpn"] else ["h3"]}
                })
                
            elif n["type"] in ["ss", "shadowsocks", "trojan"]:
                p_type = "trojan" if n["type"] == "trojan" else "shadowsocks"
                node_item = {
                    "type": p_type, "tag": n["name"], "server": n["server"], "port": n["port"],
                    "password": n["password"]
                }
                if p_type == "shadowsocks": node_item["method"] = n.get("method", "aes-256-gcm")
                else: node_item["tls"] = {"enabled": True, "server_name": n["sni"]}
                outbounds.append(node_item)
        except: continue

    outbounds.extend([{"type": "direct", "tag": "direct"}, {"type": "block", "tag": "block"}])
    
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

# ==================== 调度端 ====================

def fetch_and_get_raw_nodes(urls):
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

    if client_type == 'clash' or 'clash' in ua:
        yaml_content = build_clash_yaml(parsed_nodes)
        return Response(yaml_content, mimetype='text/yaml', headers={"Content-Disposition": "attachment; filename=config.yaml"})
        
    if client_type == 'singbox' or 'sing-box' in ua or 'karing' in ua:
        json_content = build_singbox_json(parsed_nodes)
        return Response(json_content, mimetype='application/json', headers={"Content-Disposition": "attachment; filename=config.json"})

    combined_str = "\n".join(raw_nodes)
    b64_result = base64.b64encode(combined_str.encode('utf-8')).decode('utf-8')
    return Response(b64_result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
