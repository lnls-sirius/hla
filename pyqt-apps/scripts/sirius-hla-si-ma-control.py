#!/usr/bin/env python-sirius

"""SI Magnets Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control.PSTabControlWindow import PSTabControlWindow
from siriushla import util


app = SiriusApplication()
util.set_style(app)
window = PSTabControlWindow(section="SI", discipline=1)  # MA
window.show()
sys.exit(app.exec_())
