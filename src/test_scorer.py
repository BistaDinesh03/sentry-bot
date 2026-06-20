from token_scorer import TokenScorer

scorer = TokenScorer()

print("=== TOKEN SCORING MODEL TEST ===\n")

# Test 1: Strong token (like BONK with all signals)
print("TEST 1: Strong token (BONK-like)")
result = scorer.calculate_score({
    'telegram_score': 19,
    'onchain_score': 10,
    'momentum_score': 5,
    'volume': 12000000,
    'liquidity': 5600000,
    'risk_score': 0,
    'price_change_24h': 3.0
})
print(f"  Score: {result['total_score']}/110")
print(f"  Recommendation: {result['recommendation']}")
print(f"  Breakdown: {result['breakdown']}")
print(f"  Explanation: {scorer.explain_score(result)}\n")

# Test 2: Weak token
print("TEST 2: Weak token")
result = scorer.calculate_score({
    'telegram_score': 0,
    'onchain_score': 0,
    'momentum_score': 3,
    'volume': 30000,
    'liquidity': 8000,
    'risk_score': 60,
    'price_change_24h': -25
})
print(f"  Score: {result['total_score']}/110")
print(f"  Recommendation: {result['recommendation']}")
print(f"  Explanation: {scorer.explain_score(result)}\n")

# Test 3: Medium token
print("TEST 3: Medium token (some signals)")
result = scorer.calculate_score({
    'telegram_score': 5,
    'onchain_score': 7,
    'momentum_score': 8,
    'volume': 250000,
    'liquidity': 120000,
    'risk_score': 15,
    'price_change_24h': 12
})
print(f"  Score: {result['total_score']}/110")
print(f"  Recommendation: {result['recommendation']}")
print(f"  Explanation: {scorer.explain_score(result)}\n")

# Test 4: Pumped token
print("TEST 4: Already pumped token")
result = scorer.calculate_score({
    'telegram_score': 15,
    'onchain_score': 5,
    'momentum_score': 12,
    'volume': 5000000,
    'liquidity': 800000,
    'risk_score': 10,
    'price_change_24h': 350  # Pumped 350%!
})
print(f"  Score: {result['total_score']}/110")
print(f"  Recommendation: {result['recommendation']}")
print(f"  Explanation: {scorer.explain_score(result)}\n")

print("=== SCORER TEST COMPLETE ===")
print(f"\nScorer Stats: {scorer.get_stats()}")