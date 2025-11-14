"""Implementation of the dimension-jumping Cat piece."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import List, Set

from ..utils import Coord, Move
from .base import Piece


@dataclass
class Cat(Piece):
    """A feline traveller that manipulates dimension indices."""

    name: str = "Cat"
    symbol: str = "Ct"

    def _generate_native_moves(self, board, position: Coord) -> List[Move]:
        moves: List[Move] = []
        x, y, z, w = position

        # Jump across dimension index while staying on the same field
        for candidate_w in range(board.shape[3]):
            if candidate_w == w:
                continue
            target = (x, y, z, candidate_w)
            target_piece = board.get_piece(target)
            if target_piece is None:
                moves.append(Move(actor=position, target=target, action="move"))
            elif target_piece.owner != self.owner:
                moves.append(Move(actor=position, target=target, action="capture"))

        # Reassign coordinates by permuting dimension indices
        seen: Set[Coord] = set()
        for permuted in set(permutations(position)):
            if permuted == position or permuted in seen:
                continue
            seen.add(permuted)
            if not all(0 <= permuted[i] < board.shape[i] for i in range(4)):
                continue
            target_piece = board.get_piece(permuted)
            if target_piece is None:
                moves.append(Move(actor=position, target=permuted, action="move"))
            elif target_piece.owner != self.owner:
                moves.append(Move(actor=position, target=permuted, action="capture"))

        # Scratch actions keep the cat in place but affect a target piece
        for move in list(moves):
            target_piece = board.get_piece(move.target)
            if target_piece and target_piece.owner != self.owner:
                moves.append(
                    Move(
                        actor=position,
                        target=move.target,
                        action="scratch",
                        metadata={"effect": "target movement reduced to pawn"},
                    )
                )
        return moves

    def _generate_scratched_moves(self, board, position: Coord) -> List[Move]:
        # A scratched cat moves like a pawn.
        from .standard_pieces import Pawn

        pawn = Pawn(owner=self.owner)
        return pawn._generate_native_moves(board, position)
