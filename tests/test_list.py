from nose.tools import with_setup, assert_raises
import requests
import requests_mock
from vault_tendril.main import Tendril
from configs_for_tests import VAULT_ADDR, VAULT_TOKEN
import json

def test_list_successful():
    with requests_mock.mock() as m:
        path = 'env/app'
        m.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text='{"data":{"keys":["1", "__metadata", "__versions"]}}', status_code=200)
        m.get('%s/v1/%s/%s/__metadata' % (VAULT_ADDR, 'config', path), text='{"data":{"1":{"date":"2000-01-01 00:00:00", "user":"test"}}}', status_code=200)
        m.get('%s/v1/%s/%s/__versions' % (VAULT_ADDR, 'config', path), text='{"data":{"current":null, "versions":[1]}}', status_code=200)
        t = Tendril(vault_addr=VAULT_ADDR, vault_token=VAULT_TOKEN)
        (success, message) = t.list(path)
        assert success
        assert message == None
