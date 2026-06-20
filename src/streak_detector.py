"""Streak Detector - Ride hot streaks, reduce during cold"""
import logging
logger = logging.getLogger(__name__)

class StreakDetector:
    def __init__(self):
        self.recent_trades = []  # Last 10 trade profits
        self.streak = 0
    
    def add_trade(self, profit):
        self.recent_trades.append(profit)
        if len(self.recent_trades) > 10:
            self.recent_trades.pop(0)
        
        if profit > 0:
            self.streak = max(0, self.streak + 1)
        else:
            self.streak = min(0, self.streak - 1)
    
    def get_multiplier(self):
        """Return position size multiplier"""
        if self.streak >= 3:
            return 1.25  # Hot streak - 25% bigger
        elif self.streak >= 2:
            return 1.1
        elif self.streak <= -3:
            return 0.5   # Cold streak - 50% smaller
        elif self.streak <= -2:
            return 0.75
        else:
            return 1.0   # Normal
    
    def is_hot(self):
        return self.streak >= 2
    
    def is_cold(self):
        return self.streak <= -2