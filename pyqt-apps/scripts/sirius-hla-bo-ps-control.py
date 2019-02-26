#!/usr/bin/env python-sirius

"""BO PS Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control.PSTabControlWindow import PSTabControlWindow


app = SiriusApplication()
window = PSTabControlWindow(section='BO', discipline='PS')
window.show()
sys.exit(app.exec_())
