"""
SENTRY DASHBOARD v3.0 - Complete with Equity Chart
Professional UI, real-time scores, equity curve
"""

from flask import Flask, jsonify, render_template_string
from datetime import datetime
import json

app = Flask(__name__)
bot_instance = None

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentry Bot v3.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: #0a0e17; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif;
            padding: 15px; max-width: 900px; margin: auto;
        }
        .header {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 2px solid #00d4aa; padding-bottom: 15px; margin-bottom: 15px;
            flex-wrap: wrap; gap: 10px;
        }
        h1 { color: #00d4aa; font-size: 1.6em; }
        .badge {
            background: #00d4aa; color: #000; padding: 4px 12px;
            border-radius: 20px; font-size: 0.75em; font-weight: bold;
        }
        .card {
            background: #111827; border: 1px solid #1e293b;
            border-radius: 12px; padding: 18px; margin: 12px 0;
        }
        .card h3 { color: #888; font-size: 0.8em; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 1px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; }
        .stat { text-align: center; padding: 8px; }
        .stat .val { font-size: 1.5em; font-weight: bold; color: #00d4aa; }
        .stat .lbl { font-size: 0.7em; color: #666; text-transform: uppercase; margin-top: 4px; }
        .green { color: #00ff88 !important; }
        .red { color: #ff4757 !important; }
        .yellow { color: #ffa502 !important; }
        
        table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 0.82em; }
        th, td { padding: 10px 8px; text-align: left; border-bottom: 1px solid #1e293b; }
        th { color: #666; font-size: 0.75em; text-transform: uppercase; }
        tr:hover { background: #1a1f2e; }
        
        .score-badge {
            display: inline-block; padding: 3px 10px; border-radius: 4px;
            font-size: 0.8em; font-weight: bold; min-width: 35px; text-align: center;
        }
        .score-high { background: #00d4aa22; color: #00d4aa; border: 1px solid #00d4aa44; }
        .score-med { background: #ffa50222; color: #ffa502; border: 1px solid #ffa50244; }
        .score-low { background: #ff475722; color: #ff4757; border: 1px solid #ff475744; }
        
        .equity-chart {
            background: #0a0e17; padding: 12px; border-radius: 6px;
            font-family: 'Courier New', monospace; font-size: 0.6em;
            line-height: 1.3; overflow-x: auto; white-space: pre;
            max-height: 300px; overflow-y: auto;
        }
        .equity-bar { color: #00d4aa; }
        .equity-up { color: #00ff88; }
        .equity-down { color: #ff4757; }
        
        @media (max-width: 600px) {
            .grid { grid-template-columns: repeat(2, 1fr); }
            .stat .val { font-size: 1.2em; }
            table { font-size: 0.7em; }
            th, td { padding: 6px 4px; }
            .equity-chart { font-size: 0.5em; }
        }
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="header">
        <div>
            <h1>SENTRY BOT v3.0</h1>
            <span style="color:#666;font-size:0.75em;">{{ update_time }} | Auto-Refresh 30s</span>
        </div>
        <span class="badge">{{ mode }}</span>
    </div>
    
    <div class="card">
        <h3>Portfolio Overview</h3>
        <div class="grid">
            <div class="stat">
                <div class="lbl">Total Value</div>
                <div class="val">${{ "%.2f"|format(total_value) }}</div>
            </div>
            <div class="stat">
                <div class="lbl">Cash</div>
                <div class="val">${{ "%.2f"|format(stats.balance) }}</div>
            </div>
            <div class="stat">
                <div class="lbl">P/L</div>
                <div class="val {{ 'green' if total_pl >= 0 else 'red' }}">
                    ${{ "%.2f"|format(total_pl) }}
                </div>
            </div>
            <div class="stat">
                <div class="lbl">Return</div>
                <div class="val {{ 'green' if total_return >= 0 else 'red' }}">
                    {{ "%.2f"|format(total_return) }}%
                </div>
            </div>
            <div class="stat">
                <div class="lbl">Trades</div>
                <div class="val">{{ total_trades }}</div>
            </div>
            <div class="stat">
                <div class="lbl">Win Rate</div>
                <div class="val {{ 'green' if win_rate >= 50 else 'yellow' }}">
                    {{ "%.1f"|format(win_rate) }}%
                </div>
            </div>
        </div>
    </div>
    
    <!-- Equity Curve Chart -->
    <div class="card">
        <h3>Equity Curve (Portfolio Value Over Time)</h3>
        <div class="equity-chart" id="equity-chart">Loading...</div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:0.7em;color:#666;">
            <span>High: ${{ "%.2f"|format(equity_high) }}</span>
            <span>Start: $1000.00</span>
            <span>Low: ${{ "%.2f"|format(equity_low) }}</span>
        </div>
    </div>
    
    <div class="card">
        <h3>Open Positions ({{ positions|length }})</h3>
        {% if positions %}
        <table>
            <tr><th>Token</th><th>Amount</th><th>Entry</th><th>Current</th><th>P/L</th><th>Score</th></tr>
            {% for p in positions %}
            <tr>
                <td><b>${{ p.symbol }}</b></td>
                <td>{{ "%.0f"|format(p.amount) }}</td>
                <td>${{ "%.8f"|format(p.buy_price) }}</td>
                <td>${{ "%.8f"|format(p.current_price) }}</td>
                <td class="{{ 'green' if p.pnl >= 0 else 'red' }}">
                    {{ "%+.2f"|format(p.pnl) }}%
                </td>
                <td>
                    {% set score = p.score %}
                    {% if score >= 70 %}
                        <span class="score-badge score-high">{{ score }}</span>
                    {% elif score >= 45 %}
                        <span class="score-badge score-med">{{ score }}</span>
                    {% else %}
                        <span class="score-badge score-low">{{ score }}</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p style="color:#666;text-align:center;padding:20px;">No open positions - waiting for high-conviction setup</p>
        {% endif %}
    </div>
    
    <div class="card">
        <h3>Recent Trades</h3>
        {% if trades %}
        <table>
            <tr><th>Time</th><th>Action</th><th>Token</th><th>Amount</th><th>Price</th><th>Profit</th></tr>
            {% for t in trades[-15:]|reverse %}
            <tr>
                <td style="color:#666;">{{ t.time[11:19] }}</td>
                <td class="{{ 'green' if t.action=='BUY' else 'red' }}">{{ t.action }}</td>
                <td>${{ t.token }}</td>
                <td>{{ "%.0f"|format(t.amount) }}</td>
                <td>${{ "%.8f"|format(t.price) }}</td>
                <td class="{{ 'green' if t.get('profit', 0) > 0 else 'red' if t.get('profit', 0) < 0 else '' }}">
                    {{ "$%.2f"|format(t.get('profit', 0)) if t.get('profit') is not none and t.get('profit') != 0 else '-' }}
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p style="color:#666;text-align:center;padding:20px;">No trades yet</p>
        {% endif %}
    </div>
    
    <script>
        // Fetch equity curve data
        fetch('/api/equity')
            .then(r => r.json())
            .then(data => {
                if(data.points && data.points.length > 0) {
                    let chart = '';
                    let points = data.points.slice(-60); // Last 60 points
                    let max = data.high || 1005;
                    let min = data.low || 995;
                    let range = max - min || 1;
                    let width = 60;
                    
                    for(let p of points) {
                        let height = ((p.balance - min) / range) * 15;
                        let bars = '';
                        for(let i = 0; i < Math.max(1, Math.floor(height)); i++) {
                            bars += '|';
                        }
                        let color = p.balance >= 1000 ? '#00ff88' : '#ff4757';
                        chart += `<span style="color:${color}">${bars.padEnd(20, ' ')} $${p.balance.toFixed(2)} (${p.return_pct.toFixed(2)}%)</span>\n`;
                    }
                    document.getElementById('equity-chart').innerHTML = chart;
                } else {
                    document.getElementById('equity-chart').innerHTML = '<span style="color:#666;">Collecting data... Chart will appear after a few minutes.</span>';
                }
            })
            .catch(() => {
                document.getElementById('equity-chart').innerHTML = '<span style="color:#666;">Equity data loading...</span>';
            });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    stats = {'balance': 1000, 'total_profit_loss': 0, 'total_return_percent': 0,
             'total_trades': 0, 'win_rate': 0, 'open_positions': 0}
    positions = []
    trades = []
    total_value = 1000
    total_pl = 0
    total_return = 0
    total_trades = 0
    win_rate = 0
    mode = "PAPER"
    equity_high = 1000
    equity_low = 1000
    
    if bot_instance and bot_instance.trader:
        stats = bot_instance.trader.get_stats()
        trades = bot_instance.trader.trade_history
        total_trades = stats.get('total_trades', 0)
        win_rate = stats.get('win_rate', 0)
        
        total_value = stats['balance']
        positions = []
        
        for sym, pos in bot_instance.trader.positions.items():
            current_price = pos['buy_price']
            score = 0
            
            if hasattr(bot_instance, 'scorer') and hasattr(bot_instance, 'token_scanner'):
                data = bot_instance.token_scanner.get_real_price(sym)
                if data:
                    current_price = data['price']
                    try:
                        token_data = {
                            'telegram_score': bot_instance.telegram_scanner.get_telegram_conviction_points(sym) if hasattr(bot_instance, 'telegram_scanner') else 0,
                            'onchain_score': bot_instance.onchain_scanner.get_onchain_conviction_points(sym) if hasattr(bot_instance, 'onchain_scanner') else 0,
                            'momentum_score': 5,
                            'volume': data.get('volume_24h', 0),
                            'liquidity': data.get('liquidity', 0),
                            'risk_score': 0,
                            'price_change_24h': data.get('price_change_24h', 0) or 0,
                        }
                        score_result = bot_instance.scorer.calculate_score(token_data)
                        score = score_result['total_score']
                    except:
                        score = int(pos.get('conviction', 0.5) * 110)
            else:
                score = int(pos.get('conviction', 0.5) * 110)
            
            pos_value = pos['amount'] * current_price
            total_value += pos_value
            pnl = ((current_price - pos['buy_price']) / pos['buy_price']) * 100
            
            positions.append({
                'symbol': sym,
                'amount': pos['amount'],
                'buy_price': pos['buy_price'],
                'current_price': current_price,
                'pnl': pnl,
                'score': score
            })
        
        total_pl = total_value - bot_instance.trader.initial_balance
        total_return = (total_pl / bot_instance.trader.initial_balance) * 100
        
        if hasattr(bot_instance, 'scorer'):
            mode = "MAX PROFIT"
        
        # Equity curve data
        if hasattr(bot_instance, 'equity_tracker'):
            equity = bot_instance.equity_tracker.get_curve()
            equity_high = equity.get('high', total_value)
            equity_low = equity.get('low', total_value)
    
    return render_template_string(
        HTML,
        stats=stats, positions=positions, trades=trades,
        total_value=total_value, total_pl=total_pl,
        total_return=total_return, total_trades=total_trades,
        win_rate=win_rate, mode=mode,
        equity_high=equity_high, equity_low=equity_low,
        update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/api/stats')
def api_stats():
    if bot_instance and bot_instance.trader:
        return jsonify(bot_instance.trader.get_stats())
    return jsonify({"status": "offline"})

@app.route('/api/health')
def api_health():
    if bot_instance:
        return jsonify({
            'status': 'running',
            'scans': bot_instance.scans,
            'mode': 'max_profit',
            'uptime': str(datetime.now() - bot_instance.start_time) if bot_instance.start_time else 'N/A'
        })
    return jsonify({"status": "offline"})

@app.route('/api/equity')
def api_equity():
    if bot_instance and hasattr(bot_instance, 'equity_tracker'):
        return jsonify(bot_instance.equity_tracker.get_curve())
    return jsonify({"points": [], "start_balance": 1000, "current_balance": 1000, "high": 1000, "low": 1000})

def start_dashboard(bot=None, port=8080):
    global bot_instance
    bot_instance = bot
    app.run(host='0.0.0.0', port=port, debug=False)