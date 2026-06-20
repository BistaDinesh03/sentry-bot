from backtester import Backtester

print("=== BACKTESTER TEST ===\n")

bt = Backtester()

# Try loading from portfolio
print("1. Loading trades from portfolio...")
if bt.load_trades():
    bt.print_report()
    bt.save_report()
else:
    print("   No portfolio found, trying log file...")
    
    # Try from log
    if bt.load_trades_from_log():
        bt.print_report()
    else:
        print("   No trade data found yet.")
        print("   Run the bot for a few hours to collect data.")
        
        # Show sample analysis with demo data
        print("\n2. Demo analysis (what backtest looks like):")
        demo_trades = [
            {'action': 'SELL', 'token': 'BONK', 'profit': 0.15},
            {'action': 'SELL', 'token': 'FLOKI', 'profit': 0.01},
            {'action': 'SELL', 'token': 'PENGU', 'profit': 0.00},
            {'action': 'SELL', 'token': 'ASTER', 'profit': 1.10},
            {'action': 'SELL', 'token': 'SLX', 'profit': -0.25},
            {'action': 'SELL', 'token': 'PUMP', 'profit': 0.08},
            {'action': 'SELL', 'token': 'SIREN', 'profit': -4.76},
        ]
        bt.trades = demo_trades
        bt.print_report()

print("\n=== BACKTEST COMPLETE ===")