"""Implementation of the standard chess pieces extended to 4D."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, List

from ..utils import Coord, Move, add_coords, within_bounds
from .base import Piece


@dataclass
class Rook(Piece):
    name: str = "Rook"
    symbol: str = "Rk"

    def _generate_native_moves(self, board, position: Coord) -> List[Move]:
        from ..utils import iter_directions

        return self._collect_rays(board, position, iter_directions())


@dataclass
class Bishop(Piece):
    name: str = "Bishop"
    symbol: str = "Bp"

    def _generate_native_moves(self, board, position: Coord) -> List[Move]:
        directions: List[Coord] = []
        for deltas in product([-1, 0, 1], repeat=4):
            if deltas.count(0) >= 3:
                continue  # at least two axes must change
            if all(delta == 0 for delta in deltas):
                continue
            if len({abs(delta) for delta in deltas if delta != 0}) > 1:
                continue  # require same magnitude per axis
            directions.append(deltas)  # type: ignore[arg-type]
        unique: List[Coord] = []
        for direction in directions:
            if direction not in unique:
                unique.append(direction)
        return self._collect_rays(board, position, unique)


@dataclass
class Queen(Piece):
    name: str = "Queen"
    symbol: str = "Qn"

    def _generate_native_moves(self, board, position: Coord) -> List[Move]:
        rook_moves = Rook(owner=self.owner)._generate_native_moves(board, position)
        bishop_moves = Bishop(owner=self.owner)._generate_native_moves(board, position)
        return rook_moves + bishop_moves


@dataclass
class King(Piece):
    name: str = "King"
    symbol: str = "Kg"

    def _generate_native_moves(self, board, position: Coord) -> List[Move]:
        moves: List[Move] = []
        for deltas in product([-1, 0, 1], repeat=4):
            if all(delta == 0 for delta in deltas):
                continue
            target = add_coords(position, deltas)
            if not within_bounds(target, board.shape):
                continue
            target_piece = board.get_piece(target)
            if target_piece is None:
                moves.append(Move(actor=position, target=target, action="move"))
            elif target_piece.owner != self.owner:
                moves.append(Move(actor=position, target=target, action="capture"))
        return moves


@dataclass
class Knight(Piece):
    name: str = "Knight"
    symbol: str = "Kn"

    def _generate_native_moves(self, board, position: Coord) -> List[Move]:
        deltas: List[Coord] = []
        axes = range(4)
        for axis_long in axes:
            for axis_short in axes:
                if axis_long == axis_short:
                    continue
                for sign_long in (-2, 2):
                    for sign_short in (-1, 1):
                        vector = [0, 0, 0, 0]
                        vector[axis_long] = sign_long
                        vector[axis_short] = sign_short
                        deltas.append(tuple(vector))
        return self._collect_leaps(board, position, deltas)


@dataclass
class Pawn(Piece):
    name: str = "Pawn"
    symbol: str = "Pw"

    def _generate_native_moves(self, board, position: Coord) -> List[Move]:
        moves: List[Move] = []
        forward = add_coords(position, self.owner.forward_vector)
        if within_bounds(forward, board.shape) and board.get_piece(forward) is None:
            moves.append(Move(actor=position, target=forward, action="move"))
        for capture in self._capture_targets(position):
            if not within_bounds(capture, board.shape):
                continue
            target_piece = board.get_piece(capture)
            if target_piece and target_piece.owner != self.owner:
                moves.append(Move(actor=position, target=capture, action="capture"))
        return moves

    def _capture_targets(self, position: Coord) -> Iterable[Coord]:
        for vector in self.owner.capture_vectors:
            yield add_coords(position, vector)

    def _generate_scratched_moves(self, board, position: Coord) -> List[Move]:
        # Pawns scratched by the cat remain pawns.
        return self._generate_native_moves(board, position)
