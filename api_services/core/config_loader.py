import os
from core.singleton import MetaSingleton
from configloader import ConfigLoader

config_abs_path = "/".join(os.path.abspath(__file__).split("/")[0:-1])


class Config(metaclass=MetaSingleton):
    def __init__(
        self, env_namespace="", config_file_path=f"{config_abs_path}/config.yml"
    ):
        self.config_loader = ConfigLoader()
        self.config_loader.update_from_yaml_file(config_file_path)
        self.config_loader.update_from_env_namespace(env_namespace)

    def get(self, setting_name):
        return self.config_loader.get(setting_name, None)

    def to_dict(self):
        loader = self.config_loader
        return {key: loader.get(key) for key in loader.keys()}


LOGGING_LEVEL = "LOGGING_LEVEL"
LOGGING_FORMAT = "LOGGING_FORMAT"
WEB_HOST = "WEB_HOST"
WEB_PORT = "WEB_PORT"
DB_URI = "DB_URI"
KAFKA_BROKER = "KAFKA_BROKER"
CRAWLER_REQUEST_TOPIC = "CRAWLER_REQUEST_TOPIC"
CRAWLER_STATUS_TOPIC = "CRAWLER_STATUS_TOPIC"
CONSUMER_GROUP_ID = "CONSUMER_GROUP_ID"
