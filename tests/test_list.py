from nose.tools import with_setup, assert_raises
import requests
import requests_mock
from vault_tendril.main import Tendril
from configs_for_tests import VAULT_ADDR, VAULT_TOKEN
import json

def test_list_successful():
    with requests_mock.mock() as m:
        path = 'env/app/1'
        m.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text='{"data":{"keys":["one", "two"]}}', status_code=200)
        t = Tendril(vault_addr=VAULT_ADDR, vault_token=VAULT_TOKEN)
        (success, message) = t.list(path)
        print success, message
        assert success
        assert message == None
