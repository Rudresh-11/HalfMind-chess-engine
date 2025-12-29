import chess
import math
import random
import time

CHECK_BONUS = 50000          # Logic #4: Checks are top priority
PROMOTION_BONUS = 30000      # Logic #5: Promotions are massive
CAPTURE_BONUS = 20000        # Base bonus to separate captures from quiet moves
KILLER_1_BONUS = 9000        # Logic #7: Killers above quiet moves
KILLER_2_BONUS = 8000
BAD_CAPTURE_PENALTY = 25000  # Logic #6: Enough to sink bad captures below zer
TT = {}  #Tranpostions
killers={}

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING:0
}

pawntable = [
    50,   50,   50,   50,   50,   50,   50,   50,
    30,  30,  40,  45,  45,  40,  30,  30,
    25,  25,  35,  40,  40,  35,  25,  25,
    20,  20,  30,  35,  35,  30,  20,  20,
    15,  15,  25,  30,  30,  25,  15,  15,
    10,  10,  15,  20,  20,  15,  10,  10,
    5,   5,   5,   5,   5,   5,   5,   5,
    0,   0,   0,   0,   0,   0,   0,   0,
]

knightstable = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]

bishoptable = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-15,-15,-15,-15,-15,-15,-20]

kingtable = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  -5, 10, 30, 20]
# Rooks prefer the 7th rank (to attack pawns) and central files
rooktable = [
    0,  0,  0,  0,  0,  0,  0,  0,
    10, 20, 20, 20, 20, 20, 20,  10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  -5,  0,  10,  10,  0,  -5,  -10]

# Queens are like Bishops + Rooks (Central dominance)
queentable = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20]



def sort_moves(board: chess.Board, depth=0, killers=None,hash_move=None):
    """
    Sorts moves based on the strict engineering checklist:
    Checks > Promotions > Winning Captures > Equal Captures > Killers > Quiet Improving > Quiet Junk > Losing Captures
    """
    moves = list(board.legal_moves)
    if len(moves) <= 3:
        return moves
    # Get killer moves for this depth if they exist
    killer_moves = []
    if killers and depth in killers:
        killer_moves = killers[depth]

    def move_scorer(move):
        score = 0
        
        # Cache boolean states for speed & logic flow
        is_capture = board.is_capture(move)
        is_promotion = bool(move.promotion)
        is_check = board.gives_check(move) 

        # --- TIER 1: FORCING MOVES (Checks, Promotions, Captures) ---
        
        if is_check:
            score += CHECK_BONUS

        if is_promotion:
            # Logic #5: Promotion > Everything. 
            # (Note: A promo that also checks gets both bonuses, ensuring it is #1)
            score += PROMOTION_BONUS + PIECE_VALUES.get(move.promotion,0)

        if is_capture:
            score += CAPTURE_BONUS
            
            # Logic #3: REAL MVV-LVA
            # Formula: Victim * 10 - Attacker
            
            # 1. Identify Attacker
            attacker = board.piece_at(move.from_square)
            attacker_val = PIECE_VALUES.get(attacker.piece_type,0) if attacker else 0
            
            # 2. Identify Victim
            victim_val = 0
            if board.is_en_passant(move):
                victim_val = PIECE_VALUES[chess.PAWN]
            else:
                victim = board.piece_at(move.to_square)
                if victim:
                    victim_val = PIECE_VALUES.get(victim.piece_type,0)
            
            score += (victim_val * 10) - attacker_val
            
            # Logic #6: SEE-lite (Bad Capture Penalty)
            # "If attacker > victim -> penalize"
            if attacker_val > victim_val:
                score -= BAD_CAPTURE_PENALTY 
                # Result: 20000 + (Low MVV) - 25000 = Negative Score. 
                # This pushes bad captures to the bottom (Logic #9)

        # --- TIER 2: QUIET MOVES (Killers & PST) ---
        # Logic #8: "PST only AFTER all forcing logic"
        # We only apply Killers/PST if the move is NOT forcing (no check, no capture, no promotion)
        if not is_check and not is_promotion and not is_capture:
            
            # Logic #7: Killer Moves
            if killer_moves and move in killer_moves:
                if move == killer_moves[0]:
                    score += KILLER_1_BONUS
                elif len(killer_moves) > 1 and move == killer_moves[1]:
                    score += KILLER_2_BONUS
            
            else:
                # Logic #8: PST Tie-Breaker
                # Only for quiet, non-killer moves
                piece = board.piece_at(move.from_square)
                if piece:
                    # Select Table
                    ptype = piece.piece_type
                    table = None
                    if ptype == chess.PAWN: table = pawntable
                    elif ptype == chess.KNIGHT: table = knightstable
                    elif ptype == chess.BISHOP: table = bishoptable
                    elif ptype == chess.ROOK: table = rooktable
                    elif ptype == chess.QUEEN: table = queentable
                    elif ptype == chess.KING: table = kingtable
                    
                    if table:
                        # Calculate: Value at Destination - Value at Start
                        if board.turn == chess.WHITE:
                            val_from = table[chess.square_mirror(move.from_square)]
                            val_to = table[chess.square_mirror(move.to_square)]
                        else:
                            val_from = table[move.from_square]
                            val_to = table[move.to_square]
                        
                        score += (val_to - val_from)

        return score

    # Logic #10: "Use sorted_moves in minimax"
    # We return the list directly to be iterated over

    moves= sorted(board.legal_moves, key=move_scorer, reverse=True)
    if hash_move and hash_move in moves:
        moves.remove(hash_move)
        moves.insert(0, hash_move)
    return moves



