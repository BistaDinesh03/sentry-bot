from telegram_scanner import TelegramScanner

print("=== TELEGRAM SCANNER TEST ===\n")

ts = TelegramScanner()

# Test 1: Scan single channel
print("1. Scanning SolanaAlpha channel...")
findings = ts.scan_channel("SolanaAlpha", limit=5)
if findings:
    print(f"   Found {len(findings)} messages")
    for f in findings[:3]:
        print(f"   Tokens: {f['tokens'][:5] if f['tokens'] else 'none'}")
        print(f"   Score: {f['signal_score']}/10")
else:
    print("   Channel not accessible (may be private)")

# Test 2: Scan all channels
print("\n2. Scanning all configured channels...")
all_findings = ts.scan_all()

# Test 3: Token tracking
print("\n3. Testing token tracking...")
ts.track_mentions("BONK", "SolanaAlpha")
ts.track_mentions("BONK", "memecoin_calls")
ts.track_mentions("BONK", "solana_gems_alpha")
score = ts.get_token_alpha_score("BONK")
print(f"   BONK alpha score: {score}/100")
print(f"   Channels: {len(ts.token_mentions.get('BONK', {}).get('channels', set()))}")

print("\n=== TELEGRAM TEST COMPLETE ===")