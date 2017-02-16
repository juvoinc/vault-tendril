.DEFAULT_GOAL := help

help:
	@echo
	@echo "make test               # Runs local tests with vault mocked"
	@echo "make test_primitives    # Runs tests that use vault"
	@echo "make pylint             # Runs pylint on the code"
	@echo
test:
	PYTHONPATH=modules nosetests -v -s tests

test_primitives:
	scripts/stop_vault.sh
	scripts/stop_consul.sh
	scripts/start_consul.sh
	scripts/start_vault.sh
	PYTHONPATH=modules nosetests -v -s tests/primitives
	scripts/stop_vault.sh
	scripts/stop_consul.sh

pylint:
	pylint tendril modules/vault_tendril
