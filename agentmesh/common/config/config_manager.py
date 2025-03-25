import yaml
import os

global_config = {}


def load_config():
    global global_config
    # Get the absolute path to the config.yaml file
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../config.yaml'))  # Adjust the path
    with open(config_path, 'r') as file:  
        # Load the YAML content into global_config
        global_config = yaml.safe_load(file)


def config():
    return global_config
