"""News Sentiment Analyzer"""
import re
import logging
logger = logging.getLogger(__name__)

class NewsSentiment:
    def __init__(self):
        self.bullish_words = [
            'partnership', 'launch', 'listing', 'airdrop', 'burn',
            'upgrade', 'integration', 'adoption', 'growth', 'milestone',
            'record', 'rally', 'surge', 'breakout', 'accumulation'
        ]
        self.bearish_words = [
            'hack', 'exploit', 'rug', 'scam', 'dump', 'crash',
            'delay', 'suspend', 'investigation', 'warning', 'ban',
            'liquidate', 'collapse', 'fraud', 'ponzi'
        ]
    
    def analyze(self, text):
        """Score text from -10 (bearish) to +10 (bullish)"""
        if not text:
            return 0
        
        text_lower = text.lower()
        score = 0
        
        for word in self.bullish_words:
            if word in text_lower:
                score += 2
        
        for word in self.bearish_words:
            if word in text_lower:
                score -= 3
        
        return max(-10, min(10, score))