import sys
import random
import os
import yaml
from arena_config_loader import ArenaConfigLoader


class ConfigChecker:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config_data = self._load_config_data()

    def check_overlap(self):
        """Checks whether objects overlap in the YAML configuration"""
        pass

    def _load_config_data(self):
        """Returns the loaded data from the YAML configuration"""
        with open(self.config_path) as file:
            config_data = yaml.load(file, Loader=ArenaConfigLoader)
        return config_data


if __name__ == "__main__":
    config_checker = ConfigChecker(config_path="example_configs/config.yaml")
    print(config_checker.config_data)
    print("Exit ok")