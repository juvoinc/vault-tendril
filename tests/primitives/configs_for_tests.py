import requests

CONSUL_HOST = 'http://localhost:8500'
CONSUL_TOKEN = '7493971e-6a24-2afe-1c47-4c62c7fd14fc'
VAULT_ADDR = 'http://localhost:8200'
VAULT_TOKEN = '2836814c-fb96-7c69-83fc-2ede967e697a'

def recursive_delete(endpoint):
        foo = requests.get('%s/v1/%s?list=true' % (VAULT_ADDR, endpoint), headers={'X-Vault-Token':VAULT_TOKEN})
        data = foo.json()
        if 'data' in data:
                if 'keys' in data['data']:
                        for k2 in data['data']['keys']:
                                if k2.endswith('/'):
                                        k2 = k2.replace('/','')
                                        recursive_delete("%s/%s" % (endpoint, k2))
                                        requests.delete('%s/v1/%s' % (VAULT_ADDR, endpoint + '/' + k2), headers={'X-Vault-Token':VAULT_TOKEN})
                                else:
                                        requests.delete('%s/v1/%s' % (VAULT_ADDR, endpoint + '/' + k2), headers={'X-Vault-Token':VAULT_TOKEN})

def setup():
    recursive_delete("config")

def teardown():
    recursive_delete("config")
