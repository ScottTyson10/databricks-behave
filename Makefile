PYENV_NAME = behave-tests
PYTHON_VERSION = 3.10

.PHONY: test test-%

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

test:
	behave

test-%:
	behave --tags=@$*

test-compliance:
	behave --tags=@jobs,@maintenance,@performance,@documentation

test-jobs:
	behave --tags=@jobs

test-maintenance:
	behave --tags=@maintenance

test-performance:
	behave --tags=@performance

test-documentation:
	behave --tags=@documentation

test-all-compliance: test test-jobs test-maintenance test-performance test-documentation
