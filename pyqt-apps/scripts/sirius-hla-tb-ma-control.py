#!/usr/bin/env python-sirius

"""TB Magnets Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control.PSTabControlWindow import PSTabControlWindow


app = SiriusApplication()
window = PSTabControlWindow(section="TB", discipline=1)  # MA
window.show()
sys.exit(app.exec_())
