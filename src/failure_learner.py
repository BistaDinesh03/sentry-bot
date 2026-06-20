"""
FAILURE LEARNER - Learn from losing trades
"""

from collections import defaultdict

class FailureLearner:
    def __init__(self):
        self.losing_patterns = defaultdict(int)
        self.blocked_conditions = set()
    
    def record_loss(self, token, score, hour, source, pnl):
        """Record a losing trade for pattern analysis"""
        if pnl < 0:
            # Record patterns
            self.losing_patterns[f"score_below_{score}"] += 1
            self.losing_patterns[f"hour_{hour}"] += 1
            self.losing_patterns[f"source_{source}"] += 1
            
            # If same pattern fails 3+ times, block it
            for pattern, count in self.losing_patterns.items():
                if count >= 3:
                    self.blocked_conditions.add(pattern)
    
    def should_block(self, token, score, hour, source):
        """Return True if this trade matches a known failure pattern"""
        checks = [
            f"score_below_{score}",
            f"hour_{hour}",
            f"source_{source}",
        ]
        
        for check in checks:
            if check in self.blocked_conditions:
                return True, f"Blocked by failure pattern: {check}"
        
        return False, ""
    
    def get_insights(self):
        """Return learned insights"""
        return {
            'blocked_patterns': list(self.blocked_conditions),
            'total_patterns_tracked': len(self.losing_patterns)
        }