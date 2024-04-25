from src.app.app_manager import AppManager


def main():
    # Change this path to the path to your configuration file (from this repository's root dir "aai-config-assist")
    config_path = "example_configs/config.yaml"
    app_manager = AppManager(config_path)
    app_manager.run_app()


if __name__ == "__main__":
    main()
