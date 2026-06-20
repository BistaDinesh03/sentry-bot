"""
SENTRY BOT v6.0 - GENIUS EDITION
Mempool sniping + Time filter + Correlation breaker + Preflight + Failure learner
"""

import yaml, time, logging, threading, random, re, sys, json
from datetime import datetime, timedelta
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).parent.parent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / 'logs' / 'sentry.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Scanners
from reddit_scanner import RedditScanner
from chan_scanner import ChanScanner
from token_scanner import TokenScanner
from coingecko_scanner import CoinGeckoScanner
from news_scanner import NewsScanner
from telegram_scanner import TelegramScanner
from onchain_scanner import OnChainScanner
from rugcheck_scanner import RugCheckScanner

# Core
from token_scorer import TokenScorer
from exit_strategy import ExitStrategy
from position_sizer import PositionSizer
from momentum_filter import MomentumFilter
from performance_tracker import PerformanceTracker
from paper_trader import PaperTrader
from telegram_alerts import TelegramAlerts
from dashboard import start_dashboard
from equity_tracker import EquityTracker
from auto_compounder import AutoCompounder

# Boosters
from multi_tf import MultiTimeframe
from social_proof import SocialProof
from rsi_filter import RSIFilter
from news_sentiment import NewsSentiment
from volume_profile import VolumeProfile

# Billionaire
from tiered_exit import TieredExit
from edge_sizer import EdgeSizer
from streak_sizer import StreakSizer
from time_decay_sizer import TimeDecaySizer
from risk_governor import RiskGovernor

# AI
from ai_sentiment import AISentiment
from narrative_detector import NarrativeDetector
from adaptive_threshold import AdaptiveThreshold
from crash_protection import CrashProtection
from smart_entry import SmartEntry

# GENIUS MODULES
from mempool_sniper import MempoolSniper
from time_filter import TimeFilter
from correlation_breaker import CorrelationBreaker
from preflight_check import PreflightCheck
from failure_learner import FailureLearner


