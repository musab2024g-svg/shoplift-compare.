from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Shopify Competitor Analyzer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #2c3e50; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { background: #27ae60; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        #result { background: white; padding: 20px; margin-top: 20px; border-radius: 5px; white-space: pre-wrap; display: none; }
        .loading { color: #888; }
    </style>
</head>
<body>
    <h1>🔍 Shopify Competitor Analyzer</h1>
    <p>Enter two Shopify store URLs to compare their products and prices.</p>
    <input id="store_a" placeholder="Store A URL (e.g. https://store-a.myshopify.com)" />
    <input id="store_b" placeholder="Store B URL (e.g. https://store-b.myshopify.com)" />
    <button onclick="analyze()">Analyze Now</button>
    <div id="result"></div>
    <script>
        async function analyze() {
            const a = document.getElementById('store_a').value;
            const b = document.getElementById('store_b').value;
            const result = document.getElementById('result');
            result.style.display = 'block';
            result.innerHTML = '<p class="loading">Analyzing... please wait ⏳</p>';
            const res = await fetch('/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({store_a: a, store_b: b})
            });
            const data = await res.json();
            result.innerHTML = data.report;
        }
    </script>
</body>
</html>
'''

def get_products(store_url):
    products = {}
    try:
        url = f"{store_url.rstrip('/')}/products.json?limit=250"
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        for p in r.json().get('products', []):
            title = p['title'].lower()
            price = float(p['variants'][0]['price'])
            products[title] = price
    except:
        pass
    return products

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    a = get_products(data['store_a'])
    b = get_products(data['store_b'])

    if not a and not b:
        return jsonify({"report": "❌ Could not fetch products from both stores."})

    common = set(a.keys()) & set(b.keys())
    only_a = set(a.keys()) - set(b.keys())
    only_b = set(b.keys()) - set(a.keys())

    report = f"📊 COMPARISON REPORT\n{'='*40}\n"
    report += f"Store A: {len(a)} products\n"
    report += f"Store B: {len(b)} products\n"
    report += f"Common products: {len(common)}\n\n"

    report += "💰 PRICE COMPARISON (common products):\n"
    for p in list(common)[:20]:
        diff = a[p] - b[p]
        if diff > 0:
            report += f"  {p}: A=${a[p]} | B=${b[p]} → B is cheaper by ${diff:.2f}\n"
        elif diff < 0:
            report += f"  {p}: A=${a[p]} | B=${b[p]} → A is cheaper by ${abs(diff):.2f}\n"
        else:
            report += f"  {p}: ${a[p]} (same price)\n"

    report += f"\n🅰️ Only in Store A: {len(only_a)} products\n"
    report += f"🅱️ Only in Store B: {len(only_b)} products\n"

    return jsonify({"report": report})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
