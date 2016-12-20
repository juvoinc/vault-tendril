"""Reasonable defaults are configured in this file"""

DEFAULT_CONF_FILES = ['/etc/tendril.conf', '~/.tendril', './.tendril']
DEFAULT_CONF_SECTION_NAME = 'main'

CONFIG_DEFAULTS = {
    'log_level' : 'critical',
    'use_socks' : False,
    'vault_addr' : 'http://localhost:8200',
    'vault_prefix' : 'config',
    'vault_cert_path' : '',
    'socks_addr' : '',
    'output_format' : 'export',
    'version': ''
    }

ACTIONS = [
    'list',
    'read',
    'write',
    'promote'
    ]
