"""Volume Profile - Lenient mode: allows stable volume, penalizes declining"""
import logging
logger = logging.getLogger(__name__)

class VolumeProfile:
    def __init__(self):
        self.volume_history = {}
    def update(self, token, volume):
        if token not in self.volume_history:
            self.volume_history[token] = []
        self.volume_history[token].append(volume)
        if len(self.volume_history[token]) > 10:
            self.volume_history[token] = self.volume_history[token][-10:]
    def is_rising(self, token):
        vols = self.volume_history.get(token, [])
        if len(vols) < 3:
            return True, 3  # Not enough data, allow with small bonus
        recent = vols[-3:]
        if recent[2] > recent[0] * 0.8:  # Allow slight decline (20% tolerance)
            return True, 5
        else:
            return False, 0  # Only reject if volume dropped >20%