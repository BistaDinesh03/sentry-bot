"""
MOMENTUM FILTER v3.0
Price must be above VWAP, volume 2x average, 24h change valid
"""

import logging
import time

logger = logging.getLogger(__name__)


class MomentumFilter:
    """
    Filters tokens based on momentum indicators.
    Only buys tokens with REAL momentum, not dead coins.
    """
    
    def __init__(self):
        self.price_history = {}     # token -> [(time, price, volume)]
        self.min_volume_multiplier = 2.0   # Volume must be 2x average
        self.max_price_change_24h = 200    # Max +200% (already pumped)
        self.min_price_change_24h = -20    # Min -20% (dying)
    
    def update(self, token, price, volume):
        """Record price/volume data point"""
        if token not in self.price_history:
            self.price_history[token] = []
        
        self.price_history[token].append((time.time(), price, volume))
        
        # Keep last 50 data points
        if len(self.price_history[token]) > 50:
            self.price_history[token] = self.price_history[token][-50:]
    
    def calculate_vwap(self, token, periods=20):
        """
        Calculate Volume Weighted Average Price.
        VWAP = sum(price * volume) / sum(volume)
        """
        history = self.price_history.get(token, [])
        
        if len(history) < periods:
            return None
        
        recent = history[-periods:]
        
        total_pv = 0
        total_volume = 0
        
        for _, price, volume in recent:
            if volume > 0:
                total_pv += price * volume
                total_volume += volume
        
        if total_volume > 0:
            return total_pv / total_volume
        
        return None
    
    def is_above_vwap(self, token, current_price):
        """Check if price is above VWAP (bullish signal)"""
        vwap = self.calculate_vwap(token)
        
        if vwap is None:
            return True  # Not enough data, allow trade
        
        is_above = current_price > vwap
        diff_pct = ((current_price - vwap) / vwap) * 100
        
        if not is_above:
            logger.info(f"  Below VWAP: ${current_price:.8f} < VWAP ${vwap:.8f} ({diff_pct:+.1f}%)")
        
        return is_above
    
    def check_volume_momentum(self, token, current_volume):
        """Volume must be 2x the average (real momentum)"""
        history = self.price_history.get(token, [])
        
        if len(history) < 10:
            return True  # Not enough data
        
        recent_volumes = [v for _, _, v in history[-10:] if v > 0]
        
        if not recent_volumes:
            return False
        
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        
        if avg_volume <= 0:
            return False
        
        ratio = current_volume / avg_volume
        
        if ratio < self.min_volume_multiplier:
            logger.info(f"  Low volume momentum: {ratio:.1f}x average (need {self.min_volume_multiplier}x)")
            return False
        
        return True
    
    def check_price_range(self, token, price_change_24h):
        """
        Price change must be between -20% and +200%.
        Filters dead coins and already-pumped coins.
        """
        if price_change_24h < self.min_price_change_24h:
            logger.info(f"  Dead coin: {price_change_24h:+.1f}% in 24h")
            return False
        
        if price_change_24h > self.max_price_change_24h:
            logger.info(f"  Already pumped: {price_change_24h:+.1f}% in 24h")
            return False
        
        return True
    
    def check_all(self, token, current_price, current_volume, price_change_24h):
        """
        Run all momentum checks.
        Returns: (passed: bool, failed_reasons: list)
        """
        failed = []
        
        # 1. VWAP check
        if not self.is_above_vwap(token, current_price):
            failed.append("Below VWAP")
        
        # 2. Volume momentum
        if not self.check_volume_momentum(token, current_volume):
            failed.append("Low volume momentum")
        
        # 3. Price range
        if not self.check_price_range(token, price_change_24h):
            failed.append(f"Bad price range: {price_change_24h:+.1f}%")
        
        return len(failed) == 0, failed
    
    def get_momentum_score(self, token, current_price, current_volume, price_change_24h):
        """
        Score momentum quality from 0-15 points.
        """
        score = 0
        
        # VWAP bonus (0-5 points)
        vwap = self.calculate_vwap(token)
        if vwap and current_price > vwap:
            pct_above = ((current_price - vwap) / vwap) * 100
            score += min(5, pct_above / 2)  # +1 point per 2% above VWAP, max 5
        
        # Volume bonus (0-5 points)
        history = self.price_history.get(token, [])
        if len(history) >= 10:
            recent_vol = [v for _, _, v in history[-10:] if v > 0]
            if recent_vol:
                avg_vol = sum(recent_vol) / len(recent_vol)
                if avg_vol > 0:
                    ratio = current_volume / avg_vol
                    score += min(5, ratio)  # +1 point per 1x volume, max 5
        
        # Price position bonus (0-5 points)
        if -10 <= price_change_24h <= 50:
            score += 5  # Good entry zone
        elif 50 < price_change_24h <= 100:
            score += 3  # OK entry
        elif -20 <= price_change_24h < -10:
            score += 2  # Dip buying
        
        return min(15, score)