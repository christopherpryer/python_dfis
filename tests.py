import os
import sys

from dfis import Config
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def test_config_init():
    config = Config(__name__)
    logging.info(config.to_dict())

    assert os.path.dirname(os.path.abspath(__name__)) == config.root

    assert not config.levels.empty
    assert not config.data.empty
    assert config.storage != ''