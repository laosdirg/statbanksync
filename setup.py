from setuptools import setup

setup(name='statbanksync',
      version='0.1',
      description='Synchronize DST tables to local db',
      url='http://github.com/gisgroup/statbanksync',
      author='Gis Group ApS',
      author_email='oliver@gisgroup.dk, \
                    valentin@gisgroup.dk, \
                    zacharias@gisgroup.dk',
      license='MIT',
      packages=['statbanksync'],
      install_requires=[
          'gisgroup-statbank',
          'psycopg2',
          'blinker',
          'sqlalchemy',
          'apscheduler',
      ])
