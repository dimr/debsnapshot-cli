#from distutils.core import setup
from setuptools import setup,find_packages

setup(
    name='debsnapshot-cli',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/dimr/debsnapshot-cli',
    license='',
    author='Dimitris Rongotis',
    author_email='dimitris.rongotis@gmail.com',
    description='',
    entry_points={
        'console_scripts': [
            'debsnapshot-cli=src.cli:main'
        ]
    }
   # scripts=['bin/debsnapshot-cli']

)
