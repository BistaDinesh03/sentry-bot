"""
Health Monitor - Checks if bot is alive, restarts if dead
"""

import requests
import logging
import time
import subprocess
import sys
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitors bot health and auto-recovers"""
    
    def __init__(self, dashboard_url="http://localhost:8080", check_interval=60):
        self.dashboard_url = dashboard_url
        self.check_interval = check_interval
        self.failures = 0
        self.max_failures = 3
    
    def check_dashboard(self):
        """Check if dashboard is responding"""
        try:
            r = requests.get(self.dashboard_url, timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def check_process(self):
        """Check if python is running"""
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'],
                              capture_output=True, text=True)
        return 'python.exe' in result.stdout
    
    def restart_bot(self):
        """Restart the bot"""
        logger.warning(f"Restarting bot (failure #{self.failures})...")
        subprocess.Popen([sys.executable, 'src/main.py'],
                       cwd=r'C:\Users\dines\sentry')
    
    def run(self):
        """Main monitoring loop"""
        logger.info("Health monitor started")
        
        while True:
            try:
                dashboard_ok = self.check_dashboard()
                process_ok = self.check_process()
                
                if not dashboard_ok and not process_ok:
                    self.failures += 1
                    logger.warning(f"Bot appears dead! Failure {self.failures}/{self.max_failures}")
                    
                    if self.failures >= self.max_failures:
                        self.restart_bot()
                        self.failures = 0
                else:
                    self.failures = 0
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = HealthMonitor()
    monitor.run()