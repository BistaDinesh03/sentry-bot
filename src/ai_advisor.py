"""
AI Advisor - Ollama-powered trading intelligence
Sentiment Analysis + Scam Detection + Trade Validation
"""

import ollama
import logging
import time
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AIAdvisor:
    """AI-powered trading assistant using Ollama"""
    
    def __init__(self, model="llama3.2", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.cache = {}
        self.cache_times = {}
        self.cache_ttl = 600  # 10 minutes
    
    def ask(self, prompt, system_prompt=None, use_cache=False, cache_key=None):
        """Ask the AI a question"""
        
        # Check cache
        if use_cache and cache_key:
            now = time.time()
            if cache_key in self.cache and (now - self.cache_times.get(cache_key, 0)) < self.cache_ttl:
                return self.cache[cache_key]
        
        try:
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    'temperature': 0.3,
                    'num_predict': 200
                }
            )
            
            result = response['message']['content'].strip()
            
            # Cache if needed
            if use_cache and cache_key:
                self.cache[cache_key] = result
                self.cache_times[cache_key] = time.time()
            
            return result
            
        except Exception as e:
            logger.error(f"AI error: {e}")
            return None
    
    def analyze_sentiment(self, text, source="social_media"):
        """Analyze sentiment of social media posts"""
        
        if not text or len(text) < 20:
            return {"sentiment": "neutral", "score": 5, "confidence": 0.3}
        
        system = """You are a crypto trading sentiment analyzer.
Analyze the text and respond ONLY with this JSON format:
{
    "sentiment": "bullish" or "bearish" or "neutral",
    "score": 1-10 (1=extremely bearish, 10=extremely bullish),
    "confidence": 0.0-1.0,
    "key_points": ["point1", "point2"],
    "is_hype": true/false
}"""
        
        prompt = f"Analyze this crypto/social media post from {source}:\n\n{text[:500]}"
        
        try:
            result = self.ask(prompt, system)
            if result:
                # Try to parse JSON
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {"sentiment": "neutral", "score": 5, "confidence": 0.3, "key_points": []}
        except:
            return {"sentiment": "neutral", "score": 5, "confidence": 0.3, "key_points": []}
    
    def detect_scam(self, token_symbol, token_data):
        """AI-powered scam detection"""
        
        system = """You are a crypto scam detector. Analyze token data and respond ONLY with JSON:
{
    "is_scam_likely": true/false,
    "risk_level": "low" or "medium" or "high" or "critical",
    "risk_score": 0-100,
    "red_flags": ["flag1", "flag2"],
    "recommendation": "buy" or "skip" or "wait",
    "reason": "one sentence explanation"
}"""
        
        prompt = f"""Analyze this token for potential scams:

Token: ${token_symbol}
Price: ${token_data.get('price', 'unknown')}
Volume 24h: ${token_data.get('volume_24h', 0):,.0f}
Liquidity: ${token_data.get('liquidity', 0):,.0f}
Risk Score (algorithmic): {token_data.get('risk_score', 50)}/100

Based on this data, is this token likely to be a scam or rug pull?"""
        
        try:
            result = self.ask(prompt, system)
            if result:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {"is_scam_likely": False, "risk_level": "medium", "risk_score": 50, "recommendation": "skip"}
        except:
            return {"is_scam_likely": False, "risk_level": "medium", "risk_score": 50, "recommendation": "skip"}
    
    def validate_trade(self, token_symbol, conviction, price, portfolio_balance):
        """AI validates whether to execute a trade"""
        
        system = """You are a crypto trading advisor. Analyze and respond ONLY with JSON:
{
    "should_buy": true/false,
    "adjusted_conviction": 0.0-1.0,
    "suggested_amount_usd": number,
    "reasoning": "one sentence",
    "confidence": 0.0-1.0
}"""
        
        prompt = f"""Should I buy this memecoin?

Token: ${token_symbol}
Price: ${price:.8f}
Algorithmic Conviction: {conviction:.2f}
My Portfolio Balance: ${portfolio_balance:.2f}
Max position: $100

Consider: Is this a good entry? Is the price reasonable for a memecoin?"""
        
        try:
            result = self.ask(prompt, system)
            if result:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {"should_buy": conviction > 0.5, "adjusted_conviction": conviction, "suggested_amount_usd": 50}
        except:
            return {"should_buy": conviction > 0.5, "adjusted_conviction": conviction, "suggested_amount_usd": 50}
    
    def portfolio_review(self, positions, balance, total_pl):
        """AI portfolio review"""
        
        if not positions:
            return "No open positions to review."
        
        positions_text = "\n".join([
            f"${sym}: {pos['amount']:.2f} tokens, bought at ${pos['buy_price']:.8f}"
            for sym, pos in positions.items()
        ])
        
        system = "You are a crypto portfolio advisor. Give a brief 2-3 sentence review and recommendation."
        prompt = f"""Portfolio Review:
Balance: ${balance:.2f}
Total P/L: ${total_pl:+.2f}
Open Positions:
{positions_text}

Give a brief review and any recommendations."""
        
        try:
            result = self.ask(prompt, system)
            return result if result else "AI review unavailable."
        except:
            return "AI review unavailable."
    
    def detect_narrative(self, findings_text):
        """Detect emerging narratives from social media"""
        
        if not findings_text or len(findings_text) < 100:
            return None
        
        system = """You detect emerging crypto narratives. Respond with JSON:
{
    "narrative": "narrative name or null",
    "strength": 1-10,
    "tokens_mentioned": ["TOKEN1", "TOKEN2"],
    "summary": "one sentence summary"
}"""
        
        prompt = f"Analyze these crypto social media posts and detect any emerging narrative:\n\n{findings_text[:1000]}"
        
        try:
            result = self.ask(prompt, system)
            if result:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            return None
        except:
            return None
    
    def is_available(self):
        """Check if Ollama is running"""
        try:
            response = ollama.list()
            return True
        except:
            return False