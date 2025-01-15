from .player import Player
from .hand import Hand

class Dealer(Player):
    def __init__(self):
        super().__init__("Dealer", initial_chips=5000)
    
    def should_hit(self) -> bool:
        """Dealer must hit on 16 and below, stand on 17 and above"""
        return self.hand.get_value() < 17
