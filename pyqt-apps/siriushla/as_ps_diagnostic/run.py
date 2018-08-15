#!/usr/bin/env python3
import sys
from siriushla.sirius_application import SiriusApplication

app = SiriusApplication(ui_file='main_window.py')
sys.exit(app.exec_())
