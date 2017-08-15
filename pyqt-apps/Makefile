DIR = $(shell pwd)

install:
	sudo ./setup.py install
	sudo cp -af $(DIR)/etc/sirius-hla-as-style.css /usr/local/etc/ 

develop:
	sudo ./setup.py develop
	sudo ln -sf $(DIR)/etc/sirius-hla-as-style.css /usr/local/etc/
