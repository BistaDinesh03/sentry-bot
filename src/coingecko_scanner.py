"""
CoinGecko Scanner - Trending coins, new listings, categories
FREE API - No key needed
"""

import requests
import logging
import time

logger = logging.getLogger(__name__)


class CoinGeckoScanner:
    """Gets trending and new coins from CoinGecko"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_time = {}
        self.request_delay = 2
    
    def get_trending(self):
        """Get trending coins"""
        url = f"{self.base_url}/search/trending"
        
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                coins = data.get('coins', [])
                
                trending = []
                for item in coins[:15]:
                    coin = item.get('item', {})
                    trending.append({
                        'symbol': coin.get('symbol', '').upper(),
                        'name': coin.get('name', ''),
                        'market_cap_rank': coin.get('market_cap_rank', 0),
                        'score': coin.get('score', 0),
                        'source': 'coingecko_trending'
                    })
                
                return trending
            elif response.status_code == 429:
                logger.warning("CoinGecko rate limited")
                time.sleep(30)
                return []
            else:
                return []
        except Exception as e:
            logger.error(f"CoinGecko trending error: {e}")
            return []
    
    def get_new_coins(self):
        """Get recently added coins"""
        url = f"{self.base_url}/coins/list/new"
        
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                new_coins = []
                for coin in data[:20]:
                    new_coins.append({
                        'symbol': coin.get('symbol', '').upper(),
                        'name': coin.get('name', ''),
                        'source': 'coingecko_new'
                    })
                
                return new_coins
            return []
        except Exception as e:
            logger.error(f"CoinGecko new coins error: {e}")
            return []
    
    def get_meme_category(self):
        """Get coins in meme category"""
        url = f"{self.base_url}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'category': 'meme-token',
            'order': 'volume_desc',
            'per_page': 20,
            'page': 1,
            'sparkline': False
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                memes = []
                for coin in data:
                    memes.append({
                        'symbol': coin.get('symbol', '').upper(),
                        'name': coin.get('name', ''),
                        'price': coin.get('current_price', 0),
                        'volume_24h': coin.get('total_volume', 0),
                        'market_cap': coin.get('market_cap', 0),
                        'price_change_24h': coin.get('price_change_percentage_24h', 0),
                        'source': 'coingecko_meme'
                    })
                
                return memes
            return []
        except Exception as e:
            logger.error(f"CoinGecko meme error: {e}")
            return []
    
    def scan_all(self):
        """Full scan - trending + new + meme category"""
        logger.info("CoinGecko: Scanning trending + new + meme coins...")
        
        trending = self.get_trending()
        time.sleep(self.request_delay)
        
        new_coins = self.get_new_coins()
        time.sleep(self.request_delay)
        
        meme_coins = self.get_meme_category()
        
        all_coins = trending + new_coins + meme_coins
        
        # Extract unique symbols
        symbols = list(set([c['symbol'] for c in all_coins]))
        
        logger.info(f"  CoinGecko: {len(trending)} trending, {len(new_coins)} new, {len(meme_coins)} meme")
        logger.info(f"  Total unique symbols: {len(symbols)}")
        
        if trending:
            top = trending[:5]
            logger.info(f"  Trending: {', '.join([c['symbol'] for c in top])}")
        
        return all_coins, symbols