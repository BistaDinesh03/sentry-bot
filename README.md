# Sentry

> An open-source AI-assisted memecoin trading bot for Solana.

Sentry watches the market, filters risky tokens, scores opportunities, and manages trades using a mix of market, on-chain, social, and risk signals.

## How It Works

```
Scanner → Filters → Score → Risk → Entry → Monitor → Exit
```

### Token Scoring

Every candidate token is scored based on signals such as:

- Liquidity & volume
- Momentum & RSI
- On-chain activity
- Social activity
- Token safety
- Market conditions

**Higher score = stronger setup.**

## Features

- Multi-source token discovery
- Rug & safety checks
- Market momentum analysis
- On-chain signals
- Social sentiment analysis
- AI-assisted market analysis
- Position sizing
- Tiered exits
- Crash protection
- Paper trading
- Local trading dashboard

## Current Status

🟡 **Paper / simulation trading**

Real Solana execution is under active development. The goal is to validate the full strategy safely before enabling live transactions.

## Quick Start

```bash
git clone https://github.com/BistaDinesh03/sentry-bot.git
cd sentry-bot

pip install -r requirements.txt
python src/main.py
```

Then open the local dashboard:

```
http://localhost:8080
```

## Project

Built to explore autonomous trading systems, market intelligence, and risk management on Solana.

**Not financial advice. Use at your own risk.**
