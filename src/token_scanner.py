"""
Real Token Scanner using DexScreener API
Gets REAL prices, volume, liquidity, and validates tokens
"""

import requests
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class TokenScanner:
    """Scans DexScreener for real tokens and prices"""
    
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex"
        self.session = requests.Session()
        self.rate_limit_delay = 1  # 1 second between calls
    
    def search_token(self, query):
        """Search for a token by name or symbol"""
        url = f"{self.base_url}/search?q={query}"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                return pairs
            else:
                logger.warning(f"DexScreener search returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"DexScreener error: {e}")
            return []
    
    def get_token_info(self, chain_id, pair_address):
        """Get detailed info about a specific token pair"""
        url = f"{self.base_url}/pairs/{chain_id}/{pair_address}"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return None
    
    def get_latest_tokens(self, chain="solana", limit=20):
        """Get latest tokens created on a chain"""
        url = f"{self.base_url}/search?q={chain}"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                # Filter and sort by creation time
                valid_pairs = []
                for pair in pairs[:limit]:
                    token_info = self.validate_token(pair)
                    if token_info:
                        valid_pairs.append(token_info)
                
                return valid_pairs
            return []
        except Exception as e:
            logger.error(f"Error getting latest tokens: {e}")
            return []
    
    def validate_token(self, pair):
        """Validate a token for safety and potential"""
        try:
            base_token = pair.get('baseToken', {})
            quote_token = pair.get('quoteToken', {})
            
            # Basic info
            name = base_token.get('name', 'Unknown')
            symbol = base_token.get('symbol', 'UNKNOWN')
            price_usd = float(pair.get('priceUsd', 0) or 0)
            volume_24h = float(pair.get('volume', {}).get('h24', 0) or 0)
            liquidity = float(pair.get('liquidity', {}).get('usd', 0) or 0)
            market_cap = float(pair.get('fdv', 0) or 0)
            
            # Price changes
            price_change_5m = float(pair.get('priceChange', {}).get('m5', 0) or 0)
            price_change_1h = float(pair.get('priceChange', {}).get('h1', 0) or 0)
            price_change_24h = float(pair.get('priceChange', {}).get('h24', 0) or 0)
            
            # DexScreener URL for more info
            url = pair.get('url', '')
            
            # Chain info
            chain = pair.get('chainId', 'unknown')
            
            # Liquidity check (minimum $1000 for safety)
            if liquidity < 1000:
                return None
            
            # Volume check (must have some activity)
            if volume_24h < 100:
                return None
            
            # Calculate risk score (0-100, lower is safer)
            risk_score = 50
            risk_factors = []
            
            # Liquidity risk
            if liquidity < 10000:
                risk_score += 15
                risk_factors.append("Low liquidity")
            elif liquidity > 100000:
                risk_score -= 10
            
            # Volume risk
            if volume_24h < 1000:
                risk_score += 10
                risk_factors.append("Low volume")
            
            # Price stability
            if abs(price_change_5m) > 50:
                risk_score += 20
                risk_factors.append("Extreme volatility")
            
            # Market cap
            if market_cap > 0 and market_cap < 50000:
                risk_score += 15
                risk_factors.append("Micro cap")
            
            return {
                'name': name,
                'symbol': symbol,
                'price_usd': price_usd,
                'volume_24h': volume_24h,
                'liquidity_usd': liquidity,
                'market_cap': market_cap,
                'price_change_5m': price_change_5m,
                'price_change_1h': price_change_1h,
                'price_change_24h': price_change_24h,
                'chain': chain,
                'url': url,
                'risk_score': max(0, min(100, risk_score)),
                'risk_factors': risk_factors,
                'is_safe': risk_score < 60,
                'pair_address': pair.get('pairAddress', '')
            }
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return None
    
    def scan_trending(self, chain="solana"):
        """Scan for trending tokens"""
        logger.info(f"Scanning DexScreener for trending {chain} tokens...")
        
        pairs = self.get_latest_tokens(chain)
        
        if pairs:
            logger.info(f"  Found {len(pairs)} valid tokens")
            
            # Sort by volume (most active first)
            pairs.sort(key=lambda x: x['volume_24h'], reverse=True)
            
            for token in pairs[:5]:
                risk_emoji = "🟢" if token['is_safe'] else "🟡" if token['risk_score'] < 80 else "🔴"
                logger.info(f"    {risk_emoji} ${token['symbol']} - ${token['price_usd']:.8f} | "
                          f"Vol: ${token['volume_24h']:,.0f} | "
                          f"Liq: ${token['liquidity_usd']:,.0f} | "
                          f"Risk: {token['risk_score']}/100")
                
                if token['risk_factors']:
                    logger.info(f"       Risks: {', '.join(token['risk_factors'])}")
        else:
            logger.info("  No valid tokens found")
        
        return pairs
    
    def get_real_price(self, symbol):
        """Get real price for a token symbol"""
        pairs = self.search_token(symbol)
        
        if pairs:
            # Return first valid pair with USD price
            for pair in pairs:
                price = float(pair.get('priceUsd', 0) or 0)
                if price > 0:
                    return {
                        'symbol': symbol,
                        'price': price,
                        'volume_24h': float(pair.get('volume', {}).get('h24', 0) or 0),
                        'liquidity': float(pair.get('liquidity', {}).get('usd', 0) or 0),
                        'chain': pair.get('chainId', 'unknown')
                    }
        
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scanner = TokenScanner()
    
    print("\n=== TESTING REAL TOKEN SCANNER ===\n")
    
    # Test 1: Search for a real token
    print("1. Searching for 'BONK'...")
    result = scanner.get_real_price("BONK")
    if result:
        print(f"   Found BONK: ${result['price']:.8f} | Chain: {result['chain']}")
    else:
        print("   BONK not found on DexScreener")
    
    # Test 2: Get trending tokens
    print("\n2. Scanning trending Solana tokens...")
    scanner.scan_trending("solana")
    
    print("\n=== SCANNER TEST COMPLETE ===")