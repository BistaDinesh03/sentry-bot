"""
Auto-Compounder - Reinvest profits automatically
When portfolio grows, position sizes grow proportionally
"""

import logging
logger = logging.getLogger(__name__)


class AutoCompounder:
    """Automatically compound profits by increasing position sizes"""
    
    def __init__(self, initial_balance=1000):
        self.initial_balance = initial_balance
        self.peak_balance = initial_balance
        self.current_balance = initial_balance
        self.growth_multiplier = 1.0
        self.milestones = []
    
    def update(self, current_balance):
        """Update balance and calculate growth"""
        self.current_balance = current_balance
        
        # Track peak
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        # Calculate growth
        growth_pct = ((current_balance - self.initial_balance) / self.initial_balance) * 100
        
        # Growth multiplier: increases as we profit
        if growth_pct > 0:
            self.growth_multiplier = 1.0 + (growth_pct / 100)
        else:
            self.growth_multiplier = 1.0  # Don't shrink below 1x
        
        return growth_pct
    
    def get_position_multiplier(self):
        """
        Returns position size multiplier based on profits.
        - At $1,000: 1.0x (normal)
        - At $1,050: 1.05x (5% bigger)
        - At $1,100: 1.10x (10% bigger)
        """
        return min(2.0, self.growth_multiplier)  # Cap at 2x
    
    def get_max_position_size(self, base_size=80):
        """Get adjusted max position size"""
        return base_size * self.get_position_multiplier()
    
    def should_take_profits(self, profit_threshold=50):
        """Return True if we should withdraw profits to cold wallet"""
        total_profit = self.current_balance - self.initial_balance
        return total_profit >= profit_threshold
    
    def get_stats(self):
        """Get compounding stats"""
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'peak_balance': self.peak_balance,
            'growth_pct': ((self.current_balance - self.initial_balance) / self.initial_balance) * 100,
            'multiplier': self.get_position_multiplier(),
            'max_position': self.get_max_position_size()
        }
    
    def print_status(self):
        """Print compounding status"""
        stats = self.get_stats()
        logger.info(f"  Compound: {stats['growth_pct']:+.2f}% | "
                   f"Multiplier: {stats['multiplier']:.2f}x | "
                   f"Max Size: ${stats['max_position']:.2f}")