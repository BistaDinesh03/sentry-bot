"""
CORRELATION BREAKER - Don't buy tokens that move together
"""

class CorrelationBreaker:
    def __init__(self):
        self.correlation_groups = {
            'solana_meme': ['BONK', 'WIF', 'POPCAT', 'WEN', 'MEW', 'MYRO', 'SAMO'],
            'ai_coins': ['RNDR', 'FET', 'AGIX', 'OCEAN', 'TAO'],
            'defi': ['JUP', 'RAY', 'ORCA', 'JTO'],
        }
    
    def check_correlation(self, token, current_positions):
        """Return True if too correlated with existing positions"""
        token_group = self.get_group(token)
        
        for pos in current_positions:
            pos_group = self.get_group(pos)
            if pos_group == token_group and pos_group is not None:
                return True, f"Already holding {pos} in same group ({pos_group})"
        
        return False, ""
    
    def get_group(self, token):
        for group, tokens in self.correlation_groups.items():
            if token.upper() in tokens:
                return group
        return None