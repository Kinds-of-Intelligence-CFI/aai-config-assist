from typing import Dict, List

import numpy as np

from src.structures.arena import Arena
from src.structures.rectangular_cuboid import RectangularCuboid
from src.utils.physical_item_helper import (
    get_default_item_parameter,
    set_item_name_from,
)


class Preprocessor:
    """The Preprocessor transforms raw data from an AAI YAML configuration file to a list of Arena objects.

    Note:
        - The arena list that the Preprocessor creates contains as many Arena objects as arenas described by the
        AAI YAML configuration file.
        - In the absence of an existing AAI YAML configuration, the Preprocessor can create an empty/default list
        of arenas via the create_default_arenas_list method.
    """

    DEFAULT_PASS_MARK = 0
    DEFAULT_TIMELIMIT = 1000

    def __init__(
        self, default_item_parameters: Dict, all_aai_item_names: List[str]
    ) -> None:
        self.default_items_params = default_item_parameters
        self.all_aai_item_names = all_aai_item_names

    def create_default_arenas_list(self) -> List[Arena]:
        default_arena = Arena(
            passMark=self.DEFAULT_PASS_MARK,
            timeLimit=self.DEFAULT_TIMELIMIT,
            physical_items=[],
            overlapping_items=[],
        )
        default_arenas_list = [default_arena]
        return default_arenas_list

    def create_arenas_list(self, raw_arenas_dict: Dict) -> List[Arena]:
        preprocessed_arenas_list = []
        raw_arenas = raw_arenas_dict["arenas"]

        for arena_ix in list(raw_arenas.keys()):
            raw_arena = raw_arenas[arena_ix]
            passMark = raw_arena["passMark"]
            timeLimit = raw_arena["timeLimit"]
            raw_physical_items = raw_arena["items"]
            physical_items = self._create_rectangular_cuboid_list(raw_physical_items)
            overlapping_items = []
            arena = Arena(passMark, timeLimit, physical_items, overlapping_items)
            preprocessed_arenas_list += [arena]

        return preprocessed_arenas_list

    def _create_rectangular_cuboid_list(
        self, raw_physical_items: Dict
    ) -> List[RectangularCuboid]:
        """Creates a list of RectangularCuboid instances corresponding to the objects in the configuration data.

        Returns:
            (list[RectangularCuboid]): The RectangularCuboid instances.
        """
        rec_cuboids = []
        item_types = raw_physical_items

        # For every item type
        for i, items in enumerate(item_types):
            # Check whether the item type is valid
            if items["name"] not in self.all_aai_item_names:
                raise Exception(
                    f"The name {items['name']} that you have provided "
                    f"is not in the default items list."
                )
            num_items = len(items["positions"])

            # For every item in the item type
            for j in range(num_items):
                # Extract the useful data
                name = set_item_name_from(type_name=items["name"], item_ix=j)
                position = items["positions"][j]
                rotation = items["rotations"][j] if "rotations" in items else 0

                if "sizes" in items:
                    size = items["sizes"][j]
                else:
                    size = get_default_item_parameter(
                        name, "size", self.default_items_params
                    )

                if "colors" in items:
                    colour = items["colors"][j]
                else:
                    colour = get_default_item_parameter(
                        name, "colour", self.default_items_params
                    )

                # Transform parts of the extracted data
                xzy_lower_base_centroid = np.array(
                    [position["x"], position["z"], position["y"]], dtype=float
                )
                xzy_dimensions = (size["x"], size["z"], size["y"])

                # Instantiate a RectangularCuboid with the extracted and transformed data
                rec_cuboid = RectangularCuboid(
                    lower_base_centroid=xzy_lower_base_centroid,
                    dimensions=xzy_dimensions,
                    rotation=rotation,
                    name=name,
                    colour=colour,
                )

                # Add this instance to the rectangular_cuboids list
                rec_cuboids += [rec_cuboid]

        return rec_cuboids
