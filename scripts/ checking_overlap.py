from src.config_checker import ConfigChecker

# User-defined parameters
configuration_path = "../example_configs/config.yaml"

config_checker = ConfigChecker(configuration_path)
config_checker.check_overlap()
