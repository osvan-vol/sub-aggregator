import base64
import requests
from flask import Flask, request, Response, render_template_string

app = Flask(__name__)

# 🎨 前端 HTML/CSS/JS 界面（响应式设计，支持手机和电脑）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>节点订阅链接聚合器</title>
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
            <h2 class="text-center mb-4" style="color: #1e293b; font-weight: 700;">🌐 订阅链接 & 节点聚合器</h2>
            <p class="text-muted text-center mb-4">在下方输入框中粘贴你的原始订阅链接（一行一个），或者直接粘贴 vless://, vmess://, ss:// 等单节点信息。</p>
            
            <form id="aggregatorForm">
                <div class="mb-4">
                    <label for="urlsInput" class="form-label fw-bold">输入数据（支持订阅 URL 或节点明文）：</label>
                    <textarea class="form-control" id="urlsInput" rows="8" placeholder="https://example.com/sub1&#10;https://example.com/sub2&#10;vless://xxxxxxx&#10;vmess://xxxxxxx"></textarea>
                </div>
                <div class="d-grid">
                    <button type="button" id="submitBtn" class="btn btn-primary btn-lg fw-bold">🚀 生成聚合订阅链接</button>
                </div>
            </form>

            <div id="resultContainer" class="result-box">
                <h5 class="fw-bold text-success mb-3">🎉 您的专属聚合链接生成成功：</h5>
                <div class="input-group mb-3">
                    <input type="text" id="generatedUrl" class="form-control" readonly>
                    <button class="btn btn-outline-secondary" type="button" id="copyBtn">复制链接</button>
                </div>
                <small class="text-muted">提示：将此链接复制并粘贴到您的 Clash、Shadowrocket、Sing-Box 等代理软件中即可使用。</small>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('submitBtn').addEventListener('click', function() {
            const rawInput = document.getElementById('urlsInput').value.trim();
            if (!rawInput) {
                alert('请先输入订阅链接或节点信息！');
                return;
            }

            // 将用户输入的换行文本转换为用逗号连接的参数，并进行安全编码
            const lines = rawInput.split('\\n').map(line => line.strip ? line.strip() : line.trim()).filter(line => line !== "");
            const encodedUrls = encodeURIComponent(lines.join(','));
            
            // 动态获取当前网站的根域名
            const baseUrl = window.location.origin;
            const finalLink = `${baseUrl}/aggregate?urls=${encodedUrls}`;

            // 显示结果
            document.getElementById('generatedUrl').value = finalLink;
            document.getElementById('resultContainer').style.display = 'block';
        });

        document.getElementById('copyBtn').addEventListener('click', function() {
            const copyText = document.getElementById('generatedUrl');
            copyText.select();
            copyText.setSelectionRange(0, 99999);
            navigator.clipboard.writeText(copyText.value);
            alert('链接已成功复制到剪贴板！');
        });
    </script>
</body>
</html>
"""

def decode_base64(data):
    """安全解码 Base64 字符串，自动补齐等号"""
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(data).decode('utf-8')
    except Exception:
        return ""

def fetch_and_aggregate(urls):
    """同时支持抓取 URL 订阅和直接解析明文节点"""
    all_nodes = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for item in urls:
        item = item.strip()
        if not item:
            continue
        
        # 情况 A：如果输入的是一个标准的 http/https 订阅链接
        if item.startswith('http://') or item.startswith('https://'):
            try:
                response = requests.get(item, headers=headers, timeout=10)
                if response.status_code == 200:
                    raw_content = response.text.strip()
                    # 尝试解码订阅返回的 base64 文本
                    decoded_content = decode_base64(raw_content)
                    # 如果能解码成功，说明是传统订阅；如果解码失败，说明本身就是明文节点列表
                    nodes = decoded_content.splitlines() if decoded_content else raw_content.splitlines()
                    
                    for node in nodes:
                        node = node.strip()
                        if node and ('://' in node):
                            all_nodes.add(node)
            except Exception as e:
                print(f"抓取订阅失败 {item}: {e}")
                continue
        
        # 情况 B：如果用户直接粘贴的是 vless://, vmess:// 等明文节点信息
        elif '://' in item:
            all_nodes.add(item)

    # 重新进行通用 Base64 编码输出
    combined_nodes = "\n".join(all_nodes)
    return base64.b64encode(combined_nodes.encode('utf-8')).decode('utf-8')

@app.route('/', methods=['GET'])
def index():
    """根路径返回前端可视化操作页面"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/aggregate', methods=['GET'])
def aggregate_api():
    """后端聚合接口"""
    urls_param = request.args.get('urls')
    if not urls_param:
        return "No inputs provided.", 400

    # 拆分传入的链接或明文节点
    urls = urls_param.split(',')
    result = fetch_and_aggregate(urls)
    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
