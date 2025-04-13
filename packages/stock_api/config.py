import os
import toml


def load_config(config_file: str = "config.toml") -> dict:
    base_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_path, "..")
    config_path = os.path.join(project_root, config_file)
    return toml.load(config_path)


config = load_config()
