"""Profit Lock - Never let a winner become a loser"""
import logging
logger = logging.getLogger(__name__)

class ProfitLock:
    def __init__(self):
        self.locked = {}  # token -> breakeven_price
    
    def check(self, token, entry_price, current_price, pnl_pct):
        """If profit > 5%, lock in breakeven"""
        if token in self.locked:
            return self.locked[token]
        
        if pnl_pct >= 5:
            self.locked[token] = entry_price
            logger.info(f"  LOCKED ${token}: Breakeven protected")
            return entry_price
        
        return None