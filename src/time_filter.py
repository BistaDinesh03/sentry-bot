"""
TIME FILTER - Only trade during active hours
Memecoin volume peaks: 9am-11am EST, 2pm-4pm EST, 8pm-10pm EST
"""

from datetime import datetime
import pytz

class TimeFilter:
    def __init__(self):
        self.active_hours = [
            (9, 11),   # US morning
            (14, 16),  # US afternoon
            (20, 22),  # US evening (Asia overlap)
        ]
        self.est = pytz.timezone('US/Eastern')
    
    def is_active_hour(self):
        """Return True if we're in a high-volume window"""
        try:
            now = datetime.now(self.est)
            hour = now.hour
            
            for start, end in self.active_hours:
                if start <= hour < end:
                    return True
            return False
        except:
            return True  # If pytz fails, always trade
    
    def get_position_multiplier(self):
        """Adjust position size based on time"""
        if self.is_active_hour():
            return 1.0   # Normal size during active hours
        else:
            return 0.5   # Half size during slow hours
    
    def should_trade(self):
        """Should we trade at all right now?"""
        return self.is_active_hour()