#!/usr/bin/env python3.6
import sys
from pydm import PyDMApplication

app = PyDMApplication(ui_file='si-ap-currlt.py')
sys.exit(app.exec_())
