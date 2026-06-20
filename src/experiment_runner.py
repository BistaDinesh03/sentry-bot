"""
EXPERIMENT RUNNER v3.0
A/B testing, strategy comparison, auto-optimization
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent


class ExperimentRunner:
    """Run and compare multiple trading strategies"""
    
    def __init__(self):
        self.strategies = {}
        self.results = {}
        self.best_strategy = None
        
        # Default strategies
        self.strategies['current'] = {
            'buy_threshold': 50,
            'strong_buy_threshold': 70,
            'max_positions': 6,
            'take_profit_pct': 15,
            'stop_loss_pct': 12,
            'max_position_size': 100,
            'min_conviction': 50,
        }
        
        self.strategies['aggressive'] = {
            'buy_threshold': 40,
            'strong_buy_threshold': 60,
            'max_positions': 8,
            'take_profit_pct': 10,
            'stop_loss_pct': 15,
            'max_position_size': 150,
            'min_conviction': 40,
        }
        
        self.strategies['conservative'] = {
            'buy_threshold': 65,
            'strong_buy_threshold': 80,
            'max_positions': 4,
            'take_profit_pct': 20,
            'stop_loss_pct': 8,
            'max_position_size': 50,
            'min_conviction': 65,
        }
        
        self.strategies['momentum_focused'] = {
            'buy_threshold': 55,
            'strong_buy_threshold': 75,
            'max_positions': 5,
            'take_profit_pct': 12,
            'stop_loss_pct': 10,
            'max_position_size': 80,
            'min_conviction': 55,
        }
    
    def add_strategy(self, name, config):
        """Add a custom strategy"""
        self.strategies[name] = config
        logger.info(f"Added strategy: {name}")
    
    def compare_strategies(self, backtest_results):
        """Compare multiple strategies based on backtest results"""
        rankings = []
        
        for name, config in self.strategies.items():
            score = self._score_strategy(config, backtest_results)
            rankings.append((name, score, config))
        
        # Sort by score (highest first)
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        self.results = rankings
        self.best_strategy = rankings[0] if rankings else None
        
        return rankings
    
    def _score_strategy(self, config, results):
        """Score a strategy based on backtest metrics"""
        score = 0
        
        # Win rate (0-30 points)
        win_rate = results.get('win_rate', 0)
        score += min(30, win_rate * 0.6)
        
        # Profit factor (0-30 points)
        profit_factor = results.get('profit_factor', 0)
        score += min(30, profit_factor * 10)
        
        # Max drawdown penalty (0-20 points)
        max_dd = results.get('max_drawdown', 0)
        score += max(0, 20 - max_dd)
        
        # Sharpe ratio (0-10 points)
        sharpe = results.get('sharpe_ratio', 0)
        score += max(0, min(10, sharpe * 5 + 5))
        
        # Consistency (0-10 points)
        total_trades = results.get('total_trades', 0)
        if total_trades >= 20:
            score += 10
        elif total_trades >= 10:
            score += 5
        
        return score
    
    def print_comparison(self):
        """Print strategy comparison"""
        if not self.results:
            print("No results to compare. Run compare_strategies first.")
            return
        
        print("\n" + "=" * 60)
        print("  STRATEGY COMPARISON")
        print("=" * 60)
        print(f"  {'Rank':<5} {'Strategy':<20} {'Score':<8} {'Threshold':<10} {'Positions':<10}")
        print(f"  {'-'*5} {'-'*20} {'-'*8} {'-'*10} {'-'*10}")
        
        for i, (name, score, config) in enumerate(self.results, 1):
            medal = "GOLD" if i == 1 else "SILVER" if i == 2 else "BRONZE" if i == 3 else "  "
            print(f"  {medal:<5} {name:<20} {score:<8.1f} {config['buy_threshold']:<10} {config['max_positions']:<10}")
        
        print("=" * 60)
        
        if self.best_strategy:
            print(f"\n  BEST STRATEGY: {self.best_strategy[0]}")
            print(f"  Score: {self.best_strategy[1]:.1f}")
            print(f"  Config: {json.dumps(self.best_strategy[2], indent=2)}")
    
    def auto_optimize(self, backtest_results, num_iterations=50):
        """Automatically find optimal parameters"""
        best_config = self.strategies['current'].copy()
        best_score = self._score_strategy(best_config, backtest_results)
        
        import random
        
        print(f"\nAuto-optimizing (testing {num_iterations} variations)...")
        
        for i in range(num_iterations):
            # Create variation of best config
            test_config = best_config.copy()
            
            # Randomly adjust one parameter
            param = random.choice(list(test_config.keys()))
            adjustment = random.uniform(0.7, 1.3)
            
            if param in ['buy_threshold', 'strong_buy_threshold', 'min_conviction']:
                test_config[param] = max(20, min(90, int(test_config[param] * adjustment)))
            elif param in ['max_positions']:
                test_config[param] = max(2, min(10, int(test_config[param] * adjustment)))
            elif param in ['take_profit_pct', 'stop_loss_pct']:
                test_config[param] = max(5, min(30, int(test_config[param] * adjustment)))
            elif param in ['max_position_size']:
                test_config[param] = max(20, min(200, int(test_config[param] * adjustment)))
            
            score = self._score_strategy(test_config, backtest_results)
            
            if score > best_score:
                best_score = score
                best_config = test_config.copy()
                if i % 10 == 0:
                    print(f"  Iteration {i}: New best score {best_score:.1f}")
        
        print(f"\n  Optimization complete!")
        print(f"  Best score: {best_score:.1f}")
        print(f"  Best config: {json.dumps(best_config, indent=2)}")
        
        return best_config, best_score
    
    def apply_best_strategy(self, bot_instance):
        """Apply the best strategy to the running bot"""
        if not self.best_strategy:
            print("No best strategy found")
            return False
        
        name, score, config = self.best_strategy
        
        bot_instance.scorer.buy_threshold = config['buy_threshold']
        bot_instance.scorer.strong_buy_threshold = config['strong_buy_threshold']
        bot_instance.config['trading']['max_positions'] = config['max_positions']
        bot_instance.config['trading']['take_profit_pct'] = config['take_profit_pct']
        bot_instance.config['trading']['stop_loss_pct'] = -config['stop_loss_pct']
        bot_instance.config['trading']['max_position_size'] = config['max_position_size']
        bot_instance.config['trading']['min_conviction'] = config['min_conviction'] / 100
        
        logger.info(f"Applied strategy: {name} (score: {score:.1f})")
        return True
    
    def save_results(self, filename="data/experiment_results.json"):
        """Save experiment results"""
        path = BASE_DIR / filename
        
        data = {
            'date': datetime.now().isoformat(),
            'best_strategy': {
                'name': self.best_strategy[0] if self.best_strategy else None,
                'score': self.best_strategy[1] if self.best_strategy else 0,
                'config': self.best_strategy[2] if self.best_strategy else {},
            },
            'rankings': [
                {'name': name, 'score': score, 'config': config}
                for name, score, config in self.results
            ]
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Results saved to {path}")
        return path
    
    def get_weekly_report(self):
        """Generate weekly performance report"""
        report = {
            'date': datetime.now().isoformat(),
            'best_strategy': self.best_strategy[0] if self.best_strategy else 'unknown',
            'total_strategies_tested': len(self.strategies),
            'optimization_rounds': 0,
            'recommendation': ''
        }
        
        if self.best_strategy:
            name, score, config = self.best_strategy
            report['recommendation'] = f"Use '{name}' strategy with threshold {config['buy_threshold']}"
        
        return report