"""
NARRATIVE DETECTOR - Find themes before they pump
AI coins, gaming coins, animal coins, etc.
"""

import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class NarrativeDetector:
    """Detects emerging narratives from social posts"""
    
    def __init__(self):
        self.narratives = {
            'ai': ['ai', 'artificial', 'intelligence', 'gpt', 'llm', 'neural', 'agent'],
            'gaming': ['game', 'gaming', 'playtoearn', 'p2e', 'metaverse', 'nft'],
            'defi': ['defi', 'yield', 'farm', 'stake', 'lp', 'liquidity'],
            'meme': ['meme', 'doge', 'shib', 'pepe', 'wojak', 'chad'],
            'layer2': ['l2', 'layer2', 'rollup', 'zk', 'optimism', 'arbitrum'],
            'rwa': ['real world', 'rwa', 'tokenized', 'asset', 'real estate'],
            'privacy': ['privacy', 'anonymous', 'zk', 'stealth', 'private'],
            'social': ['social', 'friend', 'profile', 'identity', 'reputation'],
        }
        self.mention_counts = Counter()
        self.trending_narrative = None
    
    def scan_posts(self, posts_text):
        """Scan posts for narrative keywords"""
        if not posts_text:
            return None
        
        text_lower = posts_text.lower()
        
        for narrative, keywords in self.narratives.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > 0:
                self.mention_counts[narrative] += count
        
        # Find trending narrative
        if self.mention_counts:
            top = self.mention_counts.most_common(1)
            if top and top[0][1] >= 3:
                self.trending_narrative = top[0][0]
                return top[0][0]
        
        return None
    
    def get_narrative_score(self, token_symbol):
        """Check if token matches trending narrative"""
        if not self.trending_narrative:
            return 0
        
        token_lower = token_symbol.lower()
        keywords = self.narratives.get(self.trending_narrative, [])
        
        # Check if token name contains narrative keywords
        for kw in keywords:
            if kw in token_lower:
                return 15  # Strong narrative match
        
        return 0
    
    def get_trending(self):
        """Get current trending narrative"""
        return self.trending_narrative