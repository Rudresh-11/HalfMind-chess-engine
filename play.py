import chess
import chess.svg
from my_engine import get_best_move # Import your engine

def play_game():
    board = chess.Board()
    # Simple setting: Depth 3 is fast but decent. Depth 4 is smarter but slower in Python.
    AI_DEPTH = 3 

    while not board.is_game_over():
        print("\n" + str(board))
        print("\n----------------")
        
        if board.turn == chess.WHITE:
            # --- HUMAN TURN (White) ---
            while True:
                # try:
                #     move_str = input("Your move (e.g., e2e4): ")
                #     move = chess.Move.from_uci(move_str)
                #     if move in board.legal_moves:
                #         board.push(move)
                #         break
                #     else:
                #         print("Illegal move. Try again.")
                # except ValueError:
                #     print("Invalid format. Use UCI (e.g., e2e4, g1f3).")
                print("AI is thinking...")
                best_move = get_best_move(board, AI_DEPTH)
                print(f"AI plays: {best_move}")
                board.push(best_move)
        else:
            # --- AI TURN (Black) ---
            print("AI is thinking...")
            best_move = get_best_move(board, AI_DEPTH)
            print(f"AI plays: {best_move}")
            board.push(best_move)

    print("Game Over!")
    print(board.result())

if __name__ == "__main__":
    play_game()