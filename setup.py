from dfis import __version__
from setuptools import setup

long_description = ''
with open('./README.md') as f:
    long_description = f.read()

setup(name='dfis',
    version=__version__,
    description='Python package to help implement a demand forecastability inventory strategy.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/christopherpryer/python_dfis',
    author='Chris Pryer',
    author_email='christophpryer@gmail.com',
    license='PUBLIC',
    packages=['dfis'],
    zip_safe=False)