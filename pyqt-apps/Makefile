
install-resources:
	cd ./resources; pyrcc5 resources.qrc -o ../siriushla/resources.py

install: clean install-resources
	sudo ./setup.py install

develop: clean install-resources
	sudo ./setup.py develop
	cd ./resources

clean:
	git clean -fdX
