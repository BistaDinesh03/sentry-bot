"""
Equity Curve Tracker - Track portfolio value over time
"""

import json
import time
from datetime import datetime
from pathlib import Path

class EquityTracker:
    """Track portfolio value for charting"""
    
    def __init__(self):
        self.equity_points = []
        self.start_time = time.time()
        self.start_balance = 1000
    
    def add_point(self, balance):
        """Record equity point"""
        self.equity_points.append({
            'time': datetime.now().isoformat(),
            'balance': balance,
            'return_pct': ((balance - self.start_balance) / self.start_balance) * 100
        })
        
        # Keep last 1000 points
        if len(self.equity_points) > 1000:
            self.equity_points = self.equity_points[-1000:]
    
    def get_curve(self):
        """Get equity curve data"""
        return {
            'points': self.equity_points[-100:],  # Last 100 points
            'start_balance': self.start_balance,
            'current_balance': self.equity_points[-1]['balance'] if self.equity_points else self.start_balance,
            'high': max(p['balance'] for p in self.equity_points) if self.equity_points else self.start_balance,
            'low': min(p['balance'] for p in self.equity_points) if self.equity_points else self.start_balance,
        }
    
    def save(self):
        """Save equity data"""
        try:
            with open('data/equity_curve.json', 'w') as f:
                json.dump(self.get_curve(), f, indent=2)
        except:
            pass