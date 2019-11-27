import os

class Config:
    def __init__(self, module):
        self.module = module
        self.root = os.path.dirname(os.path.abspath(module))
