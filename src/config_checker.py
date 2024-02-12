import yaml
from arena_config_loader import ArenaConfigLoader


class ConfigChecker:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config_data = self._load_config_data()

    def check_overlap(self,):
        # Isolate items and trim because agent does not have size fields like other items
        items = self.config_data["arenas"][0]["items"]
        items = [element for element in items if element["name"] != "agent"]

        boundaries = self._get_boundaries_of_items_in(items)

        # Items are grouped by type, so len(items) is the number of item types in this configuration,
        # not the number of items per type which could be accessed via e.g. len(items[0]) for the 0th item type
        N = len(items)

        # Main loop to check overlap between all items across all object types (with no repeated comparisons)
        for type1_ix in range(0, N):
            for item1_ix in range(0, len(items[type1_ix]["positions"])):
                for type2_ix in range(type1_ix, N):

                    # If you are assessing overlap in two items of the same type, do not re-do all previous comparisons
                    item2_ix_start = item1_ix + 1 if type1_ix == type2_ix else 0

                    for item2_ix in range(item2_ix_start, len(items[type2_ix]["positions"])):
                        # To check that all indices are being compared sensibly
                        print(type1_ix, item1_ix, type2_ix, item2_ix)

    def _load_config_data(self):
        """Returns the loaded data from the YAML configuration"""
        with open(self.config_path) as file:
            config_data = yaml.load(file, Loader=ArenaConfigLoader)
        return config_data

    def _get_boundaries_of_items_in(self, items):
        """Returns boundaries list with the same overall structure as input items but with boundary limit values
        instead of item description"""
        return 0


if __name__ == "__main__":
    config_checker = ConfigChecker(config_path="example_configs/config_short.yaml")
    print(config_checker.config_data)
    config_checker.check_overlap()

    print("Exit ok")
