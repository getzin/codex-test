# 4D Chess — Cat Scratches & Alien Layouts

Welcome to the most whimsical corner of the chess multiverse. This repository
contains a complete Python implementation of **4D chess** featuring the classic
pieces alongside two new protagonists: the dimension-jumping **Cat** and the
layout-warping **Alien**.

The project is packaged for GitHub with modular source code, a terminal
interface, and comprehensive documentation to help you understand, play, and
extend the game.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Rules of the Game](#rules-of-the-game)
   - [Board Structure](#board-structure)
   - [Players and Turn Order](#players-and-turn-order)
   - [Movement in Four Dimensions](#movement-in-four-dimensions)
   - [Special Piece: Cat](#special-piece-cat)
   - [Special Piece: Alien](#special-piece-alien)
3. [Installation](#installation)
4. [Running the Game](#running-the-game)
5. [Configuration](#configuration)
6. [Code Structure](#code-structure)
   - [Module Overview](#module-overview)
   - [Move Validation](#move-validation)
   - [Layout Operations](#layout-operations)
7. [Extending the Game](#extending-the-game)
8. [Contributing / Forking](#contributing--forking)
9. [License](#license)

---

## Project Overview

This repository implements a configurable, object-oriented engine for playing a
4-dimensional variant of chess. The engine supports **2–4 players**, lets you
**reshape the board** with Alien layout operations, and introduces a 
**Cat scratch mechanic** that permanently downgrades enemy pieces to pawn-level
movement.

All code adheres to modern Python practices: type hints, docstrings, descriptive
naming, and a clean package layout. The game can be played through a friendly
command-line interface and is easy to modify thanks to a data-driven piece and
board setup.

---

## Rules of the Game

### Board Structure

- The board is a **4D grid** addressed by coordinates `(x, y, z, w)`.
- By default the grid spans `(8, 8, 2, 4)`, but the shape is configurable via
  command-line options or programmatic configuration.
- The first three axes (`x`, `y`, `z`) can be viewed as spatial dimensions. The
  fourth axis `w` separates **world slices**. Rendering the board shows each
  `w` slice with its layers along `z`.

### Players and Turn Order

- The engine supports **two to four players**. Each player receives an entire
  slice along the `w` axis for their starting army.
- Turn order is cyclical: Player 1 → Player 2 → Player 3 → Player 4 → repeat.
- A player wins as soon as they are the only one with a surviving King.

### Movement in Four Dimensions

Classic chess pieces have been extended to use the fourth dimension:

- **King (`Kg`)** – Moves one step in any combination of axes, including the
  fourth dimension. Think of it as a 4D Chebyshev move.
- **Queen (`Qn`)** – Combines the powers of the 4D rook and bishop. She sweeps
  along orthogonal lines or along multi-axis diagonals without restriction.
- **Rook (`Rk`)** – Slides along one axis at a time. Rooks can stride through `x`,
  `y`, `z`, or `w` while keeping other coordinates fixed.
- **Bishop (`Bp`)** – Travels along diagonals where two or more axes change by
  the same magnitude. In 4D this means it can pierce space by moving like
  `(±1, ±1, 0, 0)`, `(±1, ±1, ±1, 0)`, or `(±1, ±1, ±1, ±1)` and every scaled
  variant.
- **Knight (`Kn`)** – Executes 4D L-shaped jumps: two steps on one axis combined
  with one step on a different axis.
- **Pawn (`Pw`)** – Each player receives a customised forward vector. Pawns
  advance one step forward and capture diagonally in their orientation (four
  diagonal capture directions per player). They do not currently support
  en-passant or promotion.

### Special Piece: Cat

- **Movement**
  - The Cat is obsessed with dimension indices. It can **jump between worlds** by
    staying on the same `(x, y, z)` but changing `w` to any other valid value.
  - It can also **permute its coordinates**, effectively swapping axes to reappear
    elsewhere on the board so long as the resulting coordinate remains in bounds.
- **Scratch Ability**
  - Instead of capturing, the Cat may **scratch** an opponent occupying one of its
    reachable destinations. The Cat stays put, the target remains on the board,
    but from that moment on the scratched piece moves exactly like a pawn.
  - Scratching an existing pawn has no additional effect—it keeps behaving as a
    pawn. Scratching a King is legal; the royal piece becomes dramatically less
    mobile.
  - Scratches are permanent for the duration of the game.

### Special Piece: Alien

- **Movement**
  - By default the Alien moves one step in any direction, behaving similarly to a
    King. This keeps its physical movement intuitive.
- **Layout Operations**
  - The Alien can use its turn to perform a **layout operation** that transforms
    the coordinates of every other piece on the board. The Alien itself remains at
    its logical position (the coordinate you addressed). Available operations:
    - `transpose`: swap the `x` and `y` axes for every other piece.
    - `moveaxis`: relocate the `w` axis to become the new leading axis (conceptual
      equivalent of NumPy's `moveaxis`).
    - `reshapeaxis`: rotate the `z` coordinate forward by one step, wrapping
      around.
    - `swapaxis`: exchange the top and bottom ranks along the `y` axis.
  - If a transformation would push a piece outside the board or cause a collision,
    the operation is cancelled and the turn is forfeited.

**Example** – `transpose`

Before (showing `(x, y, z, w)` tuples for two pieces):

```
Knight at (1, 0, 0, 0)
Bishop at (2, 3, 0, 2)
```

After `transpose` (swap `x` and `y`):

```
Knight at (0, 1, 0, 0)
Bishop at (3, 2, 0, 2)
```

**Example** – `reshapeaxis`

For a piece on layer `z = 1`, `reshapeaxis` (with a shift of +1) moves it to the
next layer; pieces on the highest `z` wrap back to `0`.

---

## Installation

1. Clone or download the repository.
2. Ensure Python **3.11+** is available.
3. Install dependencies (there are none beyond the standard library but this step
   keeps your workflow consistent):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\\Scripts\\activate
pip install -r requirements.txt
```

---

## Running the Game

Launch the command-line interface with:

```bash
python -m src.main
```

You will be greeted with the prompt `[Player X] >`. Type `help` to display the
available commands. Example session commands:

```
show 0                      # Render the board for world w=0
move 0 1 0 0 0 2 0 0        # Advance a pawn
scratch 2 0 1 0 2 1 1 0    # Cat scratches across dimensions
alien 5 0 1 0 transpose    # Alien rewires the board
```

Press `Ctrl+C` or type `quit` to exit.

---

## Configuration

The CLI exposes two important knobs:

- `--players N` controls the number of players (`2`–`4`). Ensure the `w` axis of
  the board is at least as large as the player count.
- `--shape X Y Z W` overrides the default board shape. Larger boards provide more
  breathing room for layout operations.

You can also configure the game programmatically by instantiating `GameConfig`
and passing it to `Game`.

---

## Code Structure

```
src/
├── __init__.py          # Package export
├── main.py              # CLI entry point
├── board.py             # Board4D container and transformations
├── game.py              # Game orchestration, turn logic
├── utils.py             # Shared helpers and Move dataclass
└── pieces/
    ├── __init__.py
    ├── base.py          # Piece base class & helpers
    ├── standard_pieces.py
    ├── cat.py
    └── alien.py
```

### Module Overview

- **`board.py`** – Stores pieces in a dictionary keyed by coordinates, provides
  ray tracing for sliding pieces, and applies Alien transformations safely.
- **`game.py`** – Builds players, sets up the default position, validates moves,
  executes scratches and layout operations, and determines the winner.
- **`pieces/`** – Each file encapsulates movement rules for a specific set of
  pieces. The base class handles scratched behaviour transparently.
- **`main.py`** – Offers the CLI loop, parsing commands and feeding them into the
  engine.

### Move Validation

Each piece produces a list of `Move` objects via polymorphic `available_actions`
methods. The `Game` class cross-checks commands against this list to ensure
requested actions are legal before applying them to the board. Scratched pieces
are automatically routed through the pawn movement generator.

### Layout Operations

Alien operations are implemented as factories that close over the board shape.
They return coordinate transforms applied to every other piece. Collision or
out-of-bounds results abort the operation and raise an error, which the CLI
catches and displays.

---

## Extending the Game

- **Add a new piece** – Create a new class in `src/pieces/`, inherit from
  `Piece`, and implement `_generate_native_moves`. Register the piece inside
  `game.py` when setting up armies.
- **Modify board size** – Update the shape passed to `GameConfig` or expose new
  CLI parameters.
- **Custom Cat/Alien behaviour** – Override `_generate_scratched_moves` or tweak
  the layout factories. Because the code is modular, you can easily provide new
  operations or additional Cat move rules.
- **Victory conditions** – The `winner` method can be swapped out to support
  checkmate detection, team victories, or point-based scoring.

---

## Contributing / Forking

1. Fork the repository on GitHub.
2. Clone your fork and set up a virtual environment:

   ```bash
   git clone https://github.com/<you>/4d-chess.git
   cd 4d-chess
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Make your changes in a feature branch, e.g. `feature/new-alien-power`.
4. Optionally add tests under `tests/` (pytest is recommended; add dependencies
   to `requirements.txt`).
5. Run the CLI to verify the behaviour, and submit a pull request describing your
   modifications.

---

## License

This project is released under the **"Meow Meow Creative Commons, for
non-commercial use"** license. You are free to fork, study, and modify the code
for personal or educational purposes. Commercial use is not permitted.
