import yaml
from src.arena_config_loader import ArenaConfigLoader
from src.separating_axis_theorem import Rectangle, apply_separating_axis_theorem
import numpy as np

class ConfigAssistant:
    def __init__(self, config_path):
        """Constructs the ConfigAssistant class.

        Args:
            config_path (str): Path to YAML Animal-AI configuration file.
        """
        self.config_path = config_path
        self.config_data = self._load_config_data()
        self.physical_items = self._create_rectangle_list()

    def _load_config_data(self):
        """Parses and loads the data from the YAML file inputted to class constructor.

        Returns:
            (dict): The loaded data.
        """
        with open(self.config_path) as file:
            config_data = yaml.load(file, Loader=ArenaConfigLoader)
        return config_data

    def _create_rectangle_list(self):
        """Creates a list of Rectangle instances corresponding to the objects in the configuration data.

        Returns:
            (list): The Rectangle instances.
        """
        rectangles = []

        # Extract the item_types from the configuration file and omit the agent
        item_types = self.config_data["arenas"][0]["items"]
        item_types = [element for element in item_types if element["name"] != "Agent"]

        # Items are grouped by type, so len(item_types) is the number of item types in this configuration,
        # not the number of items per type which could be accessed via e.g. len(item_types[0]) for the 0th item type
        num_item_types = len(item_types)

        # For every item type
        for i, items in enumerate(item_types):
            num_items = len(items["positions"])

            # For every item in the item type
            for j in range(num_items):
                # Extract the useful data
                name = self._set_item_name_from(type_name=items["name"], item_ix=j)
                position = items["positions"][j]
                size = items["sizes"][j]
                rotation = items["rotations"][j] if "rotations" in items else 0

                # Transform some of the extracted data to suit
                size_x = size["x"]
                size_y = size["y"]
                size_z = size["z"]
                xz_planar_centroid = np.array([position["x"], position["z"]])

                # Instantiate a Rectangle with the extracted and transformed data
                # TODO: Make sure that the first three parameters are correct
                rectangle = Rectangle(xz_planar_centroid, size_z, size_x, rotation, size_y, name)

                # Add this instance to the rectangles list
                rectangles += [rectangle]

        return rectangles

    def _set_item_name_from(self, type_name, item_ix):
        """Set a name for an item from its type and index (e.g. if there are several walls)"""
        return f"{type_name} {item_ix}"


if __name__ == "__main__":
    config_path = "../example_configs/config.yaml"
    config_assistant = ConfigAssistant(config_path)
    print(config_assistant.physical_items)
    print("Exit ok")