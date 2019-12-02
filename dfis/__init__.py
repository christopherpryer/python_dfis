import os
import sys

import pandas as pd
import numpy as np
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

__version__ = 'v1'

class Config:
    def __init__(self, module):
        self.module = module # main.py or run.py __name__
        self.root = os.path.dirname(os.path.abspath(module))
        self.setup()

        if self.info.empty:
            logging.warning('levels, data, and storage need configuration: %s.' % self.info_to_dict())
        elif len(self.info) > 1:
            logging.warning('only the first row was used in %s.' % config_name)

    @staticmethod
    def get_config_info(path):
        """takes path (directory); returns dataframe"""
        info_name = ''
        infodata = pd.DataFrame()
        if 'config.csv' in os.listdir(path):
            info_name = 'config.csv'
            infodata = pd.read_csv(os.path.join(path, info_name))
        elif 'testing_config.csv' in os.listdir(path):
            info_name = 'testing_config.csv'
            infodata = pd.read_csv(os.path.join(path, info_name))
        return infodata
        
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
            
    def info_to_dict(self):
        return {
            'root': self.root,
            'info': self.info.to_dict()
        }

class App(Config):
    def __init__(self, module):
        Config.__init__(self, module)

    @staticmethod
    def process_datetime(series):
        return pd.to_datetime(series, infer_datetime_format=True, errors='coerce')

    @staticmethod
    def get_population_stats(df, attributes, num_col='quantity'):
        """
        population == attributes group; returns resulting dataframe concat
        - sum
        - count
        - 𝐶𝑉2=(𝜎𝑝/𝜇𝑝)2

        𝜎𝑝: standard deviation of population
        𝜇𝑝: average of population
        𝐶𝑉2: coefficient of variation
        """
        aggfunc = {num_col: ['std', 'mean', 'count', 'sum']}
        _types = {col: str for col in attributes}
        result = df.astype(_types).groupby(attributes).agg(aggfunc)
        cv2 = ((result[(num_col, 'std')] / result[(num_col, 'mean')]) ** 2).rename('cv2')
        sums = result[(num_col, 'sum')].rename('quantity')
        counts = result[(num_col, 'count')].rename('counts')
        return pd.concat([cv2, sums, counts], axis=1)

    @staticmethod
    def get_period_df(df, period_type, date_col='date', numeric_col='quantity'):
        _cols = [col for col in df.columns if col not in [date_col, numeric_col]]
        _types = {col: str for col in _cols}
        return df.astype(_types).groupby(_cols + [pd.Grouper(key=date_col, freq=period_type)])\
            [numeric_col].sum().reset_index()

    @staticmethod
    def get_period_stats(df, attributes, period_type, n_periods):
        """
        period == period_type group; returns resulting dataframe concat
        - buckets (count of periods with demand)
        - 𝐴𝐷𝐼=𝑝𝑛/𝑑𝑛

        𝑝𝑛 : number of periods
        𝑑𝑛 : number of demand buckets
        𝐴𝐷𝐼 : Average Demand Interval
        """
        buckets = App.get_period_df(df, period_type).groupby(attributes).size().rename('buckets')
        adi = (n_periods / buckets).rename('adi')
        return pd.concat([adi, buckets], axis=1)
    
    @staticmethod
    def classify(data):
        data['classification'] = np.nan
        is_intermittent = (data.adi >= 1.32) & (data.cv2 < 0.49)
        is_lumpy = (data.adi >= 1.32) & (data.cv2 >= 0.49)
        is_smooth = (data.adi < 1.32) & (data.cv2 < 0.49)
        is_erratic = (data.adi < 1.32) & (data.cv2 >= 0.49)
        is_ext_slow = (data.buckets <= 3) | (data.cv2.isna())
        data.loc[is_intermittent, 'classification'] = 'intermittent'
        data.loc[is_lumpy, 'classification'] = 'lumpy'
        data.loc[is_smooth, 'classification'] = 'smooth'
        data.loc[is_erratic, 'classification'] = 'erratic'
        data.loc[data.cv2 >= 25, 'classification'] = 'extremely variable'
        data.loc[is_ext_slow, 'classification'] = 'extremely slow'
        return data

    def get_attributes(self):
        attributes = []
        for i in range(len(self.levels)):
            attributes.append(self.levels.attributes.iloc[i].split('+'))
        return attributes

    def run(self):
        logging.info('processing dates.')
        self.data.date = self.process_datetime(self.data.date)

        # run per level defined
        self.results = {}
        attributes = self.get_attributes()
        for i, attrs in enumerate(attributes):
            logging.info('running level %s: %s.' % (i, attrs))
            pop_stats = self.get_population_stats(self.data, attrs, 'quantity')
            period_stats = self.get_period_stats(
                self.data, attrs, self.levels.period_type.iloc[i], self.levels.n_periods.iloc[i])
            result = pd.concat([pop_stats, period_stats], axis=1)
            self.results[i] = {
                'data': self.classify(result),
                'info': self.levels.iloc[i].to_dict()
            }

    def save(self, results):
        if len(results) == 0:
            logging.warning('no result data found. %s' % results)
        
        for r in results:
            if not results[r]['data'].empty:
                filename = '%s.csv' % '_'.join([str(v) for v in results[r]['info'].values()])
                filepath = os.path.join(self.root, self.storage, filename)
                results[r]['data'].to_csv(filepath)
        logging.info('completed save to %s.' % filepath)