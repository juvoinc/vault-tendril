test:
	PYTHONPATH=modules nosetests -v -s tests

test_primitives:
	scripts/start_vault.sh
	PYTHONPATH=modules nosetests -v -s tests/primitives
	scripts/stop_vault.sh

pylint:
	pylint tendril modules/vault_tendril
