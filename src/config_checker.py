import yaml
from src.arena_config_loader import ArenaConfigLoader
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class ConfigChecker:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config_data = self._load_config_data()

    def check_overlap(self):
        # Isolate items and trim because agent does not have size fields like other items
        items = self.config_data["arenas"][0]["items"]
        items = [element for element in items if element["name"] != "Agent"]

        # Items are grouped by type, so len(items) is the number of item types in this configuration,
        # not the number of items per type which could be accessed via e.g. len(items[0]) for the 0th item type
        N = len(items)

        # The physical three-dimensional boundary values of each item will be stored in a dictionary
        boundaries = dict()

        # Main loop to check overlap between all items across all object types (with no repeated comparisons)
        for type1_ix in range(0, N):
            for item1_ix in range(0, len(items[type1_ix]["positions"])):
                for type2_ix in range(type1_ix, N):

                    # If you are assessing overlap in two items of the same type, do not re-do all previous comparisons
                    item2_ix_start = item1_ix + 1 if type1_ix == type2_ix else 0

                    for item2_ix in range(item2_ix_start, len(items[type2_ix]["positions"])):
                        # # # To check that all indices are being compared sensibly
                        # print(type1_ix, item1_ix, type2_ix, item2_ix)

                        # Only calculate boundaries if they have not been previously calculated for an item
                        pos1, size1 = items[type1_ix]["positions"][item1_ix], items[type1_ix]["sizes"][item1_ix]
                        boundaries1 = boundaries.setdefault((type1_ix, item1_ix),
                                                            self._calculate_item_bounds(pos1, size1))

                        pos2, size2 = items[type2_ix]["positions"][item2_ix], items[type2_ix]["sizes"][item2_ix]
                        boundaries2 = boundaries.setdefault((type2_ix, item2_ix),
                                                            self._calculate_item_bounds(pos2, size2))

                        overlap, xo, yo, zo = self._check_overlap_from_item_boundaries(boundaries1, boundaries2)

                        if overlap:
                            # Extract the names of the items from the data
                            name1 = self._set_item_name_from(type_name=items[type1_ix]["name"], item_ix=item1_ix)
                            name2 = self._set_item_name_from(type_name=items[type2_ix]["name"], item_ix=item2_ix)

                            self._display_overlap_summary(overlap_values=(xo, yo, zo),
                                                          boundaries1=boundaries1,
                                                          boundaries2=boundaries2,
                                                          name1=name1,
                                                          name2=name2)

    def visualise_config(self):
        items = self.config_data["arenas"][0]["items"]
        names, bounds = self._extract_names_and_bounds_from(items)

        fig = plt.figure()
        plt.xlim(0, 40.5)
        plt.ylim(0, 40.5)
        currentAxis = plt.gca()

        for k in bounds.keys():
            item_bounds = bounds[k]
            bottom_left, width, height = self._transform_corner_coordinates(item_bounds)
            currentAxis.add_patch(Rectangle(xy=bottom_left, width=width, height=height, edgecolor='k', lw=1, alpha=0.5,))
            plt.text(x=bottom_left[0] + 0.5 * width, y=bottom_left[1] + 0.5 * height, s=f"{names[k]}")

        plt.show()

    def _transform_corner_coordinates(self, bounds):
        """Transforms the corner coordinates from the format (x1, x2), (y1, y2), (z1, z2)
        to a 2d (excluding the vertical y axis) format suitable to use the matplotlib.patches.Rectangle class"""
        x1, x2 = bounds[0][0], bounds[0][1]
        z1, z2 = bounds[2][0], bounds[2][1]

        bottom_left = (min(x1, x2), min(z1, z2))
        width = x2 - x1
        height = z2 - z1

        return bottom_left, width, height

    def _extract_names_and_bounds_from(self, items):
        names = {}
        bounds = {}

        for type_ix in range(len(items)):
            if items[type_ix]["name"] == "Agent":
                print("Implement a way to deal with the agent extraction")

            else:
                item = items[type_ix]
                for item_ix in range(len(item["positions"])):
                    names[(type_ix, item_ix)] = self._set_item_name_from(type_name=item["name"], item_ix=item_ix)
                    bounds[(type_ix, item_ix)] = self._calculate_item_bounds(item["positions"][item_ix],
                                                                             item["sizes"][item_ix])

        return names, bounds

    def _load_config_data(self):
        """Returns the loaded data from the YAML configuration"""
        with open(self.config_path) as file:
            config_data = yaml.load(file, Loader=ArenaConfigLoader)
        return config_data

    def _calculate_item_bounds(self, item_position, item_size):
        """Returns three-dimensional boundaries of an item in the arena"""
        x_bounds = (item_position["x"] - 0.5 * (item_size["x"]),
                    item_position["x"] + 0.5 * (item_size["x"]))

        # The position of y is not the center of mass but the lowest point hence the difference to calculate boundaries
        y_bounds = (item_position["y"],
                    item_position["y"] + item_size["y"])

        z_bounds = (item_position["z"] - 0.5 * (item_size["z"]),
                    item_position["z"] + 0.5 * (item_size["z"]))
        return x_bounds, y_bounds, z_bounds

    def _check_overlap_from_item_boundaries(self, b1, b2):
        """Checks the overlap between two items from the item boundaries b1 and b2 in the format
        ((x_start, x_end), (y_start, y_end), (z_start, z_end)).

        Returns whether the items overlap (True/False) and the overlap values in every dimension"""

        x_overlap = max(0, min(b1[0][1], b2[0][1]) - max(b1[0][0], b2[0][0]))
        y_overlap = max(0, min(b1[1][1], b2[1][1]) - max(b1[1][0], b2[1][0]))
        z_overlap = max(0, min(b1[2][1], b2[2][1]) - max(b1[2][0], b2[2][0]))

        items_overlap = bool(x_overlap and y_overlap and z_overlap)

        return items_overlap, x_overlap, y_overlap, z_overlap

    def _set_item_name_from(self, type_name, item_ix):
        """Set a name for an item from its type and index (e.g. if there are several walls)"""
        return f"{type_name} {item_ix}"

    def _display_overlap_summary(self, overlap_values, boundaries1, boundaries2, name1, name2):
        """Display the summary of overlap in a human-readable fashion"""
        print(f"Overlap between {name1} and {name2}")
        print(f"- X direction: {overlap_values[0]}")
        print(f"- Y direction: {overlap_values[1]}")
        print(f"- Z direction: {overlap_values[2]}")
        print(f"Boundaries of {name1}: {boundaries1}")
        print(f"Boundaries of {name2}: {boundaries2}")
        print(f"\n")


if __name__ == "__main__":
    # Define a configuration checker
    config_checker = ConfigChecker(config_path="example_configs/config.yaml")

    # # Display the configuration data
    # print(config_checker.config_data)

    # # Calculate the physical boundaries of an item in three-dimensional space
    # position = config_checker.config_data["arenas"][0]["items"][0]["positions"][0]
    # size = config_checker.config_data["arenas"][0]["items"][0]["sizes"][0]
    # print(f"position1: {position}")
    # print(f"size1: {size}")
    # print(config_checker._calculate_item_bounds(position, size))

    # # Check overlaps in entire configuration file
    config_checker.check_overlap()

    # Visualise the arena from the configuration
    config_checker.visualise_config()

    print("Exit ok")
