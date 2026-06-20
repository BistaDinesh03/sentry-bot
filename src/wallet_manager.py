"""
Wallet Manager - Solana/Phantom wallet integration
Handles balances, transactions, and secure key management
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class WalletManager:
    """Manage Solana wallet - PAPER MODE first, real later"""
    
    def __init__(self, mode="paper", wallet_address=None, private_key=None):
        self.mode = mode  # "paper" or "real"
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.balance_sol = 0.0
        self.balance_usdc = 0.0
        self.initialized = False
        
        if mode == "real" and wallet_address:
            self.initialize_real_wallet()
    
    def initialize_real_wallet(self):
        """Initialize real Solana connection"""
        try:
            from solana.rpc.api import Client
            from solders.keypair import Keypair
            
            self.client = Client("https://api.mainnet-beta.solana.com")
            self.initialized = True
            logger.info(f"Wallet connected: {self.wallet_address[:8]}...")
        except Exception as e:
            logger.error(f"Wallet init error: {e}")
            logger.info("Falling back to paper mode")
            self.mode = "paper"
    
    def get_balance(self):
        """Get wallet balance (SOL + USDC)"""
        if self.mode == "paper":
            return {
                'sol': 0.15,  # Simulated
                'usdc': 50.0,  # Simulated
                'total_usd': 60.0  # Simulated
            }
        
        if not self.initialized:
            return {'sol': 0, 'usdc': 0, 'total_usd': 0}
        
        try:
            from solana.rpc.api import Client
            from solders.pubkey import Pubkey
            
            # Get SOL balance
            pubkey = Pubkey.from_string(self.wallet_address)
            response = self.client.get_balance(pubkey)
            sol_balance = response.value / 1e9 if response.value else 0
            
            self.balance_sol = sol_balance
            
            return {
                'sol': sol_balance,
                'usdc': 0,  # Need token account lookup
                'total_usd': sol_balance * 100  # Approximate SOL price
            }
        except Exception as e:
            logger.error(f"Balance check error: {e}")
            return {'sol': 0, 'usdc': 0, 'total_usd': 0}
    
    def simulate_swap(self, token_in, token_out, amount_in, slippage=5.0):
        """Simulate a swap using Jupiter API (paper mode)"""
        try:
            import requests
            
            # Jupiter quote API (real prices, no transaction)
            url = "https://quote-api.jup.ag/v6/quote"
            params = {
                'inputMint': token_in,
                'outputMint': token_out,
                'amount': int(amount_in),
                'slippageBps': int(slippage * 100)
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'in_amount': amount_in,
                    'out_amount': int(data.get('outAmount', 0)),
                    'price_impact': float(data.get('priceImpactPct', 0)),
                    'route': data.get('routePlan', [])
                }
            
            return {'success': False, 'error': response.text}
            
        except Exception as e:
            logger.error(f"Quote error: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_swap(self, token_in, token_out, amount_in, slippage=5.0):
        """Execute a real swap (only if mode='real')"""
        if self.mode == "paper":
            # Simulate swap result
            logger.info(f"[PAPER] Swap: {amount_in} {token_in} -> {token_out}")
            return {
                'success': True,
                'tx_signature': 'PAPER_MODE_SIMULATED',
                'in_amount': amount_in,
                'out_amount': amount_in * 0.99  # Simulated output
            }
        
        if not self.initialized:
            logger.error("Wallet not initialized")
            return {'success': False, 'error': 'Wallet not connected'}
        
        try:
            import requests
            
            # Step 1: Get quote
            quote = self.simulate_swap(token_in, token_out, amount_in, slippage)
            
            if not quote['success']:
                return quote
            
            # Step 2: Get swap transaction
            url = "https://quote-api.jup.ag/v6/swap"
            payload = {
                'quoteResponse': quote,
                'userPublicKey': self.wallet_address,
                'wrapAndUnwrapSol': True,
                'dynamicComputeUnitLimit': True,
                'prioritizationFeeLamports': 100000
            }
            
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                swap_data = response.json()
                
                logger.info(f"Swap prepared: {swap_data.get('swapTransaction', '')[:50]}...")
                
                # In real mode, this would be signed by Phantom wallet
                return {
                    'success': True,
                    'tx_signature': 'REQUIRES_WALLET_SIGNING',
                    'swap_transaction': swap_data.get('swapTransaction'),
                    'in_amount': amount_in,
                    'out_amount': quote.get('out_amount', 0)
                }
            
            return {'success': False, 'error': response.text}
            
        except Exception as e:
            logger.error(f"Swap error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_token_price(self, token_mint):
        """Get token price in USD via Jupiter"""
        try:
            import requests
            
            # Use USDC mint as quote
            usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            
            # Quote 1 USDC worth of token
            result = self.simulate_swap(usdc_mint, token_mint, 1000000, 1.0)
            
            if result['success'] and result['out_amount'] > 0:
                price = 1.0 / (result['out_amount'] / 1e6)
                return price
            
            return 0.0
        except:
            return 0.0
    
    def check_health(self):
        """Check wallet health"""
        balance = self.get_balance()
        
        health = {
            'mode': self.mode,
            'connected': self.initialized,
            'sol_balance': balance['sol'],
            'usdc_balance': balance['usdc'],
            'total_usd': balance['total_usd'],
            'warnings': []
        }
        
        if self.mode == "real":
            if balance['sol'] < 0.02:
                health['warnings'].append("Low SOL for fees (<0.02)")
            if balance['usdc'] < 10:
                health['warnings'].append("Low USDC balance (<$10)")
        
        return health


# Token mint addresses (Solana)
TOKEN_MINTS = {
    'SOL': 'So11111111111111111111111111111111111111112',
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    'WIF': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
    'POPCAT': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr',
}