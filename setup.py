#!/usr/bin/python
from setuptools import setup

setup(
    name='viprcommand',
    version='15.8',
    packages=['ViPRCommand',
              'ViPRCommand.bin',
              'ViPRCommand.config'],
    package_data={
        'ViPRCommand.config': ['*.ini']
    },
    install_requires=[
        'requests',
        'configparser'
    ],
    url='',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[

        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Application Frameworks',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

    ],
    license='MIT',
    description='ViPR Command',
)
