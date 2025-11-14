"""Game orchestration for 4D Chess."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .board import Board4D
from .pieces.alien import Alien
from .pieces.cat import Cat
from .pieces.standard_pieces import Bishop, King, Knight, Pawn, Queen, Rook
from .utils import Coord, Move, within_bounds


@dataclass
class Player:
    """Represents one participant in the match."""

    identifier: int
    label: str
    forward_vector: Coord
    capture_vectors: Tuple[Coord, ...]

    def owns_piece(self, piece: "Piece") -> bool:
        return piece.owner.identifier == self.identifier


@dataclass
class GameConfig:
    board_shape: Tuple[int, int, int, int] = (8, 8, 2, 4)
    num_players: int = 2
    player_labels: Tuple[str, ...] = ("Player 1", "Player 2", "Player 3", "Player 4")


class Game:
    """High level controller managing board state and turns."""

    def __init__(self, config: GameConfig | None = None) -> None:
        self.config = config or GameConfig()
        if not 2 <= self.config.num_players <= 4:
            raise ValueError("Only 2 to 4 players are supported")
        if self.config.num_players > self.config.board_shape[3]:
            raise ValueError("The w-axis must be large enough to host all players")
        self.board = Board4D(self.config.board_shape)
        self.players: List[Player] = self._build_players(self.config.num_players)
        self.current_player_index = 0
        self.history: List[Move] = []
        self._setup_initial_position()

    # Player and board setup ---------------------------------------------

    def _build_players(self, num: int) -> List[Player]:
        orientations = [
            ((0, 1, 0, 0), ((1, 1, 0, 0), (-1, 1, 0, 0), (0, 1, 1, 0), (0, 1, -1, 0))),
            ((0, -1, 0, 0), ((1, -1, 0, 0), (-1, -1, 0, 0), (0, -1, 1, 0), (0, -1, -1, 0))),
            ((1, 0, 0, 0), ((1, 1, 0, 0), (1, -1, 0, 0), (1, 0, 1, 0), (1, 0, -1, 0))),
            ((-1, 0, 0, 0), ((-1, 1, 0, 0), (-1, -1, 0, 0), (-1, 0, 1, 0), (-1, 0, -1, 0))),
        ]
        players: List[Player] = []
        for idx in range(num):
            label = self.config.player_labels[idx]
            forward, captures = orientations[idx]
            players.append(
                Player(
                    identifier=idx,
                    label=label,
                    forward_vector=forward,  # type: ignore[arg-type]
                    capture_vectors=captures,
                )
            )
        return players

    def _setup_initial_position(self) -> None:
        placement_order = [
            Rook,
            Knight,
            Bishop,
            Queen,
            King,
            Bishop,
            Knight,
            Rook,
        ]
        for player in self.players:
            w = player.identifier
            y_back = 0 if player.forward_vector[1] >= 0 else self.board.shape[1] - 1
            y_pawn = y_back + (1 if player.forward_vector[1] >= 0 else -1)
            if not within_bounds((0, y_back, 0, w), self.board.shape):
                continue
            for x, piece_cls in enumerate(placement_order):
                coord = (x, y_back, 0, w)
                if not within_bounds(coord, self.board.shape):
                    continue
                self.board.place_piece(coord, piece_cls(owner=player))
            for x in range(self.board.shape[0]):
                pawn_coord = (x, y_pawn, 0, w)
                if within_bounds(pawn_coord, self.board.shape):
                    self.board.place_piece(pawn_coord, Pawn(owner=player))
            cat_coord = (2, y_back, 1, w)
            alien_coord = (5, y_back, 1, w)
            if within_bounds(cat_coord, self.board.shape):
                self.board.place_piece(cat_coord, Cat(owner=player))
            if within_bounds(alien_coord, self.board.shape):
                self.board.place_piece(alien_coord, Alien(owner=player))

    # Game loop helpers --------------------------------------------------

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def advance_turn(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    # Move execution -----------------------------------------------------

    def actions_for(self, coord: Coord) -> List[Move]:
        piece = self.board.get_piece(coord)
        if piece is None:
            raise ValueError(f"No piece at {coord}")
        return piece.available_actions(self.board, coord)

    def perform_move(self, move: Move) -> None:
        piece = self.board.get_piece(move.actor)
        if piece is None:
            raise ValueError("No piece at actor coordinate")
        if piece.owner != self.current_player:
            raise ValueError("It is not this piece's turn")
        if move.action == "scratch":
            self._execute_scratch(move, piece)
        elif move.action == "layout":
            self._execute_layout(move, piece)
        else:
            self._execute_motion(move, piece)
        piece.history.append(move)
        self.history.append(move)
        self.advance_turn()

    def _execute_motion(self, move: Move, piece: "Piece") -> None:
        target_piece = self.board.get_piece(move.target)
        if target_piece and target_piece.owner == piece.owner:
            raise ValueError("Cannot move onto a friendly piece")
        if target_piece and move.action == "capture":
            self.board.remove_piece(move.target)
        elif target_piece and move.action != "capture":
            raise ValueError("Attempted non-capture into an occupied square")
        self.board.move_piece(move.actor, move.target)

    def _execute_scratch(self, move: Move, piece: "Piece") -> None:
        target_piece = self.board.get_piece(move.target)
        if target_piece is None:
            raise ValueError("Scratch requires a target piece")
        if target_piece.owner == piece.owner:
            raise ValueError("Cannot scratch an allied piece")
        target_piece.scratched = True

    def _execute_layout(self, move: Move, piece: "Piece") -> None:
        if not isinstance(piece, Alien):
            raise ValueError("Only aliens can perform layout operations")
        if piece.scratched:
            raise ValueError("Scratched aliens are grounded and cannot reshape the board")
        metadata = move.metadata or {}
        operation = metadata.get("operation")
        if operation not in piece.layout_operations():
            raise ValueError(f"Unknown layout operation {operation}")
        factory = piece.layout_operations()[operation]
        transform = factory(tuple(self.board.shape))
        updates = self.board.apply_transformation(move.actor, transform)
        self.history.extend(updates)

    # Victory checks -----------------------------------------------------

    def remaining_kings(self) -> Dict[int, Coord]:
        positions: Dict[int, Coord] = {}
        for coord, piece in self.board.all_pieces():
            if isinstance(piece, King):
                positions[piece.owner.identifier] = coord
        return positions

    def winner(self) -> Optional[Player]:
        kings = self.remaining_kings()
        alive_players = [player for player in self.players if player.identifier in kings]
        if len(alive_players) == 1:
            return alive_players[0]
        return None


# Local imports for typing -------------------------------------------------
from .pieces.base import Piece  # noqa: E402  # circular guards
