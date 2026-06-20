"""Multi-Timeframe Confirmation"""
import requests
import logging

logger = logging.getLogger(__name__)

class MultiTimeframe:
    def __init__(self):
        self.timeframes = {'5m': 5, '15m': 15, '1h': 60}
    
    def check(self, symbol):
        """Check if all timeframes agree - bullish"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                pairs = data.get('pairs', [])
                if pairs:
                    p = pairs[0]
                    m5 = float(p.get('priceChange', {}).get('m5', 0) or 0)
                    h1 = float(p.get('priceChange', {}).get('h1', 0) or 0)
                    h24 = float(p.get('priceChange', {}).get('h24', 0) or 0)
                    
                    # All positive = strong bullish
                    if m5 > 0 and h1 > 0 and h24 > 0:
                        return True, 15  # Bonus points
                    # Mixed = neutral
                    elif m5 > 0 or h1 > 0:
                        return True, 5
                    # All negative = avoid
                    else:
                        return False, 0
            return True, 0
        except:
            return True, 0