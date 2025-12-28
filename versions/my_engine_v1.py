import chess
import math
import random
# --- PART 1: EVALUATION (The Judge) ---
# We assign points to pieces. High positive score = White is winning.
# High negative score = Black is winning.

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-Square Tables (PSTs)
# These arrays tell the engine WHERE pieces prefer to be.
# For example, Knights (N) love the center, so the center values are higher.
# These are simplified tables for a 64-square board (0-63).

pawntable = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0]

knightstable = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]

def evaluate_board(board:chess.Board):
    if board.is_checkmate():
        if board.turn:
            return -9999  # Black wins (White is checkmated)
        else:
            return 9999   # White wins

    if board.is_stalemate():
        return 0

    evaluation = 0
    
    # Iterate through all 64 squares
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        
        # Get basic piece value
        value = piece_values[piece.piece_type]
        
        # Add positional score (PST)
        # We assume White is "down" the board (index 0-63) and Black is mirrored

        if piece.piece_type == chess.PAWN:
            position_score = pawntable[square] if piece.color == chess.WHITE else pawntable[chess.square_mirror(square)]
        elif piece.piece_type == chess.KNIGHT:
            position_score = knightstable[square] if piece.color == chess.WHITE else knightstable[chess.square_mirror(square)]
        else:
            position_score = 0 # Simplified: add other tables later

        # position_score=0
            
        total_score = value + position_score

        if piece.color == chess.WHITE:
            evaluation += total_score
        else:
            evaluation -= total_score

    return evaluation

# --- PART 2: THE BRAIN (Minimax Search) ---

def minimax(board:chess.Board, depth, alpha, beta, maximizing_player):
    # Base case: If we reached depth 0 or game is over, evaluate the board
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player: # White's turn (wants positive score)
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move) # Make move
            eval = minimax(board, depth - 1, alpha, beta, False) # Recursive call
            board.pop() # Undo move (backtrack)
            max_eval = max(max_eval, eval)
            
            # Alpha-Beta Pruning (Optimization)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break # Prune
        return max_eval
    else: # Black's turn (wants negative score)
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def get_best_move_v1(board:chess.Board, depth):
    best_move = None
    max_eval = -math.inf
    min_eval = math.inf
    
    # We need to run the loop at the top level to find WHICH move produces the best score
    is_white = board.turn
    
    # print(f"Thinking (Depth {depth})...")
    best=[move for move in board.legal_moves if move in board.legal_moves]
    random.shuffle(best)
    # best_move= random.choice(best)
    for move in best:
        board.push(move)
        # Call minimax for the resulting position
        eval_score = minimax(board, depth-1 , -math.inf, math.inf, not is_white)
        board.pop()
        
        if is_white:
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        else:
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
                
    return best_move