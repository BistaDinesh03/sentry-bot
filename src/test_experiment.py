from experiment_runner import ExperimentRunner
from backtester import Backtester

print("=== EXPERIMENT RUNNER TEST ===\n")

# Create runner
runner = ExperimentRunner()

# Sample backtest results (replace with real data)
sample_results = {
    'win_rate': 40.0,
    'profit_factor': 1.5,
    'max_drawdown': 5.0,
    'sharpe_ratio': 1.2,
    'total_trades': 20
}

# Compare strategies
print("1. Comparing strategies...")
rankings = runner.compare_strategies(sample_results)
runner.print_comparison()

# Auto-optimize
print("\n2. Auto-optimizing...")
best_config, best_score = runner.auto_optimize(sample_results, num_iterations=30)

# Save results
runner.save_results()

print("\n=== EXPERIMENT TEST COMPLETE ===")