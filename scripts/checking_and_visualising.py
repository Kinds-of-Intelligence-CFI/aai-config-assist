from src.config_assistant import ConfigAssistant

if __name__ == "__main__":
    # Change this path to the path to your configuration file (from this repository's root dir "aai-config-assist")
    config_path = "example_configs/config.yaml"
    config_assistant = ConfigAssistant(config_path)
    config_assistant.check_config_overlap()
    config_assistant.visualise_config()
