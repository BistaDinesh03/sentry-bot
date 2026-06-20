"""
RISK GOVERNOR - Never exceed portfolio heat limits
"""

class RiskGovernor:
    def __init__(self, max_portfolio_heat=0.25):
        self.max_heat = max_portfolio_heat
    
    def can_trade(self, current_exposure, account_balance, new_position_size):
        """Check if new trade keeps portfolio under heat limit"""
        current_heat = current_exposure / account_balance if account_balance > 0 else 0
        new_heat = (current_exposure + new_position_size) / account_balance
        return new_heat <= self.max_heat, current_heat
    
    def get_max_position(self, current_exposure, account_balance):
        """Maximum position size given current exposure"""
        available = (self.max_heat * account_balance) - current_exposure
        return max(0, available)