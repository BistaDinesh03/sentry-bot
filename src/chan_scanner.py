"""4chan scanner v2.0"""

import requests
import logging

logger = logging.getLogger(__name__)


class ChanScanner:
    """Scans 4chan /biz/ for crypto threads"""
    
    def __init__(self, board="biz"):
        self.board = board
        self.base_url = f"https://a.4cdn.org/{board}"
        self.keywords = [
            'memecoin', 'meme coin', 'new coin', 'gem', '100x',
            'moonshot', 'presale', 'fair launch', 'stealth launch',
            'pump', 'solana', 'token', 'defi', 'airdrop'
        ]
    
    def scan_all(self):
        """Full scan"""
        logger.info(f"Scanning 4chan /{self.board}/...")
        
        try:
            response = requests.get(f"{self.base_url}/catalog.json", timeout=10)
            
            if response.status_code == 200:
                catalog = response.json()
                findings = []
                
                for page in catalog:
                    for thread in page.get('threads', []):
                        sub = thread.get('sub', '')
                        com = thread.get('com', '')
                        text = (sub + ' ' + com).lower()
                        
                        matched = [k for k in self.keywords if k.lower() in text]
                        
                        if matched:
                            findings.append({
                                'title': sub[:200] if sub else 'No title',
                                'text': com[:500] if com else '',
                                'replies': thread.get('replies', 0),
                                'keywords': matched,
                                'source': '4chan'
                            })
                
                logger.info(f"  Found {len(findings)} crypto threads")
                for f in findings[:3]:
                    logger.info(f"    [{f['replies']} replies] {f['title'][:70]}")
                
                return findings
            else:
                logger.warning(f"4chan returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"4chan error: {e}")
            return []