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
          'configparser>=3.5.0',
          'pyyaml>=3.12',
          'requests>=2.12.4'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
     )
