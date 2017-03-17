#!/usr/bin/env python

from setuptools import setup

setup(name='vault_tendril',
      version='1.0',
      description='Key/Value Configuration Management Tool with a Hashicorp Vault backend',
      author='Pete Emerson',
      author_email='pete@juvo.com',
      url='https://github.com/juvoinc/vault-tendril',
      package_dir = {'': 'modules'},
      packages=['vault_tendril'],
      scripts=['tendril'],
      install_requires=[
        'appdirs>=1.4.3',
        'configparser>=3.5.0',
        'packaging>=16.8',
        'pyparsing>=2.2.0',
        'PySocks>=1.6.6',
        'PyYAML>=3.12',
        'requests>=2.13.0',
        'six>=1.10.0
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
     )