def evaluate_board(board: chess.Board):
    if board.is_checkmate():
        return -9999 if board.turn else 9999
    
    if board.is_game_over(): 
        return 0

    evaluation = 0
    for square, piece in board.piece_map().items():
        
        # 1. Material Value
        value = PIECE_VALUES.get(piece.piece_type, 0)
        # 2. Positional Score (PST)
        position_score = 0
        
        # Determine which table to use
        if piece.piece_type == chess.PAWN: table = pawntable
        elif piece.piece_type == chess.KNIGHT: table = knightstable
        elif piece.piece_type == chess.BISHOP:table = bishoptable
        elif piece.piece_type == chess.ROOK:table = rooktable
        elif piece.piece_type == chess.QUEEN: table = queentable
        elif piece.piece_type == chess.KING: table = kingtable
        else: table = [0] * 64 # Default to 0 if table missing
        # Handle mirroring for Black
        if piece.color == chess.WHITE:
            position_score = table[chess.square_mirror(square)]
        else:
            position_score = table[square]

        total_piece_score = value + position_score

        if piece.color == chess.WHITE:
            evaluation += total_piece_score
        else:
            evaluation -= total_piece_score
        # print(f"Eval: {evaluation} , position score:{position_score} Sqaure: {square} pice: {piece} turn:{board.turn}")

    return evaluation


def quiescence(board: chess.Board, alpha, beta, maximizing_player, killers, depth=0):
    
    key = board._transposition_key()
    hash_move=None
    if key in TT:
        _, tt_move, tt_depth, _ = TT[key]
        if tt_depth > 0:
            hash_move = tt_move
            
    stand_pat = evaluate_board(board)
    if depth > 10: return stand_pat

    if maximizing_player:
        if stand_pat >= beta: return beta
        if stand_pat > alpha: alpha = stand_pat
    else:
        if stand_pat <= alpha: return alpha
        if stand_pat < beta: beta = stand_pat


    # In quiescence search, we evaluate forcing moves (captures, promotions) 
    # to ensure the static evaluation is on a "quiet" position.
    all_legal_moves = sort_moves(board, depth, killers,hash_move)
    legal_moves=[m for m in all_legal_moves if board.is_capture(m) or m.promotion or board.gives_check(m)]
    # legal_moves=[m for m in all_legal_moves if board.is_capture(m)]
    for move in legal_moves:
        board.push(move)
        score = quiescence(board, alpha, beta, not maximizing_player, killers, depth + 1)
        board.pop()

        if maximizing_player:
            if score >= beta: return beta
            if score > alpha: alpha = score
        else:
            if score <= alpha: return alpha
            if score < beta: beta = score

    return alpha if maximizing_player else beta

