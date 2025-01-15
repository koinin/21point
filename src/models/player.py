from .hand import Hand

class Player:
    def __init__(self, name: str, initial_chips: int = 1000):
        self.name = name
        self.hand = Hand()
        self.chips = initial_chips
        self.current_bet = 0
        
    def __str__(self) -> str:
        return self.name
        
    def place_bet(self, amount: int) -> bool:
        """
        Place a bet
        Returns: True if bet is valid, False if not enough chips
        """
        if amount <= self.chips:
            self.current_bet = amount
            self.chips -= amount
            return True
        return False
        
    def win_bet(self, multiplier: float = 1.0):
        """Win bet with given multiplier (1.0 for normal win, 1.5 for blackjack)"""
        winnings = int(self.current_bet * (1 + multiplier))
        self.chips += winnings
        self.current_bet = 0
        
    def lose_bet(self):
        """Lose current bet"""
        self.current_bet = 0
        
    def push_bet(self):
        """Return bet on push"""
        self.chips += self.current_bet
        self.current_bet = 0
