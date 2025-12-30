from flask import Flask, render_template, request, jsonify
import chess
import time
from versions.my_engine_v3 import get_best_move_iterative, evaluate_board
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global board state
board = chess.Board()
move_history = []

@app.route('/')
def index():
    return render_template('index.html', fen=board.fen())

@app.route('/move', methods=['POST'])
def move():
    global move_history
    
    data = request.json
    move_uci = data.get('move')
    depth = int(data.get('depth', 3))
    time_limit = float(data.get('time_limit', 1.0))

    # 1. Apply Human Move
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            move_history.append(move)
        else:
            return jsonify({
                'status': 'illegal', 
                'fen': board.fen(),
                'message': 'Illegal move'
            })
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'fen': board.fen(),
            'message': str(e)
        })

    # Check Game Over after human move
    if board.is_game_over():
        result = get_game_result()
        return jsonify({
            'status': 'game_over', 
            'result': result, 
            'fen': board.fen()
        })

    # 2. Engine Thinking
    start = time.time()
    try:
        best_move = get_best_move_iterative(board, depth, time_limit)
        think_time = time.time() - start

        if best_move:
            board.push(best_move)
            move_history.append(best_move)
            eval_score = evaluate_board(board)
            
            # Check game over after AI move
            if board.is_game_over():
                result = get_game_result()
                return jsonify({
                    'status': 'game_over',
                    'result': result,
                    'fen': board.fen(),
                    'best_move': best_move.uci(),
                    'eval': eval_score,
                    'time': f"{think_time:.2f}s"
                })
            
            return jsonify({
                'status': 'success',
                'fen': board.fen(),
                'best_move': best_move.uci(),
                'eval': eval_score,
                'time': f"{think_time:.2f}s",
                'move_count': len(move_history)
            })
        else:
            # No legal moves (shouldn't happen if game_over check works)
            return jsonify({
                'status': 'no_move',
                'fen': board.fen(),
                'message': 'Engine could not find a move'
            })
    except Exception as e:
        return jsonify({
            'status': 'engine_error',
            'fen': board.fen(),
            'message': f'Engine error: {str(e)}',
            'time': f"{time.time() - start:.2f}s"
        })

@app.route('/reset', methods=['POST'])
def reset():
    global board, move_history
    board = chess.Board()
    move_history = []
    return jsonify({
        'status': 'reset', 
        'fen': board.fen()
    })

@app.route('/undo', methods=['POST'])
def undo():
    global move_history
    
    # Undo last 2 moves (AI and player)
    if len(move_history) >= 2:
        board.pop()  # Undo AI move
        board.pop()  # Undo player move
        move_history = move_history[:-2]
        
        return jsonify({
            'status': 'success',
            'fen': board.fen(),
            'move_count': len(move_history)
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Not enough moves to undo'
        })

@app.route('/status', methods=['GET'])
def status():
    """Get current board status"""
    eval_score = evaluate_board(board)
    
    return jsonify({
        'fen': board.fen(),
        'eval': eval_score,
        'move_count': len(move_history),
        'is_check': board.is_check(),
        'is_checkmate': board.is_checkmate(),
        'is_stalemate': board.is_stalemate(),
        'is_game_over': board.is_game_over(),
        'turn': 'white' if board.turn else 'black'
    })

@app.route('/analysis', methods=['POST'])
def analysis():
    """Analyze a position without making a move"""
    data = request.json
    depth = int(data.get('depth', 3))
    time_limit = float(data.get('time_limit', 1.0))
    
    start = time.time()
    best_move = get_best_move_iterative(board, depth, time_limit)
    think_time = time.time() - start
    
    eval_score = evaluate_board(board)
    
    return jsonify({
        'status': 'success',
        'best_move': best_move.uci() if best_move else None,
        'eval': eval_score,
        'time': f"{think_time:.2f}s",
        'legal_moves': [move.uci() for move in board.legal_moves]
    })

def get_game_result():
    """Get human-readable game result"""
    if board.is_checkmate():
        winner = 'Black' if board.turn else 'White'
        return f'{winner} wins by checkmate'
    elif board.is_stalemate():
        return 'Draw by stalemate'
    elif board.is_insufficient_material():
        return 'Draw by insufficient material'
    elif board.can_claim_threefold_repetition():
        return 'Draw by threefold repetition'
    elif board.can_claim_fifty_moves():
        return 'Draw by fifty-move rule'
    else:
        return board.result()

if __name__ == '__main__':
    print("🎮 Chess Engine Server Starting...")
    print("📊 Features: Move history, Undo, Analysis, Enhanced error handling")
    print("🌐 Server running at: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)