class SentryBot:
    """Sentry v6.0 - Genius Edition"""
    
    def __init__(self):
        with open(BASE_DIR / 'config' / 'settings.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Scanners
        self.reddit = RedditScanner(self.config['scanners']['reddit'].get('subreddits', []), 2.0)
        self.chan = ChanScanner()
        self.token_scanner = TokenScanner()
        self.coingecko = CoinGeckoScanner()
        self.news = NewsScanner()
        self.telegram_scanner = TelegramScanner()
        self.onchain_scanner = OnChainScanner()
        self.rugcheck = RugCheckScanner()
        
        # Core
        self.scorer = TokenScorer()
        self.exit_strategy = ExitStrategy()
        self.position_sizer = PositionSizer(account_balance=1000)
        self.momentum_filter = MomentumFilter()
        self.performance = PerformanceTracker()
        self.equity_tracker = EquityTracker()
        self.compounder = AutoCompounder(initial_balance=1000)
        
        # Boosters
        self.multi_tf = MultiTimeframe()
        self.social_proof = SocialProof()
        self.rsi_filter = RSIFilter()
        self.news_sentiment = NewsSentiment()
        self.volume_profile = VolumeProfile()
        
        # Billionaire
        self.tiered_exit = TieredExit()
        self.edge_sizer = EdgeSizer(account_balance=1000)
        self.streak_sizer = StreakSizer()
        self.time_decay = TimeDecaySizer()
        self.risk_governor = RiskGovernor(max_portfolio_heat=0.25)
        
        # AI
        self.ai_sentiment = AISentiment()
        self.narrative_detector = NarrativeDetector()
        self.adaptive_threshold = AdaptiveThreshold()
        self.crash_protection = CrashProtection()
        self.smart_entry = SmartEntry()
        
        # GENIUS
        self.mempool_sniper = MempoolSniper()
        self.time_filter = TimeFilter()
        self.correlation_breaker = CorrelationBreaker()
        self.preflight = PreflightCheck()
        self.failure_learner = FailureLearner()
        
        # Trader
        self.trader = PaperTrader(1000)
        self.trader.load_state(BASE_DIR / 'data' / 'portfolio.json')
        
        # Telegram
        tg_config = self.config.get('telegram_bot', {})
        self.telegram = TelegramAlerts(tg_config.get('token', ''), tg_config.get('chat_id', '')) if tg_config.get('enabled') else None
        if self.telegram: self.telegram.bot_instance = self
        
        self.blacklist = [t.strip().upper() for t in self.config['token_filter']['blacklist']]
        self.allowed = [t.strip().upper() for t in self.config['token_filter']['allowed_memecoins']]
        
        self.scans = 0
        self.running = False
        self.start_time = None
        self.buys_today = 0
        self.sells_today = 0
        self.profits_today = 0.0
        self.scams_blocked = 0
        self.crash_mode = False
        self.smart_rejects = 0
        self.correlation_rejects = 0
        self.preflight_rejects = 0
        self.time_skips = 0
    
    def log(self, msg, level='info'):
        if level == 'warning': logger.warning(msg)
        elif level == 'error': logger.error(msg)
        else: logger.info(msg)
    
    def get_total_exposure(self):
        total = 0
        for sym, pos in self.trader.positions.items():
            data = self.token_scanner.get_real_price(sym)
            total += pos['amount'] * (data['price'] if data else pos['buy_price'])
        return total
    
    def extract_symbols(self, all_findings):
        text = str(all_findings).lower()
        symbols = set()
        for token in self.allowed:
            if token.lower() in text: symbols.add(token)
        matches = re.findall(r'\$([A-Za-z]{2,10})', str(all_findings))
        for m in matches:
            upper = m.upper()
            if upper not in self.blacklist and len(upper) <= 10: symbols.add(upper)
        for finding in all_findings:
            if isinstance(finding, dict):
                if finding.get('source') in ['coingecko_trending', 'coingecko_new', 'coingecko_meme']:
                    sym = finding.get('symbol', '')
                    if sym and sym.upper() not in self.blacklist: symbols.add(sym.upper())
                if finding.get('source') == 'telegram':
                    for t in finding.get('tokens', []):
                        if not t.startswith('CA:') and t.upper() not in self.blacklist: symbols.add(t.upper())
        return list(symbols)[:15]
    
    def verify_tokens(self, symbols, all_findings):
        verified = []
        cfg = self.config['trading']
        
        for finding in all_findings:
            if isinstance(finding, dict):
                for sym in symbols:
                    if sym.lower() in str(finding).lower():
                        self.social_proof.track_mention(sym.upper(), finding.get('source', 'unknown'))
        
        for symbol in symbols[:10]:
            data = self.token_scanner.get_real_price(symbol)
            if not data: continue
            price, volume, liquidity = data['price'], data['volume_24h'], data['liquidity']
            if price <= 0 or price > cfg['max_token_price']: continue
            if volume < cfg['min_volume_24h']: continue
            if liquidity < cfg['min_liquidity']: continue
            if symbol.upper() in self.blacklist: continue
            
            self.rsi_filter.update(symbol.upper(), price)
            self.volume_profile.update(symbol.upper(), volume)
            self.smart_entry.record_price(symbol.upper(), price)
            
            scam_result = self.rugcheck.scan_token(symbol)
            if not scam_result['is_safe'] and scam_result['risk_score'] > 60:
                self.scams_blocked += 1; continue
            
            if self.rsi_filter.should_avoid(symbol.upper())[0]: continue
            
            vol_rising, vol_bonus = self.volume_profile.is_rising(symbol.upper())
            if not vol_rising: continue
            
            onchain_points = self.onchain_scanner.get_onchain_conviction_points(symbol)
            if onchain_points == -100: continue
            
            price_change_24h = data.get('price_change_24h', 0) or 0
            self.momentum_filter.update(symbol, price, volume)
            if not self.momentum_filter.check_all(symbol, price, volume, price_change_24h)[0]: continue
            
            momentum_score = self.momentum_filter.get_momentum_score(symbol, price, volume, price_change_24h)
            telegram_score = self.telegram_scanner.get_telegram_conviction_points(symbol)
            
            score_result = self.scorer.calculate_score({
                'telegram_score': telegram_score,
                'onchain_score': onchain_points if onchain_points > 0 else 0,
                'momentum_score': momentum_score,
                'volume': volume, 'liquidity': liquidity,
                'risk_score': scam_result['risk_score'],
                'price_change_24h': price_change_24h
            })
            base_score = score_result['total_score']
            
            bonus = 0
            tf_ok, tf_bonus = self.multi_tf.check(symbol)
            if tf_bonus > 0: bonus += tf_bonus
            bonus += self.social_proof.get_score(symbol.upper())
            bonus += vol_bonus
            bonus += self.narrative_detector.get_narrative_score(symbol)
            
            total_score = base_score + bonus
            
            if total_score >= 70: recommendation = "STRONG_BUY"
            elif total_score >= 50: recommendation = "BUY"
            else: recommendation = "SKIP"
            
            if recommendation in ['BUY', 'STRONG_BUY']:
                verified.append({
                    'symbol': symbol.upper(), 'price': price, 'volume': volume,
                    'liquidity': liquidity, 'score': total_score,
                    'recommendation': recommendation, 'data': data,
                    'vol_rising': vol_rising, 'telegram_score': telegram_score,
                    'social_proof': self.social_proof.get_score(symbol.upper())
                })
            time.sleep(0.4)
        return verified
    
    def manage_positions_professional(self, verified):
        cfg = self.config['trading']
        max_pos = cfg['max_positions']
        current_pos_count = len(self.trader.positions)
        
        sorted_positions = []
        for symbol in list(self.trader.positions.keys()):
            pos = self.trader.positions[symbol]
            price_data = self.token_scanner.get_real_price(symbol)
            if price_data and price_data['price'] > 0:
                pnl = ((price_data['price'] - pos['buy_price']) / pos['buy_price']) * 100
                sorted_positions.append((symbol, pos, price_data, pnl))
        sorted_positions.sort(key=lambda x: x[3])
        
        for symbol, pos, price_data, pnl_pct in sorted_positions:
            current_price = price_data['price']
            if current_price <= 0: continue
            
            self.exit_strategy.update_price(symbol, current_price, price_data.get('volume_24h', 0))
            if symbol not in self.exit_strategy.entry_prices:
                self.exit_strategy.record_entry(symbol, pos['buy_price'])
            
            should_tier, tier_fraction, tier_reason = self.tiered_exit.check(symbol, pnl_pct)
            if should_tier:
                sell_amount = pos['amount'] * tier_fraction
                result = self.trader.sell(symbol, sell_amount, current_price)
                if result:
                    self.performance.add_trade(result)
                    profit = result.get('profit', 0)
                    if profit > 0: self.profits_today += profit
                    self.sells_today += 1
                    self.log(f"  TIER SELL ${symbol}: {tier_reason} | P/L: ${profit:+.2f}")
                    self.streak_sizer.add_result(profit > 0)
                    self.crash_protection.add_trade(profit)
                    self.failure_learner.record_loss(symbol, int(pos.get('conviction', 0.5)*110), datetime.now().hour, 'tier', profit)
                continue
            
            should_sell, reasons = self.exit_strategy.should_sell(symbol, current_price, price_data.get('volume_24h', 0))
            if current_pos_count > max_pos and not should_sell:
                if pnl_pct < -3: should_sell = True; reasons = ["OVERFLOW"]
            
            if should_sell:
                sell_amount = pos['amount']
                if 'TakeProfit' in str(reasons): sell_amount = pos['amount'] * 0.5
                result = self.trader.sell(symbol, sell_amount, current_price)
                if result:
                    self.performance.add_trade(result)
                    profit = result.get('profit', 0)
                    if profit > 0: self.profits_today += profit
                    self.sells_today += 1; current_pos_count -= 1
                    self.log(f"  SELL ${symbol}: {' | '.join(reasons)} | P/L: ${profit:+.2f}")
                    self.streak_sizer.add_result(profit > 0)
                    self.crash_protection.add_trade(profit)
                    self.failure_learner.record_loss(symbol, int(pos.get('conviction', 0.5)*110), datetime.now().hour, 'standard', profit)
                    if self.telegram: self.telegram.alert_sell(symbol, sell_amount, current_price, result.get('revenue', 0), profit, ' | '.join(reasons))
                    time.sleep(0.3)
    
    def find_buys_professional(self, verified):
        if self.crash_mode:
            self.log("  CRASH MODE: No buys"); return
        
        # TIME FILTER
        if not self.time_filter.should_trade():
            self.time_skips += 1
            self.log(f"  TIME SKIP: Outside active hours"); return
        
        cfg = self.config['trading']
        max_pos = cfg['max_positions']
        current_pos = len(self.trader.positions)
        if current_pos >= max_pos: return
        
        verified.sort(key=lambda x: x.get('score', 0), reverse=True)
        current_exposure = self.get_total_exposure()
        account_balance = self.trader.balance + current_exposure
        
        for token in verified[:max_pos - current_pos]:
            symbol = token['symbol']
            if symbol in self.trader.positions: continue
            
            score = token.get('score', 0)
            buy_th, _ = self.adaptive_threshold.get_thresholds()
            effective_threshold = max(48, buy_th - 5)
            
            # CORRELATION BREAKER
            is_correlated, corr_reason = self.correlation_breaker.check_correlation(symbol, list(self.trader.positions.keys()))
            if is_correlated:
                self.correlation_rejects += 1
                self.log(f"  CORR SKIP ${symbol}: {corr_reason}"); continue
            
            # FAILURE LEARNER
            should_block, block_reason = self.failure_learner.should_block(symbol, score, datetime.now().hour, 'social')
            if should_block:
                self.log(f"  FAIL SKIP ${symbol}: {block_reason}"); continue
            
            # SMART ENTRY
            multi_source = (token.get('telegram_score', 0) > 0 or token.get('social_proof', 0) > 5)
            can_buy, entry_reason = self.smart_entry.should_buy(symbol, token['price'], score, token.get('vol_rising', True), multi_source)
            if not can_buy:
                self.smart_rejects += 1
                self.log(f"  ENTRY SKIP ${symbol}: {entry_reason}"); continue
            
            # PREFLIGHT CHECK
            position_size_usd = 10  # Estimate
            can_exit, exit_reason = self.preflight.can_exit(symbol, position_size_usd, token['liquidity'])
            if not can_exit:
                self.preflight_rejects += 1
                self.log(f"  PREFLIGHT SKIP ${symbol}: {exit_reason}"); continue
            
            # SIZE
            base_size, signal_count = self.edge_sizer.get_position_size({
                'telegram_score': token.get('telegram_score', 0),
                'onchain_score': token.get('onchain_score', 0) if 'onchain_score' in token else 0,
                'momentum_score': token.get('momentum_score', 0) if 'momentum_score' in token else 5,
                'volume': token.get('volume', 0),
                'liquidity': token.get('liquidity', 0),
                'social_proof': token.get('social_proof', 0),
            })
            
            position_size_usd = base_size * self.streak_sizer.get_multiplier() * self.time_decay.get_multiplier(symbol) * self.ai_sentiment.get_regime_multiplier() * self.time_filter.get_position_multiplier()
            
            can_trade, _ = self.risk_governor.can_trade(current_exposure, account_balance, position_size_usd)
            if not can_trade or position_size_usd < 3: continue
            
            if token.get('recommendation') in ['BUY', 'STRONG_BUY'] and score >= effective_threshold:
                cost = position_size_usd; amount = cost / token['price']
                if cost <= self.trader.balance * 0.15:
                    self.trader.buy(symbol, amount, token['price'], score / 160)
                    self.buys_today += 1; self.exit_strategy.record_entry(symbol, token['price'])
                    self.log(f"  BUY ${symbol} | ${cost:.2f} | Score:{score} | {entry_reason}")
                    if self.telegram: self.telegram.alert_buy(symbol, amount, token['price'], cost, score/160, entry_reason)
    
    def run_cycle(self):
        self.scans += 1
        crashed, _ = self.crash_protection.check()
        if crashed: self.crash_mode = True
        
        active = "ACTIVE" if self.time_filter.is_active_hour() else "SLOW"
        self.log(f"\n{'='*50} SCAN #{self.scans} | {datetime.now().strftime('%H:%M:%S')} | {active} {'='*50}")
        
        stats = self.trader.get_stats(); total_value = stats['balance']
        for sym, pos in self.trader.positions.items():
            data = self.token_scanner.get_real_price(sym)
            total_value += pos['amount'] * (data['price'] if data else pos['buy_price'])
        
        total_pl = total_value - self.trader.initial_balance
        self.equity_tracker.add_point(total_value)
        exposure = self.get_total_exposure()
        heat = (exposure / total_value * 100) if total_value > 0 else 0
        
        self.log(f"Value: ${total_value:.2f} | P/L: ${total_pl:+.2f} | Pos: {stats['open_positions']}/{self.config['trading']['max_positions']} | Heat: {heat:.0f}%")
        self.log(f"Genius: Corr={self.correlation_rejects} Preflight={self.preflight_rejects} Fail={len(self.failure_learner.blocked_conditions)} Time={self.time_skips}")
        
        all_findings = []
        try: all_findings.extend(self.telegram_scanner.scan_all())
        except: pass
        try: all_findings.extend(self.reddit.scan_all())
        except: pass
        try: all_findings.extend(self.chan.scan_all())
        except: pass
        try: gd, gs = self.coingecko.scan_all(); all_findings.extend(gd)
        except: pass
        try: all_findings.extend(self.news.scan_all())
        except: pass
        try: all_findings.extend(self.onchain_scanner.scan_all())
        except: pass
        
        symbols = self.extract_symbols(all_findings)
        verified = self.verify_tokens(symbols, all_findings)
        self.manage_positions_professional(verified)
        self.find_buys_professional(verified)
        self.trader.save_state(BASE_DIR / 'data' / 'portfolio.json')
        self.equity_tracker.save()
    
    def start(self):
        self.log("=" * 50)
        self.log("  SENTRY v6.0 - GENIUS EDITION")
        self.log("  Mempool + Time + Correlation + Preflight + Learner")
        self.log(f"  Dashboard: http://localhost:8080")
        self.log("=" * 50)
        threading.Thread(target=start_dashboard, args=(self, 8080), daemon=True).start()
        self.running = True; self.start_time = datetime.now()
        while self.running:
            try:
                self.run_cycle()
                time.sleep(60)
            except KeyboardInterrupt: self.running = False
            except Exception as e: self.log(f"Error: {e}", 'error'); time.sleep(30)
        self.shutdown()
    
    def shutdown(self):
        self.trader.save_state(BASE_DIR / 'data' / 'portfolio.json')
        self.equity_tracker.save()
        self.log(f"\nSHUTDOWN | Genius rejects: Corr={self.correlation_rejects} Pre={self.preflight_rejects} Time={self.time_skips}")


if __name__ == "__main__":
    bot = SentryBot()
    bot.start()