INSTALL_INSTALL_DIR ?= /usr/local/altschool/django-scheduler

# Helpers
PIP = $(INSTALL_DIR)/bin/pip
PYTHON = $(INSTALL_DIR)/bin/python
MANAGE_PY = $(PYTHON) manage.py
SETUP_PY = $(PYTHON) setup.py

.PHONY: clean install test

define header
  @tput setaf 6
  @echo "==> $1"
  @tput sgr0
endef

$(INSTALL_DIR): $(INSTALL_DIR)/bin/activate
	mkdir -p $(INSTALL_DIR)/www/static

$(INSTALL_DIR)/bin/activate: setup.py
	$(call header,"Installing")
	@test -d $(INSTALL_DIR) || virtualenv $(INSTALL_DIR)
	@$(PIP) install -q --upgrade pip==8.0.0
	@touch $(INSTALL_DIR)/bin/activate

install: $(INSTALL_DIR)
	$(call header,"Building")
	@$(SETUP_PY) -q install

test: install
	$(call header,"Running unit tests")
	@$(SETUP_PY) test

# Create new migrations
migrations: $(INSTALL_DIR)
	$(call header,"Creating migrations")
	@$(MANAGE_PY) makemigrations

uninstall:
	$(call header,"Uninstalling")
	@rm -rf $(INSTALL_DIR)

clean: uninstall
	$(call header,"Cleaning")
	@rm -rf django_scheduler.egg-info
