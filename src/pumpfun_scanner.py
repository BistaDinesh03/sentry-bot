"""
Pump.fun Scanner - Detect tokens graduating to Raydium
This is where 100x memecoins are born
"""

import requests
import logging
import time

logger = logging.getLogger(__name__)

class PumpFunScanner:
    """Scans for Pump.fun tokens graduating to Raydium"""
    
    def __init__(self):
        self.base_url = "https://frontend-api.pump.fun"
    
    def get_new_graduates(self, limit=20):
        """Get tokens that recently graduated from Pump.fun"""
        try:
            url = f"{self.base_url}/coins?offset=0&limit={limit}&sort=created&order=DESC&includeNsfw=false"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tokens = []
                for coin in data[:limit]:
                    if coin.get('complete', False):  # Graduated
                        tokens.append({
                            'symbol': coin.get('symbol', 'UNKNOWN'),
                            'name': coin.get('name', ''),
                            'address': coin.get('mint', ''),
                            'market_cap': coin.get('usd_market_cap', 0),
                            'graduated': True,
                            'source': 'pumpfun'
                        })
                return tokens
            return []
        except Exception as e:
            logger.debug(f"PumpFun error: {e}")
            return []
    
    def scan_all(self):
        logger.info("Scanning Pump.fun graduates...")
        tokens = self.get_new_graduates()
        if tokens:
            logger.info(f"  Found {len(tokens)} graduated tokens")
            for t in tokens[:5]:
                logger.info(f"    ${t['symbol']} - MC: ${t['market_cap']:,.0f}")
        return tokens