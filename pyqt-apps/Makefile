DESIGNER_PLUGIN_FILE = designer_plugin.py
INSTALL_DESIGNER_DIR ?= /usr/local/share/Qt/designer

DISTPATH=$(shell python-sirius -c "import site; print(site.getsitepackages())" | cut -f2 -d"'")
PACKAGE=siriushla
ISINST=$(shell sudo pip-sirius show $(PACKAGE) | wc -l )
EGGLINK=$(DISTPATH)/$(PACKAGE).egg-link
TMPFOLDER=/tmp/install-$(PACKAGE)


install-designer:
	mkdir -p $(INSTALL_DESIGNER_DIR)
	cp $(DESIGNER_PLUGIN_FILE) $(INSTALL_DESIGNER_DIR)

install: clean uninstall
	sudo ./setup.py install --single-version-externally-managed --compile --force --record /dev/null

install-all: install install-designer

develop: clean uninstall
	sudo -H pip-sirius install --no-deps -e ./

uninstall:
ifneq (,$(wildcard $(EGGLINK)))
	sudo rm -r $(EGGLINK)
endif
ifneq ($(ISINST),0)
	sudo -H pip-sirius uninstall -y $(PACKAGE)
	sudo sed -i '/pyqt-apps/d' $(DISTPATH)/easy-install.pth
else
	echo 'already uninstalled $(PACKAGE)'
endif

clean:
	git clean -fdX
