"""Daily Profit Target - Lock in daily gains"""
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

class DailyTarget:
    def __init__(self, target_pct=2.0):
        self.target_pct = target_pct
        self.daily_pl = 0.0
        self.start_balance = 1000.0
        self.target_hit = False
        self.last_reset = datetime.now().date()
    
    def update(self, current_balance, initial_balance=1000):
        today = datetime.now().date()
        
        # Reset daily
        if today != self.last_reset:
            self.daily_pl = 0.0
            self.target_hit = False
            self.start_balance = current_balance
            self.last_reset = today
        
        self.daily_pl = current_balance - self.start_balance
        
        target_amount = initial_balance * (self.target_pct / 100)
        
        if self.daily_pl >= target_amount:
            self.target_hit = True
            logger.info(f"DAILY TARGET HIT: +${self.daily_pl:.2f} ({self.target_pct}%)")
        
        return self.target_hit
    
    def should_stop(self):
        return self.target_hit
    
    def get_progress(self):
        return f"${self.daily_pl:+.2f}"