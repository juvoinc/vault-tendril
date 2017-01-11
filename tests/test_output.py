from nose.tools import with_setup, assert_raises
import requests
import requests_mock
from vault_tendril.main import Tendril
from configs_for_tests import VAULT_ADDR, VAULT_TOKEN
import json

def test_write_successful():
    with requests_mock.mock() as m:
        path = 'env/app'
        m.get('%s/v1/%s/%s/__metadata' % (VAULT_ADDR, 'config', path), text='{}', status_code=200)
        m.post('%s/v1/%s/%s/%s' % (VAULT_ADDR, 'config', path, '1'), status_code=204)
        m.post('%s/v1/%s/%s/__metadata' % (VAULT_ADDR, 'config', path), status_code=204)
        t = Tendril(vault_addr=VAULT_ADDR, vault_token=VAULT_TOKEN, use_editor=False, force=True)
        (success, message) = t.write(path, data={"one":"two"})
        assert ' UTC version 1 created by ' in message
def test_read_successful():
    with requests_mock.mock() as m:
        path = 'env/app'
        m.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text='{"data":{"keys":["1", "2", "3", "__metadata"]}}', status_code=200)
        m.get('%s/v1/%s/%s/__metadata' % (VAULT_ADDR, 'config', path), text='{"data":{"current":"3","versions":["1","2","3"],"history":[{"version":"1","action":"created","date":"2000-01-0100:00:00","user":"test"},{"version":"1","action":"current","date":"2000-01-0100:01:00","user":"test"},{"user":"test","date":"2000-01-0100:02:00","version":"2","action":"created"},{"user":"test","version":"2","action":"current","date":"2000-01-0100:03:00"},{"action":"created","version":"3","date":"2000-01-0100:04:00","user":"test"},{"version":"3","date":"2000-01-0100:05:00","action":"current","user":"test"}]}}', status_code=200)
        m.get('%s/v1/%s/%s/3' % (VAULT_ADDR, 'config', path), text='{"data":{"one":"two"}}', status_code=200)
        t = Tendril(vault_addr=VAULT_ADDR, vault_token=VAULT_TOKEN, use_editor=False, force=True)
        (success, message) = t.read("%s/3" % path)
        assert success       
        data = json.loads(message)
        assert data['one'] == 'two'
