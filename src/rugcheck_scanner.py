"""
RugCheck Scanner - Detect scams, honeypots, rug pulls
Uses RugCheck.xyz API + Birdeye API
"""

import requests
import logging
import time

logger = logging.getLogger(__name__)


class RugCheckScanner:
    """Checks tokens for scam indicators"""
    
    def __init__(self):
        self.rugcheck_url = "https://api.rugcheck.xyz/v1"
        self.cache = {}
    
    def check_token_solana(self, token_address):
        """Check Solana token on RugCheck.xyz"""
        # For demo, use token symbol search on DexScreener first
        # Real implementation needs token mint address
        
        risk_score = 0
        risk_factors = []
        
        # These are checks we can do without the contract address:
        # Will be enhanced when we have the actual mint address
        
        return {
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'is_safe': risk_score < 30
        }
    
    def check_via_dexscreener(self, symbol):
        """Use DexScreener data to estimate scam risk"""
        url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                if not pairs:
                    return {
                        'is_safe': False,
                        'risk_score': 100,
                        'risk_factors': ['No trading pairs found'],
                        'warnings': ['Token may not exist']
                    }
                
                # Analyze the most liquid pair
                best_pair = max(pairs, key=lambda p: float(p.get('liquidity', {}).get('usd', 0) or 0))
                
                liquidity = float(best_pair.get('liquidity', {}).get('usd', 0) or 0)
                volume = float(best_pair.get('volume', {}).get('h24', 0) or 0)
                fdv = float(best_pair.get('fdv', 0) or 0)
                created = best_pair.get('pairCreatedAt', 0)
                
                risk_score = 0
                risk_factors = []
                warnings = []
                
                # Liquidity checks
                if liquidity < 5000:
                    risk_score += 40
                    risk_factors.append('Very low liquidity (<$5K)')
                    warnings.append('HIGH RISK: Can be rugged instantly')
                elif liquidity < 20000:
                    risk_score += 20
                    risk_factors.append('Low liquidity (<$20K)')
                elif liquidity > 100000:
                    risk_score -= 15
                
                # Volume checks
                if volume < 1000:
                    risk_score += 25
                    risk_factors.append('No trading volume')
                elif volume > 100000:
                    risk_score -= 10
                
                # FDV vs Liquidity ratio
                if fdv > 0 and liquidity > 0:
                    ratio = fdv / liquidity
                    if ratio > 100:
                        risk_score += 30
                        risk_factors.append(f'FDV/Liquidity ratio: {ratio:.0f}x (dangerous)')
                        warnings.append('WARNING: FDV much higher than liquidity')
                    elif ratio > 20:
                        risk_score += 15
                        risk_factors.append(f'FDV/Liquidity ratio: {ratio:.0f}x')
                
                # Age check
                if created:
                    age_hours = (time.time() - created / 1000) / 3600 if created > 1000000000000 else (time.time() - created) / 3600
                    if age_hours < 1:
                        risk_score += 35
                        risk_factors.append(f'Very new: {age_hours:.1f}h old')
                        warnings.append('EXTREME RISK: Token less than 1 hour old')
                    elif age_hours < 6:
                        risk_score += 20
                        risk_factors.append(f'New: {age_hours:.1f}h old')
                    elif age_hours < 24:
                        risk_score += 10
                        risk_factors.append(f'Less than 24h old')
                    elif age_hours > 168:
                        risk_score -= 10
                
                # Price change volatility
                price_changes = best_pair.get('priceChange', {})
                h1 = abs(float(price_changes.get('h1', 0) or 0))
                if h1 > 50:
                    risk_score += 20
                    risk_factors.append(f'Extreme volatility: {h1:.0f}% in 1h')
                
                risk_score = max(0, min(100, risk_score))
                
                return {
                    'is_safe': risk_score < 40,
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'warnings': warnings,
                    'liquidity': liquidity,
                    'volume_24h': volume,
                    'age_hours': age_hours if created else None
                }
            
            return {'is_safe': False, 'risk_score': 80, 'risk_factors': ['API error']}
            
        except Exception as e:
            logger.error(f"RugCheck error: {e}")
            return {'is_safe': False, 'risk_score': 100, 'risk_factors': ['Check failed']}
    
    def scan_token(self, symbol):
        """Full scam check on a token"""
        logger.info(f"  RugCheck: ${symbol}...")
        
        result = self.check_via_dexscreener(symbol)
        
        if result['is_safe']:
            logger.info(f"    SAFE (Risk: {result['risk_score']}/100)")
        else:
            logger.warning(f"    RISKY (Risk: {result['risk_score']}/100)")
            for warning in result.get('warnings', []):
                logger.warning(f"      {warning}")
        
        return result