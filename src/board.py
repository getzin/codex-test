"""Implementation of the 4D board representation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Sequence

from .utils import Coord, Move, add_coords, within_bounds


@dataclass
class Board4D:
    """Container for the pieces that live on the 4D board.

    The board is represented by a tuple of four integers describing the size of
    each axis. Coordinates are zero-based ``(x, y, z, w)`` tuples.
    """

    shape: Sequence[int]
    pieces: Dict[Coord, "Piece"] = field(default_factory=dict)

    def place_piece(self, coord: Coord, piece: "Piece") -> None:
        """Place *piece* at *coord* raising ``ValueError`` if occupied."""

        if not within_bounds(coord, self.shape):
            raise ValueError(f"Coordinate {coord} outside of board {self.shape}")
        if coord in self.pieces:
            raise ValueError(f"Coordinate {coord} already occupied")
        self.pieces[coord] = piece

    def move_piece(self, start: Coord, end: Coord) -> None:
        """Move the piece from *start* to *end* without validation."""

        piece = self.pieces.pop(start)
        self.pieces[end] = piece

    def remove_piece(self, coord: Coord) -> "Piece":
        """Remove and return the piece at *coord*."""

        return self.pieces.pop(coord)

    def get_piece(self, coord: Coord) -> "Piece | None":
        """Return the piece located at *coord* or ``None``."""

        return self.pieces.get(coord)

    def all_pieces(self) -> Iterable[tuple[Coord, "Piece"]]:
        """Iterate over all pieces on the board."""

        return self.pieces.items()

    def apply_transformation(self, actor: Coord, transform: "CoordinateTransform") -> List[Move]:
        """Apply *transform* to every piece except the one at *actor*.

        Returns a list of ``Move`` objects describing the resulting relocation
        of the other pieces. The actor is expected to be an Alien performing the
        operation and therefore remains at its logical position.
        """

        updates: List[Move] = []
        mapping: Dict[Coord, "Piece"] = {}
        for coord, piece in list(self.pieces.items()):
            if coord == actor:
                mapping[coord] = piece
                continue
            new_coord = transform(coord)
            if not within_bounds(new_coord, self.shape):
                raise ValueError(
                    f"Transformation {transform.__name__} moved {piece} to {new_coord},"
                    f" outside the board with shape {self.shape}."
                )
            if new_coord in mapping:
                raise ValueError(
                    f"Transformation {transform.__name__} collided pieces at {new_coord}"
                )
            mapping[new_coord] = piece
            updates.append(Move(actor=coord, target=new_coord, action="layout"))
        self.pieces = mapping
        return updates

    def trace_ray(self, start: Coord, direction: Coord) -> Iterable[Coord]:
        """Yield coordinates from *start* when moving along *direction*."""

        current = start
        while True:
            current = add_coords(current, direction)
            if not within_bounds(current, self.shape):
                break
            yield current

    def render(self, focus_w: int | None = None) -> str:
        """Return a readable multi-line representation of the board.

        When ``focus_w`` is provided only the slices at the specified ``w``
        coordinate are shown. Each ``z`` layer is printed as a plane.
        """

        slices: List[str] = []
        w_range = range(self.shape[3]) if focus_w is None else range(focus_w, focus_w + 1)
        for w in w_range:
            slices.append(f"=== World w={w} ===")
            for z in range(self.shape[2]):
                slices.append(f"-- Layer z={z} --")
                for y in range(self.shape[1]):
                    row: List[str] = []
                    for x in range(self.shape[0]):
                        piece = self.get_piece((x, y, z, w))
                        row.append(piece.symbol if piece else "..")
                    slices.append(" ".join(row))
                slices.append("")
        return "\n".join(slices)


CoordinateTransform = Callable[[Coord], Coord]


from .pieces.base import Piece  # noqa: E402  (circular import guard)
