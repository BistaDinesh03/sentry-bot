"""Paper Trading Engine - Simulates real trading"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class PaperTrader:
    """Simulates trading with fake money"""
    
    def __init__(self, initial_balance=1000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}  # token -> {amount, buy_price, buy_time}
        self.trade_history = []
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit_loss = 0
    
    def get_portfolio_value(self, current_prices=None):
        """Calculate total portfolio value"""
        value = self.balance
        
        for token, position in self.positions.items():
            if current_prices and token in current_prices:
                value += position['amount'] * current_prices[token]
            else:
                value += position['amount'] * position['buy_price']  # Assume no change
        
        return value
    
    def buy(self, token, amount, price, conviction=0.5):
        """Buy a token (paper trade)"""
        cost = amount * price
        
        if cost > self.balance:
            logger.warning(f"Cannot buy {token}: insufficient balance (need ${cost:.2f}, have ${self.balance:.2f})")
            return None
        
        if cost > self.balance * 0.1:  # Max 10% per trade
            logger.warning(f"Trade too large: ${cost:.2f} exceeds 10% limit")
            return None
        
        self.balance -= cost
        
        if token in self.positions:
            # Average down/up
            old = self.positions[token]
            total_amount = old['amount'] + amount
            avg_price = (old['amount'] * old['buy_price'] + cost) / total_amount
            self.positions[token] = {
                'amount': total_amount,
                'buy_price': avg_price,
                'buy_time': datetime.now().isoformat(),
                'conviction': conviction
            }
        else:
            self.positions[token] = {
                'amount': amount,
                'buy_price': price,
                'buy_time': datetime.now().isoformat(),
                'conviction': conviction
            }
        
        trade = {
            'action': 'BUY',
            'token': token,
            'amount': amount,
            'price': price,
            'cost': cost,
            'time': datetime.now().isoformat(),
            'conviction': conviction
        }
        self.trade_history.append(trade)
        self.total_trades += 1
        
        logger.info(f"BUY  {amount:>8.2f} {token:<10} @ ${price:<8.4f} = ${cost:.2f} [Balance: ${self.balance:.2f}]")
        
        return trade
    
    def sell(self, token, amount, price):
        """Sell a token (paper trade)"""
        if token not in self.positions:
            logger.warning(f"Cannot sell {token}: not in portfolio")
            return None
        
        position = self.positions[token]
        if amount > position['amount']:
            amount = position['amount']  # Sell all
        
        revenue = amount * price
        cost_basis = amount * position['buy_price']
        profit = revenue - cost_basis
        profit_percent = ((price - position['buy_price']) / position['buy_price']) * 100
        
        self.balance += revenue
        self.total_profit_loss += profit
        
        if profit > 0:
            self.winning_trades += 1
        
        # Update or remove position
        remaining = position['amount'] - amount
        if remaining <= 0.0001:
            del self.positions[token]
        else:
            self.positions[token]['amount'] = remaining
        
        trade = {
            'action': 'SELL',
            'token': token,
            'amount': amount,
            'price': price,
            'revenue': revenue,
            'profit': profit,
            'profit_percent': profit_percent,
            'time': datetime.now().isoformat()
        }
        self.trade_history.append(trade)
        self.total_trades += 1
        
        emoji = "GREEN" if profit > 0 else "RED"
        logger.info(f"SELL {amount:>8.2f} {token:<10} @ ${price:<8.4f} = ${revenue:.2f} [{emoji} ${profit:+.2f} ({profit_percent:+.1f}%)] [Balance: ${self.balance:.2f}]")
        
        return trade
    
    def check_exit_conditions(self, token, current_price, volume_24h, avg_volume, hours_held):
        """Check if we should exit a position"""
        if token not in self.positions:
            return None
        
        position = self.positions[token]
        buy_price = position['buy_price']
        price_change = ((current_price - buy_price) / buy_price) * 100
        
        reasons = []
        
        # Price drop
        if price_change <= -15:
            reasons.append(f"Price dropped {price_change:.1f}%")
        
        # Time decay
        if hours_held >= 48:
            reasons.append(f"Held for {hours_held:.1f} hours")
        
        # Volume collapse
        if volume_24h < avg_volume * 0.3:
            reasons.append(f"Volume collapsed {(volume_24h/avg_volume*100):.0f}%")
        
        if reasons:
            return reasons
        
        return None
    
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
            'positions': self.positions
        }
    
    def save_state(self, path="data/portfolio.json"):
        """Save portfolio state"""
        state = {
            'balance': self.balance,
            'positions': self.positions,
            'trade_history': self.trade_history[-100:],  # Last 100 trades
            'stats': self.get_stats()
        }
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, path="data/portfolio.json"):
        """Load portfolio state"""
        try:
            with open(path, 'r') as f:
                state = json.load(f)
                self.balance = state.get('balance', self.initial_balance)
                self.positions = state.get('positions', {})
                self.trade_history = state.get('trade_history', [])
                logger.info(f"Loaded portfolio: ${self.balance:.2f} balance, {len(self.positions)} positions")
        except FileNotFoundError:
            logger.info("No saved portfolio found, starting fresh")