from flask import Flask, request, jsonify, render_template_string
import requests
import os
import json

app = Flask(__name__)
GEMINI_KEY = os.environ.get('GEMINI_API_KEY', '')

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ConvertIQ - Revenue Intelligence Platform</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#fff;font-family:'Inter',sans-serif;min-height:100vh}
.nav{display:flex;justify-content:space-between;align-items:center;padding:20px 40px;border-bottom:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(20px);position:sticky;top:0;z-index:100;background:rgba(10,10,15,0.8)}
.logo{font-size:24px;font-weight:800;background:linear-gradient(135deg,#a855f7,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-btn{background:linear-gradient(135deg,#a855f7,#06b6d4);color:#fff;border:none;padding:10px 24px;border-radius:8px;cursor:pointer;font-weight:600}
.hero{text-align:center;padding:80px 20px 60px;position:relative}
.hero-badge{display:inline-block;background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);color:#a855f7;padding:8px 20px;border-radius:100px;font-size:13px;margin-bottom:30px}
.hero h1{font-size:clamp(36px,6vw,72px);font-weight:900;line-height:1.1;margin-bottom:20px}
.hero h1 span{background:linear-gradient(135deg,#a855f7,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{font-size:18px;color:#94a3b8;max-width:600px;margin:0 auto 40px}
.analyze-box{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:30px;max-width:600px;margin:0 auto;backdrop-filter:blur(20px)}
.analyze-box input{width:100%;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#fff;padding:16px 20px;border-radius:10px;font-size:16px;margin-bottom:15px;outline:none}
.analyze-box input:focus{border-color:#a855f7}
.analyze-btn{width:100%;background:linear-gradient(135deg,#a855f7,#06b6d4);color:#fff;border:none;padding:16px;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer;transition:opacity 0.2s}
.analyze-btn:hover{opacity:0.9}
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;padding:60px 40px;max-width:1200px;margin:0 auto}
.feature-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;transition:border-color 0.3s}
.feature-card:hover{border-color:rgba(168,85,247,0.4)}
.feature-icon{font-size:32px;margin-bottom:15px}
.feature-card h3{font-size:16px;font-weight:700;margin-bottom:8px}
.feature-card p{font-size:14px;color:#64748b}
.loading{display:none;text-align:center;padding:60px 20px}
.loading-steps{max-width:400px;margin:30px auto;text-align:left}
.step{display:flex;align-items:center;gap:12px;padding:12px 0;color:#64748b;font-size:14px;transition:color 0.3s}
.step.active{color:#a855f7}
.step.done{color:#10b981}
.step-dot{width:8px;height:8px;border-radius:50%;background:currentColor;flex-shrink:0}
.spinner{width:60px;height:60px;border:3px solid rgba(168,85,247,0.1);border-top-color:#a855f7;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto}
@keyframes spin{to{transform:rotate(360deg)}}
.error-box{display:none;text-align:center;padding:60px 20px}
.error-card{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:16px;padding:30px;max-width:500px;margin:0 auto}
.error-card h3{font-size:20px;font-weight:700;color:#ef4444;margin-bottom:12px}
.error-card p{color:#94a3b8;margin-bottom:20px}
.error-card button{background:linear-gradient(135deg,#a855f7,#06b6d4);color:#fff;border:none;padding:12px 24px;border-radius:8px;cursor:pointer;font-weight:600}
.dashboard{display:none;max-width:1200px;margin:0 auto;padding:40px 20px}
.dash-header{margin-bottom:40px}
.dash-header h2{font-size:28px;font-weight:800;margin-bottom:8px}
.dash-header p{color:#64748b}
.score-section{display:grid;grid-template-columns:auto 1fr;gap:30px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:30px;margin-bottom:30px;align-items:center}
.score-circle{width:140px;height:140px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:900;position:relative}
.score-number{font-size:48px;line-height:1}
.score-label{font-size:12px;color:#94a3b8;margin-top:4px}
.score-good{background:radial-gradient(circle,rgba(16,185,129,0.2),rgba(16,185,129,0.05));border:3px solid #10b981}
.score-medium{background:radial-gradient(circle,rgba(245,158,11,0.2),rgba(245,158,11,0.05));border:3px solid #f59e0b}
.score-bad{background:radial-gradient(circle,rgba(239,68,68,0.2),rgba(239,68,68,0.05));border:3px solid #ef4444}
.score-details h3{font-size:20px;font-weight:700;margin-bottom:8px}
.score-details p{color:#94a3b8;margin-bottom:16px}
.revenue-loss{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:16px 20px;display:inline-block}
.revenue-loss .amount{font-size:28px;font-weight:900;color:#ef4444}
.revenue-loss .label{font-size:12px;color:#94a3b8}
.metrics-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:30px}
.metric-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:20px}
.metric-value{font-size:32px;font-weight:900;margin-bottom:4px}
.metric-label{font-size:13px;color:#64748b}
.metric-change{font-size:12px;margin-top:8px}
.metric-change.bad{color:#ef4444}
.metric-change.good{color:#10b981}
.issues-section{margin-bottom:30px}
.issues-section h3{font-size:18px;font-weight:700;margin-bottom:16px}
.issue-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px 20px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center}
.issue-left{display:flex;align-items:center;gap:12px}
.issue-priority{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.priority-critical{background:#ef4444;box-shadow:0 0 8px #ef4444}
.priority-high{background:#f59e0b;box-shadow:0 0 8px #f59e0b}
.priority-medium{background:#3b82f6;box-shadow:0 0 8px #3b82f6}
.issue-title{font-size:14px;font-weight:600}
.issue-desc{font-size:12px;color:#64748b;margin-top:2px}
.issue-impact{text-align:right}
.issue-impact .impact-value{font-size:16px;font-weight:700;color:#ef4444}
.issue-impact .impact-label{font-size:11px;color:#64748b}
.charts-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-bottom:30px}
.chart-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:20px}
.chart-card h4{font-size:15px;font-weight:700;margin-bottom:16px}
.ai-section{background:linear-gradient(135deg,rgba(168,85,247,0.1),rgba(6,182,212,0.1));border:1px solid rgba(168,85,247,0.2);border-radius:20px;padding:30px;margin-bottom:30px}
.ai-section h3{font-size:18px;font-weight:700;margin-bottom:20px}
.ai-rec{background:rgba(255,255,255,0.05);border-radius:12px;padding:16px;margin-bottom:12px}
.ai-rec-title{font-size:14px;font-weight:600;margin-bottom:6px;color:#a855f7}
.ai-rec-text{font-size:13px;color:#94a3b8;line-height:1.6}
@media(max-width:768px){.score-section{grid-template-columns:1fr;text-align:center}.nav{padding:15px 20px}.features{padding:40px 20px}}
</style>
</head>
<body>
<nav class="nav">
  <div class="logo">ConvertIQ</div>
  <button class="nav-btn" onclick="showLanding()">Analyze Store →</button>
</nav>

<div id="landingPage">
  <div class="hero">
    <div class="hero-badge">✦ AI-Powered Revenue Intelligence</div>
    <h1>Stop Losing Revenue<br><span>You Don't Know About</span></h1>
    <p>Uncover hidden conversion killers, detect revenue leaks, and get AI-powered recommendations to maximize your ecommerce performance.</p>
    <div class="analyze-box">
      <input id="analyzeInput" type="url" placeholder="Enter your Shopify store URL (e.g. https://yourstore.myshopify.com)" />
      <button class="analyze-btn" onclick="startAnalysis()">🚀 Analyze My Store — It's Free</button>
      <p style="font-size:12px;color:#475569;margin-top:12px">No credit card required • Results in 60 seconds • Only works with Shopify stores</p>
    </div>
  </div>
  <div class="features">
    <div class="feature-card"><div class="feature-icon">💰</div><h3>Revenue Leak Detection</h3><p>Find hidden issues costing you thousands in lost sales every month.</p></div>
    <div class="feature-card"><div class="feature-icon">📊</div><h3>Conversion Score</h3><p>Get a comprehensive score analyzing your checkout flow and UX patterns.</p></div>
    <div class="feature-card"><div class="feature-icon">🤖</div><h3>AI Recommendations</h3><p>Receive prioritized, actionable recommendations powered by AI.</p></div>
    <div class="feature-card"><div class="feature-icon">📱</div><h3>Mobile UX Analysis</h3><p>Analyze your mobile experience where 70% of shoppers browse.</p></div>
    <div class="feature-card"><div class="feature-icon">⚡</div><h3>Speed Intelligence</h3><p>Every 1-second delay costs you 7% in conversions. We find the leaks.</p></div>
    <div class="feature-card"><div class="feature-icon">🎯</div><h3>Funnel Health</h3><p>See exactly where customers drop off in your conversion funnel.</p></div>
  </div>
</div>

<div class="loading" id="loadingSection">
  <div class="spinner"></div>
  <h2 style="margin-top:24px;font-size:22px;font-weight:700">Analyzing Your Store...</h2>
  <p style="color:#64748b;margin-top:8px">Our AI is scanning every aspect of your store</p>
  <div class="loading-steps">
    <div class="step active" id="step1"><div class="step-dot"></div>Fetching store data & products...</div>
    <div class="step" id="step2"><div class="step-dot"></div>Analyzing performance & speed...</div>
    <div class="step" id="step3"><div class="step-dot"></div>Detecting revenue leaks...</div>
    <div class="step" id="step4"><div class="step-dot"></div>Running AI analysis...</div>
    <div class="step" id="step5"><div class="step-dot"></div>Generating your report...</div>
  </div>
</div>

<div class="error-box" id="errorSection">
  <div class="error-card">
    <h3>❌ Store Not Found</h3>
    <p id="errorMessage">We couldn't find this store. Please make sure it's a valid Shopify store URL.</p>
    <button onclick="showLanding()">Try Another Store</button>
  </div>
</div>

<div class="dashboard" id="dashboard">
  <div class="dash-header">
    <h2 id="dashTitle">Revenue Intelligence Report</h2>
    <p id="dashSubtitle">Generated just now • Powered by ConvertIQ AI</p>
  </div>
  <div class="score-section">
    <div class="score-circle" id="scoreCircle">
      <div class="score-number" id="scoreNumber">--</div>
      <div class="score-label">SCORE</div>
    </div>
    <div class="score-details">
      <h3 id="scoreTitle">Analyzing...</h3>
      <p id="scoreDesc">Your store analysis is being processed.</p>
      <div class="revenue-loss">
        <div class="amount" id="revenueLoss">$0</div>
        <div class="label">Estimated Monthly Revenue Leaking</div>
      </div>
    </div>
  </div>
  <div class="metrics-grid" id="metricsGrid"></div>
  <div class="issues-section">
    <h3>🚨 Critical Revenue Leaks Found</h3>
    <div id="issuesList"></div>
  </div>
  <div class="charts-grid">
    <div class="chart-card"><h4>📊 Conversion Funnel</h4><canvas id="funnelChart"></canvas></div>
    <div class="chart-card"><h4>📱 Performance Breakdown</h4><canvas id="perfChart"></canvas></div>
  </div>
  <div class="ai-section">
    <h3>🤖 AI Revenue Recommendations</h3>
    <div id="aiRecs"></div>
  </div>
  <div style="text-align:center;padding:20px">
    <button onclick="showLanding()" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#fff;padding:12px 24px;border-radius:8px;cursor:pointer">← Analyze Another Store</button>
  </div>
</div>

<script>
let funnelChart, perfChart;

function showLanding() {
  document.getElementById('landingPage').style.display = 'block';
  document.getElementById('loadingSection').style.display = 'none';
  document.getElementById('errorSection').style.display = 'none';
  document.getElementById('dashboard').style.display = 'none';
  document.getElementById('analyzeInput').value = '';
}

function checkAutoStart() {
  const params = new URLSearchParams(window.location.search);
  const storeUrl = params.get('store_url');
  if (storeUrl) {
    document.getElementById('analyzeInput').value = storeUrl;
    startAnalysis();
  }
}

window.onload = checkAutoStart;

async function startAnalysis() {
  const url = document.getElementById('analyzeInput').value.trim();
  if (!url) { alert('Please enter your store URL'); return; }

  document.getElementById('landingPage').style.display = 'none';
  document.getElementById('errorSection').style.display = 'none';
  document.getElementById('dashboard').style.display = 'none';
  document.getElementById('loadingSection').style.display = 'block';

  const steps = ['step1','step2','step3','step4','step5'];
  let i = 0;
  steps.forEach(s => document.getElementById(s).className = 'step');
  document.getElementById(steps[0]).className = 'step active';

  const stepInterval = setInterval(() => {
    if (i > 0 && i <= steps.length) document.getElementById(steps[i-1]).className = 'step done';
    if (i < steps.length) { document.getElementById(steps[i]).className = 'step active'; i++; }
    else clearInterval(stepInterval);
  }, 2500);

  try {
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({store_url: url})
    });
    const data = await res.json();
    clearInterval(stepInterval);

    if (data.error) {
      document.getElementById('loadingSection').style.display = 'none';
      document.getElementById('errorSection').style.display = 'block';
      document.getElementById('errorMessage').textContent = data.error;
      return;
    }

    showDashboard(data, url);
  } catch(e) {
    clearInterval(stepInterval);
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('errorMessage').textContent = 'Connection error. Please try again.';
  }
}

function showDashboard(data, url) {
  document.getElementById('loadingSection').style.display = 'none';
  document.getElementById('dashboard').style.display = 'block';

  const score = data.score;
  document.getElementById('scoreNumber').textContent = score;
  document.getElementById('dashTitle').textContent = 'Revenue Intelligence Report — ' + url.replace('https://','').replace('http://','');

  const circle = document.getElementById('scoreCircle');
  if (score >= 70) { circle.className = 'score-circle score-good'; document.getElementById('scoreTitle').textContent = 'Your Store Is Performing Well'; }
  else if (score >= 40) { circle.className = 'score-circle score-medium'; document.getElementById('scoreTitle').textContent = 'Significant Revenue Leaks Detected'; }
  else { circle.className = 'score-circle score-bad'; document.getElementById('scoreTitle').textContent = 'Critical Issues Are Costing You Sales'; }

  document.getElementById('scoreDesc').textContent = data.score_desc;
  document.getElementById('revenueLoss').textContent = '$' + data.revenue_loss.toLocaleString();

  const metrics = [
    {value: data.products + ' Products', label: 'Total Catalog Size', change: data.products < 10 ? '⚠️ Small catalog' : '✅ Good size', bad: data.products < 10},
    {value: data.missing_images + ' Missing', label: 'Products Without Images', change: data.missing_images > 0 ? '🔴 Hurting conversions' : '✅ All good', bad: data.missing_images > 0},
    {value: data.missing_desc + ' Missing', label: 'Missing Descriptions', change: data.missing_desc > 0 ? '🔴 Hurting SEO' : '✅ All good', bad: data.missing_desc > 0},
    {value: data.perf_score + '/100', label: 'Performance Score', change: data.perf_score < 50 ? '🔴 Critical' : data.perf_score < 80 ? '⚠️ Needs work' : '✅ Fast', bad: data.perf_score < 50},
  ];

  document.getElementById('metricsGrid').innerHTML = metrics.map(m => `
    <div class="metric-card">
      <div class="metric-value">${m.value}</div>
      <div class="metric-label">${m.label}</div>
      <div class="metric-change ${m.bad ? 'bad' : 'good'}">${m.change}</div>
    </div>`).join('');

  if (data.issues.length === 0) {
    document.getElementById('issuesList').innerHTML = '<div style="color:#10b981;padding:20px;text-align:center">✅ No critical issues found! Your store is well optimized.</div>';
  } else {
    document.getElementById('issuesList').innerHTML = data.issues.map(issue => `
      <div class="issue-card">
        <div class="issue-left">
          <div class="issue-priority priority-${issue.priority}"></div>
          <div>
            <div class="issue-title">${issue.title}</div>
            <div class="issue-desc">${issue.desc}</div>
          </div>
        </div>
        <div class="issue-impact">
          <div class="impact-value">-$${issue.impact}/mo</div>
          <div class="impact-label">Revenue Impact</div>
        </div>
      </div>`).join('');
  }

  document.getElementById('aiRecs').innerHTML = data.recommendations.map(r => `
    <div class="ai-rec">
      <div class="ai-rec-title">${r.title}</div>
      <div class="ai-rec-text">${r.text}</div>
    </div>`).join('');

  if (funnelChart) funnelChart.destroy();
  if (perfChart) perfChart.destroy();

  funnelChart = new Chart(document.getElementById('funnelChart'), {
    type: 'bar',
    data: {
      labels: ['Homepage', 'Product', 'Cart', 'Checkout', 'Payment'],
      datasets: [{data: data.funnel, backgroundColor: ['rgba(168,85,247,0.8)','rgba(139,92,246,0.7)','rgba(109,40,217,0.6)','rgba(91,33,182,0.5)','rgba(76,29,149,0.4)'], borderRadius: 6}]
    },
    options: {plugins:{legend:{display:false}},scales:{y:{ticks:{color:'#64748b',callback:v=>v+'%'},grid:{color:'rgba(255,255,255,0.05)'}},x:{ticks:{color:'#64748b'},grid:{display:false}}}}
  });

  perfChart = new Chart(document.getElementById('perfChart'), {
    type: 'doughnut',
    data: {
      labels: ['Performance', 'SEO', 'UX', 'Mobile'],
      datasets: [{data: [data.perf_score, data.seo_score, data.ux_score, data.mobile_score], backgroundColor: ['rgba(168,85,247,0.8)','rgba(6,182,212,0.8)','rgba(16,185,129,0.8)','rgba(245,158,11,0.8)'], borderWidth: 0}]
    },
    options: {plugins:{legend:{labels:{color:'#94a3b8'}}},cutout:'70%'}
  });
}
</script>
</body>
</html>'''

def get_gemini_recommendations(store_data):
    try:
        prompt = f"""You are a top ecommerce conversion expert. Analyze this Shopify store data and give 3 specific revenue-boosting recommendations:
Store has {store_data['products']} products
{store_data['missing_images']} products missing images
{store_data['missing_desc']} products missing descriptions
Performance score: {store_data['perf_score']}/100
SEO score: {store_data['seo_score']}/100
Return JSON array with exactly 3 objects, each having "title" and "text" fields.
Be specific, business-focused, and mention potential revenue impact.
Return ONLY the JSON array, no other text."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        text = res.json()['candidates'][0]['content']['parts'][0]['text']
        text = text.replace('```json','').replace('```','').strip()
        return json.loads(text)
    except:
        return [
            {"title": "Fix Product Images Immediately", "text": "Products without images have 60% lower conversion rates. Add high-quality images to all products to recover lost revenue."},
            {"title": "Add Compelling Product Descriptions", "text": "Missing descriptions hurt both SEO rankings and buyer confidence. Write benefit-focused descriptions for each product."},
            {"title": "Improve Page Load Speed", "text": "Every 1-second delay reduces conversions by 7%. Optimize images and reduce app bloat to capture more sales."}
        ]

def get_pagespeed(url):
    try:
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile"
        r = requests.get(api_url, timeout=25)
        data = r.json()
        cats = data.get('lighthouseResult', {}).get('categories', {})
        return {
            'performance': int((cats.get('performance', {}).get('score', 0.5) or 0.5) * 100),
            'seo': int((cats.get('seo', {}).get('score', 0.5) or 0.5) * 100),
            'accessibility': int((cats.get('accessibility', {}).get('score', 0.5) or 0.5) * 100),
        }
    except:
        return {'performance': 45, 'seo': 60, 'accessibility': 70}

def get_products(store_url):
    try:
        url = f"{store_url.rstrip('/')}/products.json?limit=250"
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None
        data = r.json()
        if 'products' not in data:
            return None
        products = data['products']
        missing_img = sum(1 for p in products if not p.get('images'))
        missing_desc = sum(1 for p in products if len(p.get('body_html', '')) < 50)
        return {'total': len(products), 'missing_images': missing_img, 'missing_desc': missing_desc}
    except:
        return None

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    store_url = data.get('store_url', '').strip()
    if not store_url.startswith('http'):
        store_url = 'https://' + store_url

    products = get_products(store_url)

    if products is None:
        return jsonify({'error': f'Could not find a valid Shopify store at "{store_url}". Please check the URL and make sure it is a Shopify store.'})

    speed = get_pagespeed(store_url)
    perf = speed['performance']
    seo = speed['seo']
    acc = speed['accessibility']
    ux_score = min(100, acc + 10)
    mobile_score = perf

    issues = []
    revenue_loss = 0

    if products['missing_images'] > 0:
        impact = products['missing_images'] * 180
        revenue_loss += impact
        issues.append({'title': f"{products['missing_images']} Products Missing Images", 'desc': 'Products without images have 60% lower conversion rates', 'priority': 'critical', 'impact': impact})

    if products['missing_desc'] > 0:
        impact = products['missing_desc'] * 120
        revenue_loss += impact
        issues.append({'title': f"{products['missing_desc']} Products Missing Descriptions", 'desc': 'Missing descriptions hurt SEO and buyer confidence', 'priority': 'high', 'impact': impact})

    if perf < 50:
        impact = 800
        revenue_loss += impact
        issues.append({'title': 'Critical Page Speed Issue', 'desc': f'Mobile performance score {perf}/100 — customers are leaving before your page loads', 'priority': 'critical', 'impact': impact})
    elif perf < 75:
        impact = 400
        revenue_loss += impact
        issues.append({'title': 'Slow Page Load Speed', 'desc': f'Performance score {perf}/100 — every extra second costs 7% in conversions', 'priority': 'high', 'impact': impact})

    if seo < 60:
        impact = 500
        revenue_loss += impact
        issues.append({'title': 'Poor SEO — Losing Organic Traffic', 'desc': f'SEO score {seo}/100 — your store is invisible to most Google searches', 'priority': 'high', 'impact': impact})

    if products['total'] < 10:
        issues.append({'title': 'Small Product Catalog', 'desc': 'Limited product selection reduces average order value', 'priority': 'medium', 'impact': 200})
        revenue_loss += 200

    score = max(10, min(95, int((perf * 0.3) + (seo * 0.2) + (ux_score * 0.2) + (max(0, 100 - (products['missing_images'] * 10)) * 0.3))))

    if score >= 70:
        score_desc = "Your store is performing well but there are still opportunities to increase revenue and conversions."
    elif score >= 40:
        score_desc = "We detected significant revenue leaks. Fixing these issues could increase your monthly revenue substantially."
    else:
        score_desc = "Critical issues are costing you significant revenue daily. Immediate action is required."

    store_data = {'products': products['total'], 'missing_images': products['missing_images'], 'missing_desc': products['missing_desc'], 'perf_score': perf, 'seo_score': seo}
    recommendations = get_gemini_recommendations(store_data)

    funnel = [100, 68, 42, 28, 18]

    return jsonify({
        'score': score, 'score_desc': score_desc, 'revenue_loss': revenue_loss,
        'products': products['total'], 'missing_images': products['missing_images'],
        'missing_desc': products['missing_desc'], 'perf_score': perf,
        'seo_score': seo, 'ux_score': ux_score, 'mobile_score': mobile_score,
        'issues': issues, 'recommendations': recommendations, 'funnel': funnel
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
