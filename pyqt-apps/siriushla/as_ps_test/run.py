#!/usr/bin/env python-sirius
import sys
from pydm import PyDMApplication

app = PyDMApplication(ui_file='main_window.py')
sys.exit(app.exec_())
