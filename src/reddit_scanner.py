"""Reddit scanner v2.0 - RSS with rate limiting"""

import requests
import logging
import time
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class RedditScanner:
    """Scans Reddit via RSS feeds with caching"""
    
    def __init__(self, subreddits=None, delay=3.0):
        self.subreddits = subreddits or ["CryptoMoonShots", "SolanaMemeCoins", "memecoin"]
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.cache = {}
        self.cache_time = {}
    
    def scan_subreddit(self, subreddit, limit=25):
        """Get posts via RSS feed"""
        # Check cache
        now = time.time()
        if subreddit in self.cache and (now - self.cache_time.get(subreddit, 0)) < 300:
            logger.info(f"  Using cached data for r/{subreddit}")
            return self.cache[subreddit]
        
        url = f"https://www.reddit.com/r/{subreddit}/new/.rss?limit={limit}"
        
        try:
            time.sleep(self.delay)
            response = requests.get(url, headers=self.headers, timeout=20)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                findings = []
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns)
                    content = entry.find('atom:content', ns)
                    link = entry.find('atom:link', ns)
                    
                    findings.append({
                        'title': title.text if title is not None else '',
                        'text': content.text[:500] if content is not None and content.text else '',
                        'subreddit': subreddit,
                        'url': link.get('href') if link is not None else '',
                        'source': 'reddit'
                    })
                
                # Cache results
                self.cache[subreddit] = findings
                self.cache_time[subreddit] = now
                
                return findings
            else:
                logger.warning(f"Reddit RSS returned {response.status_code}")
                return []
                
        except ET.ParseError:
            logger.warning(f"XML parse error for r/{subreddit}")
            return []
        except Exception as e:
            logger.error(f"Error scanning r/{subreddit}: {e}")
            return []
    
    def scan_all(self):
        """Scan all subreddits"""
        all_findings = []
        
        for subreddit in self.subreddits:
            logger.info(f"Scanning r/{subreddit}...")
            posts = self.scan_subreddit(subreddit)
            
            if posts:
                logger.info(f"  Found {len(posts)} posts in r/{subreddit}")
                for post in posts[:2]:
                    logger.info(f"    - {post['title'][:80]}")
                all_findings.extend(posts)
            else:
                logger.info(f"  No posts in r/{subreddit}")
        
        return all_findings