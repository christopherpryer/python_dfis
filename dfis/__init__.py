import os
import sys

import pandas as pd
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class Config:
    def __init__(self, module):
        self.module = module # main.py or run.py __name__
        self.root = os.path.dirname(os.path.abspath(module))
        self.setup()

        if self.info.empty:
            logging.warn('levels, data, and storage need configuration: %s' % self.to_dict)
        elif len(self.info) > 1:
            logging.warn('only the first row was used in %s.' % config_name)

    @staticmethod
    def get_config_info(path):
        """takes path (directory); returns dataframe"""
        info_name = ''
        info_data = pd.DataFrame()
        if 'config.csv' in os.listdir(self.root):
            config_name = 'config.csv'
            info_data = pd.read_csv(os.path.join(path, info_name))
        elif 'testing_config.csv' in os.listdir(self.root):
            config_name = 'testing_config.csv'
            info_data = pd.read_csv(os.path.join(path, info_name))
        return info_data
        
    def setup(self):
        self.levels = pd.DataFrame() # algo config data
        self.data = pd.DataFrame() # input data
        self.storage = '' # path to storage directory
        self.info = self.get_config_info(self.root)

        if not self.info.empty:
            # currently expects everything to be relative to self.root.
            self.levels = pd.read_csv(os.path.join(self.root, self.info.levels.iloc[0]))
            self.data = pd.read_csv(os.path.join(self.root, self.info.data.iloc[0]))
            self.storage = os.path.join(self.root, self.info.storage.iloc[0])
            
    def to_dict(self):
        return {
            'root': self.root,
            'info': self.info.to_dict()
        }