#!/usr/bin/python
from setuptools import setup

setup(
    name='viprshell',
    version='15.7',
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
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',

    ],
    license='MPL 2.0 ',
    description='ViPR Shell',
)
