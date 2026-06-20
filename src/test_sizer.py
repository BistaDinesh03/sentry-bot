from position_sizer import PositionSizer

ps = PositionSizer(account_balance=1000)

print("=== KELLY CRITERION POSITION SIZER TEST ===\n")

# Test 1: High conviction, good liquidity
print("TEST 1: High conviction trade")
size = ps.calculate_position_size(
    conviction_score=80,
    volatility_pct=8,
    liquidity_usd=200000
)
print(f"Position size: ${size:.2f}\n")

# Test 2: Low conviction, low liquidity
print("TEST 2: Low conviction, low liquidity")
size = ps.calculate_position_size(
    conviction_score=30,
    volatility_pct=15,
    liquidity_usd=8000
)
print(f"Position size: ${size:.2f}\n")

# Test 3: High volatility
print("TEST 3: High volatility warning")
size = ps.calculate_position_size(
    conviction_score=70,
    volatility_pct=35,
    liquidity_usd=100000
)
print(f"Position size: ${size:.2f}\n")

# Test 4: Should trade check
print("TEST 4: Should we trade?")
should, reasons = ps.should_trade(45, 50000, 10)
print(f"Conviction 45, Liq $50K, Vol 10%")
print(f"Should trade: {should}")
if not should:
    print(f"Reasons: {reasons}")

print("\n=== SIZER TEST COMPLETE ===")
ps.print_stats()