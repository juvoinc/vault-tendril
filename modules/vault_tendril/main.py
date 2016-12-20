"""The tendril class"""

#from __future__ import print_function
#import logging
import getpass
import os
import sys
import json
import select
import time
import datetime
import yaml
import requests

class Tendril(object):
    """This class does all of the heavy lifting for tendril, including
    the raw reads and writes to the vault database and the logic for read /
    write / list."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments

    def __init__(self,
                 vault_token=None,
                 vault_addr='http://localhost:8200',
                 vault_prefix='config',
                 vault_cert_path=None,
                 use_socks=False,
                 socks_addr=None,
                 output_format=None,
                 version=None
                ):
        self.vault_addr = vault_addr
        self.vault_prefix = vault_prefix
        self.vault_cert_path = vault_cert_path
        if vault_cert_path is not None:
            self.vault_cert_path = os.path.expanduser(vault_cert_path)
        if use_socks == "yes":
            self.proxies = {
                'http': socks_addr,
                'https': socks_addr
            }
        else:
            self.proxies = None
        self.use_socks = use_socks
        self.output_format = output_format
        self.version = version
        self.headers = {'X-Vault-Token': vault_token}

    def _write_data(self, path, data):
        try:
            response = requests.post(
                '%s/v1/%s/%s' % (self.vault_addr, self.vault_prefix, path),
                json=data, headers=self.headers)
        except requests.exceptions.ConnectionError, error:
            return False, str(error)
        if response.status_code == 204:
            return True, None
        elif response.status_code == 400:
            return False, "Permission denied"
        return False, "Unknown error"

    def _read_data(self, path):
        try:
            response = requests.get(
                '%s/v1/%s/%s' % (self.vault_addr, self.vault_prefix, path),
                headers=self.headers, verify=self.vault_cert_path)
        except requests.exceptions.ConnectionError, error:
            return False, str(error)
        if response.status_code == 200:
            if 'data' in response.json():
                return True, response.json()['data']
            else:
                return False, "No data returned"
        elif response.status_code == 404:
            return False, "No data found at %s" % path
        elif response.status_code == 400:
            return False, "Permission denied"
        return False, "Unknown error"

    def _list_path(self, path):

        # pylint: disable=too-many-return-statements

        try:
            response = requests.get(
                '%s/v1/%s/%s?list=true' % (self.vault_addr, self.vault_prefix, path),
                headers=self.headers, verify=self.vault_cert_path, proxies=self.proxies)
        except requests.exceptions.ConnectionError, error:
            return False, str(error)
        if response.status_code == 200:
            if 'data' in response.json():
                if 'keys' in response.json()['data']:
                    return True, response.json()['data']['keys']
                else:
                    return False, "No keys in data"
            else:
                return False, "No data in response"
        elif response.status_code == 404:
            if path == '':
                return False, 'No keys found'
            return False, "No keys found at %s" % path
        elif response.status_code == 400:
            return False, "Permission denied"
        return False, "Unknown error"

    def list(self, path):
        """Given a path this will list the next available branches in the path,
        or if the path has versions available (i.e. the path has no sub-paths
        except for versions) then it will show the available versions along
        with available metadata"""
        path = path.lstrip('/').rstrip('/')
        (success, response) = self._list_path(path)
        if not success:
            return False, response
        (success, metadata) = self._read_data('%s/__metadata' % (path))
        if success:
            if '__versions' in response:
                (success, response) = self._read_data('%s/__versions' % path)
                for version in response['versions']:
                    if 'current' in response and version == response['current']:
                        print "%s by %s on %s (current)" % (
                            version, metadata[str(version)]['user'], metadata[str(version)]['date'])
                    else:
                        print "%s by %s on %s" % (
                            version, metadata[str(version)]['user'], metadata[str(version)]['date'])
            else:
                for k in response:
                    if path == '':
                        print k
                    else:
                        print "%s/%s" % (path, k)
        else:
            return False, "No metadata found"
        return True, None

    def write(self, path, raw_data=None):
        """Given a path this will write the raw_data (either passed in or from
        STDIN) to vault, computing the appropriate version."""
        path = path.lstrip('/').rstrip('/')
        last = path.split('/')[-1]
        try:
            int(last)
            return False, "Cannot save to a specific version"
        except ValueError:
            (success, versions) = self._read_data('%s/__versions' % path)
        if success:
            next_version = int(versions['versions'][-1]) + 1
            versions['versions'].append(next_version)
        else:
            next_version = 1
            versions = {"current":None, "versions":[next_version]}
        if raw_data is None:
            if select.select([sys.stdin,], [], [], 0.0)[0]:
                raw_data = sys.stdin.read()
            else:
                return False, "No data supplied to STDIN"
        try:
            data = json.loads(raw_data)
        except ValueError:
            try:
                data = yaml.load(raw_data)
            except yaml.scanner.ScannerError:
                return False, "Data is neither JSON nor YAML"
        (success, response) = self._write_data('%s/%s' % (path, next_version), data)
        if success:
            (success, response) = self._write_data('%s/%s' % (path, '__versions'), versions)
        if success:
            (success, metadata) = self._read_data('%s/__metadata' % path)
            if not success:
                metadata = {}
            metadata[next_version] = {}
            metadata[next_version]['date'] = datetime.datetime.fromtimestamp(
                time.time()).strftime('%Y-%m-%d %H:%M:%S')
            metadata[next_version]['user'] = getpass.getuser()
            (success, response) = self._write_data('%s/%s' % (path, '__metadata'), metadata)
        return success, response

    def read(self, full_path):
        """Given a path this will read the key/value pairs from vault and
        present them to the user in the desired format. If the path does not
        have a version, the current version will be pulled from vault and used.
        If there is no current version, a list of available options will be
        provided instead of the key/value pairs."""
        full_path = full_path.lstrip('/').rstrip('/')
        try:
            version = full_path.split('/')[-1]
            path = '/'.join(full_path.split('/')[:-1])
            int(version)
            (success, response) = self._read_data('%s/%s' % (path, version))
        except ValueError:
            (success, response) = self._read_data('%s/__versions' % full_path)
            if 'current' in response and response['current'] is not None:
                version = response['current']
                (success, response) = self._read_data('%s/%s' % (full_path, version))
            else:
                if isinstance(response, dict):
                    if 'versions' in response:
                        print "Available versions are:"
                        for version in response['versions']:
                            print version
                        success = False
                        response = None
        if success:
            if self.output_format == 'export':
                for key in sorted(response):
                    print "export %s=\"%s\"" % (key, response[key])
            elif self.output_format == 'json':
                print json.dumps(response, indent=2)
            elif self.output_format == 'yaml':
                print '---'
                print yaml.safe_dump(response, default_flow_style=False),
            return True, None
        return success, response

    def promote(self, full_path):
        """This will promote a given path to mark it as 'current'. The path must
        end with a version number or an errro will be returned."""
        full_path = full_path.lstrip('/').rstrip('/')

        version = full_path.split('/')[-1]
        path = '/'.join(full_path.split('/')[:-1])
        (success, versions) = self._read_data('%s/__versions' % path)
        if success:
            if int(version) in versions['versions']:
                if int(version) != versions['current']:
                    versions['current'] = int(version)
                    (success, response) = self._write_data('%s/__versions' % path, versions)
                    return success, response
                else:
                    return False, "%s is already current" % version
            else:
                return False, "%s is not in %s" % (version, versions['versions'])
        else:
            return False, "Error: %s" % versions
