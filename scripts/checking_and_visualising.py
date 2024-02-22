from src.config_assistant import ConfigAssistant

if __name__ == "__main__":
    # Change config_path to the path to your config.yaml file (path relative to this script)
    config_path = "../example_configs/config.yaml"

    config_assistant = ConfigAssistant(config_path)
    config_assistant.check_config_overlap()
    config_assistant.visualise_config()