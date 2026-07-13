"""Topology-only classifier for Grammar v2 four-way corridor crossings."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from style_sample_system_v2_base import Point

CrossJunctionKind = Literal["four_way_cross"]


@dataclass(frozen=True, order=True)
class CrossJunction:
    """One plus-shaped corridor intersection centered on a floor section."""

    kind: CrossJunctionKind
    center: Point


def cross_junctions(cells: frozenset[Point]) -> tuple[CrossJunction, ...]:
    """Return local plus intersections with open diagonal quadrants.

    Requiring all four cardinal neighbors and no diagonal neighbors separates a
    one-section-wide corridor crossing from an ordinary interior room section.
    """
    result: list[CrossJunction] = []
    for center in sorted(cells):
        cardinal = {
            Point(center.x, center.y - 1),
            Point(center.x + 1, center.y),
            Point(center.x, center.y + 1),
            Point(center.x - 1, center.y),
        }
        diagonal = {
            Point(center.x - 1, center.y - 1),
            Point(center.x + 1, center.y - 1),
            Point(center.x - 1, center.y + 1),
            Point(center.x + 1, center.y + 1),
        }
        if cardinal.issubset(cells) and diagonal.isdisjoint(cells):
            result.append(CrossJunction("four_way_cross", center))
    return tuple(result)
