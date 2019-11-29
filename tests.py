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

def test_app_run():
    app = App(__name__)
    app.run()

    assert app.data.date.dtype != str
    assert len(app.get_attributes()) >= 1
    assert len(list(app.results)) > 0

    app.save(app.results)

    assert os.path.exists(os.path.join(app.root, app.storage))
    assert len(os.listdir(os.path.join(app.root, app.storage))) > 1