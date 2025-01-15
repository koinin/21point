import random
from typing import List
from .card import Card, Suit, Rank

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self._initialize_deck()
    
    def _initialize_deck(self):
        """Initialize a standard deck of 52 cards"""
        self.cards = [Card(suit, rank) 
                     for suit in Suit 
                     for rank in Rank]
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def draw_card(self) -> Card:
        """Draw a card from the deck"""
        if not self.cards:
            raise ValueError("Deck is empty")
        return self.cards.pop()
