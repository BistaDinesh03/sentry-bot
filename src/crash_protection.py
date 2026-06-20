"""
CRASH PROTECTION - Stop trading when market tanks
"""

import logging
logger = logging.getLogger(__name__)

class CrashProtection:
    def __init__(self):
        self.crash_mode = False
        self.consecutive_losses = 0
        self.max_consecutive_losses = 5
        self.daily_loss_limit = -50  # Stop if lose $50 in a day
        self.daily_loss = 0
    
    def add_trade(self, profit):
        if profit < 0:
            self.consecutive_losses += 1
            self.daily_loss += profit
        else:
            self.consecutive_losses = 0
    
    def check(self):
        """Return True if bot should stop trading"""
        reasons = []
        
        if self.consecutive_losses >= self.max_consecutive_losses:
            reasons.append(f"CRASH: {self.consecutive_losses} consecutive losses")
        
        if self.daily_loss <= self.daily_loss_limit:
            reasons.append(f"CRASH: Daily loss ${self.daily_loss:.0f} exceeded ${self.daily_loss_limit}")
        
        if reasons:
            self.crash_mode = True
            for r in reasons:
                logger.warning(r)
            return True, reasons
        
        return False, []
    
    def reset_daily(self):
        self.daily_loss = 0
        self.consecutive_losses = 0
        self.crash_mode = False