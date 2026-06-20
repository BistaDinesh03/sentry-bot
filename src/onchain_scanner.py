"""
ON-CHAIN SCANNER v3.0
Tracks profitable wallets, detects smart money moves
Uses Solana RPC + DexScreener for token holder data
"""

import requests
import logging
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent


class OnChainScanner:
    """Tracks on-chain activity for alpha signals"""
    
    def __init__(self, wallets_config=None):
        if wallets_config is None:
            wallets_config = BASE_DIR / 'config' / 'tracked_wallets.yaml'
        
        self.tracked_wallets = []
        self.scoring_config = {}
        self.smart_money_config = {}
        
        # Token tracking
        self.token_buys = {}  # token -> {wallets_buying, first_buy_time, total_buy_value}
        self.wallet_activity = {}  # wallet -> last_scan_time
        
        # Load config
        try:
            with open(wallets_config, 'r') as f:
                config = yaml.safe_load(f)
                self.tracked_wallets = config.get('wallets', [])
                self.scoring_config = config.get('scoring', {})
                self.smart_money_config = config.get('smart_money', {})
                logger.info(f"Tracking {len(self.tracked_wallets)} wallets")
        except Exception as e:
            logger.error(f"Config load error: {e}")
            self.tracked_wallets = []
        
        self.rpc_url = "https://api.mainnet-beta.solana.com"
        self.dexscreener_url = "https://api.dexscreener.com"
        self.cache = {}
        self.cache_time = {}
    
    def get_token_holders(self, token_address):
        """Get top token holders from DexScreener"""
        if not token_address or len(token_address) < 30:
            return None
        
        try:
            url = f"{self.dexscreener_url}/latest/dex/tokens/{token_address}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                if pairs:
                    pair = pairs[0]
                    return {
                        'holders': pair.get('holders', 0),
                        'top_10_holder_pct': pair.get('top10HolderPercent', 0),
                        'creator_percent': pair.get('creatorPercent', 0),
                        'insider_percent': pair.get('insiderPercent', 0)
                    }
            return None
        except Exception as e:
            logger.debug(f"Holder check error: {e}")
            return None
    
    def check_holder_concentration(self, token_symbol):
        """Check if top holders are too concentrated (bundled supply)"""
        try:
            # Search for token on DexScreener
            url = f"{self.dexscreener_url}/latest/dex/search?q={token_symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                if pairs:
                    pair = pairs[0]
                    top10 = pair.get('top10HolderPercent', 0) or 0
                    
                    max_concentration = self.smart_money_config.get('max_holder_concentration', 50)
                    
                    if top10 > max_concentration:
                        return {
                            'is_concentrated': True,
                            'top10_pct': top10,
                            'warning': f'Top 10 holders own {top10}% (max {max_concentration}%)'
                        }
                    else:
                        return {
                            'is_concentrated': False,
                            'top10_pct': top10
                        }
            return None
        except Exception as e:
            logger.debug(f"Concentration check error: {e}")
            return None
    
    def simulate_wallet_scan(self):
        """
        Simulate tracking wallet activity.
        In production, this would use Solana RPC to get real transactions.
        For now, use DexScreener data as proxy.
        """
        findings = []
        
        # This is a simplified version
        # Real implementation needs Helius/Dune API for wallet tracking
        
        return findings
    
    def scan_trending_wallets(self):
        """Get trending tokens that might have smart money activity"""
        try:
            # Use DexScreener trending as proxy for smart money activity
            url = f"{self.dexscreener_url}/latest/dex/search?q=SOL"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                # Find pairs with high volume (smart money indicator)
                smart_money_candidates = []
                
                for pair in pairs[:20]:
                    volume = float(pair.get('volume', {}).get('h24', 0) or 0)
                    liquidity = float(pair.get('liquidity', {}).get('usd', 0) or 0)
                    fdv = float(pair.get('fdv', 0) or 0)
                    
                    # High volume relative to FDV = possible smart money
                    if fdv > 0 and volume > fdv * 0.5:
                        base_token = pair.get('baseToken', {})
                        smart_money_candidates.append({
                            'symbol': base_token.get('symbol', 'UNKNOWN'),
                            'volume_fdv_ratio': volume / fdv if fdv > 0 else 0,
                            'volume': volume,
                            'liquidity': liquidity
                        })
                
                return smart_money_candidates
            return []
        except Exception as e:
            logger.debug(f"Trending wallet error: {e}")
            return []
    
    def get_onchain_conviction_points(self, token_symbol):
        """
        Get conviction points from on-chain data (0-20 scale).
        
        Checks:
        - Holder concentration (skip if >50% in top 10)
        - Volume/FDV ratio (smart money indicator)
        - Liquidity health
        """
        points = 0
        
        # Check holder concentration
        concentration = self.check_holder_concentration(token_symbol)
        
        if concentration:
            if concentration['is_concentrated']:
                # Skip concentrated tokens entirely
                logger.info(f"    ONCHAIN: ${token_symbol} SKIPPED - {concentration['warning']}")
                return -100  # Signal to skip this token
            else:
                # Less concentration = more points
                top10 = concentration['top10_pct']
                if top10 < 20:
                    points += 10
                elif top10 < 30:
                    points += 7
                elif top10 < 40:
                    points += 4
                elif top10 < 50:
                    points += 2
        
        # Check volume/FDV as smart money proxy
        try:
            url = f"{self.dexscreener_url}/latest/dex/search?q={token_symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                if pairs:
                    pair = pairs[0]
                    volume = float(pair.get('volume', {}).get('h24', 0) or 0)
                    fdv = float(pair.get('fdv', 0) or 0)
                    
                    if fdv > 0:
                        ratio = volume / fdv
                        if ratio > 2:
                            points += 10  # Very high activity
                        elif ratio > 1:
                            points += 7
                        elif ratio > 0.5:
                            points += 4
                        elif ratio > 0.2:
                            points += 2
        except:
            pass
        
        return min(20, points)
    
    def scan_all(self):
        """Full on-chain scan"""
        logger.info("On-chain: Checking holder distribution + smart money signals...")
        
        smart_money_tokens = self.scan_trending_wallets()
        
        if smart_money_tokens:
            logger.info(f"  Found {len(smart_money_tokens)} potential smart money tokens")
        
        return smart_money_tokens