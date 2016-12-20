test:
	PYTHONPATH=modules nosetests -v -s tests

test_primitives:
	scripts/start_daemons.sh
	PYTHONPATH=modules nosetests -v -s tests/primitives
	scripts/stop_daemons.sh

pylint:
	pylint tendril modules/vault_tendril
