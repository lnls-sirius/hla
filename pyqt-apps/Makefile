
install-resources:
	cd ./resources; pyrcc5 resources.qrc -o ../siriushla/resources.py

install: install-resources
	sudo ./setup.py install

develop: install-resources
	sudo ./setup.py develop
	cd ./resources
