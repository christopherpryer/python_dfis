import os

from dfis import Config

def test_config_init():
    config = Config(__name__)
    assert os.path.dirname(os.path.abspath(__name__)) == config.root