import yaml

from src.arena_config_loader import ArenaConfigLoader


class Loader:
    @staticmethod
    def load_config_data(config_path):
        """Parses and loads the data from the YAML file inputted to class constructor.

        Args:
            config_path (str): Path to a YAML configuration file.

        Returns:
            (dict): The loaded data.
        """
        with open(config_path) as file:
            config_data = yaml.load(file, Loader=ArenaConfigLoader)
        return config_data

# TODO: could combine this class and the ArenaConfigLoader into the same python file OR could get rid of this file
#  altogether if it simply clutters the codebase. Either case must resolve the conflict, and the naming clashes
