"""Social Proof - Multi-source confirmation"""
import logging
logger = logging.getLogger(__name__)

class SocialProof:
    def __init__(self):
        self.sources = {}
    
    def track_mention(self, token, source):
        if token not in self.sources:
            self.sources[token] = set()
        self.sources[token].add(source)
    
    def get_score(self, token):
        """More unique sources = higher conviction"""
        sources = self.sources.get(token, set())
        count = len(sources)
        
        if count >= 4: return 15  # Viral
        elif count >= 3: return 10  # Trending
        elif count >= 2: return 5   # Growing
        else: return 0              # Unproven
    
    def get_sources(self, token):
        return list(self.sources.get(token, set()))