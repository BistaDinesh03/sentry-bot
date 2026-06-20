"""RSI Filter - Avoid buying tops"""
import logging
logger = logging.getLogger(__name__)

class RSIFilter:
    def __init__(self):
        self.price_history = {}
    
    def update(self, token, price):
        if token not in self.price_history:
            self.price_history[token] = []
        self.price_history[token].append(price)
        if len(self.price_history[token]) > 20:
            self.price_history[token] = self.price_history[token][-20:]
    
    def calculate_rsi(self, token, periods=14):
        prices = self.price_history.get(token, [])
        if len(prices) < periods:
            return 50  # Neutral
        
        gains, losses = [], []
        for i in range(1, len(prices[-periods:])):
            diff = prices[-periods:][i] - prices[-periods:][i-1]
            gains.append(diff if diff > 0 else 0)
            losses.append(abs(diff) if diff < 0 else 0)
        
        avg_gain = sum(gains) / periods
        avg_loss = sum(losses) / periods
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def should_avoid(self, token):
        """Return True if token is overbought (RSI > 75)"""
        rsi = self.calculate_rsi(token)
        return rsi > 75, rsi