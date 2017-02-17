"""These are helper functions for parsing command line arguments and
config files"""

import os
import sys
import argparse
import configparser
import logging
from vault_tendril.defaults import DEFAULT_CONF_FILES
from vault_tendril.defaults import CONFIG_DEFAULTS
from vault_tendril.defaults import DEFAULT_CONF_SECTION_NAME
from vault_tendril.defaults import ACTIONS


def load_arguments():
    """Parse the command line for frequently changed arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true', default=False,
                        help='This will send logs to STDERR')
    parser.add_argument('--conf', nargs='+', default=DEFAULT_CONF_FILES)
    parser.add_argument('action', choices=ACTIONS)
    parser.add_argument('path', nargs='?', default='')
    parser.add_argument('--account', '-a', default=os.getenv('TENDRIL_ACCOUNT', DEFAULT_CONF_SECTION_NAME))
    parser.add_argument('--format', choices=['export', 'json', 'yaml', 'raw'], dest='format')
    parser.add_argument('--force', action='store_true', default=False)
    parser.add_argument('--no-edit', action='store_false', default=True, dest='use_editor')
    return parser.parse_args()


def load_configs():
    """Load in configurations from one or more files"""
    args = load_arguments()
    config = configparser.ConfigParser()
    config['DEFAULT'] = CONFIG_DEFAULTS
    config.read(args.conf)
    if DEFAULT_CONF_SECTION_NAME not in config:
        config[DEFAULT_CONF_SECTION_NAME] = {}
    (okay, problems) = check_config(config[args.account])
    if not okay:
        logging.critical("%s", problems)
        sys.exit(1)
    return set_defaults(args, config[args.account])


def set_defaults(args, config):
    """Apply command line arguments to the config when applicable"""
    for key in vars(args):
        value = getattr(args, key)
        if value is not None:
            config[key] = str(value)
    return config


def check_config(config):
    """Check configuration requirements"""
    problems = []
    for k in ['vault_token']:
        if k not in config:
            problems.append("No variable %s found in config file" % k)
    if len(problems) > 0:
        return (False, problems)
    return (True, None)
