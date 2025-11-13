import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

from proct_olis.core.config import JsonTemplate

import yaml

@dataclass
class Settings:
    settings_file: str = "settings.yml"
    BASE_DIR: Path = field(default=Path(__file__).resolve().parent, init=False)
    settings: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        self.setting_path = os.path.join(self.BASE_DIR, self.settings_file)
        self.load_settings()
        self.replace_placeholders()

    def load_settings(self):
        try:
            with open(self.setting_path, 'r') as f:
                self.settings = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Settings file not found at {self.setting_path}. Using empty settings.")
            self.settings = {}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing the settings file: {e}")
    
    def replace_placeholders(self):
        load_dotenv()
        config = {
            "minio_endpoint": os.getenv("MINIO_ENDPOINT"),
            "minio_access_key": os.getenv("MINIO_ACCESS_KEY"),
            "minio_secret_key": os.getenv("MINIO_SECRET_KEY"),
            "postgres_host": os.getenv("POSTGRES_HOST"),
            "postgres_port": os.getenv("POSTGRES_PORT"),
            "postgres_database": os.getenv("POSTGRES_DATABASE"),
            "postgres_user": os.getenv("POSTGRES_USER"),
            "postgres_password": os.getenv("POSTGRES_PASSWORD"),
            "postgres_dw_host": os.getenv("POSTGRES_DW_HOST"),
            "postgres_dw_port": os.getenv("POSTGRES_DW_PORT"),
            "postgres_dw_database": os.getenv("POSTGRES_DW_DATABASE"),
            "postgres_dw_user": os.getenv("POSTGRES_DW_USER"),
            "postgres_dw_password": os.getenv("POSTGRES_DW_PASSWORD"),
        }
        for key, value in self.settings.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    new_value = JsonTemplate(str(sub_value)).safe_substitute(config)
                    self.settings[key][sub_key] = new_value
            else:
                self.settings[key] = JsonTemplate(str(value)).safe_substitute(config)

    def get(self, key: str, default=None):
        return self.settings.get(key, default)