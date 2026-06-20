"""
TELEGRAM SCANNER v3.0 - Real Alpha Source
Scrapes public Telegram channels for memecoin calls
Tracks first mentions, coordinated shilling, signal strength
"""

import requests
import logging
import re
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent


class TelegramScanner:
    """Scans Telegram public channels for memecoin alpha"""
    
    def __init__(self, channels_config=None):
        if channels_config is None:
            channels_config = BASE_DIR / 'config' / 'telegram_channels.yaml'
        
        self.channels = []
        self.scoring_config = {}
        self.strong_signals = []
        self.weak_signals = []
        
        # Token tracking
        self.token_mentions = {}  # token -> {first_seen, channels, count}
        self.channel_activity = {}  # channel -> last_scan_time
        
        # Load config
        try:
            with open(channels_config, 'r') as f:
                config = yaml.safe_load(f)
                self.channels = config.get('channels', [])
                self.scoring_config = config.get('scoring', {})
                self.strong_signals = config.get('strong_signals', [])
                self.weak_signals = config.get('weak_signals', [])
                logger.info(f"Loaded {len(self.channels)} Telegram channels")
        except Exception as e:
            logger.error(f"Config load error: {e}")
            self.channels = [
                {'name': 'SolanaAlpha', 'type': 'alpha', 'priority': 10},
                {'name': 'memecoin_calls', 'type': 'calls', 'priority': 9},
                {'name': 'crypto_gems_calls', 'type': 'calls', 'priority': 8},
                {'name': 'solana_gems_alpha', 'type': 'alpha', 'priority': 9},
                {'name': 'crypto_alpha_calls', 'type': 'alpha', 'priority': 8},
                {'name': 'cryptopumpsignals', 'type': 'pump', 'priority': 7},
            ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scan_channel(self, channel_name, limit=20):
        """Scan a public Telegram channel via web preview"""
        url = f"https://t.me/s/{channel_name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                messages = soup.select('.tgme_widget_message_wrap')
                
                findings = []
                for msg in messages[:limit]:
                    # Get message text
                    text_elem = msg.select_one('.tgme_widget_message_text')
                    if not text_elem:
                        continue
                    
                    text = text_elem.get_text(strip=True)
                    
                    # Get timestamp
                    time_elem = msg.select_one('.tgme_widget_message_date time')
                    msg_time = time_elem.get('datetime') if time_elem else None
                    
                    # Extract token symbols
                    tokens_found = self.extract_tokens(text)
                    
                    # Score the message
                    signal_score = self.score_message(text, channel_name)
                    
                    if tokens_found or signal_score > 3:
                        findings.append({
                            'channel': channel_name,
                            'text': text[:500],
                            'tokens': tokens_found,
                            'signal_score': signal_score,
                            'time': msg_time,
                            'source': 'telegram'
                        })
                
                self.channel_activity[channel_name] = time.time()
                return findings
            else:
                logger.debug(f"Channel {channel_name}: HTTP {response.status_code}")
                return []
                
        except requests.Timeout:
            logger.debug(f"Timeout: {channel_name}")
            return []
        except Exception as e:
            logger.debug(f"Scan error {channel_name}: {e}")
            return []
    
    def extract_tokens(self, text):
        """Extract token symbols and contract addresses from message"""
        tokens = []
        
        # $TOKEN pattern
        dollar_matches = re.findall(r'\$([A-Za-z]{2,15})', text)
        tokens.extend(dollar_matches)
        
        # Solana contract addresses (base58, 44 chars)
        sol_matches = re.findall(r'([1-9A-HJ-NP-Za-km-z]{40,45})', text)
        for addr in sol_matches:
            if len(addr) >= 40:
                tokens.append(f"CA:{addr[:8]}...")
        
        # "Token: TOKEN" or "Ticker: TOKEN" patterns
        ticker_matches = re.findall(r'(?:Token|Ticker|Symbol)[:\s]+([A-Za-z]{2,10})', text)
        tokens.extend(ticker_matches)
        
        return list(set(tokens))[:10]
    
    def score_message(self, text, channel_name):
        """Score a message for signal strength (0-10)"""
        score = 0
        text_lower = text.lower()
        
        # Strong signals
        for signal in self.strong_signals:
            if signal.lower() in text_lower:
                score += 3
        
        # Weak signals (negative)
        for signal in self.weak_signals:
            if signal.lower() in text_lower:
                score -= 2
        
        # Has contract address = more serious
        if re.search(r'[1-9A-HJ-NP-Za-km-z]{44}', text):
            score += 4
        
        # Has dollar amounts (serious traders)
        if re.search(r'\$[\d,]+', text):
            score += 2
        
        # Has percentage predictions (less reliable)
        if re.search(r'\d{3,4}%|\d+x', text):
            score -= 1
        
        # Too short (not informative)
        if len(text) < 50:
            score -= 1
        
        return max(0, min(10, score))
    
    def track_mentions(self, token, channel_name, msg_time=None):
        """Track when tokens are first mentioned and by which channels"""
        now = datetime.now()
        
        if token not in self.token_mentions:
            self.token_mentions[token] = {
                'first_seen': now,
                'channels': set(),
                'count': 0,
                'first_channel': channel_name
            }
        
        self.token_mentions[token]['channels'].add(channel_name)
        self.token_mentions[token]['count'] += 1
    
    def detect_coordinated_shilling(self, token, time_window_minutes=5):
        """Detect if multiple channels mention same token within time window"""
        if token not in self.token_mentions:
            return False, 0
        
        channels = self.token_mentions[token]['channels']
        
        if len(channels) >= 3:
            return True, len(channels)
        
        return False, len(channels)
    
    def get_token_alpha_score(self, token):
        """Calculate alpha score for a token based on Telegram signals"""
        if token not in self.token_mentions:
            return 0
        
        data = self.token_mentions[token]
        score = 0
        
        # Channel diversity (different channels = stronger signal)
        unique_channels = len(data['channels'])
        score += min(20, unique_channels * 5)
        
        # First mention recency (caught early = more alpha)
        minutes_ago = (datetime.now() - data['first_seen']).total_seconds() / 60
        if minutes_ago < 30:
            score += self.scoring_config.get('first_mention_bonus', 10)
        elif minutes_ago < 60:
            score += 5
        
        # Coordinated shilling detection
        is_coordinated, coord_count = self.detect_coordinated_shilling(token)
        if is_coordinated:
            score += self.scoring_config.get('coordinated_shill_bonus', 15)
        
        # Mention count
        score += min(10, data['count'] * 2)
        
        return min(100, score)
    
    def scan_all(self):
        """Scan all configured channels"""
        logger.info("Scanning Telegram channels...")
        all_findings = []
        all_tokens = set()
        
        # Sort channels by priority
        sorted_channels = sorted(self.channels, key=lambda c: c.get('priority', 5), reverse=True)
        
        channels_scanned = 0
        channels_with_data = 0
        
        for channel_config in sorted_channels[:15]:  # Limit to 15 channels per scan
            channel_name = channel_config.get('name', '')
            
            # Rate limiting check
            last_scan = self.channel_activity.get(channel_name, 0)
            if time.time() - last_scan < 30:
                continue  # Skip recently scanned
            
            findings = self.scan_channel(channel_name, limit=15)
            channels_scanned += 1
            
            if findings:
                channels_with_data += 1
                
                for finding in findings:
                    # Track all tokens found
                    for token in finding['tokens']:
                        self.track_mentions(token, channel_name, finding.get('time'))
                        all_tokens.add(token)
                    
                    # Add channel type to finding
                    finding['channel_type'] = channel_config.get('type', 'unknown')
                    finding['channel_priority'] = channel_config.get('priority', 5)
                    all_findings.append(finding)
            
            time.sleep(1)  # Rate limit between channels
        
        logger.info(f"  Scanned {channels_scanned} channels, {channels_with_data} active")
        logger.info(f"  Found {len(all_findings)} messages with {len(all_tokens)} unique tokens")
        
        # Show top tokens by alpha score
        if all_tokens:
            token_scores = {}
            for token in all_tokens:
                token_scores[token] = self.get_token_alpha_score(token)
            
            top_tokens = sorted(token_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_tokens:
                logger.info(f"  Top Telegram tokens:")
                for token, score in top_tokens:
                    data = self.token_mentions.get(token, {})
                    channels = len(data.get('channels', set()))
                    logger.info(f"    ${token}: Alpha={score}/100 ({channels} channels)")
        
        return all_findings
    
    def get_telegram_conviction_points(self, token):
        """Get conviction points from Telegram data (0-25 scale)"""
        alpha_score = self.get_token_alpha_score(token)
        
        # Scale to 0-25 points for the scoring model
        points = alpha_score / 4  # 100/4 = 25
        
        return round(points, 1)