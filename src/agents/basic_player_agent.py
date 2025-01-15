from .player_agent import PlayerAgent
from ..models.card import Card

class BasicPlayerAgent(PlayerAgent):
    def __init__(self, name: str = "Basic Player"):
        super().__init__(name)
        
    def decide_bet(self) -> int:
        """
        使用固定的下注策略：
        - 如果筹码小于500，下注10%
        - 如果筹码在500-2000之间，下注15%
        - 如果筹码大于2000，下注20%
        """
        if self.chips < 500:
            bet_ratio = 0.1
        elif self.chips < 2000:
            bet_ratio = 0.15
        else:
            bet_ratio = 0.2
            
        bet = max(10, min(int(self.chips * bet_ratio), self.chips))
        return bet
        
    def decide_action(self, dealer_up_card: Card) -> str:
        """
        使用固定的基本策略：
        1. 如果有A（软手）：
           - 17及以下要牌
           - 18看庄家牌（9及以上要牌）
           - 19及以上停牌
        2. 无A（硬手）：
           - 11及以下要牌
           - 12-16看庄家牌（2-6停牌，7及以上要牌）
           - 17及以上停牌
        """
        player_value = self.hand.get_value()
        dealer_value = dealer_up_card.get_value()
        
        # 检查是否有A
        has_ace = any(card.rank.value == 1 for card in self.hand.cards)
        if has_ace and player_value <= 21:  # 软手
            if player_value <= 17:
                return 'H'
            elif player_value == 18:
                return 'H' if dealer_value >= 9 else 'S'
            else:
                return 'S'
        else:  # 硬手
            if player_value <= 11:
                return 'H'
            elif 12 <= player_value <= 16:
                return 'S' if 2 <= dealer_value <= 6 else 'H'
            else:
                return 'S'
