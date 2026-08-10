import base64
import json
import os
import random
import re
import string
import urllib.parse
import requests
import yaml
from flask import Flask, request, Response, render_template_string, abort

app = Flask(__name__)
DB_FILE = "short_urls.json"

def public_base_url():
    """反代后强制使用 https，避免生成 http 短链"""
    host = request.headers.get("X-Forwarded-Host") or request.host
    return f"https://{host}/"

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
    <title>NextGen GAGE全协议聚合</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>
<body class="bg-[#f4f5f6] text-slate-800 antialiased min-h-screen flex items-center justify-center p-4">

    <div class="w-full max-w-xl bg-white rounded-2xl border border-slate-200/80 shadow-[0_10px_30px_-10px_rgba(0,0,0,0.05)] p-6 md:p-8">
        <div class="mb-6">
            <h1 class="text-xl font-bold text-slate-900 flex items-center gap-2">
                <i class="bi bi-cloud-arrow-up-fill text-blue-600 text-2xl"></i> 全协议万能订阅聚合器
            </h1>
            <p class="text-xs text-slate-400 mt-1">完美原生支持 Xray/Sing-box 全协议全传输层矩阵，自动适配分流与路由树。</p>
        </div>

        <form class="space-y-4">
            <div>
                <textarea id="urlsInput" rows="7" 
                    class="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs font-mono text-slate-600 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 outline-none transition-all resize-none placeholder:text-slate-300"
                    placeholder="支持打包粘贴各类原生订阅或单节点链接...&#10;vless://&#10;vmess://&#10;hysteria2://&#10;tuic://"></textarea>
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
            <p class="text-[11px] text-slate-400 text-center"><i class="bi bi-shield-lock"></i> 本地环境动态安全打包，绝无第三方中转泄漏风险。</p>
        </div>
    </div>

    <script>
        let baseShortUrl = "";

        document.getElementById('genBtn').addEventListener('click', async function() {
            const rawInput = document.getElementById('urlsInput').value.trim();
            if (!rawInput) return;
            let lines = rawInput.split('\\n').map(line => line.trim()).filter(line => line !== "");
            const hasLink = lines.some(l => l.includes('://'));
            if (!hasLink) {
                const longLines = lines.filter(l => l.length > 80);
                if (longLines.length > 1 && longLines.length === lines.length) {
                    lines = longLines;
                } else {
                    lines = [rawInput.trim()];
                }
            }
            
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
                } else {
                    const err = await response.json().catch(() => ({}));
                    alert(err.error || ('生成失败: HTTP ' + response.status));
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

# ==================== 后端万能协议解构内核 ====================

def decode_safe_base64(data):
    if not data:
        return ""
    data = "".join(str(data).split())
    data = data.replace('-', '+').replace('_', '/')
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except Exception:
        return ""


def parse_node_to_dict(node_str):
    """地毯式泛型动态提取器：提取任意节点的协议、传输层参数与安全控制流"""
    try:
        node_str = node_str.strip()
        if not node_str or "://" not in node_str: return None
        
        protocol, rest = node_str.split("://", 1)
        protocol = protocol.lower()
        
        # 针对标准加密 JSON 的 VMESS
        if protocol == "vmess":
            try:
                padded = rest.split("#")[0]
                config = json.loads(decode_safe_base64(padded))
                is_tls = True if str(config.get("tls")).lower() in ["tls", "true"] else False
                return {
                    "type": "vmess", "name": config.get("ps", "VMess_Node"),
                    "server": config.get("add"), "port": int(config.get("port", 443)),
                    "uuid": config.get("id"), "aid": int(config.get("aid", 0)),
                    "net": str(config.get("net", "tcp")).lower(), "path": config.get("path", ""),
                    "host": config.get("host", ""), "tls": is_tls,
                    "security": "tls" if is_tls else "none",
                    "sni": config.get("sni", ""), "flow": "",
                    "skip_cert": True if str(config.get("verify_cert")).lower() == "false" else False
                }
            except: return None

        # 针对带有标准 URL 结构的复杂协议簇（VLESS, Trojan, SS, Hysteria2, TUIC, AnyTLS...）
        url_parsed = urllib.parse.urlparse(node_str)
        name = urllib.parse.unquote(url_parsed.fragment) if url_parsed.fragment else f"{protocol.upper()}_Node"
        queries = dict(urllib.parse.parse_qsl(url_parsed.query))
        
        netloc = url_parsed.netloc
        user_info = ""
        if "@" in netloc:
            user_info, netloc = netloc.split("@", 1)
            user_info = urllib.parse.unquote(user_info)

        # 兼容 IPv6 地址及端口分离
        if "]" in netloc:
            server = netloc.split("]")[0] + "]"
            port_part = netloc.split("]")[-1]
            port = int(port_part.split(":")[1]) if ":" in port_part else 443
        else:
            server = netloc.split(":")[0]
            port = int(netloc.split(":")[1]) if ":" in netloc else 443

        # 泛型参数统抓归一化（通吞所有可能的 Xray 混淆字段参数）
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

        # 🌟 核心修复：精准捕获原链接中的 insecure=1 或 allowInsecure 等参数，没写则默认为自签安全节点兜底强开跳过
        is_insecure = queries.get("insecure", queries.get("allowInsecure", ""))
        if is_insecure in ["1", "true", "True"] or res["security"] == "insecure" or protocol in ["hysteria2", "anytls"]:
            res["skip_cert"] = True
        else:
            res["skip_cert"] = False

        # 兼容特异性复合型凭据
        if protocol == "tuic" and ":" in user_info:
            res["uuid"], res["password"] = user_info.split(":", 1)
        elif protocol in ["ss", "shadowsocks"]:
            raw_userinfo = user_info
            if ":" not in raw_userinfo:
                decoded = decode_safe_base64(raw_userinfo)
                if ":" in decoded:
                    raw_userinfo = decoded
            if ":" in raw_userinfo:
                res["method"], res["password"] = raw_userinfo.split(":", 1)

        return res
    except: return None

# ==================== 工业级多端订阅编译器 ====================

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
                if n["skip_cert"]: item["skip-cert-verify"] = True
                if n["flow"]: item["flow"] = n["flow"]
                if n["net"] == "ws": item["ws-opts"] = {"path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["sni"]}}
                if n["net"] == "grpc": item["grpc-opts"] = {"grpc-service-name": n["path"]}
                proxies.append(item)
                
            elif n["type"] == "vmess":
                item = {
                    "name": n["name"], "type": "vmess", "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "alterId": n["aid"], "cipher": "auto", "tls": n["tls"] or (n.get("security") == "tls"), "udp": True, "network": n["net"]
                }
                if n["skip_cert"]: item["skip-cert-verify"] = True
                if n["net"] == "ws": item["ws-opts"] = {"path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["server"]}}
                if n["net"] == "grpc": item["grpc-opts"] = {"grpc-service-name": n["path"]}
                if n["sni"]: item["servername"] = n["sni"]
                proxies.append(item)
                
            elif n["type"] == "hysteria2":
                proxies.append({
                    "name": n["name"], "type": "hysteria2", "server": n["server"], "port": n["port"],
                    "password": n["password"], 
                    "skip-cert-verify": n.get("skip_cert", True),  # ✅ 核心修复：Clash 内核标准格式
                    "sni": n["sni"],
                    "alpn": n["alpn"].split(",") if n["alpn"] else ["h3"]
                })
                
            elif n["type"] == "tuic":
                proxies.append({
                    "name": n["name"], "type": "tuic", "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "password": n["password"],
                    "alpn": n["alpn"].split(",") if n["alpn"] else ["h3"],
                    "clash-mode": "bbr", "udp": True,
                    "skip-cert-verify": n.get("skip_cert", True)
                })
                
            elif n["type"] == "anytls":
                item = {
                    "name": n["name"], "type": "anytls", "server": n["server"], "port": n["port"],
                    "password": n["password"], "sni": n["sni"],
                    "client-fingerprint": n.get("fp", "chrome"), "udp": True,
                    "skip-cert-verify": n.get("skip_cert", True)  # ✅ 核心修复：Clash 内核标准格式
                }
                if n.get("alpn"): item["alpn"] = n["alpn"].split(",")
                proxies.append(item)

            elif n["type"] in ["ss", "shadowsocks", "trojan"]:
                p_type = "trojan" if n["type"] == "trojan" else "ss"
                item = {
                    "name": n["name"], "type": p_type, "server": n["server"], "port": n["port"],
                    "password": n["password"], "udp": True
                }
                if p_type == "ss": item["cipher"] = n.get("method", "aes-256-gcm")
                else: 
                    item["sni"] = n["sni"]
                    if n["skip_cert"]: item["skip-cert-verify"] = True
                proxies.append(item)
        except: continue

    if not proxies: 
        proxies = [{"name": "防报错兜底空节点", "type": "ss", "server": "127.0.0.1", "port": 8388, "cipher": "aes-256-gcm", "password": "123"}]

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
    return yaml.dump(clash_config, allow_unicode=True, default_flow_style=False)


def build_singbox_json(nodes_dict_list):
    """完美原生适配 Karing / Sing-box 1.11+ 规范"""
    node_outbounds = []

    for n in nodes_dict_list:
        try:
            # 1. 动态编排 VLESS
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
                    node_item["tls"] = {"enabled": True, "server_name": n["sni"], "insecure": n["skip_cert"]}
                
                if n["net"] == "ws": node_item["transport"] = {"type": "ws", "path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["sni"]}}
                elif n["net"] == "grpc": node_item["transport"] = {"type": "grpc", "service_name": n["path"]}
                node_outbounds.append(node_item)
                
            # 2. 动态编排 VMESS
            elif n["type"] == "vmess":
                node_item = {
                    "type": "vmess", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "security": "auto", "packet_encoding": "xray"
                }
                if n["tls"] or (n.get("security") == "tls"):
                    node_item["tls"] = {"enabled": True, "server_name": n["sni"] if n["sni"] else n["server"], "insecure": n["skip_cert"]}
                if n["net"] == "ws": node_item["transport"] = {"type": "ws", "path": n["path"], "headers": {"Host": n["host"] if n["host"] else n["server"]}}
                elif n["net"] == "grpc": node_item["transport"] = {"type": "grpc", "service_name": n["path"]}
                node_outbounds.append(node_item)
                
            # 3. 动态编排 Hysteria2
            elif n["type"] == "hysteria2":
                node_outbounds.append({
                    "type": "hysteria2", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "password": n["password"], 
                    "tls": {
                        "enabled": True, 
                        "server_name": n["sni"],
                        "insecure": n.get("skip_cert", True)  # ✅ 核心修复：Singbox 标准格式
                    }
                })
                
            # 4. 动态编排 TUIC
            elif n["type"] == "tuic":
                node_outbounds.append({
                    "type": "tuic", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "uuid": n["uuid"], "password": n["password"], "congestion_control": "bbr",
                    "tls": {"enabled": True, "server_name": n["sni"], "alpn": n["alpn"].split(",") if n["alpn"] else ["h3"], "insecure": n.get("skip_cert", True)}
                })
                
            # 5. 动态编排 AnyTLS
            elif n["type"] == "anytls":
                node_outbounds.append({
                    "type": "anytls", "tag": n["name"], "server": n["server"], "port": n["port"],
                    "password": n["password"],
                    "tls": {
                        "enabled": True, 
                        "server_name": n["sni"],
                        "insecure": n.get("skip_cert", True)  # ✅ 核心修复：Singbox 标准格式
                    }
                })

            # 6. 其余协议标准兼容
            elif n["type"] in ["ss", "shadowsocks", "trojan"]:
                p_type = "trojan" if n["type"] == "trojan" else "shadowsocks"
                node_item = {
                    "type": p_type, "tag": n["name"], "server": n["server"], "port": n["port"],
                    "password": n["password"]
                }
                if p_type == "shadowsocks": node_item["method"] = n.get("method", "aes-256-gcm")
                else: node_item["tls"] = {"enabled": True, "server_name": n["sni"], "insecure": n["skip_cert"]}
                node_outbounds.append(node_item)
        except: continue

    node_tags = [item["tag"] for item in node_outbounds] or ["direct"]
    outbounds = [
        {"type": "selector", "tag": "proxy", "outbounds": ["auto-test"] + node_tags},
        {"type": "urltest", "tag": "auto-test", "outbounds": node_tags,
         "url": "https://www.gstatic.com/generate_204", "interval": "3m"}
    ]
    outbounds.extend(node_outbounds)
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

# ==================== Flask 调度核心 ====================

def dedupe_node_names(nodes):
    seen = {}
    for n in nodes:
        base_name = n["name"]
        if base_name not in seen:
            seen[base_name] = 1
        else:
            seen[base_name] += 1
            n["name"] = f"{base_name} #{seen[base_name]}"
    return nodes


def normalize_input_items(items):
    """整理前端提交的内容。
    - URL / 节点链接：原样保留
    - 多段完整 base64（每行很长）：分别解码，不要拼在一起
    - 一段 base64 被折成多行：合并后再解码
    """
    if not items:
        return []
    items = [str(x).strip() for x in items if str(x).strip()]
    if not items:
        return []

    def is_b64_line(s):
        s2 = "".join(s.split())
        if len(s2) < 20:
            return False
        return re.match(r'^[A-Za-z0-9+/_=-]+$', s2) is not None

    links = []
    others = []
    for i in items:
        if i.startswith(('http://', 'https://')) or '://' in i:
            links.append(i)
        else:
            others.append(i)

    result = list(links)
    if not others:
        return result

    # 多段完整 base64：每段单独处理（一次粘贴多个订阅 base64）
    if len(others) > 1 and all(is_b64_line(x) and len("".join(x.split())) > 80 for x in others):
        result.extend(others)
        return result

    # 一段被折行的 base64 / 文本
    result.append("\n".join(others))
    return result


def fetch_and_get_raw_nodes(urls):
    all_nodes = []
    seen = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    def add_node(line):
        line = line.strip()
        if line and '://' in line and line not in seen:
            seen.add(line)
            all_nodes.append(line)

    def extract_nodes_from_text(text):
        text = (text or '').strip()
        if not text:
            return
        for line in text.splitlines():
            add_node(line)
        decoded = decode_safe_base64(text)
        if decoded and decoded != text:
            for line in decoded.splitlines():
                add_node(line)

    for item in normalize_input_items(urls):
        item = item.strip()
        if not item:
            continue
        if item.startswith('http://') or item.startswith('https://'):
            try:
                response = requests.get(item, headers=headers, timeout=15)
                if response.status_code == 200:
                    extract_nodes_from_text(response.text)
            except Exception:
                continue
        elif '://' in item:
            add_node(item)
        else:
            extract_nodes_from_text(item)

    return all_nodes


def load_source_list(stored):
    """兼容旧版逗号拼接与新版 JSON 数组存储"""
    if stored is None:
        return []
    if isinstance(stored, list):
        return stored
    if not isinstance(stored, str):
        return []
    s = stored.strip()
    if not s:
        return []
    if s.startswith('['):
        try:
            data = json.loads(s)
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return [x for x in s.split(',') if x.strip()]


@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/create_short', methods=['POST'])
def create_short():
    data = request.json
    if not data or 'urls' not in data:
        return {"error": "Invalid data"}, 400

    items = normalize_input_items(data.get('urls') or [])
    if not items:
        return {"error": "empty input"}, 400

    preview_nodes = fetch_and_get_raw_nodes(items)
    if not preview_nodes:
        return {"error": "未能解析出任何节点，请检查 base64/订阅内容"}, 400

    db = load_db()
    urls_key = json.dumps(items, ensure_ascii=False)

    for code, stored in db.items():
        if stored == urls_key or load_source_list(stored) == items:
            return {"short_url": f"{public_base_url()}s/{code}", "nodes": len(preview_nodes)}

    while True:
        code = generate_short_code()
        if code not in db:
            break

    db[code] = urls_key
    save_db(db)
    return {"short_url": f"{public_base_url()}s/{code}", "nodes": len(preview_nodes)}


@app.route('/s/<code>', methods=['GET'])
def redirect_short(code):
    db = load_db()
    if code not in db:
        abort(404)

    original_urls = load_source_list(db[code])
    raw_nodes = fetch_and_get_raw_nodes(original_urls)

    if not raw_nodes:
        return Response("no valid nodes", status=400, mimetype='text/plain')

    client_type = request.args.get('type', '').lower()
    ua = request.headers.get('User-Agent', '').lower()

    parsed_nodes = []
    for n in raw_nodes:
        p = parse_node_to_dict(n)
        if p:
            parsed_nodes.append(p)
    parsed_nodes = dedupe_node_names(parsed_nodes)

    if client_type == 'clash' or 'clash' in ua:
        yaml_content = build_clash_yaml(parsed_nodes)
        return Response(
            yaml_content,
            mimetype='text/yaml; charset=utf-8',
            headers={"Content-Disposition": "attachment; filename=config.yaml"},
        )

    if client_type == 'singbox' or 'sing-box' in ua or 'karing' in ua:
        json_content = build_singbox_json(parsed_nodes)
        return Response(
            json_content,
            mimetype='application/json; charset=utf-8',
            headers={"Content-Disposition": "attachment; filename=config.json"},
        )

    combined_str = "\n".join(raw_nodes)
    b64_result = base64.b64encode(combined_str.encode('utf-8')).decode('utf-8')
    return Response(b64_result, mimetype='text/plain; charset=utf-8')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"[sub-aggregator] listening on 0.0.0.0:{port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
