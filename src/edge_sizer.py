"""
EDGE-BASED POSITION SIZER
More confirming signals = bigger bet
"""

class EdgeSizer:
    def __init__(self, account_balance=1000):
        self.balance = account_balance
    
    def count_signals(self, token_data):
        """Count independent confirming signals"""
        count = 0
        
        # Telegram signal
        if token_data.get('telegram_score', 0) >= 5:
            count += 1
        
        # On-chain signal
        if token_data.get('onchain_score', 0) >= 10:
            count += 1
        
        # Momentum signal
        if token_data.get('momentum_score', 0) >= 10:
            count += 1
        
        # Volume signal
        if token_data.get('volume', 0) >= 200000:
            count += 1
        
        # Liquidity signal
        if token_data.get('liquidity', 0) >= 100000:
            count += 1
        
        # Social proof (multi-source)
        if token_data.get('social_proof', 0) >= 10:
            count += 1
        
        return count
    
    def get_position_size(self, token_data):
        """Return position size based on signal count"""
        signals = self.count_signals(token_data)
        
        sizing = {
            0: 0,
            1: 0.005,   # 0.5%
            2: 0.01,    # 1%
            3: 0.02,    # 2%
            4: 0.04,    # 4%
            5: 0.06,    # 6%
            6: 0.06,    # Cap at 6%
        }
        
        fraction = sizing.get(signals, 0)
        return self.balance * fraction, signals