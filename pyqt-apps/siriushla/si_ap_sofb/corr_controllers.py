"""Define Controllers for the orbits displayed in the graphic."""

from functools import partial as _part
import numpy as _np
from qtpy.QtWidgets import QWidget, QLabel, QComboBox, QGroupBox, \
                            QPushButton, QVBoxLayout, QHBoxLayout, \
                            QSpacerItem, QSizePolicy, QFormLayout
from pydm.widgets import PyDMPushButton
from siriushla.widgets import SiriusConnectionSignal, PyDMLed, \
                                PyDMStateButton, SiriusLedAlert, \
                                SiriusDialog
import siriushla.util as _util
import siriuspy.csdevice.orbitcorr as _csorb

CONST = _csorb.get_consts('SI')


class ControlCorrectors(QWidget):

    def __init__(self, parent, prefix):
        super(ControlCorrectors, self).__init__(parent)
        self.prefix = prefix
        self.setup_ui()

    def setup_ui(self):
        hbl = QHBoxLayout(self)
        grp_bx = QGroupBox(self)
        hbl.addWidget(grp_bx)
        grp_bx.setTitle('Correctors')

        fbl = QFormLayout(grp_bx)
        fbl.setContentsMargins(9, -1, -1, 9)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + pref+'SI-Glob:AP-SOFB:'
    wid = ControlCorrectors(win, prefix)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
