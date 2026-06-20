"""
EXIT STRATEGY v4.0 - Balanced: 15-25% ATR trail + 6% hard stop
"""

import time
import logging
logger = logging.getLogger(__name__)

class ExitStrategy:
    def __init__(self):
        self.price_history = {}
        self.highest_prices = {}
        self.entry_prices = {}
        self.entry_times = {}

    def record_entry(self, token, entry_price, entry_time=None):
        self.entry_prices[token] = entry_price
        self.entry_times[token] = entry_time or time.time()
        self.highest_prices[token] = entry_price
        if token not in self.price_history:
            self.price_history[token] = []

    def update_price(self, token, current_price, current_volume=None):
        if token not in self.price_history:
            self.price_history[token] = []
            self.highest_prices[token] = current_price
            self.entry_prices[token] = current_price
            self.entry_times[token] = time.time()
        self.price_history[token].append((time.time(), current_price))
        if current_price > self.highest_prices.get(token, 0):
            self.highest_prices[token] = current_price
        if len(self.price_history[token]) > 100:
            self.price_history[token] = self.price_history[token][-100:]

    def calculate_atr(self, token, periods=20):
        history = self.price_history.get(token, [])
        if len(history) < periods:
            entry = self.entry_prices.get(token, 0)
            return entry * 0.03 if entry > 0 else 0.01
        prices = [p[1] for p in history[-periods:]]
        tr = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
        return sum(tr) / len(tr) if tr else prices[-1] * 0.03

    def check_trailing_stop(self, token, current_price):
        highest = self.highest_prices.get(token, current_price)
        atr = self.calculate_atr(token)
        if current_price <= 0:
            return False, ""
        trail_pct = (2.5 * atr / current_price) * 100
        trail_pct = max(15, min(25, trail_pct))  # Between 15% and 25%
        stop_price = highest * (1 - trail_pct / 100)
        if current_price <= stop_price and highest > self.entry_prices.get(token, current_price):
            drop = ((highest - current_price) / highest) * 100
            return True, f"Trail:{trail_pct:.0f}% (-{drop:.1f}% from high)"
        return False, ""

    def check_hard_stop(self, token, current_price):
        entry = self.entry_prices.get(token, current_price)
        if entry <= 0:
            return False, ""
        pnl = ((current_price - entry) / entry) * 100
        if pnl <= -6:
            return True, f"HardStop:{pnl:.1f}%"
        return False, ""

    def check_take_profit(self, token, current_price):
        entry = self.entry_prices.get(token, current_price)
        if entry <= 0:
            return False, ""
        pnl = ((current_price - entry) / entry) * 100
        if pnl >= 15:
            return True, f"TakeProfit:+{pnl:.1f}%"
        return False, ""

    def should_sell(self, token, current_price, current_volume=None, entry_time=None):
        signals = []
        # Hard stop first
        sell, reason = self.check_hard_stop(token, current_price)
        if sell: signals.append(reason); return True, signals
        # Take profit
        sell, reason = self.check_take_profit(token, current_price)
        if sell: signals.append(reason); return True, signals
        # Trailing stop
        sell, reason = self.check_trailing_stop(token, current_price)
        if sell: signals.append(reason); return True, signals
        return False, signals