from typing import TYPE_CHECKING, Dict, List, Union

if TYPE_CHECKING:
    import numpy as np

from src.structures.arena import Arena
from src.structures.rectangular_cuboid import RectangularCuboid


class Dumper:
    """Custom dumper for the Animal-AI (A-AI) arena configurations.

    Note:
          - Decided to write the dumper from scratch rather than construct custom dumpers on top of PyYaml for
            extra transparency and control, given the numerous custom tags and data structures in the A-AI configs.

          - Built on an indenting system where levels increase automatically. This way, if the absolute levels change
            at some point, the logic will still be sound while removing the need for repeatedly encoding indents in each
            method. Rather, every time an element is added to the overall_str, the _indent method must be employed.

    """

    def __init__(self, arenas: List[Arena], destination_file_path: str) -> None:
        self.arenas = arenas
        self.destination_file_path = destination_file_path

    def dump(self) -> None:
        overall_str = f"{self._get_complete_config_str(level=0)}"
        with open(self.destination_file_path, "w") as file:
            file.write(overall_str)

    def _get_complete_config_str(self, level: int) -> str:
        """Gets the complete string representation of the updated yaml configuration."""
        result = self._get_heading_str(level) + "\n"
        for ix, arena in enumerate(self.arenas):
            result += self._get_arena_config_str(ix, level + 1)
            return result

    def _get_heading_str(self, level: int) -> str:
        """Gets the string representation of the overall arena configuration tag and arenas attribute."""
        return (
            self._indent("!ArenaConfig", level) + "\n" + self._indent("arenas:", level)
        )

    def _get_arena_config_str(self, ix: int, level: int) -> str:
        """Gets the string representation of the updated arena at index ix inside the arenas class attribute."""
        result = (
            self._indent(f"{ix}: !Arena", level)
            + "\n"
            + self._get_arena_settings_str(ix, level + 1)
            + "\n"
            + self._get_arena_items_str(ix, level + 1)
            + "\n"
        )
        return result

    def _get_arena_settings_str(self, ix: int, level: int) -> str:
        """Gets the string representation of all the arena config attributes other than items (passMark, timeLimit)."""
        passMark = self.arenas[ix].passMark
        timeLimit = self.arenas[ix].timeLimit
        return (
            self._indent(f"passMark: {passMark}", level)
            + "\n"
            + self._indent(f"timeLimit: {timeLimit}", level)
        )

    def _get_arena_items_str(self, ix: int, level: int) -> str:
        """Gets the string representation of all the items in the configuration."""
        items = self.arenas[ix].physical_items
        items_grouped_per_type = self._rearrange_items_per_type(items)
        result = self._indent("items:", level) + "\n"
        for item_type_dict in items_grouped_per_type:
            result += self._indent("- !Item", level) + "\n"
            result += self._get_item_type_str(item_type_dict, level + 1)
        return result

    def _get_item_type_str(self, item_type_dict: Dict, level: int) -> str:
        """Gets the string representation of the A-AI style yaml configuration for an item type."""
        result = self._indent(f"name: {item_type_dict['name']}", level) + "\n"

        def _add_item_section_to_result(item_section_title: str, res: str) -> str:
            res += self._indent(f"{item_section_title}:", level) + "\n"
            for arr in item_type_dict[f"{item_section_title}"]:
                res += self._indent("- " + arr, level) + "\n"
            return res

        result = _add_item_section_to_result("positions", result)
        result = _add_item_section_to_result("rotations", result)
        result = _add_item_section_to_result("sizes", result)
        result = _add_item_section_to_result("colors", result)

        return result

    @staticmethod
    def _rearrange_items_per_type(items: List[RectangularCuboid]) -> List:
        """Rearranges the items from an item-by-item list to a by-type list with the correct output yaml format."""

        def _get_new_item_structure(curr_item_type: str) -> Dict:
            """Gets the A-AI structure for a new item."""
            return {
                "name": curr_item_type,
                "positions": [],
                "rotations": [],
                "sizes": [],
                "colors": [],
            }

        def _get_vector3_representation(a: float, b: float, c: float) -> str:
            """Gets the A-AI Vector3 representation of a triple."""
            return f"!Vector3 {{x: {a}, y: {b}, z: {c}}}"

        def _get_rgb_representation(a: float, b: float, c: float) -> str:
            """Gets the A-AI RGB representation of a triple."""
            return f"!RGB {{r: {a}, g: {b}, b: {c}}}"

        current_item_type = items[0].name.split(" ")[0]
        result = dict()
        result[current_item_type] = _get_new_item_structure(current_item_type)

        for item in items:
            name = item.name.split(" ")[0]
            if name not in result:
                result[name] = _get_new_item_structure(item.name.split(" ")[0])
            result[name]["rotations"] += [str(item.deg_rotation)]
            result[name]["positions"] += [
                _get_vector3_representation(
                    item.center_x,
                    item.center_y,
                    item.center_z,
                )
            ]
            result[name]["sizes"] += [
                _get_vector3_representation(item.length, item.height, item.width)
            ]
            result[name]["colors"] += [
                _get_rgb_representation(
                    item.colour_red, item.colour_green, item.colour_blue
                )
            ]

        # Convert result dict into simply a list of its values
        result = list(result.values())

        return result

    @staticmethod
    def _indent(element: str, level: int) -> str:
        return "  " * level + element


def dumper_example() -> None:
    from dataclasses import dataclass

    import numpy as np

    @dataclass
    class DummyCuboid:
        name: str
        center: np.array
        length: float
        height: float
        width: float
        colour: dict[str, int]
        deg_rotation: float

    arena1 = {
        "passMark": 0,
        "timeLimit": 1000,
        "items": [
            DummyCuboid(
                name="Wall 0",
                center=np.array([18, 0, 37.5]),
                length=30,
                height=15,
                width=7.5,
                colour={"r": 30, "g": 15, "b": 7.5},
                deg_rotation=0,
            ),
            DummyCuboid(
                name="Wall 1",
                center=np.array([10, 5, 10.5]),
                length=10,
                height=5,
                width=2.5,
                colour={"r": 10, "g": 5, "b": 2.5},
                deg_rotation=10,
            ),
            DummyCuboid(
                name="Ramp 0",
                center=np.array([2, 10, 20]),
                length=29,
                height=1,
                width=5,
                colour={"r": 10, "g": 10, "b": 10},
                deg_rotation=34.6,
            ),
        ],
    }

    arenas = [
        arena1,
    ]

    destination_path = f"example_configs/auto_updated_config.yaml"
    arena_config_dumper = Dumper(arenas, destination_path)
    arena_config_dumper.dump()


if __name__ == "__main__":
    dumper_example()
