"""
Crypto News Scanner - CryptoPanic RSS + CoinTelegraph
FREE - No API key needed
"""

import requests
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class NewsScanner:
    """Scans crypto news sites for memecoin mentions"""
    
    def __init__(self):
        self.sources = [
            {
                'name': 'CryptoPanic',
                'url': 'https://cryptopanic.com/news/rss/',
                'type': 'rss'
            },
            {
                'name': 'CoinTelegraph',
                'url': 'https://cointelegraph.com/rss/tag/memecoin',
                'type': 'rss'
            }
        ]
        self.keywords = [
            'memecoin', 'meme coin', 'new token', 'solana meme',
            'pump', '100x', 'launch', 'gem', 'airdrop',
            'bonk', 'wif', 'pepe', 'popcat', 'wen', 'mew'
        ]
    
    def scan_rss(self, source):
        """Scan RSS feed"""
        try:
            response = requests.get(source['url'], timeout=15, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                findings = []
                for item in root.findall('.//item'):
                    title = item.find('title')
                    description = item.find('description')
                    link = item.find('link')
                    
                    title_text = title.text if title is not None else ''
                    desc_text = description.text if description is not None else ''
                    
                    full_text = (title_text + ' ' + desc_text).lower()
                    
                    matched = [k for k in self.keywords if k.lower() in full_text]
                    
                    if matched:
                        findings.append({
                            'title': title_text[:200],
                            'text': desc_text[:500] if desc_text else '',
                            'keywords': matched,
                            'source': f"news_{source['name'].lower()}",
                            'url': link.text if link is not None else ''
                        })
                
                return findings
            return []
        except Exception as e:
            logger.debug(f"News {source['name']} error: {e}")
            return []
    
    def scan_all(self):
        """Scan all news sources"""
        logger.info("Scanning crypto news...")
        all_findings = []
        
        for source in self.sources:
            findings = self.scan_rss(source)
            if findings:
                logger.info(f"  {source['name']}: {len(findings)} articles")
                all_findings.extend(findings)
        
        if all_findings:
            # Extract symbols from headlines
            import re
            text = ' '.join([f['title'] for f in all_findings])
            symbols = re.findall(r'\$?([A-Z]{2,10})', text)
            symbols = [s for s in symbols if s.isalpha() and len(s) >= 3]
            
            if symbols:
                logger.info(f"  Symbols in news: {list(set(symbols))[:10]}")
        
        logger.info(f"  Total news findings: {len(all_findings)}")
        return all_findings