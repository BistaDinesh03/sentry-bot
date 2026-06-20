"""
Birdeye Scanner - Better memecoin trending data
"""

import requests
import logging

logger = logging.getLogger(__name__)

class BirdeyeScanner:
    """Gets trending tokens from Birdeye"""
    
    def __init__(self):
        self.base_url = "https://public-api.birdeye.so"
    
    def get_trending(self, limit=20):
        """Get trending tokens on Solana"""
        try:
            url = f"{self.base_url}/public/tokenlist?sort_by=v24hUSD&sort_type=desc&offset=0&limit={limit}"
            headers = {
                'x-chain': 'solana',
                'User-Agent': 'Mozilla/5.0'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tokens = []
                for token in data.get('data', {}).get('tokens', [])[:limit]:
                    tokens.append({
                        'symbol': token.get('symbol', 'UNKNOWN'),
                        'name': token.get('name', ''),
                        'price': token.get('price', 0),
                        'volume_24h': token.get('v24hUSD', 0),
                        'price_change_24h': token.get('priceChange24hPercent', 0),
                        'source': 'birdeye'
                    })
                return tokens
            return []
        except Exception as e:
            logger.debug(f"Birdeye error: {e}")
            return []
    
    def scan_all(self):
        logger.info("Scanning Birdeye trending...")
        tokens = self.get_trending()
        if tokens:
            logger.info(f"  Found {len(tokens)} trending tokens")
        return tokens