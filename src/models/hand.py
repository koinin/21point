from typing import List
from .card import Card

class Hand:
    def __init__(self):
        self.cards: List[Card] = []
    
    def add_card(self, card: Card):
        """Add a card to the hand"""
        self.cards.append(card)
    
    def get_value(self) -> int:
        """Calculate the value of the hand"""
        value = 0
        num_aces = 0
        
        # First count non-aces
        for card in self.cards:
            if card.rank.value == 1:  # Ace
                num_aces += 1
            else:
                value += card.get_value()
        
        # Then add aces
        for _ in range(num_aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1
                
        return value
    
    def is_blackjack(self) -> bool:
        """Check if the hand is a blackjack"""
        return len(self.cards) == 2 and self.get_value() == 21
    
    def is_bust(self) -> bool:
        """Check if the hand is bust"""
        return self.get_value() > 21
