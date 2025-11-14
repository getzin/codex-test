"""Utility helpers for the 4D chess engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

Coord = Tuple[int, int, int, int]


@dataclass(frozen=True)
class Move:
    """Represents an action in the game.

    Attributes:
        actor: Coordinate of the acting piece before the move.
        target: Coordinate of the destination or affected square.
        action: Name of the action (``"move"``, ``"capture"``, ``"scratch"``,
            ``"layout"``).
        metadata: Optional additional data encoded as a dictionary.
    """

    actor: Coord
    target: Coord
    action: str
    metadata: dict | None = None

    def describe(self) -> str:
        """Return a human readable description of the move."""

        components: List[str] = [self.action.upper(), f"from {self.actor} to {self.target}"]
        if self.metadata:
            components.append(str(self.metadata))
        return " - ".join(components)


def add_coords(a: Coord, b: Coord) -> Coord:
    """Add two coordinates component-wise."""

    return tuple(ax + bx for ax, bx in zip(a, b))  # type: ignore[return-value]


def within_bounds(coord: Coord, shape: Sequence[int]) -> bool:
    """Return True if *coord* lies within the board described by *shape*."""

    return all(0 <= c < limit for c, limit in zip(coord, shape))


def iter_directions(step: int = 1) -> Iterable[Coord]:
    """Yield orthogonal direction vectors of length ``step`` in 4D space."""

    deltas = [step, -step]
    zero = 0
    for axis in range(4):
        for delta in deltas:
            vector = [zero, zero, zero, zero]
            vector[axis] = delta
            yield tuple(vector)  # type: ignore[return-value]


def iter_diagonals(step: int = 1) -> Iterable[Coord]:
    """Yield diagonal direction vectors in 4D space."""

    deltas = [step, -step]
    for dx in deltas:
        for dy in deltas:
            for dz in deltas:
                for dw in deltas:
                    yield dx, dy, dz, dw


def manhattan_distance(a: Coord, b: Coord) -> int:
    """Compute the Manhattan distance between two coordinates."""

    return sum(abs(ax - bx) for ax, bx in zip(a, b))
