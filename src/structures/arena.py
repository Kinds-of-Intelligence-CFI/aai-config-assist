from typing import List

from src.structures.rectangular_cuboid import RectangularCuboid


class Arena:
    """The Arena class describes a single AAI arena configuration."""

    def __init__(
        self,
        pass_mark: float,
        t: float,
        physical_items: List[RectangularCuboid],
        overlapping_items: List[str],
    ) -> None:
        self.pass_mark = pass_mark
        self.t = t
        self.physical_items = physical_items
        self.overlapping_items = overlapping_items
