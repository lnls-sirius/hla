DESIGNER_PLUGIN_FILE = designer_plugin.py
INSTALL_DESIGNER_DIR ?= /usr/local/share/Qt/designer

PACKAGE=siriushla
PREFIX ?=
PIP ?= pip
ifeq ($(CONDA_PREFIX),)
	PREFIX=sudo -H
	PIP=pip-sirius
endif

install-designer:
	mkdir -p $(INSTALL_DESIGNER_DIR)
	cp $(DESIGNER_PLUGIN_FILE) $(INSTALL_DESIGNER_DIR)

install: clean uninstall
	$(PREFIX) $(PIP) install --no-deps --compile ./

uninstall:
	$(PREFIX) $(PIP) uninstall -y $(PACKAGE)

install-all: install install-designer

develop-install: clean develop-uninstall
	$(PIP) install --no-deps -e ./

develop-uninstall:
	$(PIP) uninstall -y $(PACKAGE)

clean:
	git clean -fdX
