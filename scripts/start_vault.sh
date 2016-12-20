#!/bin/bash

vault server -dev --dev-root-token-id 2836814c-fb96-7c69-83fc-2ede967e697a > /dev/null 2>&1 &
exit_code=1
while [ "$exit_code" -ne "0" ] ; do
	curl -s -H "X-Vault-Token: 2836814c-fb96-7c69-83fc-2ede967e697a" -H "Content-Type: application/json" -X POST -d '{"type":"generic"}' http://127.0.0.1:8200/v1/sys/mounts/config
	exit_code=$?
done
