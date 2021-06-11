from setuptools import find_packages, setup

install_requires = [
    'networkx',
    'pandas',
    'datetime',
    'pytz',
    'matplotlib',
    'seaborn',
    'tqdm',
]

setup_requires = ['pytest-runner']

tests_require = [
    'pytest',
    'pytest-cov',
    'codecov'
]

keywords = [
    "graph",
    "dynamic graph",
    "temporal network",
    "mention graph",
    "twitter"
]

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='twittertennis',
      version='0.1.2',
      description='Utility packages for Twitter tennis tournaments data sets.',
      url='https://github.com/ferencberes/twittertennis',
      author='Ferenc Beres',
      author_email='fberes@info.ilab.sztaki.hu',
      packages = find_packages(),
      install_requires=install_requires,
      setup_requires = setup_requires,
      tests_require = tests_require,
      keywords = keywords,
      long_description=long_description,
      long_description_content_type='text/markdown',
      python_requires = '>=3.6',
)
