# config_manager.py

import os
import yaml

class Config_Manager:
    """
    Loads and stores project-wide configuration from a YAML file.
    You can extend it to merge environment variables or a default config.
    """

    def __init__(self, config_path: str = "config.yaml"):
        """
        :param config_path: Path to the YAML configuration file.
        """
        self.config_path = config_path
        self.config = {}
        self.load_config()

    def load_config(self):
        """
        Loads or reloads the YAML config into self.config.
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as file:
            self.config = yaml.safe_load(file) or {}
    
    def get(self, key: str, default=None):
        """
        Retrieves a configuration value by key, or returns default if not found.
        Supports nested keys separated by '.', e.g. 'logging.level'.
        """
        keys = key.split(".")
        val = self.config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val
