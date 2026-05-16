from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Shopify Store Analyzer Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; max-width: 900px; margin: 40px auto; padding: 20px; background: #f0f2f5; }
        h1 { color: #1a1a2e; font-size: 28px; }
        .card { background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 2px solid #e0e0e0; border-radius: 8px; box-sizing: border-box; font-size: 15px; }
        button { background: #4CAF50; color: white; padding: 14px 35px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%; margin-top: 10px; }
        #result { white-space: pre-wrap; font-family: monospace; font-size: 14px; line-height: 1.8; }
    </style>
</head>
<body>
    <h1>🔍 Shopify Store Analyzer Pro</h1>
    <div class="card">
        <input id="store_a" placeholder="Your Store URL" />
        <input id="store_b" placeholder="Competitor Store URL" />
        <button onclick="analyze()">🚀 Analyze Now</button>
    </div>
    <div class="card" id="result_card" style="display:none">
        <div id="result"></div>
    </div>
    <script>
        async function analyze() {
            const a = document.getElementById('store_a').value;
            const b = document.getElementById('store_b').value;
            document.getElementById('result_card').style.display = 'block';
            document.getElementById('result').innerHTML = '⏳ Analyzing... please wait...';
            const res = await fetch('/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({store_a: a, store_b: b})
            });
            const data = await res.json();
            document.getElementById('result').innerHTML = data.report;
        }
    </script>
</body>
</html>
'''

def get_products(store_url):
    products = {}
    try:
        clean_url = store_url.rstrip('/')
        url = f"{clean_url}/products.json?limit=250"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            for p in r.json().get('products', []):
                title = p['title'].lower()
                price = float(p['variants'][0]['price'])
                has_image = len(p.get('images', [])) > 0
                has_desc = len(p.get('body_html', '')) > 50
                products[title] = {'price': price, 'has_image': has_image, 'has_desc': has_desc}
    except Exception as e:
        print(f"Error: {e}")
    return products

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    store_a = data.get('store_a', '').strip()
    store_b = data.get('store_b', '').strip()
    
    a = get_products(store_a)
    b = get_products(store_b)

    if not a and not b:
        return jsonify({"report": "❌ Could not fetch both stores. They may be blocking automated requests."})

    common = set(a.keys()) & set(b.keys())
    only_a = set(a.keys()) - set(b.keys())
    only_b = set(b.keys()) - set(a.keys())

    report = "📊 FULL STORE ANALYSIS REPORT\n" + "="*45 + "\n\n"
    report += f"🅰️ Your Store: {len(a)} products\n"
    report += f"🅱️ Competitor: {len(b)} products\n"
    report += f"🔗 Common products: {len(common)}\n\n"

    if common:
        report += "💰 PRICE COMPARISON\n" + "-"*30 + "\n"
        expensive = 0
        cheaper = 0
        for p in list(common)[:15]:
            pa = a[p]['price']
            pb = b[p]['price']
            diff = pa - pb
            if diff > 0:
                expensive += 1
                report += f"  📈 {p[:35]}: You=${pa} | Comp=${pb} → ${diff:.2f} more expensive\n"
            elif diff < 0:
                cheaper += 1
                report += f"  📉 {p[:35]}: You=${pa} | Comp=${pb} → ${abs(diff):.2f} cheaper ✅\n"
            else:
                report += f"  ➡️ {p[:35]}: ${pa} same price\n"
        report += f"\n📌 {expensive} overpriced | {cheaper} competitively priced\n\n"

    report += "🐛 YOUR STORE AUDIT\n" + "-"*30 + "\n"
    no_img = sum(1 for d in a.values() if not d['has_image'])
    no_desc = sum(1 for d in a.values() if not d['has_desc'])
    if no_img: report += f"  ⚠️ {no_img} products missing images\n"
    if no_desc: report += f"  ⚠️ {no_desc} products missing descriptions\n"
    if not no_img and not no_desc: report += "  ✅ Store looks good!\n"

    report += "\n💡 RECOMMENDATIONS\n" + "-"*30 + "\n"
    if only_b: report += f"  • Competitor has {len(only_b)} products you don't — consider adding\n"
    if only_a: report += f"  • You have {len(only_a)} unique products — market them as exclusive\n"
    report += "  • Add descriptions to all products for better SEO\n"
    report += "  • Ensure all products have high-quality images\n"

    return jsonify({"report": report})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
