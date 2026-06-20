"""
TOKEN SCORER v5.0 - Strict thresholds
Buy >= 55, Strong buy >= 70, Skip < 40
"""

import logging

logger = logging.getLogger(__name__)


class TokenScorer:
    """Scores tokens 0-110 based on HARD DATA"""
    
    def __init__(self):
        self.weights = {
            'telegram': 25, 'onchain': 20, 'momentum': 15,
            'volume': 15, 'liquidity': 15, 'safety': 10, 'entry_timing': 10,
        }
        
        # STRICT thresholds
        self.buy_threshold = 55
        self.strong_buy_threshold = 70
        self.skip_threshold = 40
        
        self.scores_given = 0
        self.buys_recommended = 0
        self.skips_recommended = 0
    
    def score_telegram(self, points): return min(25, points)
    def score_onchain(self, points): return min(20, points)
    def score_momentum(self, points): return min(15, points)
    
    def score_volume(self, volume_24h):
        if volume_24h <= 0: return 0
        if volume_24h >= 10000000: return 15
        elif volume_24h >= 5000000: return 14
        elif volume_24h >= 1000000: return 12
        elif volume_24h >= 500000: return 10
        elif volume_24h >= 200000: return 8
        elif volume_24h >= 100000: return 6
        elif volume_24h >= 50000: return 4
        else: return 2
    
    def score_liquidity(self, liquidity_usd):
        if liquidity_usd <= 0: return 0
        if liquidity_usd >= 5000000: return 15
        elif liquidity_usd >= 1000000: return 14
        elif liquidity_usd >= 500000: return 12
        elif liquidity_usd >= 200000: return 10
        elif liquidity_usd >= 100000: return 8
        elif liquidity_usd >= 50000: return 6
        elif liquidity_usd >= 20000: return 4
        else: return 2
    
    def score_safety(self, risk_score):
        if risk_score <= 0: return 10
        elif risk_score <= 10: return 9
        elif risk_score <= 20: return 8
        elif risk_score <= 30: return 6
        elif risk_score <= 40: return 4
        elif risk_score <= 50: return 2
        else: return 0
    
    def score_entry_timing(self, price_change_24h):
        if price_change_24h is None: return 5
        if 0 < price_change_24h <= 10: return 10
        elif 10 < price_change_24h <= 30: return 8
        elif 30 < price_change_24h <= 50: return 6
        elif 50 < price_change_24h <= 100: return 3
        elif price_change_24h > 100: return 1
        elif -10 <= price_change_24h <= 0: return 7
        elif -20 <= price_change_24h < -10: return 5
        else: return 3
    
    def calculate_score(self, token_data):
        breakdown = {}
        breakdown['telegram'] = self.score_telegram(token_data.get('telegram_score', 0))
        breakdown['onchain'] = self.score_onchain(token_data.get('onchain_score', 0))
        breakdown['momentum'] = self.score_momentum(token_data.get('momentum_score', 0))
        breakdown['volume'] = self.score_volume(token_data.get('volume', 0))
        breakdown['liquidity'] = self.score_liquidity(token_data.get('liquidity', 0))
        breakdown['safety'] = self.score_safety(token_data.get('risk_score', 50))
        breakdown['entry_timing'] = self.score_entry_timing(token_data.get('price_change_24h', 0))
        
        total_score = sum(breakdown.values())
        total_score = min(110, total_score)
        
        price_change = token_data.get('price_change_24h', 0) or 0
        if price_change > 200:
            return {'total_score': min(total_score, 39), 'breakdown': breakdown,
                'recommendation': 'SKIP', 'confidence': 0, 'buy_threshold': self.buy_threshold,
                'strong_buy_threshold': self.strong_buy_threshold, 'pump_penalty': True,
                'reason': f'Pumped {price_change:.0f}%'}
        
        if price_change < -30:
            return {'total_score': min(total_score, 39), 'breakdown': breakdown,
                'recommendation': 'SKIP', 'confidence': 0, 'buy_threshold': self.buy_threshold,
                'strong_buy_threshold': self.strong_buy_threshold, 'reason': f'Dumping {price_change:.0f}%'}
        
        if total_score >= self.strong_buy_threshold:
            recommendation = "STRONG_BUY"
        elif total_score >= self.buy_threshold:
            recommendation = "BUY"
        elif total_score >= self.skip_threshold:
            recommendation = "WATCH"
        else:
            recommendation = "SKIP"
        
        self.scores_given += 1
        if recommendation in ["BUY", "STRONG_BUY"]:
            self.buys_recommended += 1
        else:
            self.skips_recommended += 1
        
        return {'total_score': total_score, 'breakdown': breakdown,
            'recommendation': recommendation, 'confidence': min(100, total_score),
            'buy_threshold': self.buy_threshold, 'strong_buy_threshold': self.strong_buy_threshold}
    
    def explain_score(self, result):
        if not result: return "No score"
        if result.get('reason'): return result['reason']
        b = result['breakdown']
        parts = []
        if b['telegram'] >= 15: parts.append(f"TG:{b['telegram']}/25")
        if b['onchain'] >= 10: parts.append(f"Chain:{b['onchain']}/20")
        if b['volume'] >= 10: parts.append(f"Vol:{b['volume']}/15")
        if b['liquidity'] >= 10: parts.append(f"Liq:{b['liquidity']}/15")
        rec = result['recommendation']
        s = result['total_score']
        if rec == "STRONG_BUY": return f"STRONG BUY ({s}/110) | " + " | ".join(parts[:3])
        elif rec == "BUY": return f"BUY ({s}/110) | " + " | ".join(parts[:2])
        else: return f"{rec} ({s}/110)"
    
    def get_stats(self):
        return {'scores_given': self.scores_given, 'buys_recommended': self.buys_recommended,
            'skips_recommended': self.skips_recommended, 'buy_threshold': self.buy_threshold}