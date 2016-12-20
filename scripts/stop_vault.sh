#!/bin/bash

vault_pid=`ps -A | grep 'vault server -dev --dev-root-token-id 2836814c-fb96-7c69-83fc-2ede967e697a' | grep -v grep | awk '{print $1}'`
if [ "$vault_pid" != "" ] ; then
	kill $vault_pid
fi
