# from distutils.core import setup
from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

setup(
    name='debsnapshot-cli',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/dimr/debsnapshot-cli',
    license='',
    author='Dimitris Rongotis',
    author_email='dimitris.rongotis@gmail.com',
    description='',
    install_requires=required,
    entry_points={
        'console_scripts': [
            'debsnapshot-cli=src.cli:main'
        ]
    }
    # scripts=['bin/debsnapshot-cli']

)
