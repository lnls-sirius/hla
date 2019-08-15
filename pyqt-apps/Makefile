DESIGNER_PLUGIN_FILE = designer_plugin.py
INSTALL_DESIGNER_DIR ?= /usr/local/share/Qt/designer

install-resources:
	cd ./resources; pyrcc5 resources.qrc -o ../siriushla/resources.py

install-designer:
	mkdir -p $(INSTALL_DESIGNER_DIR)
	cp $(DESIGNER_PLUGIN_FILE) $(INSTALL_DESIGNER_DIR)

install: clean install-resources
	sudo ./setup.py install

install-all: install-resources install-designer
	./setup.py install

develop: clean install-resources
	sudo ./setup.py develop
	cd ./resources

clean:
	git clean -fdX
