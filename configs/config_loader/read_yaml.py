from pathlib import Path

import yaml

from configs.config_loader.config_interface import ConfigReaderInterface
from configs.config_loader.serializer import Struct

class YamlConfigReader(ConfigReaderInterface):

    def __init__(self):
        super(YamlConfigReader, self).__init__()

    def read_config_from_file(self, config_path: str):
        with open(config_path) as file:
            config = yaml.safe_load(file)
        # config_object = Struct(**config)
        return config
