from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)
SCRAPER_KEY = os.environ.get('SCRAPER_API_KEY', '')

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Shopify Store Analyzer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; max-width: 900px; margin: 40px auto; padding: 20px; background: #f0f2f5; }
        h1 { color: #1a1a2e; font-size: 28px; }
        .subtitle { color: #666; margin-bottom: 30px; }
        .card { background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 2px solid #e0e0e0; border-radius: 8px; box-sizing: border-box; font-size: 15px; }
        input:focus { border-color: #4CAF50; outline: none; }
        button { background: #4CAF50; color: white; padding: 14px 35px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%; margin-top: 10px; }
        button:hover { background: #45a049; }
        #result { white-space: pre-wrap; font-family: monospace; font-size: 14px; line-height: 1.8; display: none; }
        .loading { text-align: center; color: #888; font-size: 18px; padding: 20px; }
        .features { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; }
        .feature { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50; }
        .feature h3 { margin: 0 0 5px 0; font-size: 14px; color: #333; }
        .feature p { margin: 0; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <h1>🔍 Shopify Store Analyzer Pro</h1>
    <p class="subtitle">Complete competitor analysis & store audit tool</p>
    
    <div class="features">
        <div class="feature"><h3>📊 Price Comparison</h3><p>Compare prices with competitors</p></div>
        <div class="feature"><h3>🐛 Error Detection</h3><p>Find issues hurting your sales</p></div>
        <div class="feature"><h3>💡 Smart Suggestions</h3><p>Get actionable recommendations</p></div>
        <div class="feature"><h3>📈 SEO Check</h3><p>Basic SEO analysis included</p></div>
    </div>

    <div class="card">
        <h2 style="margin-top:0">Enter Store URLs</h2>
        <input id="store_a" placeholder="Your Store URL (e.g. https://your-store.myshopify.com)" />
        <input id="store_b" placeholder="Competitor Store URL (e.g. https://competitor.myshopify.com)" />
        <button onclick="analyze()">🚀 Analyze Now</button>
    </div>

    <div class="card" id="result_card" style="display:none">
        <div id="result"></div>
    </div>

    <script>
        async function analyze() {
            const a = document.getElementById('store_a').value;
            const b = document.getElementById('store_b').value;
            if (!a || !b) { alert('Please enter both store URLs'); return; }
            document.getElementById('result_card').style.display = 'block';
            document.getElementById('result').innerHTML = '<div class="loading">⏳ Analyzing stores... this may take 30 seconds...</div>';
            try {
                const res = await fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({store_a: a, store_b: b})
                });
                const data = await res.json();
                document.getElementById('result').innerHTML = data.report;
            } catch(e) {
                document.getElementById('result').innerHTML = '❌ Error occurred. Please try again.';
            }
        }
    </script>
</body>
</html>
'''

def get_products(store_url):
    products = {}
    try:
        url = f"{store_url.rstrip('/')}/products.json?limit=250"
        if SCRAPER_KEY:
            proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_KEY}&url={url}"
            r = requests.get(proxy_url, timeout=30)
        else:
            r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        data = r.json()
        for p in data.get('products', []):
            title = p['title'].lower()
            price = float(p['variants'][0]['price'])
            has_image = len(p.get('images', [])) > 0
            description = p.get('body_html', '')
            products[title] = {
                'price': price,
                'has_image': has_image,
                'has_description': len(description) > 50,
                'variants': len(p.get('variants', [])),
                'handle': p.get('handle', '')
            }
    except Exception as e:
        pass
    return products

def audit_store(products, store_name):
    issues = []
    no_image = [t for t, d in products.items() if not d['has_image']]
    no_desc = [t for t, d in products.items() if not d['has_description']]
    
    if no_image:
        issues.append(f"  ⚠️  {len(no_image)} products missing images")
    if no_desc:
        issues.append(f"  ⚠️  {len(no_desc)} products missing descriptions (hurts SEO)")
    if len(products) < 10:
        issues.append(f"  ⚠️  Very few products ({len(products)}) - consider expanding catalog")
    if not issues:
        issues.append("  ✅ No major issues found")
    return issues

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    a = get_products(data['store_a'])
    b = get_products(data['store_b'])

    if not a and not b:
        return jsonify({"report": "❌ Could not fetch products. Please check the URLs and try again."})

    common = set(a.keys()) & set(b.keys())
    only_a = set(a.keys()) - set(b.keys())
    only_b = set(b.keys()) - set(a.keys())

    report = "📊 FULL STORE ANALYSIS REPORT\n" + "="*50 + "\n\n"
    
    report += f"🅰️ Your Store: {len(a)} products\n"
    report += f"🅱️ Competitor: {len(b)} products\n"
    report += f"🔗 Products in common: {len(common)}\n\n"

    report += "💰 PRICE COMPARISON\n" + "-"*30 + "\n"
    cheaper_count = 0
    expensive_count = 0
    for p in list(common)[:15]:
        pa = a[p]['price']
        pb = b[p]['price']
        diff = pa - pb
        if diff > 0:
            expensive_count += 1
            report += f"  📈 {p[:40]}: You=${pa} | Competitor=${pb} → You are ${diff:.2f} MORE expensive\n"
        elif diff < 0:
            cheaper_count += 1
            report += f"  📉 {p[:40]}: You=${pa} | Competitor=${pb} → You are ${abs(diff):.2f} cheaper ✅\n"
        else:
            report += f"  ➡️  {p[:40]}: ${pa} (same price)\n"
    
    report += f"\n📌 Summary: {expensive_count} products overpriced vs competitor, {cheaper_count} competitively priced\n\n"

    report += "🐛 STORE AUDIT - YOUR STORE\n" + "-"*30 + "\n"
    if a:
        for issue in audit_store(a, "Your Store"):
            report += issue + "\n"
    report += "\n"

    report += "🐛 STORE AUDIT - COMPETITOR\n" + "-"*30 + "\n"
    if b:
        for issue in audit_store(b, "Competitor"):
            report += issue + "\n"
    report += "\n"

    report += "💡 SMART RECOMMENDATIONS\n" + "-"*30 + "\n"
    if expensive_count > 0:
        report += f"  1. Consider reducing prices on {expensive_count} overpriced products\n"
    if only_b:
        report += f"  2. Competitor sells {len(only_b)} products you don't — consider adding them\n"
    if only_a:
        report += f"  3. You have {len(only_a)} unique products — highlight these as exclusive\n"
    report += "  4. Add detailed descriptions to all products for better Google ranking\n"
    report += "  5. Ensure all products have high-quality images\n"

    return jsonify({"report": report})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
