#!/usr/bin/env python-sirius

import sys
from pydm import PyDMApplication
from siriushla.si_ap_sofb import main


app = PyDMApplication(None, sys.argv)
window = main()
window.show()
sys.exit(app.exec_())
