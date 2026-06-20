"""
Performance Tracker - Track win rate, profit factor, metrics
"""

import json
import time
from datetime import datetime
from pathlib import Path

class PerformanceTracker:
    """Track and analyze trading performance"""
    
    def __init__(self, save_path="data/performance.json"):
        self.save_path = save_path
        self.trades = []
        self.daily_pnl = {}
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'best_token': '',
            'worst_token': '',
            'token_performance': {}
        }
        self.load()
    
    def add_trade(self, trade):
        """Record a completed trade"""
        self.trades.append(trade)
        
        profit = trade.get('profit', 0)
        token = trade.get('token', 'unknown')
        date = datetime.now().strftime('%Y-%m-%d')
        
        # Update metrics
        self.metrics['total_trades'] += 1
        
        if profit > 0:
            self.metrics['winning_trades'] += 1
            self.metrics['total_profit'] += profit
            self.metrics['largest_win'] = max(self.metrics['largest_win'], profit)
        else:
            self.metrics['losing_trades'] += 1
            self.metrics['total_loss'] += abs(profit)
            self.metrics['largest_loss'] = min(self.metrics['largest_loss'], profit)
        
        # Token performance
        if token not in self.metrics['token_performance']:
            self.metrics['token_performance'][token] = {'trades': 0, 'profit': 0.0}
        self.metrics['token_performance'][token]['trades'] += 1
        self.metrics['token_performance'][token]['profit'] += profit
        
        # Daily P/L
        if date not in self.daily_pnl:
            self.daily_pnl[date] = 0.0
        self.daily_pnl[date] += profit
        
        # Calculate derived metrics
        self._calculate_metrics()
        self.save()
    
    def _calculate_metrics(self):
        """Calculate performance metrics"""
        total = self.metrics['total_trades']
        wins = self.metrics['winning_trades']
        losses = self.metrics['losing_trades']
        
        # Win rate
        self.metrics['win_rate'] = (wins / total * 100) if total > 0 else 0
        
        # Average win/loss
        self.metrics['avg_win'] = (self.metrics['total_profit'] / wins) if wins > 0 else 0
        self.metrics['avg_loss'] = (self.metrics['total_loss'] / losses) if losses > 0 else 0
        
        # Profit factor
        if self.metrics['total_loss'] > 0:
            self.metrics['profit_factor'] = self.metrics['total_profit'] / self.metrics['total_loss']
        else:
            self.metrics['profit_factor'] = self.metrics['total_profit'] if self.metrics['total_profit'] > 0 else 0
        
        # Best/worst token
        token_perf = self.metrics['token_performance']
        if token_perf:
            best = max(token_perf.items(), key=lambda x: x[1]['profit'])
            worst = min(token_perf.items(), key=lambda x: x[1]['profit'])
            self.metrics['best_token'] = best[0]
            self.metrics['worst_token'] = worst[0]
    
    def get_summary(self):
        """Get performance summary"""
        return {
            'total_trades': self.metrics['total_trades'],
            'win_rate': f"{self.metrics['win_rate']:.1f}%",
            'profit_factor': f"{self.metrics['profit_factor']:.2f}",
            'total_profit': f"${self.metrics['total_profit']:+.2f}",
            'avg_win': f"${self.metrics['avg_win']:.2f}",
            'avg_loss': f"${self.metrics['avg_loss']:.2f}",
            'largest_win': f"${self.metrics['largest_win']:.2f}",
            'largest_loss': f"${self.metrics['largest_loss']:.2f}",
            'best_token': f"${self.metrics['best_token']}",
            'worst_token': f"${self.metrics['worst_token']}",
            'today_pnl': f"${self.daily_pnl.get(datetime.now().strftime('%Y-%m-%d'), 0):+.2f}"
        }
    
    def save(self):
        """Save to file"""
        try:
            data = {
                'metrics': self.metrics,
                'daily_pnl': self.daily_pnl,
                'trades_count': len(self.trades),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def load(self):
        """Load from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                self.metrics = data.get('metrics', self.metrics)
                self.daily_pnl = data.get('daily_pnl', {})
        except:
            pass
    
    def print_report(self):
        """Print performance report"""
        print("\n" + "=" * 50)
        print("  PERFORMANCE REPORT")
        print("=" * 50)
        print(f"  Total Trades: {self.metrics['total_trades']}")
        print(f"  Win Rate: {self.metrics['win_rate']:.1f}%")
        print(f"  Profit Factor: {self.metrics['profit_factor']:.2f}")
        print(f"  Total P/L: ${self.metrics['total_profit'] - self.metrics['total_loss']:+.2f}")
        print(f"  Avg Win: ${self.metrics['avg_win']:.2f}")
        print(f"  Avg Loss: ${self.metrics['avg_loss']:.2f}")
        print(f"  Best Token: ${self.metrics['best_token']}")
        print(f"  Worst Token: ${self.metrics['worst_token']}")
        print(f"  Today P/L: ${self.daily_pnl.get(datetime.now().strftime('%Y-%m-%d'), 0):+.2f}")
        print("=" * 50)