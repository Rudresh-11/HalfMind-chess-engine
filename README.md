
# HalfMind

**HalfMind** is a handcrafted chess engine written in Python, designed to play sharp, principled openings and dynamic middlegame positions.

It deliberately keeps endgame heuristics lightweight, resulting in **aggressive, human-like play** that can dominate early phases but occasionally struggles to convert in simplified positions — a conscious design tradeoff.

> *Sharp ideas, short memory.*

---

## Project Overview

HalfMind was built to explore **classical chess engine design** rather than neural networks.
The focus is on search quality, move ordering, and real-time decision making under time constraints.

The engine is exposed through a **web interface** that allows users to play against it directly, adjust difficulty, and visualize evaluations.

---

## Core Features

### Search & Engine Logic

* Minimax with **Alpha–Beta pruning**
* **Iterative deepening** with aspiration windows
* **Transposition tables** (hash-based caching)
* **Quiescence search** for tactical stability
* **Move ordering heuristics**:

  * Checks
  * Promotions
  * MVV–LVA captures
  * Killer moves
  * Positional (PST) tie-breakers
* Late Move Reductions (LMR)

### Evaluation

* Material balance
* Piece-Square Tables (PST)
* Passed pawn bonuses
* Basic endgame detection

Endgame logic is intentionally minimal to prioritize speed and middlegame sharpness.

---

## Web Interface

The engine is wrapped in a Flask-based web application with a modern UI.

### UI Features

* Drag-and-drop chessboard (chessboard.js)
* Adjustable search depth
* Adjustable time limit
* Live evaluation bar
* Move history (PGN-style)
* Undo, board flip, FEN copy
* Docker-ready deployment

---

## Live Demo

Experience HalfMind Chess Engine live: [https://halfmind-chess-engine.onrender.com/](https://halfmind-chess-engine.onrender.com/)

---

## Running Locally

### Requirements

* Python 3.10+
* pip

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the server

```bash
python app.py
```

---

## Configuration Notes

* Depth and time limits are **hard-capped server-side** to prevent abuse.
* Designed for **single-worker execution** (CPU-bound engine).
* Not intended for massive concurrency (yet).

---

## Known Limitations (By Design)

* Weak endgame technique in low-material positions
* No tablebases
* No neural evaluation (NNUE)
* No UCI protocol (web-first design)

These are conscious tradeoffs, not oversights.

---

## Project Goals

* Demonstrate understanding of **search-based AI**
* Build a full-stack system around a non-trivial algorithm
* Prioritize clarity, correctness, and controllable behavior
* Embrace imperfection as part of the engine’s identity

---

## Tech Stack

* **Python** (engine & backend)
* **Flask** (web server)
* **python-chess** (board representation)
* **JavaScript + chessboard.js** (frontend)
* **Docker** (deployment)

---

## License

This project is intended for **educational and demonstration purposes**.

---

## Author

Built by an engineering student as an exploration of classical game AI, search optimization, and systems integration.


