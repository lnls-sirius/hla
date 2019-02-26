#!/usr/bin/env python-sirius

"""TS PS Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control.PSTabControlWindow import PSTabControlWindow


app = SiriusApplication()
window = PSTabControlWindow(section='TS', discipline='PS')
window.show()
sys.exit(app.exec_())
