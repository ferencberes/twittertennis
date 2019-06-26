from distutils.core import setup

setup(name='twittertennis',
      version='0.1',
      description='Utility packages for data Twitter tennis tournaments data.',
      url='',
      author='Ferenc Beres',
      author_email='fberes@info.ilab.sztaki.hu',
      packages=['twittertennis'],
      install_requires=[
          'pandas',
          'datetime',
          'pytz'
      ],
zip_safe=False)