#!/usr/bin/python
from setuptools import setup

setup(
    name='vse-viprshell',
    version='1.0',
    packages=['ViPRShell',
              'ViPRShell.bin',
              'ViPRShell.config'],
    package_data={
        #Include python and .ini files
        'ViPRShell.config': ['*.ini']
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
        'License :: Other/Proprietary License',

    ],
    license='EMC Corp',
    description='ViPR Shell'
)
