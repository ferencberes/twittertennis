from setuptools import find_packages, setup

install_requires = [
    'pandas',
    'datetime',
    'pytz',
    'matplotlib',
    'seaborn'
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

setup(name='twittertennis',
      version='0.1.1',
      description='Utility packages for data Twitter tennis tournaments data.',
      url='https://github.com/ferencberes/twittertennis',
      author='Ferenc Beres',
      author_email='fberes@info.ilab.sztaki.hu',
      packages = find_packages(),
      install_requires=install_requires,
      setup_requires = setup_requires,
      tests_require = tests_require,
      keywords = keywords,
      python_requires = '>=3.5',
)
