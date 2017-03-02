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
    parser.add_argument('--account', '-a', default=os.getenv(
        'TENDRIL_ACCOUNT', DEFAULT_CONF_SECTION_NAME))

    subparsers = parser.add_subparsers()
    for action in ACTIONS:
        subparser = subparsers.add_parser(action)
        subparser.set_defaults(action=action)
        if action == 'list':
            subparser.add_argument('path', nargs='?', default='')
        else:
            subparser.add_argument('path', default='')
        if action == 'read':
            subparser.add_argument('--format', choices=[
                'export', 'json', 'yaml', 'raw'], dest='format')
        if action == 'write':
            subparser.add_argument('--force', action='store_true',
                                   default=False)
            subparser.add_argument('--no-edit', action='store_false',
                                   default=True, dest='use_editor')
        if action == 'readfiles':
            subparser.add_argument('destination', nargs='?', default='.')
        if action == 'writefiles':
            subparser.add_argument('files', nargs='+')
    return parser.parse_args()

def load_configs():
    """Load in configurations from one or more files"""
    args = load_arguments()
    config = configparser.ConfigParser()
    config['DEFAULT'] = CONFIG_DEFAULTS
    config.read(args.conf)
    if DEFAULT_CONF_SECTION_NAME not in config:
        config[DEFAULT_CONF_SECTION_NAME] = {}
    if args.account in config:
        (okay, problems) = check_config(config[args.account])
    else:
        okay = False
        accounts = []
        for account in config:
            accounts.append(account)
        accounts.sort()
        problems = '%s is not a valid account in your config files, valid accounts are: %s' % (
            args.account, ', '.join(accounts))
    if not okay:
        logging.critical("%s", problems)
        sys.exit(1)
    return set_defaults(args, config[args.account])


def set_defaults(args, config):
    """Apply command line arguments to the config when applicable"""
    for key in vars(args):
        value = getattr(args, key)
        if value is not None:
            if isinstance(value, list):
                config[key] = str(','.join(value))
            else:
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
