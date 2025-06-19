PYENV_NAME = behave-tests
PYTHON_VERSION = 3.10

.PHONY: pyenv-rm install-requirements install-venv pyenv-activate

# Remove venv if exists
pyenv-rm:
	@pyenv virtualenv-delete -f $(PYENV_NAME) || true

# Install requirements
install-requirements:
	pip install --upgrade pip
	pip install -r requirements.txt

# Complete installation/reinstallation of the repo pyenv
install-venv:
	pyenv virtualenv $(PYTHON_VERSION) $(PYENV_NAME)
	pyenv local $(PYENV_NAME)
	$(MAKE) install-requirements

# Activates repo pyenv if exists, else runs installation
venv:
	@if ! pyenv versions --bare | grep -qx $(PYENV_NAME); then \
		$(MAKE) install-venv; \
	else \
		pyenv local $(PYENV_NAME); \
	fi

test: venv
	behave

setup-dbx-test-env:
	@echo "Setting up dbx test environment..."
	python -m scripts.create_test_clustering_tables
	@echo "dbx test environment setup complete."

dbx-test: setup-dbx-test-env
	@echo "Running dbx tests..."
	behave
	@echo "dbx tests completed."