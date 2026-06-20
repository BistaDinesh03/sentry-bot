from live_trader import LiveTrader

print("=== LIVE TRADER TEST ===\n")

# Test 1: Paper mode (safe)
print("1. PAPER MODE (default, safe):")
lt = LiveTrader(mode="paper")
result = lt.execute_paper_trade("BUY", "BONK", 25.0, 0.0000045)
print(f"   {result['mode']}: {result['amount_usd']:.2f} = {result['token_amount']:.0f} tokens")
print(f"   TX: {result['tx_id']}")

# Test 2: Get real Jupiter quote
print("\n2. REAL JUPITER QUOTE (test mode):")
lt2 = LiveTrader(mode="simulate")
try:
    quote = lt2.get_real_quote_buy("BONK", 10.0)
    if quote['success']:
        print(f"   ${quote['amount_usd']} BONK -> {quote['out_amount_raw']} raw tokens")
        print(f"   Price Impact: {quote['price_impact']}%")
    else:
        print(f"   Quote failed: {quote.get('error', 'Unknown')}")
except Exception as e:
    print(f"   Jupiter API blocked on this network: {e}")

# Test 3: Health check
print("\n3. HEALTH CHECK:")
health = lt.check_health()
for k, v in health.items():
    print(f"   {k}: {v}")

# Test 4: Token price
print("\n4. TOKEN PRICE LOOKUP:")
price = lt.get_token_price_usd("BONK")
print(f"   BONK price via Jupiter: ${price}")

print("\n=== LIVE TRADER TEST COMPLETE ===")
print(f"\nStats: {lt.get_stats()}")