#!/usr/bin/env python-sirius

"""SI PS Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control.PSTabControlWindow \
    import PSTabControlWindow
from siriushla import util


app = SiriusApplication()
util.set_style(app)
window = PSTabControlWindow(section="SI")
window.show()
sys.exit(app.exec_())
