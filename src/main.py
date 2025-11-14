###########################
## python -m day05.src.main
###########################

"""Command line interface for the 4D Chess game."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, Optional

from .game import Game, GameConfig
from .pieces.alien import Alien
from .pieces.cat import Cat
from .utils import Coord, Move


def parse_coord(values: Iterable[str]) -> Coord:
    numbers = [int(v) for v in values]
    if len(numbers) != 4:
        raise ValueError("Coordinates must contain four integers")
    return tuple(numbers)  # type: ignore[return-value]


def locate_action(game: Game, coord: Coord, target: Coord, action_types: Iterable[str]) -> Move:
    actions = game.actions_for(coord)
    for action in actions:
        if action.target == target and action.action in action_types:
            return action
    raise ValueError(f"No matching action for {coord} -> {target}")


def run_cli(args: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Play 4D chess in the terminal")
    parser.add_argument("--players", type=int, default=2, help="Number of players (2-4)")
    parser.add_argument(
        "--shape",
        type=int,
        nargs=4,
        default=[8, 8, 2, 4],
        metavar=("X", "Y", "Z", "W"),
        help="Board dimensions",
    )
    parsed = parser.parse_args(args)

    config = GameConfig(board_shape=tuple(parsed.shape), num_players=parsed.players)
    game = Game(config)

    print("Welcome to 4D Chess! Type 'help' for a list of commands.")
    while True:
        try:
            command = input(f"[{game.current_player.label}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()  # newline for clean exit
            break
        if not command:
            continue
        if command.lower() in {"quit", "exit"}:
            break
        if command.lower() == "help":
            print_help()
            continue
        if command.lower().startswith("show"):
            parts = command.split()
            focus = int(parts[1]) if len(parts) > 1 else None
            print(game.board.render(focus_w=focus))
            continue
        if command.lower().startswith("actions"):
            parts = command.split()
            try:
                coord = parse_coord(parts[1:5])
                for action in game.actions_for(coord):
                    print(action.describe())
            except Exception as exc:
                print(f"Error: {exc}")
            continue
        try:
            process_action(command, game)
        except Exception as exc:
            print(f"Error: {exc}")
            continue
        winner = game.winner()
        if winner:
            print(f"{winner.label} wins the game!")
            break
    return 0


def process_action(command: str, game: Game) -> None:
    parts = command.split()
    if parts[0] == "move":
        if len(parts) != 9:
            raise ValueError("Usage: move x y z w x2 y2 z2 w2")
        origin = parse_coord(parts[1:5])
        target = parse_coord(parts[5:9])
        move = locate_action(game, origin, target, {"move", "capture"})
        game.perform_move(move)
        print(f"Moved from {origin} to {target} ({move.action}).")
    elif parts[0] == "scratch":
        if len(parts) != 9:
            raise ValueError("Usage: scratch x y z w x2 y2 z2 w2")
        origin = parse_coord(parts[1:5])
        target = parse_coord(parts[5:9])
        piece = game.board.get_piece(origin)
        if not isinstance(piece, Cat):
            raise ValueError("Selected piece is not a cat")
        move = locate_action(game, origin, target, {"scratch"})
        game.perform_move(move)
        print(f"Cat scratched the piece at {target}. It now moves like a pawn.")
    elif parts[0] == "alien":
        if len(parts) < 6:
            raise ValueError("Usage: alien x y z w operation")
        origin = parse_coord(parts[1:5])
        operation = parts[5].lower()
        piece = game.board.get_piece(origin)
        if not isinstance(piece, Alien):
            raise ValueError("Selected piece is not an alien")
        if operation not in piece.layout_operations():
            valid = ", ".join(piece.layout_operations())
            raise ValueError(f"Unknown operation. Choose from: {valid}")
        move = Move(actor=origin, target=origin, action="layout", metadata={"operation": operation})
        game.perform_move(move)
        print(f"Alien performed {operation}. The board has been reshaped.")
    else:
        raise ValueError("Unknown command. Type 'help' for assistance.")


def print_help() -> None:
    print(
        "Available commands:\n"
        "  show [w]             - Display the current board (optionally focus on w).\n"
        "  actions x y z w      - List available actions for the piece at the coordinate.\n"
        "  move ...             - Perform a move or capture.\n"
        "  scratch ...          - Command a cat to scratch an opponent piece.\n"
        "  alien ...            - Ask an alien to reshape the board.\n"
        "  help                 - Display this help text.\n"
        "  quit/exit            - Leave the game."
    )


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(run_cli())
