"""
AI SENTIMENT ANALYZER - Ollama-powered crowd sentiment
Only used for market regime detection, NOT trade decisions
"""

import ollama
import logging
import json
import time

logger = logging.getLogger(__name__)

class AISentiment:
    """Analyzes social media sentiment using Ollama"""
    
    def __init__(self, model="llama3.2"):
        self.model = model
        self.last_analysis = None
        self.cache = {}
        self.cache_time = 0
    
    def analyze_market_sentiment(self, posts_text, max_posts=20):
        """Analyze overall market sentiment from social posts"""
        if not posts_text or len(posts_text) < 100:
            return {"sentiment": "neutral", "score": 5, "confidence": 0.3}
        
        # Check cache (5 minute TTL)
        if time.time() - self.cache_time < 300 and self.cache:
            return self.cache
        
        try:
            prompt = f"""Analyze these crypto social media posts. 
Return ONLY JSON:
{{
    "sentiment": "bullish/neutral/bearish",
    "score": 1-10 (10=extremely bullish),
    "hype_level": "low/medium/high/extreme",
    "main_narrative": "what people are talking about",
    "confidence": 0.0-1.0
}}

Posts:
{posts_text[:2000]}"""

            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ], options={'temperature': 0.2, 'num_predict': 150})
            
            result = response['message']['content'].strip()
            
            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                self.cache = data
                self.cache_time = time.time()
                self.last_analysis = data
                return data
            
            return {"sentiment": "neutral", "score": 5, "confidence": 0.3}
        except Exception as e:
            logger.error(f"AI Sentiment error: {e}")
            return {"sentiment": "neutral", "score": 5, "confidence": 0.3}
    
    def get_regime_multiplier(self):
        """Convert sentiment to position size multiplier"""
        if not self.last_analysis:
            return 1.0
        
        sentiment = self.last_analysis.get('sentiment', 'neutral')
        score = self.last_analysis.get('score', 5)
        hype = self.last_analysis.get('hype_level', 'medium')
        
        if sentiment == 'bullish' and score >= 7:
            return 1.3  # Aggressive in bull market
        elif sentiment == 'bullish' and score >= 5:
            return 1.1
        elif sentiment == 'bearish' and score <= 3:
            return 0.5  # Defensive in bear market
        elif sentiment == 'bearish':
            return 0.7
        else:
            return 1.0
    
    def get_narrative_bonus(self, token_symbol, narrative_text):
        """Check if token matches current narrative"""
        if not self.last_analysis:
            return 0
        
        narrative = self.last_analysis.get('main_narrative', '').lower()
        token_lower = token_symbol.lower()
        
        # Check if token is related to current narrative
        if token_lower in narrative or any(word in narrative for word in token_lower.split()):
            return 10  # Bonus points for narrative alignment
        
        return 0