def minimax(board: chess.Board, depth, alpha, beta, maximizing_player):
    alpha_orig = alpha
    beta_orig = beta
    key = board._transposition_key()
    hash_move=None

    # TT READ
    if key in TT:
        tt_value, tt_move, tt_depth, tt_flag = TT[key]
        hash_move = tt_move # Use this for sorting!
        if tt_depth >= depth:
            if tt_flag == "EXACT": return tt_value
            elif tt_flag == "LOWERBOUND": alpha = max(alpha, tt_value)
            elif tt_flag == "UPPERBOUND": beta = min(beta, tt_value)
            if alpha >= beta: return tt_value
    
    if depth == 0: return quiescence(board, alpha, beta, maximizing_player,killers=killers)
    if board.is_game_over(): return evaluate_board(board)

    # Pass hash_move to sorter
    legal = sort_moves(board, depth, killers,hash_move)

    best_val = -math.inf if maximizing_player else math.inf
    best_move_this_node = None # Track the move!

    for move in legal:
        board.push(move)
        eval = minimax(board, depth - 1, alpha, beta, not maximizing_player)
        board.pop()

        if maximizing_player:
            if eval > best_val:
                best_val = eval
                best_move_this_node = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                # Killer Logic
                if not board.is_capture(move):
                    if depth not in killers: killers[depth] = []
                    if move not in killers[depth]:
                        killers[depth].insert(0, move)
                        killers[depth] = killers[depth][:2]
                break
        else:
            if eval < best_val:
                best_val = eval
                best_move_this_node = move
            beta = min(beta, eval)
            if beta <= alpha:
                # Killer Logic
                if not board.is_capture(move):
                    if depth not in killers: killers[depth] = []
                    if move not in killers[depth]:
                        killers[depth].insert(0, move)
                        killers[depth] = killers[depth][:2]
                break

    # TT WRITE (Include best_move)
    flag = "EXACT"
    if best_val <= alpha_orig: flag = "UPPERBOUND"
    elif best_val >= beta_orig: flag = "LOWERBOUND"

    TT[key] = (best_val, best_move_this_node, depth, flag)
    return best_val

def get_best_move_v3(board: chess.Board, depth, hash_move=None):
    if board.fullmove_number <= 15:
        move = book_move(board)
        if move:
            print(f"[Book] Played {move}")
            return 0 , move

    best_moves = []
    max_eval = -math.inf
    min_eval = math.inf
    is_white = board.turn
    
    # 1. Get Sorted Moves
    legal_moves = list(sort_moves(board, depth, killers, hash_move))
    
    if not legal_moves:
        return 0, None # Handle stalemate/mate check outside or return static eval

    for move in legal_moves:
        board.push(move)
        eval_score = minimax(board, depth-1 , -math.inf, math.inf, not is_white)
        board.pop()
        
        if is_white:
            if eval_score > max_eval:
                max_eval = eval_score
                best_moves = [move]
            elif eval_score == max_eval:
                best_moves.append(move)
        else:
            if eval_score < min_eval:
                min_eval = eval_score
                best_moves = [move]
            elif eval_score == min_eval:
                best_moves.append(move)
    
    final_score = max_eval if is_white else min_eval
    
    # Safety check if best_moves is empty (rare)
    if not best_moves: return final_score, None
    
    return final_score, random.choice(best_moves)

def get_best_move_iterative(board: chess.Board,depth, time_limit=math.inf ):
    #temp fix
    return get_best_move_v3(board, depth, hash_move=None)[1]
    global TT, killers

    # Reset ONCE per move
    TT.clear()
    killers.clear()

    best_move = None
    best_score = None

    start_time = time.time()
    current_depth = 1

    while True:
        if time.time() - start_time > time_limit:
            break

        # Root search with previous best as hash move
        score, move = get_best_move_v3(board, current_depth, best_move)
        if move is None:
            break

        if (
            best_score is not None
            and move == best_move
            and ((abs(score) - abs(best_score)) < 20)
            and current_depth >= 3
        ):
            break
        best_move = move
        best_score = score

        # Stop on mate
        if abs(score) > 9000:
            break

        print(f"Info: Depth {current_depth} score {score} best {move}")
        current_depth += 1
        if current_depth > depth:
            break

    return best_move

def book_move(board):
    import chess.polyglot
    BOOK_PATH="Perfect2021.bin"
    try:
        with chess.polyglot.open_reader(BOOK_PATH) as reader:

            # Weighted random choice (important)
            entry = reader.weighted_choice(board)
            if not entry:
                return None
            return entry.move
    except (FileNotFoundError, IndexError) as e:
        print(e)
        pass

    return None
