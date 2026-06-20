"""
BACKTESTER v3.0 - Test scoring model against historical data
Shows if your strategy would have made money
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent


class Backtester:
    """Test trading strategies against historical trades"""
    
    def __init__(self):
        self.trades = []
        self.results = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'total_return': 0.0,
        }
    
    def load_trades(self, portfolio_file="data/portfolio.json"):
        """Load trade history from portfolio file"""
        try:
            path = BASE_DIR / portfolio_file
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.trades = data.get('trade_history', [])
                    logger.info(f"Loaded {len(self.trades)} trades")
                    return True
            else:
                logger.warning(f"No portfolio file found at {path}")
                return False
        except Exception as e:
            logger.error(f"Load error: {e}")
            return False
    
    def load_trades_from_log(self, log_file="logs/sentry.log"):
        """Extract trades from log file"""
        try:
            path = BASE_DIR / log_file
            if not path.exists():
                return False
            
            trades = []
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'SELL' in line and 'P/L:' in line:
                        # Parse sell lines for profit/loss
                        try:
                            parts = line.split('|')
                            token = ''
                            profit = 0.0
                            
                            for part in parts:
                                if 'SELL $' in part:
                                    token = part.split('$')[1].split(':')[0].strip()
                                if 'P/L: $' in part:
                                    profit_str = part.split('P/L: $')[1].strip()
                                    profit = float(profit_str)
                            
                            if token:
                                trades.append({
                                    'action': 'SELL',
                                    'token': token,
                                    'profit': profit,
                                    'time': line[:19] if len(line) > 19 else ''
                                })
                        except:
                            pass
            
            if trades:
                self.trades = trades
                logger.info(f"Extracted {len(trades)} trades from log")
                return True
            return False
        except Exception as e:
            logger.error(f"Log parse error: {e}")
            return False
    
    def analyze(self):
        """Analyze all trades and calculate metrics"""
        if not self.trades:
            logger.warning("No trades to analyze")
            return self.results
        
        profits = []
        balance = 1000  # Starting balance
        balance_history = [1000]
        current_drawdown = 0
        max_drawdown = 0
        peak = 1000
        
        for trade in self.trades:
            profit = trade.get('profit', 0)
            
            self.results['total_trades'] += 1
            
            if profit > 0:
                self.results['winning_trades'] += 1
                self.results['total_profit'] += profit
                self.results['largest_win'] = max(self.results['largest_win'], profit)
            else:
                self.results['losing_trades'] += 1
                self.results['total_loss'] += abs(profit)
                self.results['largest_loss'] = min(self.results['largest_loss'], profit)
            
            profits.append(profit)
            balance += profit
            balance_history.append(balance)
            
            # Track drawdown
            if balance > peak:
                peak = balance
                current_drawdown = 0
            else:
                current_drawdown = (peak - balance) / peak * 100
                max_drawdown = max(max_drawdown, current_drawdown)
        
        # Calculate metrics
        total = self.results['total_trades']
        wins = self.results['winning_trades']
        losses = self.results['losing_trades']
        
        if total > 0:
            self.results['win_rate'] = (wins / total) * 100
        
        if wins > 0:
            self.results['avg_win'] = self.results['total_profit'] / wins
        
        if losses > 0:
            self.results['avg_loss'] = self.results['total_loss'] / losses
        
        if self.results['total_loss'] > 0:
            self.results['profit_factor'] = self.results['total_profit'] / self.results['total_loss']
        elif self.results['total_profit'] > 0:
            self.results['profit_factor'] = 999  # Infinite (no losses)
        
        self.results['total_return'] = ((balance - 1000) / 1000) * 100
        self.results['max_drawdown'] = max_drawdown
        self.results['final_balance'] = balance
        
        # Sharpe ratio (simplified)
        if len(profits) > 1:
            avg_return = sum(profits) / len(profits)
            variance = sum((r - avg_return) ** 2 for r in profits) / len(profits)
            std_dev = variance ** 0.5
            if std_dev > 0:
                self.results['sharpe_ratio'] = (avg_return / std_dev) * (252 ** 0.5)  # Annualized
        
        return self.results
    
    def print_report(self):
        """Print formatted backtest report"""
        r = self.analyze()
        
        print("\n" + "=" * 50)
        print("  BACKTEST RESULTS")
        print("=" * 50)
        print(f"  Total Trades: {r['total_trades']}")
        print(f"  Win Rate: {r['win_rate']:.1f}%")
        print(f"  Profit Factor: {r['profit_factor']:.2f}")
        print(f"  Total P/L: ${r['total_profit'] - r['total_loss']:+.2f}")
        print(f"  Return: {r['total_return']:+.2f}%")
        print(f"  Max Drawdown: {r['max_drawdown']:.1f}%")
        print(f"  Sharpe Ratio: {r['sharpe_ratio']:.2f}")
        print(f"  Final Balance: ${r['final_balance']:.2f}")
        print(f"  Avg Win: ${r['avg_win']:.2f}")
        print(f"  Avg Loss: ${r['avg_loss']:.2f}")
        print(f"  Largest Win: ${r['largest_win']:.2f}")
        print(f"  Largest Loss: ${r['largest_loss']:.2f}")
        print("=" * 50)
        
        # Grade
        if r['profit_factor'] > 2 and r['win_rate'] > 40:
            grade = "A - PROFESSIONAL GRADE"
        elif r['profit_factor'] > 1.5 and r['win_rate'] > 35:
            grade = "B - GOOD"
        elif r['profit_factor'] > 1.2:
            grade = "C - DECENT"
        elif r['profit_factor'] > 1.0:
            grade = "D - BREAKEVEN"
        else:
            grade = "F - LOSING"
        
        print(f"\n  GRADE: {grade}")
        print("=" * 50)
        
        return r
    
    def compare_strategies(self, strategy_a_trades, strategy_b_trades):
        """Compare two strategies"""
        print("\n" + "=" * 50)
        print("  STRATEGY COMPARISON")
        print("=" * 50)
        
        self.trades = strategy_a_trades
        a = self.analyze()
        
        self.trades = strategy_b_trades
        b = self.analyze()
        
        print(f"  {'Metric':<20} {'Strategy A':>12} {'Strategy B':>12}")
        print(f"  {'-'*20} {'-'*12} {'-'*12}")
        print(f"  {'Win Rate':<20} {a['win_rate']:>11.1f}% {b['win_rate']:>11.1f}%")
        print(f"  {'Profit Factor':<20} {a['profit_factor']:>12.2f} {b['profit_factor']:>12.2f}")
        print(f"  {'Total Return':<20} {a['total_return']:>11.2f}% {b['total_return']:>11.2f}%")
        print(f"  {'Max Drawdown':<20} {a['max_drawdown']:>11.1f}% {b['max_drawdown']:>11.1f}%")
        print(f"  {'Sharpe Ratio':<20} {a['sharpe_ratio']:>12.2f} {b['sharpe_ratio']:>12.2f}")
        print("=" * 50)
        
        winner = "A" if a['profit_factor'] > b['profit_factor'] else "B"
        print(f"\n  WINNER: Strategy {winner}")
    
    def save_report(self, filename="data/backtest_report.json"):
        """Save backtest results to file"""
        r = self.analyze()
        path = BASE_DIR / filename
        
        report = {
            'date': datetime.now().isoformat(),
            'results': r,
            'trades_analyzed': len(self.trades)
        }
        
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {path}")
        return path