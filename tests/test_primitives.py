from nose.tools import with_setup, assert_raises
import requests
import requests_mock
from vault_tendril.main import Tendril
from configs_for_tests import CONSUL_ADDR, CONSUL_TOKEN, VAULT_ADDR, VAULT_TOKEN
import json

CONSUL_HEADERS = {'X-Consul-Token': CONSUL_TOKEN}
VAULT_HEADERS = {'X-Vault-Token': VAULT_TOKEN}

def test_successful_write():
    with requests_mock.mock() as m:
        path = 'env/app/1'
        m.post('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=204)
        m.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text='{"data":{"one":"first","two":"second"}}', status_code=200)
        t = Tendril(vault_token=VAULT_TOKEN)
        success, message = t._write_data(path, {"one":"first","two":"second"})
        assert success
        assert message == None
        r = requests.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), headers=VAULT_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert 'data' in data
        assert len(data['data']) == 2
        assert 'one' in data['data']
        assert data['data']['one'] == 'first'
        assert 'two' in data['data']
        assert data['data']['two'] == 'second'

def test_successful_read():
    path = 'env/app/1'
    with requests_mock.mock() as m:
        path = 'env/app/1'
        m.post('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=204)
        m.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text='{"data":{"one":"first","two":"second"}}', status_code=200)
        t = Tendril(vault_token=VAULT_TOKEN)
        success, message = t._write_data(path, {"one":"first","two":"second"})
        assert success
        assert message == None
        success, data = t._read_data(path)
        assert success
        assert len(data) == 2
        assert 'one' in data
        assert data['one'] == 'first'
        assert 'two' in data
        assert data['two'] == 'second'

def test_bad_token_write():
    path = 'env/app/1'
    with requests_mock.mock() as m:
        path = 'env/app/1'
        m.post('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=400)
        t = Tendril(vault_token='00000000-0000-0000-0000-000000000000')
        success, message = t._write_data(path, {"one":"first","two":"second"})
        assert success == False
        assert message == "Permission denied"

def test_missing_data_read():
    with requests_mock.mock() as m:
        path = 'env/app/1'
        m.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=404)
        t = Tendril(vault_token=VAULT_TOKEN)
        success, data = t._read_data(path)
        assert not success
        assert data == "No data found at %s" % path

def test_bad_token_read():
    with requests_mock.mock() as m:
        path = 'env/app/1'
        m.post('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=204)
        m.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=400)
        path = 'env/app/1'
        t = Tendril(vault_token=VAULT_TOKEN)
        success, message = t._write_data(path, {"one":"first","two":"second"})
        assert success
        assert message == None
        t = Tendril(vault_token='00000000-0000-0000-0000-000000000000')
        success, data = t._read_data(path)
        assert not success
        assert data == "Permission denied"

def test_bad_vault_host_write():
    path = 'env/app/1'
    t = Tendril(vault_addr='http://localhost:8201', vault_token=VAULT_TOKEN)
    success, message = t._write_data(path, {"one":"first","two":"second"})
    assert not success
    assert "Failed to establish a new connection: [Errno 61] Connection refused" in message

def test_bad_vault_host_read():
    path = 'env/app/1'
    t = Tendril(vault_addr='http://localhost:8201', vault_token=VAULT_TOKEN)
    success, data = t._read_data(path)
    assert not success
    assert "Failed to establish a new connection: [Errno 61] Connection refused" in data

def test_successful_path_read():
    with requests_mock.mock() as m:
        path = 'env/app/1'
        m.post('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=204)
        path = 'env2/app2/1'
        m.post('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=204)
        path = 'raw'
        m.post('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=204)
        # m.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), text=None, status_code=400)
        path = ''
        m.get('%s/v1/%s/%s?list=true' % (VAULT_ADDR, 'config', path), text='{"data":{"keys":["env/","env2/","raw"]}}', status_code=200)

        t = Tendril(vault_token=VAULT_TOKEN)
        path = 'env/app/1'
        success, message = t._write_data('env/app/1', {"one":"first","two":"second"})
        assert success
        assert message == None
        success, message = t._write_data('env2/app2/1', {"one":"first","two":"second"})
        assert success
        assert message == None
        success, message = t._write_data('raw', {"one":"first","two":"second"})
        assert success
        assert message == None
        success, data = t._list_path('')
        assert len(data) == 3
        assert success
        assert 'env/' in data
        assert 'env2/' in data
        assert 'raw' in data

def test_missing_path_read():
    with requests_mock.mock() as m:
        path = 'foo'
        m.get('%s/v1/%s/%s?list=true' % (VAULT_ADDR, 'config', path), text=None, status_code=404)
        t = Tendril(vault_token=VAULT_TOKEN)
        success, data = t._list_path(path)
        assert not success
        assert data == "No keys found at %s" % path

def test_bad_token_list():
    with requests_mock.mock() as m:
        path = 'env/app/1'
        m.get('%s/v1/%s/%s?list=true' % (VAULT_ADDR, 'config', path), text=None, status_code=400)
        t = Tendril()
        success, data = t._list_path(path)
        assert not success
        assert data == "Permission denied"

def test_lock():
    with requests_mock.mock() as m:
        path = 'env/app/1'
        m.put('%s/v1/session/create' % CONSUL_ADDR, text='{"ID": "4cc1e37d-53cc-0d61-3985-0e0d9eff457d"}', status_code=200)
        m.put('%s/v1/session/renew/%s' % (CONSUL_ADDR, "4cc1e37d-53cc-0d61-3985-0e0d9eff457d"), text='[{"ID": "4cc1e37d-53cc-0d61-3985-0e0d9eff457d"}]', status_code=200)
        m.put('%s/v1/kv/lock/%s?acquire=%s' % (CONSUL_ADDR, path, '4cc1e37d-53cc-0d61-3985-0e0d9eff457d'), text="true", status_code=200)
        m.put('%s/v1/kv/lock/%s?release=%s' % (CONSUL_ADDR, path, '4cc1e37d-53cc-0d61-3985-0e0d9eff457d'), text="true", status_code=200)
        m.put('%s/v1/session/destroy/%s' % (CONSUL_ADDR, '4cc1e37d-53cc-0d61-3985-0e0d9eff457d'), text='{"ID": "4cc1e37d-53cc-0d61-3985-0e0d9eff457d"}', status_code=200)
        t = Tendril()
        success, data = t._acquire_lock(path)
        assert success
	lock_path = ".%s.lock" % path.replace('/', '.')
        assert data == "Locked with lockfile: %s" % lock_path
        success, data = t._acquire_lock(path)
        assert success
        assert data == "Renewed lock with lockfile: %s" % lock_path
        success, data = t._release_lock(path)
        assert success
        assert data == "Unlocked with lockfile: %s" % lock_path
