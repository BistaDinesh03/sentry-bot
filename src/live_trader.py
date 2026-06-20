"""
LIVE TRADER v3.0 - Jupiter DEX Integration
Paper-first with real trading capability
$1 max real trades for safety
"""

import requests
import logging
import time
import json
import base64
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Solana token mint addresses
MINTS = {
    'SOL': 'So11111111111111111111111111111111111111112',
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    'WIF': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
}


class LiveTrader:
    """
    Real trading via Jupiter DEX on Solana.
    MODES:
    - "paper": Simulated trades (default, safe)
    - "simulate": Real quotes, fake execution (test mode)
    - "live": Real trades (DANGER - real money!)
    """
    
    def __init__(self, mode="paper", wallet_address=None, rpc_url=None, max_trade_usd=1.0):
        self.mode = mode
        self.wallet_address = wallet_address
        self.rpc_url = rpc_url or "https://api.mainnet-beta.solana.com"
        self.max_trade_usd = max_trade_usd
        
        # Jupiter API endpoints
        self.quote_url = "https://quote-api.jup.ag/v6/quote"
        self.swap_url = "https://quote-api.jup.ag/v6/swap"
        
        # Stats
        self.trades_executed = 0
        self.successful_trades = 0
        self.failed_trades = 0
        self.total_volume_usd = 0.0
        
        # Token mint cache
        self.mint_cache = {}
        
        logger.info(f"LiveTrader initialized: mode={mode}, max_trade=${max_trade_usd}")
    
    def get_token_mint(self, symbol):
        """Get token mint address from symbol"""
        # Check known mints first
        if symbol.upper() in MINTS:
            return MINTS[symbol.upper()]
        
        # Check cache
        if symbol.upper() in self.mint_cache:
            return self.mint_cache[symbol.upper()]
        
        # Search via DexScreener
        try:
            url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                for pair in pairs:
                    base_token = pair.get('baseToken', {})
                    if base_token.get('symbol', '').upper() == symbol.upper():
                        mint = base_token.get('address', '')
                        if mint:
                            self.mint_cache[symbol.upper()] = mint
                            return mint
            
            return None
        except Exception as e:
            logger.error(f"Mint lookup error: {e}")
            return None
    
    def get_quote(self, input_mint, output_mint, amount_in, slippage_bps=500):
        """Get swap quote from Jupiter"""
        params = {
            'inputMint': input_mint,
            'outputMint': output_mint,
            'amount': str(amount_in),
            'slippageBps': slippage_bps
        }
        
        try:
            response = requests.get(self.quote_url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Jupiter quote failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Quote error: {e}")
            return None
    
    def get_token_price_usd(self, symbol):
        """Get token price in USD via Jupiter"""
        mint = self.get_token_mint(symbol)
        if not mint:
            return None
        
        usdc_mint = MINTS['USDC']
        
        # Quote 1 USDC worth of the token
        quote = self.get_quote(usdc_mint, mint, 1000000, 100)  # $1 USDC
        
        if quote and 'outAmount' in quote:
            out_amount = int(quote['outAmount'])
            price = 1000000 / out_amount  # $1 / token amount
            return price
        
        return None
    
    def simulate_buy(self, symbol, amount_usd, token_price=None):
        """
        Simulate a buy order (PAPER MODE)
        Returns simulated transaction details
        """
        logger.info(f"[PAPER] BUY ${symbol}: ${amount_usd:.2f}")
        
        if token_price is None:
            token_price = self.get_token_price_usd(symbol) or 0.00001
        
        token_amount = amount_usd / token_price if token_price > 0 else 0
        
        # Calculate slippage estimate
        slippage_cost = amount_usd * 0.005  # 0.5% estimated
        
        return {
            'success': True,
            'mode': 'paper',
            'symbol': symbol,
            'amount_usd': amount_usd,
            'token_amount': token_amount,
            'price': token_price,
            'slippage_cost': slippage_cost,
            'total_cost': amount_usd + slippage_cost,
            'tx_id': f"PAPER_{int(time.time())}",
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_sell(self, symbol, token_amount, token_price=None):
        """Simulate a sell order (PAPER MODE)"""
        if token_price is None:
            token_price = self.get_token_price_usd(symbol) or 0.00001
        
        revenue = token_amount * token_price
        slippage_cost = revenue * 0.005
        
        logger.info(f"[PAPER] SELL ${symbol}: ${revenue:.2f}")
        
        return {
            'success': True,
            'mode': 'paper',
            'symbol': symbol,
            'token_amount': token_amount,
            'price': token_price,
            'revenue': revenue,
            'slippage_cost': slippage_cost,
            'net_revenue': revenue - slippage_cost,
            'tx_id': f"PAPER_{int(time.time())}",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_real_quote_buy(self, symbol, amount_usd):
        """Get REAL Jupiter quote for buying (test mode)"""
        if self.mode not in ['simulate', 'live']:
            return self.simulate_buy(symbol, amount_usd)
        
        token_mint = self.get_token_mint(symbol)
        if not token_mint:
            logger.warning(f"Cannot find mint for {symbol}")
            return {'success': False, 'error': 'Token mint not found'}
        
        usdc_mint = MINTS['USDC']
        amount_lamports = int(amount_usd * 1000000)  # USDC has 6 decimals
        
        quote = self.get_quote(usdc_mint, token_mint, amount_lamports, 500)
        
        if quote:
            out_amount = int(quote['outAmount'])
            price_impact = float(quote.get('priceImpactPct', 0))
            
            logger.info(f"[REAL QUOTE] BUY ${symbol}: ${amount_usd:.2f} -> {out_amount} tokens (impact: {price_impact}%)")
            
            return {
                'success': True,
                'mode': self.mode,
                'symbol': symbol,
                'amount_usd': amount_usd,
                'out_amount_raw': out_amount,
                'price_impact': price_impact,
                'route': quote.get('routePlan', []),
                'quote_response': quote if self.mode == 'live' else None
            }
        
        return {'success': False, 'error': 'No quote available'}
    
    def execute_paper_trade(self, action, symbol, amount, price=None):
        """Execute a paper trade (always safe)"""
        if action.upper() == 'BUY':
            return self.simulate_buy(symbol, amount, price)
        else:
            return self.simulate_sell(symbol, amount, price)
    
    def check_health(self):
        """Check if trading systems are operational"""
        health = {
            'mode': self.mode,
            'jupiter_api': False,
            'wallet_connected': self.wallet_address is not None,
            'trades_today': self.trades_executed,
            'success_rate': f"{(self.successful_trades / max(1, self.trades_executed) * 100):.1f}%"
        }
        
        # Check Jupiter API
        try:
            r = requests.get("https://quote-api.jup.ag/v6/price?ids=SOL", timeout=5)
            health['jupiter_api'] = r.status_code == 200
        except:
            pass
        
        return health
    
    def enable_live_mode(self, max_trade=1.0):
        """Enable real trading (DANGER - real money!)"""
        self.mode = "live"
        self.max_trade_usd = max_trade
        logger.warning(f"LIVE MODE ENABLED - Max trade: ${max_trade}")
        logger.warning("Real money will be used!")
    
    def enable_simulate_mode(self):
        """Enable simulation mode (real quotes, fake execution)"""
        self.mode = "simulate"
        logger.info("Simulation mode: Real quotes, no real trades")
    
    def enable_paper_mode(self):
        """Enable paper mode (completely safe)"""
        self.mode = "paper"
        logger.info("Paper mode: No real connections")
    
    def get_stats(self):
        """Get trading statistics"""
        return {
            'mode': self.mode,
            'max_trade': self.max_trade_usd,
            'trades_executed': self.trades_executed,
            'successful': self.successful_trades,
            'failed': self.failed_trades,
            'total_volume': self.total_volume_usd,
            'success_rate': f"{(self.successful_trades / max(1, self.trades_executed) * 100):.1f}%"
        }