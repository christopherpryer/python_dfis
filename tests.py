import os
import sys

from dfis import Config, App
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def check_instance(obj):
    logging.info(obj.info_to_dict())

    assert os.path.dirname(os.path.abspath(__name__)) == obj.root

    assert not obj.levels.empty
    assert not obj.data.empty
    assert obj.storage != ''

def test_config_init():
    config = Config(__name__)
    check_instance(config)

def test_app_init():
    app = App(__name__)
    check_instance(app)