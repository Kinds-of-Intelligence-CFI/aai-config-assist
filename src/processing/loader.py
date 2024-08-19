from typing import Dict

import yaml

from src.processing.arena_config_loader import ArenaConfigLoader


class Loader:
    @staticmethod
    def load_config_data(config_path: str) -> Dict:
        """Parses and loads the data from the YAML file inputted to class constructor.

        Args:
            config_path (str): Path to a YAML configuration file.

        Returns:
            (dict): The loaded data.
        """
        with open(config_path) as file:
            config_data = yaml.load(file, Loader=ArenaConfigLoader)
        return config_data
