import requests
import json

print("Testing REAL price APIs...\n")

# Test 1: DexScreener (we know this works)
print("1. DexScreener API:")
try:
    r = requests.get("https://api.dexscreener.com/latest/dex/search?q=BONK", timeout=10)
    if r.status_code == 200:
        data = r.json()
        pairs = data.get('pairs', [])
        if pairs:
            price = pairs[0].get('priceUsd', 'N/A')
            print(f"   BONK Price: ${price}")
            print(f"   Status: WORKING")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Jupiter (may be blocked)
print("\n2. Jupiter API:")
try:
    r = requests.get("https://quote-api.jup.ag/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=10000000&slippageBps=500", timeout=10)
    if r.status_code == 200:
        print(f"   Jupiter API: WORKING")
        data = r.json()
        print(f"   Out amount: {data.get('outAmount', 'N/A')}")
    else:
        print(f"   Status code: {r.status_code}")
except Exception as e:
    print(f"   Jupiter blocked on this network")
    print(f"   Will use DexScreener for prices instead")

print("\nDone! DexScreener is sufficient for paper trading.")