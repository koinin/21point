from typing import Optional
from ..models.player import Player
from ..models.card import Card

class PlayerAgent(Player):
    def __init__(self, name: str = "AI Player"):
        super().__init__(name)
        
    def decide_action(self, dealer_up_card: Card) -> str:
        """
        Decide whether to hit or stand based on basic strategy
        Returns: 'H' for hit, 'S' for stand
        """
        player_value = self.hand.get_value()
        dealer_value = dealer_up_card.get_value()
        
        # If we have an Ace (soft hand)
        has_ace = any(card.rank.value == 1 for card in self.hand.cards)
        if has_ace and player_value <= 21:
            return self._decide_soft_hand(player_value, dealer_value)
        
        # Hard hand strategy
        return self._decide_hard_hand(player_value, dealer_value)
    
    def _decide_soft_hand(self, player_value: int, dealer_value: int) -> str:
        """Strategy for hands with an Ace counted as 11"""
        # Always hit soft 17 or below
        if player_value <= 17:
            return 'H'
        
        # Stand on soft 20 or 21
        if player_value >= 20:
            return 'S'
            
        # Soft 18-19
        if player_value == 18:
            # Hit against dealer 9,10,11
            if dealer_value >= 9:
                return 'H'
            return 'S'
            
        # Stand on soft 19
        return 'S'
    
    def _decide_hard_hand(self, player_value: int, dealer_value: int) -> str:
        """Strategy for hands without an Ace counted as 11"""
        # Always hit 11 or below
        if player_value <= 11:
            return 'H'
            
        # Always stand on 17 or above
        if player_value >= 17:
            return 'S'
            
        # 12-16: Stand against dealer 2-6, hit against 7 or higher
        if 12 <= player_value <= 16:
            if 2 <= dealer_value <= 6:
                return 'S'
            return 'H'
            
        return 'S'  # Default to stand
