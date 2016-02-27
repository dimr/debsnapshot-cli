# from distutils.core import setup
from setuptools import setup, find_packages
import re

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

# taken from https://github.com/kennethreitz/requests/blob/master/setup.py
version = ''
with open('src/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='debsnapshot-cli',
    version=version,
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
