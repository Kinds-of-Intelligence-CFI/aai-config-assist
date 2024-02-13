import yaml
from arena_config_loader import ArenaConfigLoader


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
                        boundaries_item1 = boundaries.setdefault((type1_ix, item1_ix),
                                                                 self._calculate_item_bounds(pos1, size1))

                        pos2, size2 = items[type2_ix]["positions"][item2_ix], items[type2_ix]["sizes"][item2_ix]
                        boundaries_item2 = boundaries.setdefault((type2_ix, item2_ix),
                                                                 self._calculate_item_bounds(pos2, size2))

                        # overlap = self._check_overlap_between_items()
                        #
                        # if overlap:
                        #     # Fetch the names of the items that are overlapping and display a summary of their overlap
                        #     name1 = self._get_item_name_from_indices(..., ...)
                        #     name2 = self._get_item_name_from_indices(..., ...)
                        #     self._display_overlap_summary(overlap, name1, name2)

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

    # def _check_overlap_between_items(self,):
    #     """Checks the overlap between two items in the boundaries list. Returns None if there is no overlap and
    #     returns the x, y, and z overlap if there is an overlap"""
    #     return 0
    #
    # def _display_overlap_summary(self, overlap, name1, name2):
    #     """Display the summary of overlap in a human-readable fashion"""
    #     return 0
    #
    # def _get_item_name_from_indices(self, items, type_idx, item_idx):
    #     """Get the exact name and identification number (e.g. if there are several walls)"""
    #     return 0


if __name__ == "__main__":
    # Define a configuration checker
    config_checker = ConfigChecker(config_path="example_configs/config.yaml")

    # # Display the configuration data
    # print(config_checker.config_data)

    # Calculate the physical boundaries of an item in three-dimensional space
    position = config_checker.config_data["arenas"][0]["items"][0]["positions"][0]
    size = config_checker.config_data["arenas"][0]["items"][0]["sizes"][0]
    print(f"position1: {position}")
    print(f"size1: {size}")
    print(config_checker._calculate_item_bounds(position, size))

    # Check overlaps in entire configuration file
    config_checker.check_overlap()

    print("Exit ok")
