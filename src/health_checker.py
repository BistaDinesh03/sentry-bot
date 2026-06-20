"""Health checker for Sentry Bot"""

import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthChecker:
    """Check all systems are operational"""
    
    @staticmethod
    def check_dexscreener():
        """Check DexScreener API"""
        try:
            r = requests.get("https://api.dexscreener.com/latest/dex/search?q=SOL", timeout=5)
            return r.status_code == 200
        except:
            return False
    
    @staticmethod
    def check_reddit():
        """Check Reddit RSS"""
        try:
            r = requests.get("https://www.reddit.com/r/CryptoMoonShots/new/.rss", timeout=5)
            return r.status_code in [200, 429]
        except:
            return False
    
    @staticmethod
    def check_4chan():
        """Check 4chan API"""
        try:
            r = requests.get("https://a.4cdn.org/biz/catalog.json", timeout=5)
            return r.status_code == 200
        except:
            return False
    
    @staticmethod
    def run_all():
        """Run all health checks"""
        results = {
            "DexScreener": HealthChecker.check_dexscreener(),
            "Reddit": HealthChecker.check_reddit(),
            "4chan": HealthChecker.check_4chan(),
            "Time": datetime.now().isoformat()
        }
        
        logger.info("=== HEALTH CHECK ===")
        for service, status in results.items():
            if service != "Time":
                logger.info(f"[{'OK' if status else 'FAIL'}] {service}")
        
        return results