"""Base classes and helper mixins for chess pieces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, List, Sequence

from ..board import Board4D
from ..utils import Coord, Move, add_coords, within_bounds

if TYPE_CHECKING:  # pragma: no cover - imported only for typing
    from ..game import Player


@dataclass
class Piece:
    """Base representation of a piece on the board."""

    owner: "Player"
    name: str = ""
    symbol: str = ""
    scratched: bool = False
    history: List[Move] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"{self.name}({self.owner.label})"

    def available_actions(self, board: Board4D, position: Coord) -> List[Move]:
        """Return all legal actions for the piece at *position*.

        When ``self.scratched`` is ``True`` the piece temporarily borrows the
        pawn movement logic. Pieces may override ``_generate_scratched_moves`` to
        implement bespoke behaviour.
        """

        if self.scratched:
            return self._generate_scratched_moves(board, position)
        return self._generate_native_moves(board, position)

    # The following methods are intended to be overridden by subclasses.

    def _generate_native_moves(self, board: Board4D, position: Coord) -> List[Move]:
        raise NotImplementedError

    def _generate_scratched_moves(self, board: Board4D, position: Coord) -> List[Move]:
        from .standard_pieces import Pawn

        pawn = Pawn(owner=self.owner)
        return pawn._generate_native_moves(board, position)

    # Shared helpers -----------------------------------------------------

    def _collect_rays(
        self,
        board: Board4D,
        position: Coord,
        directions: Iterable[Coord],
        repeat: bool = True,
    ) -> List[Move]:
        moves: List[Move] = []
        for direction in directions:
            for coord in board.trace_ray(position, direction):
                target_piece = board.get_piece(coord)
                if target_piece is None:
                    moves.append(Move(actor=position, target=coord, action="move"))
                    if not repeat:
                        break
                    continue
                if target_piece.owner != self.owner:
                    moves.append(Move(actor=position, target=coord, action="capture"))
                break
        return moves

    def _collect_leaps(
        self,
        board: Board4D,
        position: Coord,
        deltas: Sequence[Coord],
    ) -> List[Move]:
        moves: List[Move] = []
        for delta in deltas:
            target = add_coords(position, delta)
            if not within_bounds(target, board.shape):
                continue
            target_piece = board.get_piece(target)
            if target_piece is None:
                moves.append(Move(actor=position, target=target, action="move"))
            elif target_piece.owner != self.owner:
                moves.append(Move(actor=position, target=target, action="capture"))
        return moves

