"""
Real Trading Module - Hybrid Paper/Real trading
Paper mode with real wallet connection for testing
"""

import logging
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class RealTrader:
    """Real trading with paper mode safety"""
    
    def __init__(self, wallet_manager, initial_balance=1000):
        self.wallet = wallet_manager
        self.mode = "paper"  # Always start paper
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}
        self.trade_history = []
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit_loss = 0.0
        self.max_real_trade_size = 1.0  # Max $1 per real trade initially
    
    def get_stats(self):
        """Get trading statistics"""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'balance': self.balance,
            'initial_balance': self.initial_balance,
            'total_profit_loss': self.total_profit_loss,
            'total_return_percent': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': win_rate,
            'open_positions': len(self.positions),
            'positions': self.positions,
            'mode': self.mode
        }
    
    def buy(self, token_symbol, amount, price, conviction=0.5):
        """Buy token - paper or real based on mode"""
        cost = amount * price
        
        if cost > self.balance * 0.1:
            logger.warning(f"Trade too large: ${cost:.2f}")
            return None
        
        if self.mode == "real" and cost > self.max_real_trade_size:
            logger.info(f"[PAPER FALLBACK] Real trades limited to ${self.max_real_trade_size}")
        
        # Always track paper first
        self.balance -= cost
        
        if token_symbol in self.positions:
            old = self.positions[token_symbol]
            total_amount = old['amount'] + amount
            avg_price = (old['amount'] * old['buy_price'] + cost) / total_amount
            self.positions[token_symbol] = {
                'amount': total_amount,
                'buy_price': avg_price,
                'buy_time': datetime.now().isoformat(),
                'conviction': conviction
            }
        else:
            self.positions[token_symbol] = {
                'amount': amount,
                'buy_price': price,
                'buy_time': datetime.now().isoformat(),
                'conviction': conviction
            }
        
        trade = {
            'action': 'BUY',
            'token': token_symbol,
            'amount': amount,
            'price': price,
            'cost': cost,
            'time': datetime.now().isoformat(),
            'conviction': conviction,
            'mode': self.mode
        }
        self.trade_history.append(trade)
        self.total_trades += 1
        
        # If real mode and small enough, execute on-chain
        if self.mode == "real" and cost <= self.max_real_trade_size:
            logger.info(f"[REAL BUY] {amount:.2f} {token_symbol} @ ${price:.8f} = ${cost:.2f}")
            # TODO: Execute real swap via Jupiter
        else:
            logger.info(f"[PAPER BUY] {amount:.2f} {token_symbol} @ ${price:.8f} = ${cost:.2f}")
        
        return trade
    
    def sell(self, token_symbol, amount, price):
        """Sell token"""
        if token_symbol not in self.positions:
            return None
        
        position = self.positions[token_symbol]
        if amount > position['amount']:
            amount = position['amount']
        
        revenue = amount * price
        cost_basis = amount * position['buy_price']
        profit = revenue - cost_basis
        
        self.balance += revenue
        self.total_profit_loss += profit
        
        if profit > 0:
            self.winning_trades += 1
        
        remaining = position['amount'] - amount
        if remaining <= 0.0001:
            del self.positions[token_symbol]
        else:
            self.positions[token_symbol]['amount'] = remaining
        
        trade = {
            'action': 'SELL',
            'token': token_symbol,
            'amount': amount,
            'price': price,
            'revenue': revenue,
            'profit': profit,
            'profit_percent': ((price - position['buy_price']) / position['buy_price']) * 100,
            'time': datetime.now().isoformat(),
            'mode': self.mode
        }
        self.trade_history.append(trade)
        self.total_trades += 1
        
        if profit > 0:
            logger.info(f"[SELL PROFIT] {token_symbol}: ${profit:+.2f}")
        else:
            logger.info(f"[SELL LOSS] {token_symbol}: ${profit:+.2f}")
        
        return trade
    
    def enable_real_mode(self, max_trade_size=1.0):
        """Switch to real trading with safety limits"""
        self.mode = "real"
        self.max_real_trade_size = max_trade_size
        logger.info(f"REAL MODE ENABLED - Max trade: ${max_trade_size}")
        logger.info(f"Start with small amounts and increase gradually!")
    
    def enable_paper_mode(self):
        """Switch back to paper trading"""
        self.mode = "paper"
        logger.info("Switched to PAPER mode")
    
    def save_state(self, path="data/portfolio.json"):
        """Save portfolio state"""
        try:
            state = {
                'balance': self.balance,
                'positions': self.positions,
                'trade_history': self.trade_history[-100:],
                'stats': self.get_stats(),
                'mode': self.mode
            }
            with open(path, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def load_state(self, path="data/portfolio.json"):
        """Load portfolio state"""
        try:
            with open(path, 'r') as f:
                state = json.load(f)
                self.balance = state.get('balance', self.initial_balance)
                self.positions = state.get('positions', {})
                self.trade_history = state.get('trade_history', [])
                self.mode = state.get('mode', 'paper')
                logger.info(f"Loaded portfolio: ${self.balance:.2f} ({self.mode} mode)")
        except FileNotFoundError:
            logger.info("Fresh portfolio started")
        except Exception as e:
            logger.error(f"Load error: {e}")