from src.rectangular_cuboid import RectangularCuboid


class Arena:
    def __init__(self,
                 pass_mark: float,
                 t: float,
                 physical_items: list[RectangularCuboid],
                 overlapping_items: list[str]) -> None:
        self.pass_mark = pass_mark
        self.t = t
        self.physical_items = physical_items
        self.overlapping_items = overlapping_items
