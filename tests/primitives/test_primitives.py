from nose.tools import with_setup, assert_raises
import requests
from vault_tendril.main import Tendril
from configs_for_tests import recursive_delete, VAULT_ADDR, VAULT_TOKEN, setup, teardown
import json

HEADERS = {'X-Vault-Token': VAULT_TOKEN}

@with_setup(setup, teardown)
def test_successful_write():
    path = 'env/app/1'
    t = Tendril(vault_token=VAULT_TOKEN)
    success, message = t._write_data(path, {"one":"first","two":"second"})
    assert success
    assert message == None
    r = requests.get('%s/v1/%s/%s' % (VAULT_ADDR, 'config', path), headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert 'data' in data
    assert len(data['data']) == 2
    assert 'one' in data['data']
    assert data['data']['one'] == 'first'
    assert 'two' in data['data']
    assert data['data']['two'] == 'second'

@with_setup(setup, teardown)
def test_successful_read():
    path = 'env/app/1'
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

@with_setup(setup, teardown)
def test_bad_token_write():
    path = 'env/app/1'
    t = Tendril(vault_token='00000000-0000-0000-0000-000000000000')
    success, message = t._write_data(path, {"one":"first","two":"second"})
    assert success == False
    assert message == "Permission denied"

@with_setup(setup, teardown)
def test_missing_data_read():
    t = Tendril(vault_token=VAULT_TOKEN)
    success, data = t._read_data('foo')
    assert not success
    assert data == "No data found at foo"

@with_setup(setup, teardown)
def test_bad_token_read():
    path = 'env/app/1'
    t = Tendril(vault_token=VAULT_TOKEN)
    success, message = t._write_data(path, {"one":"first","two":"second"})
    assert success
    assert message == None
    t = Tendril(vault_token='00000000-0000-0000-0000-000000000000')
    success, data = t._read_data(path)
    assert not success
    assert data == "Permission denied"

@with_setup(setup, teardown)
def test_bad_vault_host_write():
    path = 'env/app/1'
    t = Tendril(vault_addr='http://localhost:8201', vault_token=VAULT_TOKEN)
    success, message = t._write_data(path, {"one":"first","two":"second"})
    assert not success
    assert "Failed to establish a new connection: [Errno 61] Connection refused" in message

@with_setup(setup, teardown)
def test_bad_vault_host_read():
    path = 'env/app/1'
    t = Tendril(vault_token=VAULT_TOKEN)
    success, message = t._write_data(path, {"one":"first","two":"second"})
    assert success
    assert message == None
    t = Tendril(vault_addr='http://localhost:8201')
    success, data = t._read_data(path)
    assert not success
    assert "Failed to establish a new connection: [Errno 61] Connection refused" in data

@with_setup(setup, teardown)
def test_successful_path_read():
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
    success, data = t._list_path('/')
    assert len(data) == 3
    assert success
    assert 'env/' in data
    assert 'env2/' in data
    assert 'raw' in data

@with_setup(setup, teardown)
def test_missing_path_read():
    t = Tendril(vault_token=VAULT_TOKEN)
    success, data = t._list_path('foo')
    assert not success
    assert data == "No keys found at foo"

@with_setup(setup, teardown)
def test_bad_token_list():
    path = 'env/app/1'
    t = Tendril(vault_token=VAULT_TOKEN)
    success, message = t._write_data(path, {"one":"first","two":"second"})
    assert success
    assert message == None
    t = Tendril(vault_token='00000000-0000-0000-0000-000000000000')
    success, data = t._list_path('env')
    assert not success
    assert data == "Permission denied"
@with_setup(setup, teardown)
def test_lock():
    path = 'env/app/1'
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
