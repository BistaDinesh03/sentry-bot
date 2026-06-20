"""
SMART ENTRY FILTER - Balanced mode
Need 3 out of 4 conditions to pass
"""

class SmartEntry:
    def __init__(self):
        self.price_snapshots = {}
    
    def record_price(self, token, price):
        if token not in self.price_snapshots:
            self.price_snapshots[token] = []
        self.price_snapshots[token].append(price)
        if len(self.price_snapshots[token]) > 10:
            self.price_snapshots[token] = self.price_snapshots[token][-10:]
    
    def is_dip(self, token, current_price):
        prices = self.price_snapshots.get(token, [])
        if len(prices) < 5:
            return True  # Not enough data, allow it
        recent_high = max(prices[-5:])
        dip_pct = ((current_price - recent_high) / recent_high) * 100
        return dip_pct <= -1  # Only need 1% dip (was 2%)
    
    def should_buy(self, token, current_price, score, volume_rising, multi_source):
        """
        Need 3 out of 4 conditions to pass (was 4/4)
        """
        passed = 0
        reasons = []
        
        # 1. Dip check
        if self.is_dip(token, current_price):
            passed += 1
        else:
            reasons.append("No dip")
        
        # 2. Score check
        if score >= 50:  # Lowered from 55
            passed += 1
        else:
            reasons.append(f"Score {score}<50")
        
        # 3. Volume check
        if volume_rising:
            passed += 1
        else:
            reasons.append("Vol flat")
        
        # 4. Multi-source
        if multi_source:
            passed += 1
        else:
            reasons.append("1 source")
        
        if passed >= 3:  # Need 3 of 4 (was 4 of 4)
            return True, f"PASS {passed}/4"
        
        return False, f"FAIL {passed}/4: {', '.join(reasons[:2])}"