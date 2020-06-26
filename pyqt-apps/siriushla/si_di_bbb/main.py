"""BbB Main Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QWidget

from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from siriushla.util import connect_window
from siriushla.widgets import SiriusMainWindow
from .bbb import BbBControlWindow, BbBMainSettingsWidget
from .util import get_bbb_icon


class BbBMainWindow(SiriusMainWindow):
    """BbB Main Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix):
        super().__init__(parent)
        self.prefix = prefix
        self.setWindowTitle('BbB Control Window')
        self.setObjectName('SIApp')
        self.setWindowIcon(get_bbb_icon())
        self._setupUi()

    def _setupUi(self):
        self._ld_bbb = QLabel(
            '<h3>BbB Control Window</h3>', self, alignment=Qt.AlignCenter)

        self._bbb_widgets = list()
        idcs_types = ['H', 'V', 'L']

        cwt = QWidget(self)
        self.setCentralWidget(cwt)
        lay = QGridLayout(cwt)
        lay.addWidget(self._ld_bbb, 0, 0, 1, len(idcs_types))

        for col, idc in enumerate(idcs_types):
            dev_pref = 'SI-Glob:DI-BbBProc-'+idc

            wid = BbBMainSettingsWidget(self, self.prefix, dev_pref)
            connect_window(
                wid.pb_detail, BbBControlWindow, self,
                prefix=self.prefix, device=dev_pref)

            lay.addWidget(wid, 1, col)
            self._bbb_widgets.append(wid)

        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 6)


if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    w = BbBMainWindow(prefix=_vaca_prefix)
    w.show()
    sys.exit(app.exec_())
