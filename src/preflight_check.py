"""
PRE-FLIGHT CHECK - Simulate sell before buying
If exit is impossible, don't enter
"""

import requests

class PreflightCheck:
    def __init__(self):
        self.min_liquidity_ratio = 10  # Must be able to sell 10% of position
    
    def can_exit(self, token, amount_usd, liquidity_usd):
        """
        Check if we can sell without massive slippage.
        Rule: Position size should be < 10% of liquidity.
        """
        if liquidity_usd <= 0:
            return False, "No liquidity"
        
        ratio = (amount_usd / liquidity_usd) * 100
        
        if ratio > 10:
            return False, f"Position is {ratio:.0f}% of liquidity (too large)"
        
        return True, f"Exit OK ({ratio:.0f}% of liquidity)"
    
    def estimate_slippage(self, token, amount_usd, volume_24h):
        """Estimate slippage based on volume"""
        if volume_24h <= 0:
            return 100  # 100% slippage = impossible
        
        # Rough estimate: slippage increases with position size relative to volume
        ratio = (amount_usd / volume_24h) * 100
        
        if ratio < 0.1:
            return 0.5  # 0.5% slippage
        elif ratio < 0.5:
            return 2.0
        elif ratio < 1.0:
            return 5.0
        else:
            return 15.0