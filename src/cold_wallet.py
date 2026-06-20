"""
Cold Wallet Manager - Auto-withdraw profits to safe wallet
"""

import logging
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ColdWallet:
    """Manage profit withdrawals to cold storage"""
    
    def __init__(self, wallet_address=None, profit_threshold=50):
        self.wallet_address = wallet_address or "YOUR_COLD_WALLET_ADDRESS"
        self.profit_threshold = profit_threshold
        self.total_withdrawn = 0.0
        self.withdrawal_history = []
        self.last_withdrawal = None
    
    def should_withdraw(self, current_balance, initial_balance):
        """Check if we should withdraw profits"""
        profit = current_balance - initial_balance
        return profit >= self.profit_threshold
    
    def simulate_withdrawal(self, amount, current_balance):
        """Simulate withdrawing profits to cold wallet"""
        if amount <= 0:
            return None
        
        withdrawal = {
            'amount': amount,
            'time': datetime.now().isoformat(),
            'wallet': self.wallet_address[:8] + '...',
            'new_balance': current_balance - amount
        }
        
        self.total_withdrawn += amount
        self.withdrawal_history.append(withdrawal)
        self.last_withdrawal = datetime.now()
        
        logger.info(f"  WITHDRAWAL: ${amount:.2f} to cold wallet")
        logger.info(f"  New Balance: ${withdrawal['new_balance']:.2f}")
        
        return withdrawal
    
    def get_stats(self):
        """Get withdrawal stats"""
        return {
            'wallet': self.wallet_address[:8] + '...',
            'total_withdrawn': self.total_withdrawn,
            'withdrawals': len(self.withdrawal_history),
            'threshold': self.profit_threshold,
            'last_withdrawal': self.last_withdrawal.isoformat() if self.last_withdrawal else None
        }
    
    def save_history(self):
        """Save withdrawal history"""
        try:
            with open('data/withdrawals.json', 'w') as f:
                json.dump({
                    'total_withdrawn': self.total_withdrawn,
                    'history': self.withdrawal_history,
                    'updated': datetime.now().isoformat()
                }, f, indent=2)
        except:
            pass