#!/usr/bin/env python-sirius

"""SI Magnets Application."""

import sys
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ma_control.MagnetTabControlWindow \
    import MagnetTabControlWindow
from siriushla import util


app = SiriusApplication()
util.set_style(app)
window = MagnetTabControlWindow(section="SI")
window.show()
sys.exit(app.exec_())
