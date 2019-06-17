"""DCCT Monitor Windows."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, \
    QPushButton
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla.widgets import SiriusMainWindow
from siriushla import util
from siriushla.as_di_dccts.graphics import DCCTMonitor, BORampEffMonitor
from siriushla.as_di_dccts.settings import DCCTSettings


class DCCTMain(SiriusMainWindow):
    """DCCT Main Window."""

    def __init__(self, parent=None, prefix='', device=''):
        """Initialize."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = device
        self.setWindowTitle(device)
        self._setupUi()

    def _setupUi(self):
        cw = QWidget()
        lay = QGridLayout(cw)
        lay.setVerticalSpacing(10)
        self.setCentralWidget(cw)

        self.curr_graph = DCCTMonitor(self, self.prefix, self.device)
        aux = QLabel('')
        aux.setStyleSheet('min-height:1.5em; max-height:1.5em;')
        self.curr_graph.layout().addWidget(aux)
        self.settings = DCCTSettings(self, self.prefix, self.device)

        lay.addWidget(
            QLabel('<h3>'+self.device+'</h3>', alignment=Qt.AlignCenter),
            0, 0, 1, 2)
        lay.addWidget(self.curr_graph, 1, 0)
        lay.addWidget(self.settings, 1, 1)

        if 'BO' in self.device:
            self.ramfeff_graph = BORampEffMonitor(self, self.prefix)
            lay.addWidget(self.ramfeff_graph, 2, 0, 1, 2)


class SISelectDCCT(QWidget):
    """Select Screens."""

    def __init__(self, parent=None, prefix=_vaca_prefix):
        """Init."""
        super().__init__(parent=parent)
        self.prefix = prefix
        self.dcct_list = ['SI-13C4:DI-DCCT', 'SI-14C4:DI-DCCT']
        self.setWindowTitle('Select a DCCT')
        self._setupUi()

    def _setupUi(self):
        vlay = QVBoxLayout(self)
        vlay.setSpacing(15)
        self.setLayout(vlay)

        lab = QLabel('<h2>Sirius DCCT List</h2>',
                     alignment=Qt.AlignCenter)
        vlay.addWidget(lab)

        for dcct in self.dcct_list:
            pbt = QPushButton(dcct)
            pbt.setStyleSheet("""min-width:10em;""")
            util.connect_window(pbt, DCCTMain, parent=None,
                                prefix=self.prefix, device=dcct)
            vlay.addWidget(pbt)


if __name__ == '__main__':
    """Run test."""
    import sys as _sys
    from siriuspy.envars import vaca_prefix as _vaca_prefix
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    device = 'BO-35D:DI-DCCT'
    window = DCCTMain(None, prefix=_vaca_prefix, device=device)
    window.show()
    _sys.exit(app.exec_())
