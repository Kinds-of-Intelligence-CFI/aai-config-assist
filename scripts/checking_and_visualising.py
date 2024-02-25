from src.config_assistant import ConfigAssistant
import os

if __name__ == "__main__":
    # Change this path to the path to your configuration file (from the repository root)
    config_path = os.path.join("discard_competition", "09-15-01.yaml")
    config_assistant = ConfigAssistant(config_path)
    config_assistant.check_config_overlap()
    config_assistant.visualise_config()