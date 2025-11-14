"""Implementation of the layout-bending Alien piece."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from ..board import CoordinateTransform
from ..utils import Coord, Move
from .base import Piece


LayoutFactory = Callable[[Tuple[int, ...]], CoordinateTransform]


@dataclass
class Alien(Piece):
    """An extra-terrestrial piece capable of reshaping the board."""

    name: str = "Alien"
    symbol: str = "Al"

    def _generate_native_moves(self, board, position: Coord) -> List[Move]:
        # By default the alien moves like a king: one step in any direction.
        from .standard_pieces import King

        return King(owner=self.owner)._generate_native_moves(board, position)

    # Layout operations -------------------------------------------------

    def layout_operations(self) -> Dict[str, LayoutFactory]:
        """Return a mapping of operation names to factory functions."""

        return {
            "transpose": self._build_transpose,
            "moveaxis": self._build_moveaxis,
            "reshapeaxis": self._build_reshapeaxis,
            "swapaxis": self._build_swapaxis,
        }

    def _build_transpose(self, shape: Tuple[int, ...]) -> CoordinateTransform:
        axis_a = 0
        axis_b = 1

        def transform(coord: Coord) -> Coord:
            temp = list(coord)
            temp[axis_a], temp[axis_b] = temp[axis_b], temp[axis_a]
            result = tuple(temp)
            return result  # type: ignore[return-value]

        transform.__name__ = f"transpose_{axis_a}_{axis_b}"
        return transform

    def _build_moveaxis(self, shape: Tuple[int, ...]) -> CoordinateTransform:
        axis = 3
        destination = 0

        def transform(coord: Coord) -> Coord:
            temp = list(coord)
            element = temp.pop(axis)
            temp.insert(destination, element)
            return tuple(temp)  # type: ignore[return-value]

        transform.__name__ = f"moveaxis_{axis}_to_{destination}"
        return transform

    def _build_reshapeaxis(self, shape: Tuple[int, ...]) -> CoordinateTransform:
        axis = 2
        shift = 1 % shape[axis]

        def transform(coord: Coord) -> Coord:
            temp = list(coord)
            temp[axis] = (temp[axis] + shift) % shape[axis]
            return tuple(temp)  # type: ignore[return-value]

        transform.__name__ = f"reshapeaxis_{axis}_shift_{shift}"
        return transform

    def _build_swapaxis(self, shape: Tuple[int, ...]) -> CoordinateTransform:
        axis = 1
        value_a = 0
        value_b = shape[axis] - 1

        def transform(coord: Coord) -> Coord:
            temp = list(coord)
            if temp[axis] == value_a:
                temp[axis] = value_b
            elif temp[axis] == value_b:
                temp[axis] = value_a
            return tuple(temp)  # type: ignore[return-value]

        transform.__name__ = f"swapaxis_{axis}_{value_a}_{value_b}"
        return transform

    def _generate_scratched_moves(self, board, position: Coord) -> List[Move]:
        from .standard_pieces import Pawn

        pawn = Pawn(owner=self.owner)
        return pawn._generate_native_moves(board, position)

    def available_layout_moves(self, board, position: Coord) -> List[Move]:
        moves: List[Move] = []
        for name, factory in self.layout_operations().items():
            transform = factory(tuple(board.shape))
            moves.append(
                Move(
                    actor=position,
                    target=position,
                    action="layout",
                    metadata={"operation": name, "function": transform.__name__},
                )
            )
        return moves
