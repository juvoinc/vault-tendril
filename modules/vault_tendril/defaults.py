"""Reasonable defaults are configured in this file"""

import os

DEFAULT_CONF_FILES = ['/etc/tendril.conf', '~/.tendril', './.tendril']

DEFAULT_CONF_SECTION_NAME = 'main'

CONFIG_DEFAULTS = {
    'force' : False,
    'log_level' : 'critical',
    'use_editor' : True,
    'use_socks' : False,
    'consul_addr' : 'http://localhost:8500',
    'consul_prefix' : 'lock',
    'consul_cert_path' : '',
    'vault_addr' : 'http://localhost:8200',
    'vault_prefix' : 'config',
    'vault_cert_path' : '',
    'socks_addr' : '',
    'format' : 'export',
    'version': ''
    }

ACTIONS = [
    'list',
    'history',
    'read',
    'write',
    'promote',
    'lock',
    'unlock',
    'readfiles',
    'writefiles'
    ]

for index, filename in enumerate(DEFAULT_CONF_FILES):
    DEFAULT_CONF_FILES[index] = os.path.expanduser(filename)
