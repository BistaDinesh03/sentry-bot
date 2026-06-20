from exit_strategy import ExitStrategy

es = ExitStrategy()
print("=== TESTING NEW EXIT STRATEGY ===")
es.record_entry("TEST", 1.00)
print("Bought TEST @ $1.00")
es.update_price("TEST", 1.20, 50000)
print("Price: $1.20")
es.update_price("TEST", 1.50, 60000)
print("Price: $1.50 (highest)")
es.update_price("TEST", 1.27, 40000)
should_sell, reasons, sell_pct = es.get_exit_decision("TEST", 1.27, 40000)
print(f"Price drops to $1.27")
print(f"Should sell: {should_sell}")
if should_sell:
    print(f"Reasons: {reasons}")
    print(f"Sell: {sell_pct*100}%")

es2 = ExitStrategy()
es2.record_entry("TEST2", 1.00)
for i in range(20):
    es2.update_price("TEST2", 1.00 + (i * 0.001), 50000)
es2.update_price("TEST2", 0.80, 30000)
should_sell, reasons, sell_pct = es2.get_exit_decision("TEST2", 0.80, 30000)
print(f"\nTEST2 drops to $0.80")
print(f"Should sell: {should_sell}")
if should_sell:
    print(f"Reasons: {reasons}")
print("\n=== TEST COMPLETE ===")