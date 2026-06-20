"""
ADAPTIVE THRESHOLDS - Adjust based on market conditions
Bull market: lower thresholds (more buys)
Bear market: higher thresholds (less buys)
"""

class AdaptiveThreshold:
    def __init__(self):
        self.base_buy_threshold = 55
        self.base_strong_buy = 70
        self.current_buy = 55
        self.current_strong = 70
    
    def update(self, market_sentiment_score, market_hype):
        """Adjust thresholds based on market conditions"""
        # 1-10 scale, 10 = extremely bullish
        if market_sentiment_score >= 8:
            # Bull market: be more aggressive
            self.current_buy = self.base_buy_threshold - 5  # 50
            self.current_strong = self.base_strong_buy - 5  # 65
        elif market_sentiment_score >= 6:
            # Slightly bullish
            self.current_buy = self.base_buy_threshold - 2  # 53
            self.current_strong = self.base_strong_buy - 2  # 68
        elif market_sentiment_score <= 3:
            # Bear market: be defensive
            self.current_buy = self.base_buy_threshold + 10  # 65
            self.current_strong = self.base_strong_buy + 5   # 75
        elif market_sentiment_score <= 5:
            # Slightly bearish
            self.current_buy = self.base_buy_threshold + 5   # 60
            self.current_strong = self.base_strong_buy + 3   # 73
        else:
            # Neutral: use base
            self.current_buy = self.base_buy_threshold
            self.current_strong = self.base_strong_buy
        
        # Hype adjustment
        if market_hype == 'extreme':
            self.current_buy += 5  # Be cautious in extreme hype
    
    def get_thresholds(self):
        return self.current_buy, self.current_strong