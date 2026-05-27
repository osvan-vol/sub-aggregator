import base64
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# 📊 默认的订阅链接列表（如果请求时不传 urls 参数，默认聚合这两个）
DEFAULT_SUBSCRIPTIONS = [
    "https://example.com/sub1",
    "https://example.com/sub2"
]

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
    """抓取并聚合节点逻辑"""
    all_nodes = set()  # 使用 set 集合自动去重
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for url in urls:
        url = url.strip()
        if not url:
            continue
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                raw_content = response.text.strip()
                decoded_content = decode_base64(raw_content)
                nodes = decoded_content.splitlines()
                
                for node in nodes:
                    node = node.strip()
                    if node and ('://' in node):  # 过滤掉空行和非节点文本
                        all_nodes.add(node)
        except Exception as e:
            print(f"抓取订阅失败 {url}: {e}")
            continue

    combined_nodes = "\n".join(all_nodes)
    return base64.b64encode(combined_nodes.encode('utf-8')).decode('utf-8')

@app.route('/aggregate', methods=['GET'])
def aggregate_api():
    """路由接口"""
    urls_param = request.args.get('urls')
    
    if urls_param:
        urls = urls_param.split(',')
    else:
        urls = DEFAULT_SUBSCRIPTIONS

    if not urls:
        return "No subscription URLs provided.", 400

    result = fetch_and_aggregate(urls)
    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)