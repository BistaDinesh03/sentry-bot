"""
BALANCED POSITION SIZER v4.0
Moderate risk: 0.5% to 2.5% of bankroll based on score
"""

import logging
logger = logging.getLogger(__name__)

class PositionSizer:
    def __init__(self, account_balance=1000):
        self.account_balance = account_balance
        self.win_rate = 0.38
        self.avg_win = 3.0
        self.avg_loss = 1.0

    def update_performance(self, win_rate, avg_win, avg_loss):
        self.win_rate = max(0.1, min(0.9, win_rate))
        self.avg_win = max(0.1, avg_win)
        self.avg_loss = max(0.1, avg_loss)

    def get_dynamic_fraction(self, total_score, max_score=160, min_score=50):
        """
        Risk scales linearly with conviction.
        At min_score (50): 0.5% of bankroll
        At max_score (160): 2.5% of bankroll
        """
        if total_score < min_score:
            return 0.0
        normalized = (total_score - min_score) / (max_score - min_score)
        fraction = 0.005 + normalized * 0.02  # 0.5% to 2.5%
        return min(0.025, fraction)

    def calculate_position_size(self, score, volatility_pct, liquidity_usd):
        fraction = self.get_dynamic_fraction(score)
        if fraction <= 0:
            return 0.0
        base = self.account_balance * fraction
        # Reduce for high volatility
        if volatility_pct > 50:
            base *= 0.6
        elif volatility_pct > 30:
            base *= 0.8
        # Reduce for low liquidity
        if liquidity_usd < 20000:
            base *= 0.5
        elif liquidity_usd < 50000:
            base *= 0.75
        return round(base, 2)

    def should_trade(self, score, liquidity_usd, volatility_pct):
        reasons = []
        if score < 50:
            reasons.append("Score below 50")
        if liquidity_usd < 5000:
            reasons.append("Liquidity < $5k")
        if volatility_pct > 100:
            reasons.append("Extreme volatility")
        return len(reasons) == 0, reasons