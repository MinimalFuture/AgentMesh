import yaml
import os

global_config = {}


def load_config():
    global global_config
    # Get config path from environment variable or use default path
    config_path = os.environ.get("CONFIG_PATH")

    if not config_path:
        # Default path as fallback
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../config.yaml'))

    # Check if config file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, 'r') as file:
        # Load the YAML content into global_config
        global_config = yaml.safe_load(file)


def config():
    return global_config
