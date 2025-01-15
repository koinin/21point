from typing import List, Dict
from ..models.deck import Deck
from ..models.player import Player
from ..models.dealer import Dealer
from ..models.card import Card
from ..agents.dealer_agent import DealerAgent

class GameEngine:
    def __init__(self, use_ai_dealer: bool = True):
        self.deck = Deck()
        self.players: List[Player] = []
        self.dealer = DealerAgent() if use_ai_dealer else Dealer()
        
    def add_player(self, player: Player):
        """Add a player to the game"""
        self.players.append(player)
        
    def start_round(self):
        """Start a new round of the game"""
        # Clear all hands
        for player in self.players:
            player.hand.cards.clear()
        self.dealer.hand.cards.clear()
        
        # Shuffle deck if needed
        if len(self.deck.cards) < (len(self.players) + 1) * 4:
            self.deck = Deck()
        self.deck.shuffle()
        
        # Deal initial cards
        for _ in range(2):
            for player in self.players:
                player.hand.add_card(self.deck.draw_card())
            self.dealer.hand.add_card(self.deck.draw_card())
    
    def player_hit(self, player: Player) -> bool:
        """
        Give the player another card
        Returns True if player busts, False otherwise
        """
        player.hand.add_card(self.deck.draw_card())
        return player.hand.is_bust()

    def _handle_bets(self, verbose: bool = False) -> Dict[str, int]:
        """Handle betting phase for all players"""
        bets = {}
        for player in self.players:
            bet = player.decide_bet()
            if player.place_bet(bet):
                bets[player.name] = bet
                if verbose:
                    print(f"{player.name} bets {bet} chips")
            else:
                if verbose:
                    print(f"{player.name} cannot bet {bet} chips (not enough chips)")
        return bets

    def _settle_bets(self, results: Dict[str, str], bets: Dict[str, int], verbose: bool = False):
        """Settle all bets based on game results"""
        for player in self.players:
            result = results[player.name]
            bet = bets[player.name]
            
            if result == 'WIN':
                multiplier = 1.5 if player.hand.is_blackjack() else 1.0
                win_amount = int(bet * multiplier)
                player.win_bet(multiplier)
                self.dealer.chips -= win_amount
                if verbose:
                    print(f"{player.name} wins {win_amount} chips")
            elif result == 'LOSE' or result == 'BUST':
                player.lose_bet()
                self.dealer.chips += bet
                if verbose:
                    print(f"{player.name} loses {bet} chips")
            else:  # PUSH
                player.push_bet()
                if verbose:
                    print(f"{player.name} gets their bet back")

    def play_round(self, verbose: bool = False) -> Dict[str, str]:
        """
        Play a complete round with all players
        Returns: Dictionary mapping player names to their results
        """
        results = {}
        
        # Betting phase
        bets = self._handle_bets(verbose)
        if verbose:
            print("\nBetting phase complete")
        
        # Players' turns
        for player in self.players:
            if verbose:
                print(f"\n{player.name}'s turn:")
                print(f"Initial hand: {', '.join(str(card) for card in player.hand.cards)}")
            
            # Player's turn
            while True:
                action = player.decide_action(self.dealer.hand.cards[0])
                if verbose:
                    print(f"{player.name} decides to: {'Hit' if action == 'H' else 'Stand'}")
                
                if action == 'S':
                    break
                if action == 'H':
                    bust = self.player_hit(player)
                    if verbose:
                        print(f"New hand: {', '.join(str(card) for card in player.hand.cards)}")
                    if bust:
                        if verbose:
                            print("Bust!")
                        break
        
        # Dealer's turn
        if verbose:
            print("\nDealer's turn:")
        while self.dealer.should_hit():
            self.dealer.hand.add_card(self.deck.draw_card())
            if verbose:
                print(f"Dealer's hand: {', '.join(str(card) for card in self.dealer.hand.cards)}")
        
        # Get results and settle bets
        for player in self.players:
            results[player.name] = self._get_game_result(player)
            if verbose:
                print(f"\n{player.name}'s result: {results[player.name]}")
        
        self._settle_bets(results, bets, verbose)
        if verbose:
            for player in self.players:
                print(f"{player.name}'s remaining chips: {player.chips}")
            print(f"Dealer's remaining chips: {self.dealer.chips}")
        
        return results
            
    def _get_game_result(self, player: Player) -> str:
        """Determine the game result for a player"""
        # 检查爆牌
        if player.hand.is_bust():
            return "BUST"
        if self.dealer.hand.is_bust():
            return "WIN"
            
        # 检查Blackjack
        player_blackjack = player.hand.is_blackjack()
        dealer_blackjack = self.dealer.hand.is_blackjack()
        
        if player_blackjack and not dealer_blackjack:
            return "WIN"
        if dealer_blackjack and not player_blackjack:
            return "LOSE"
        if player_blackjack and dealer_blackjack:
            return "PUSH"
            
        # 比较普通点数
        player_value = player.hand.get_value()
        dealer_value = self.dealer.hand.get_value()
        
        if player_value > dealer_value:
            return "WIN"
        elif player_value < dealer_value:
            return "LOSE"
        else:
            return "PUSH"
