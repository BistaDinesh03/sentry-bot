"""
TIERED EXIT STRATEGY - Asymmetric profit taking
Sell portions at different profit levels, let remainder run
"""

class TieredExit:
    def __init__(self):
        self.exit_levels = {
            10: 0.25,   # Sell 25% at +10%
            20: 0.25,   # Sell 25% at +20%
            50: 0.25,   # Sell 25% at +50%
        }
        self.sold_levels = {}  # token -> set of levels already triggered
    
    def check(self, token, pnl_pct):
        """Returns (should_sell, sell_fraction, reason)"""
        if token not in self.sold_levels:
            self.sold_levels[token] = set()
        
        for level, fraction in sorted(self.exit_levels.items()):
            if pnl_pct >= level and level not in self.sold_levels[token]:
                self.sold_levels[token].add(level)
                return True, fraction, f"Tier{level}:+{pnl_pct:.1f}%"
        
        return False, 0, ""