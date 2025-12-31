from flask import Flask, render_template, request, jsonify
import chess
import time
from flask_cors import CORS

# --- IMPORT YOUR ENGINE ---
# Ensure your engine logic is in 'versions/my_engine_v3.py' or 'engine.py'
try:
    from versions.my_engine_v3 import get_best_move_iterative, evaluate_board
except ImportError:
    # Fallback if file structure differs
    from versions.my_engine_v3 import get_best_move_iterative, evaluate_board

app = Flask(__name__)
CORS(app)

# Global board state (optional usage, mostly relying on FEN from frontend)
board = chess.Board()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    fen = data.get('fen')
    move_uci = data.get('move') # This might be None if engine moves first!
    depth = int(data.get('depth', 3))
    time_limit = float(data.get('time_limit', 1.0))

    # 1. Initialize board from client state
    board = chess.Board(fen)

    # 2. Apply Human Move (ONLY if one was sent)
    if move_uci:
        try:
            move = chess.Move.from_uci(move_uci)
            if move in board.legal_moves:
                board.push(move)
            else:
                return jsonify({'status': 'illegal', 'fen': board.fen(), 'message': 'Illegal move'})
        except:
            return jsonify({'status': 'error', 'fen': board.fen(), 'message': 'Invalid move format'})

    # 3. Check Game Over (After human move)
    if board.is_game_over():
        return jsonify({
            'status': 'game_over', 
            'result': get_game_result(board), 
            'fen': board.fen()
        })

    # 4. Engine Thinking
    start = time.time()
    try:
        best_move = get_best_move_iterative(board, depth, time_limit)
        think_time = time.time() - start

        if best_move:
            board.push(best_move)
            eval_score = evaluate_board(board)
            
            # Check game over (After AI move)
            status = 'game_over' if board.is_game_over() else 'success'
            result = get_game_result(board) if board.is_game_over() else None

            return jsonify({
                'status': status,
                'result': result,
                'fen': board.fen(),
                'best_move': best_move.uci(),
                'eval': eval_score,
                'time': f"{think_time:.2f}s"
            })
        else:
            return jsonify({'status': 'no_move', 'fen': board.fen()})

    except Exception as e:
        print(f"Engine Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/reset', methods=['POST'])
def reset():
    return jsonify({'status': 'reset'})

def get_game_result(board):
    if board.is_checkmate(): return 'Checkmate'
    if board.is_stalemate(): return 'Stalemate'
    if board.is_insufficient_material(): return 'Draw (Insufficient Material)'
    return 'Draw'

if __name__ == '__main__':
    app.run(debug=True, port=5000)