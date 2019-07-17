#!/usr/bin/env python-sirius

"""Open power supplies test window."""

import sys
from siriushla.sirius_application import SiriusApplication

try:
    from siriushla.as_ps_test.ps_test_window import PSTestWindow

    app = SiriusApplication()
    app.open_window(PSTestWindow)
    sys.exit(app.exec_())
except:
    app = SiriusApplication.instance()
    if app is None:
        app = SiriusApplication(None, sys.argv)
    app.disclaimer()
