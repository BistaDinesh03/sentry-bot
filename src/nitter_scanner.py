"""Twitter scanner using Nitter (no API key needed)"""

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NitterScanner:
    """Scans Twitter via Nitter instances"""
    
    def __init__(self):
        # Free Nitter instances (no API key needed)
        self.instances = [
            "https://nitter.net",
            "https://nitter.1d4.us",
            "https://nitter.kavin.rocks"
        ]
        self.keywords = [
            "new memecoin", "just launched", "fair launch", "stealth launch",
            "gem", "100x", "moonshot", "presale", "new token", "airdrop"
        ]
    
    def search(self, keyword, limit=10):
        """Search Twitter for keyword"""
        instance = self.instances[0]
        url = f"{instance}/search?f=tweets&q={keyword}&since=&until=&near="
        
        try:
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                tweets = []
                
                for item in soup.select('.timeline-item')[:limit]:
                    content = item.select_one('.tweet-content')
                    date = item.select_one('.tweet-date a')
                    username = item.select_one('.username')
                    
                    if content:
                        tweets.append({
                            'username': username.text.strip() if username else 'unknown',
                            'content': content.text.strip()[:300],
                            'date': date.get('title', '') if date else '',
                            'keyword': keyword
                        })
                
                return tweets
            else:
                logger.warning(f"Nitter returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Nitter error: {e}")
            return []
    
    def scan_all(self):
        """Scan all keywords"""
        logger.info("Scanning Twitter via Nitter...")
        all_tweets = []
        
        for keyword in self.keywords[:5]:  # Limit to 5 keywords to avoid rate limits
            tweets = self.search(keyword, limit=5)
            all_tweets.extend(tweets)
            if tweets:
                logger.info(f"  Keyword '{keyword}': {len(tweets)} tweets")
        
        logger.info(f"  Total tweets found: {len(all_tweets)}")
        
        # Show sample tweets
        for tweet in all_tweets[:3]:
            logger.info(f"    @{tweet['username']}: {tweet['content'][:80]}...")
        
        return all_tweets