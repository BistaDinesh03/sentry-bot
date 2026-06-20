"""
TELEGRAM BOT v3.0 - Simple & Fast
Instant responses, clean messages, easy to understand
"""

import requests
import logging
import threading
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramAlerts:
    """Telegram bot - Alerts + Instant Commands"""
    
    def __init__(self, token=None, chat_id=None):
        self.token = token
        self.chat_id = chat_id
        self.enabled = bool(token and chat_id)
        self.bot_instance = None
        self.last_update_id = 0
        self.running = True
        
        if self.enabled:
            logger.info(f"Telegram ready for chat {chat_id}")
            # Start background command listener
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()
            # Send welcome
            self.send_welcome()
    
    def send_welcome(self):
        """Send welcome message with commands"""
        msg = (
            "Sentry Bot v3.0\n\n"
            "Commands:\n"
            "/s - Quick status\n"
            "/p - Open positions\n"
            "/t - Recent trades\n"
            "/$ - Profit/Loss\n"
            "/score BONK - Token score\n"
            "/h - Help"
        )
        self._send(msg)
    
    def _send(self, text):
        """Send message to Telegram"""
        if not self.enabled:
            return False
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            requests.post(url, json={
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }, timeout=10)
            return True
        except:
            return False
    
    def _listen_loop(self):
        """Background thread - checks for commands every 2 seconds"""
        while self.running:
            try:
                self._check_incoming()
            except:
                pass
            time.sleep(2)
    
    def _check_incoming(self):
        """Check for new messages and respond"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 5,
                'allowed_updates': ['message']
            }
            r = requests.get(url, params=params, timeout=8)
            
            if r.status_code == 200:
                data = r.json()
                for update in data.get('result', []):
                    self.last_update_id = update['update_id']
                    msg = update.get('message', {})
                    text = msg.get('text', '')
                    user_id = str(msg.get('chat', {}).get('id', ''))
                    
                    # Only respond to authorized user
                    if user_id == self.chat_id and text.startswith('/'):
                        self._handle(text)
        except:
            pass
    
    def _handle(self, command):
        """Handle incoming command"""
        cmd = command.lower().strip().split()[0]
        
        if cmd in ['/s', '/status']:
            self._cmd_status()
        elif cmd in ['/p', '/positions']:
            self._cmd_positions()
        elif cmd in ['/t', '/trades']:
            self._cmd_trades()
        elif cmd in ['/$', '/pnl']:
            self._cmd_pnl()
        elif cmd == '/score':
            parts = command.split()
            if len(parts) > 1:
                self._cmd_score(parts[1].upper().replace('$', ''))
            else:
                self._send("Use: /score TOKEN\nExample: /score BONK")
        elif cmd in ['/h', '/help']:
            self._cmd_help()
        elif cmd == '/start':
            self.send_welcome()
    
    def _cmd_help(self):
        msg = (
            "<b>Commands</b>\n\n"
            "/s - Portfolio status\n"
            "/p - Open positions\n"
            "/t - Last 10 trades\n"
            "/$ - Profit/Loss summary\n"
            "/score TOKEN - Score any token\n"
            "/h - This help\n\n"
            "<i>Auto-alerts on every trade!</i>"
        )
        self._send(msg)
    
    def _cmd_status(self):
        if not self.bot_instance:
            self._send("Waiting for bot data...")
            return
        
        try:
            t = self.bot_instance.trader
            stats = t.get_stats()
            
            total = stats['balance']
            for sym, pos in t.positions.items():
                d = self.bot_instance.token_scanner.get_real_price(sym)
                total += pos['amount'] * (d['price'] if d else pos['buy_price'])
            
            pl = total - t.initial_balance
            ret = (pl / t.initial_balance) * 100
            
            emoji = "GREEN" if pl >= 0 else "RED"
            
            msg = (
                f"<b>PORTFOLIO</b>\n\n"
                f"Value: ${total:.2f}\n"
                f"Cash: ${stats['balance']:.2f}\n"
                f"P/L: {pl:+.2f} ({ret:+.1f}%)\n"
                f"Positions: {stats['open_positions']}/6\n"
                f"Trades: {stats['total_trades']}\n"
                f"Win Rate: {stats['win_rate']:.1f}%\n"
                f"\n{datetime.now().strftime('%H:%M:%S')}"
            )
            self._send(msg)
        except Exception as e:
            self._send(f"Error: {e}")
    
    def _cmd_positions(self):
        if not self.bot_instance or not self.bot_instance.trader.positions:
            self._send("No open positions")
            return
        
        msg = "<b>POSITIONS</b>\n\n"
        
        for sym, pos in self.bot_instance.trader.positions.items():
            d = self.bot_instance.token_scanner.get_real_price(sym)
            cp = d['price'] if d else pos['buy_price']
            pnl = ((cp - pos['buy_price']) / pos['buy_price']) * 100
            
            emoji = "GREEN" if pnl > 0 else "RED" if pnl < 0 else "WHITE"
            
            msg += f"{emoji} <b>{sym}</b>\n"
            msg += f"  {pos['amount']:,.0f} tokens\n"
            msg += f"  Entry: ${pos['buy_price']:.8f}\n"
            msg += f"  Now: ${cp:.8f}\n"
            msg += f"  P/L: {pnl:+.2f}%\n\n"
        
        self._send(msg)
    
    def _cmd_trades(self):
        if not self.bot_instance:
            self._send("Waiting for bot data...")
            return
        
        trades = self.bot_instance.trader.trade_history[-10:]
        
        if not trades:
            self._send("No trades yet")
            return
        
        msg = "<b>LAST 10 TRADES</b>\n\n"
        
        for t in reversed(trades):
            act = "BUY" if t['action'] == 'BUY' else "SELL"
            emoji = "BUY" if t['action'] == 'BUY' else ("PROFIT" if t.get('profit', 0) > 0 else "LOSS")
            profit = t.get('profit', 0)
            pstr = f" (${profit:+.2f})" if profit else ""
            
            msg += f"{emoji} <b>{t['token']}</b>{pstr}\n"
            msg += f"  {t['amount']:,.0f} @ ${t['price']:.8f}\n"
            msg += f"  {t['time'][11:19]}\n\n"
        
        self._send(msg)
    
    def _cmd_pnl(self):
        if not self.bot_instance:
            self._send("Waiting for bot data...")
            return
        
        stats = self.bot_instance.trader.get_stats()
        perf = self.bot_instance.performance
        
        today = perf.daily_pnl.get(datetime.now().strftime('%Y-%m-%d'), 0)
        
        msg = (
            f"<b>PROFIT / LOSS</b>\n\n"
            f"Today: ${today:+.2f}\n"
            f"Total: ${stats['total_profit_loss']:+.2f}\n"
            f"Win Rate: {stats['win_rate']:.1f}%\n"
            f"Trades: {stats['total_trades']}\n"
            f"\n{datetime.now().strftime('%H:%M:%S')}"
        )
        self._send(msg)
    
    def _cmd_score(self, symbol):
        if not self.bot_instance or not hasattr(self.bot_instance, 'scorer'):
            self._send("Scoring not available")
            return
        
        try:
            data = self.bot_instance.token_scanner.get_real_price(symbol)
            if not data:
                self._send(f"{symbol} not found")
                return
            
            tg = self.bot_instance.telegram_scanner.get_telegram_conviction_points(symbol) if hasattr(self.bot_instance, 'telegram_scanner') else 0
            oc = self.bot_instance.onchain_scanner.get_onchain_conviction_points(symbol) if hasattr(self.bot_instance, 'onchain_scanner') else 0
            
            result = self.bot_instance.scorer.calculate_score({
                'telegram_score': tg,
                'onchain_score': oc if oc > 0 else 0,
                'momentum_score': 5,
                'volume': data.get('volume_24h', 0),
                'liquidity': data.get('liquidity', 0),
                'risk_score': 0,
                'price_change_24h': data.get('price_change_24h', 0) or 0,
            })
            
            b = result['breakdown']
            rec = result['recommendation']
            remoji = "STRONG BUY" if rec == "STRONG_BUY" else ("BUY" if rec == "BUY" else "SKIP")
            
            msg = (
                f"<b>{symbol} SCORE: {result['total_score']}/110</b>\n"
                f"Verdict: {remoji}\n\n"
                f"Telegram: {b['telegram']}/25\n"
                f"On-Chain: {b['onchain']}/20\n"
                f"Momentum: {b['momentum']}/15\n"
                f"Volume: {b['volume']}/15\n"
                f"Liquidity: {b['liquidity']}/15\n"
                f"Safety: {b['safety']}/10\n"
                f"Entry: {b['entry_timing']}/10\n\n"
                f"Price: ${data['price']:.8f}\n"
                f"Vol: ${data['volume_24h']:,.0f}"
            )
            self._send(msg)
        except Exception as e:
            self._send(f"Error: {e}")
    
    # ---- TRADE ALERTS ----
    
    def alert_buy(self, token, amount, price, cost, conviction, reason=""):
        emoji = "STRONG" if conviction > 0.7 else ""
        msg = (
            f"BUY {emoji}\n\n"
            f"<b>{token}</b>\n"
            f"{amount:,.0f} tokens\n"
            f"Price: ${price:.8f}\n"
            f"Cost: ${cost:.2f}\n"
            f"Score: {int(conviction * 110)}/110\n"
            f"\n{datetime.now().strftime('%H:%M:%S')}"
        )
        self._send(msg)
    
    def alert_sell(self, token, amount, price, revenue, profit, reason=""):
        emoji = "PROFIT" if profit > 0 else "LOSS"
        msg = (
            f"SELL {emoji}\n\n"
            f"<b>{token}</b>\n"
            f"{amount:,.0f} tokens\n"
            f"Price: ${price:.8f}\n"
            f"Revenue: ${revenue:.2f}\n"
            f"Profit: ${profit:+.2f}\n"
            f"Signal: {reason[:80]}\n"
            f"\n{datetime.now().strftime('%H:%M:%S')}"
        )
        self._send(msg)
    
    def alert_portfolio(self, balance, total_value, pl, positions, trades, win_rate):
        emoji = "GREEN" if pl >= 0 else "RED"
        msg = (
            f"HOURLY UPDATE\n\n"
            f"Value: ${total_value:.2f}\n"
            f"Cash: ${balance:.2f}\n"
            f"P/L: {pl:+.2f}\n"
            f"Positions: {positions}\n"
            f"Trades: {trades}\n"
            f"Win: {win_rate:.1f}%\n"
            f"\n{datetime.now().strftime('%H:%M:%S')}"
        )
        self._send(msg)
    
    def alert_scam_blocked(self, token, reason):
        msg = (
            f"SCAM BLOCKED\n\n"
            f"<b>{token}</b>\n"
            f"Reason: {reason}\n"
            f"\nTrade prevented!"
        )
        self._send(msg)
    
    def alert_startup(self):
        self.send_welcome()
    
    def alert_shutdown(self, runtime, trades, pl):
        msg = (
            f"BOT STOPPED\n\n"
            f"Runtime: {runtime}\n"
            f"Trades: {trades}\n"
            f"P/L: ${pl:+.2f}\n"
            f"\n{datetime.now().strftime('%H:%M:%S')}"
        )
        self._send(msg)