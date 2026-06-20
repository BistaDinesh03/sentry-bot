"""
STREAK-BASED ADJUSTMENT
Hot streak = bigger bets, Cold streak = smaller
"""

class StreakSizer:
    def __init__(self):
        self.last_5_trades = []  # True=win, False=loss
    
    def add_result(self, profit):
        self.last_5_trades.append(profit > 0)
        if len(self.last_5_trades) > 5:
            self.last_5_trades.pop(0)
    
    def get_multiplier(self):
        """Return position multiplier based on recent performance"""
        if len(self.last_5_trades) < 3:
            return 1.0
        
        wins = sum(self.last_5_trades)
        
        if wins >= 4:      # Hot streak (4-5 wins)
            return 1.5
        elif wins == 3:    # Doing well
            return 1.2
        elif wins == 2:    # Normal
            return 1.0
        elif wins == 1:    # Cold
            return 0.7
        else:              # Ice cold (0 wins)
            return 0.5
    
    def get_status(self):
        if len(self.last_5_trades) < 3:
            return "WARMUP"
        wins = sum(self.last_5_trades)
        if wins >= 4: return "HOT"
        elif wins >= 3: return "WARM"
        elif wins >= 2: return "NEUTRAL"
        elif wins >= 1: return "COLD"
        else: return "FROZEN"