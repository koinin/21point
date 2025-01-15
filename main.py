from src.game.game_engine import GameEngine
from src.agents.basic_player_agent import BasicPlayerAgent
from src.agents.gpt_player_agent import GPTPlayerAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import matplotlib.pyplot as plt
import time
import numpy as np

class GameStats:
    def __init__(self, total_rounds: int):
        self.lock = Lock()
        self.total_rounds = total_rounds
        self.chips_history = {}  # Record chips history for each player
        
    def update_chips(self, player_name: str, chips: int, round_num: int):
        with self.lock:
            if player_name not in self.chips_history:
                self.chips_history[player_name] = [None] * self.total_rounds
            self.chips_history[player_name][round_num] = chips
            
    def plot_chips_history(self):
        plt.figure(figsize=(15, 10))
        
        # Plot chips history for each player
        for name, history in self.chips_history.items():
            valid_data = [h for h in history if h is not None]
            plt.plot(range(len(valid_data)), valid_data, label=name, marker='o')
        
        plt.title('Player Chips History')
        plt.xlabel('Round Number')
        plt.ylabel('Chips')
        plt.legend()
        plt.grid(True)
        plt.savefig('chips_history.png')
        plt.close()

def play_game_thread(thread_id: int, start_round: int, num_rounds: int, stats: GameStats):
    # Create game instance
    game = GameEngine()
    
    # Create 3 players with different styles
    players = [
        BasicPlayerAgent("Basic Strategy Player"),
        GPTPlayerAgent("Conservative AI Player", style="conservative"),
        GPTPlayerAgent("Aggressive AI Player", style="aggressive")
    ]
    
    # Add players to game
    for player in players:
        game.add_player(player)
    
    # Record initial chips
    for player in players:
        stats.update_chips(player.name, player.chips, start_round)
    stats.update_chips("Dealer", game.dealer.chips, start_round)
    
    # Play specified number of rounds
    for round_num in range(num_rounds):
        global_round = start_round + round_num
        
        # Start new round
        game.start_round()
        
        # Play round and get results
        results = game.play_round(verbose=False)
        
        # Record chips for each player
        for player in players:
            stats.update_chips(player.name, player.chips, global_round)
        stats.update_chips("Dealer", game.dealer.chips, global_round)
        
        time.sleep(0.05)  # Avoid too frequent API calls
    
    return {player.name: player.chips for player in players}, game.dealer.chips

def main():
    # Configuration parameters
    num_threads = 4  # Number of threads
    total_rounds = 40  # Total rounds
    rounds_per_thread = total_rounds // num_threads
    
    # Initialize statistics
    stats = GameStats(total_rounds)
    
    print(f"Starting {total_rounds} rounds of games using {num_threads} threads...")
    print("Each game includes 3 players (Basic Strategy, Conservative AI, Aggressive AI)")
    print("Initial chips: Players 1000, Dealer 5000")
    
    # Use thread pool to run games
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(
                play_game_thread, 
                i, 
                i * rounds_per_thread,  # Start round
                rounds_per_thread, 
                stats
            )
            for i in range(num_threads)
        ]
        
        # Collect results
        final_results = []
        for future in as_completed(futures):
            try:
                player_chips, dealer_chips = future.result()
                final_results.append((player_chips, dealer_chips))
            except Exception as e:
                print(f"Thread execution error: {e}")
    
    # Plot chips history
    stats.plot_chips_history()
    print("\nChips history chart has been saved as chips_history.png")
    
    # Print final statistics
    print("\n=== Final Chips Statistics ===")
    for player_chips, dealer_chips in final_results:
        for name, chips in player_chips.items():
            profit = chips - 1000
            print(f"{name}: {chips} chips ({'+' if profit >= 0 else ''}{profit})")
        dealer_profit = dealer_chips - 5000
        print(f"Dealer: {dealer_chips} chips ({'+' if dealer_profit >= 0 else ''}{dealer_profit})")

if __name__ == "__main__":
    main()
