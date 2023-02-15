import os
from singleton import MetaSingleton
from configloader import ConfigLoader

config_abs_path = "/".join(os.path.abspath(__file__).split("/")[0:-1])


class Config(metaclass=MetaSingleton):
    def __init__(self, config_file_path=f"{config_abs_path}/config.yml"):
        self.config_loader = ConfigLoader()
        self.config_loader.update_from_yaml_file(config_file_path)
        self.config_loader.update_from_env_namespace("DATA_PROCESSOR")

    def get(self, setting_name):
        return self.config_loader.get(setting_name, None)

    def to_dict(self):
        loader = self.config_loader
        return {key: loader.get(key) for key in loader.keys()}


LOGGING_LEVEL = "LOGGING_LEVEL"
LOGGING_FORMAT = "LOGGING_FORMAT"
KAFKA_BROKER = "KAFKA_BROKER"
SOURCE_CRAWLER_REQUEST_TOPIC = "SOURCE_CRAWLER_REQUEST_TOPIC"
PRODUCE_CRAWLER_STATUS_TOPIC = "PRODUCE_CRAWLER_STATUS_TOPIC"
PROMETHEUS_PORT = "PROMETHEUS_PORT"
URL_CACHE_TABLE_NAME = "URL_CACHE_TABLE_NAME"
CACHE_MAX_AGE_DAYS = "CACHE_MAX_AGE_DAYS"
SERVICE_NAME = "SERVICE_NAME"
