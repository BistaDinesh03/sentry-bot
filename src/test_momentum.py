from momentum_filter import MomentumFilter

mf = MomentumFilter()
print("=== MOMENTUM FILTER TEST ===\n")

# Simulate price/volume data
token = "TEST"
for i in range(30):
    mf.update(token, 1.00 + (i * 0.01), 50000)

# Test 1: Price above VWAP, high volume
print("TEST 1: Good momentum")
passed, reasons = mf.check_all(token, 1.50, 150000, +30)
print(f"Price: $1.50, Vol: 150K, 24h: +30%")
print(f"Passed: {passed}")
if not passed:
    print(f"Failed: {reasons}")
print(f"Momentum Score: {mf.get_momentum_score(token, 1.50, 150000, +30)}/15\n")

# Test 2: Below VWAP
print("TEST 2: Below VWAP")
passed, reasons = mf.check_all(token, 1.10, 80000, -5)
print(f"Price: $1.10, Vol: 80K, 24h: -5%")
print(f"Passed: {passed}")
if not passed:
    print(f"Failed: {reasons}")
print(f"Momentum Score: {mf.get_momentum_score(token, 1.10, 80000, -5)}/15\n")

# Test 3: Already pumped
print("TEST 3: Already pumped +300%")
passed, reasons = mf.check_all(token, 3.00, 200000, +300)
print(f"Price: $3.00, Vol: 200K, 24h: +300%")
print(f"Passed: {passed}")
if not passed:
    print(f"Failed: {reasons}")

print("\n=== MOMENTUM TEST COMPLETE ===")