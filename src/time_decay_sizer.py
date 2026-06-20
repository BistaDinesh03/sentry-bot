"""
TIME-BASED POSITION ADJUSTMENT
First mention = bigger bet, older news = smaller
"""

import time

class TimeDecaySizer:
    def __init__(self):
        self.discovery_times = {}  # token -> timestamp
    
    def record_discovery(self, token):
        if token not in self.discovery_times:
            self.discovery_times[token] = time.time()
    
    def get_multiplier(self, token):
        """Return multiplier based on how long ago token was discovered"""
        if token not in self.discovery_times:
            return 1.0
        
        age_minutes = (time.time() - self.discovery_times[token]) / 60
        
        if age_minutes < 30:
            return 1.5    # Fresh - bet bigger
        elif age_minutes < 60:
            return 1.2    # Recent
        elif age_minutes < 120:
            return 1.0    # Normal
        elif age_minutes < 240:
            return 0.7    # Getting old
        else:
            return 0.5    # Old news - reduce