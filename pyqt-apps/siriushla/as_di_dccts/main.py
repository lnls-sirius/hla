"""DCCT Monitor Windows."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, \
    QPushButton
import qtawesome as qta
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName
from siriushla.widgets import SiriusMainWindow
from siriushla import util
from siriushla.as_di_dccts.graphics import DCCTMonitor, BORampEffMonitor
from siriushla.as_di_dccts.settings import DCCTSettings


def get_dcct_list(sec):
    if sec == 'SI':
        return ['SI-13C4:DI-DCCT', 'SI-14C4:DI-DCCT']
    else:
        return ['BO-35D:DI-DCCT']


class DCCTMain(SiriusMainWindow):
    """DCCT Main Window."""

    def __init__(self, parent=None, prefix='', device=''):
        """Initialize."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = SiriusPVName(device)
        self.section = self.device.sec
        if 'BO' in device:
            self.setObjectName('BOApp')
        else:
            self.setObjectName('SIApp')
        self.setWindowTitle(device)
        self.setWindowIcon(
            qta.icon('mdi.current-dc',
                     color=util.get_appropriate_color(self.section)))
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        cw = QWidget()
        lay = QGridLayout(cw)
        lay.setVerticalSpacing(10)
        self.setCentralWidget(cw)

        self.curr_graph = DCCTMonitor(self, self.prefix, self.device,
                                      layout_with_settings=True)
        self.settings = DCCTSettings(self, self.prefix, self.device)

        lay.addWidget(
            QLabel('<h3>'+self.device+'</h3>', alignment=Qt.AlignCenter),
            0, 0, 1, 2)
        lay.addWidget(self.curr_graph, 1, 0)
        self.curr_graph.layout().addWidget(self.settings, 0, 1, 2, 1)
        self.settings.layout().setContentsMargins(0, 0, 0, 0)

        if 'BO' in self.device:
            self.ramfeff_graph = BORampEffMonitor(self, self.prefix)
            lay.addWidget(self.ramfeff_graph, 2, 0, 1, 2)


class SISelectDCCT(QWidget):
    """Select Screens."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """Init."""
        super().__init__(parent=parent)
        self.prefix = prefix
        self.setObjectName('SIApp')
        self.dcct_list = get_dcct_list('SI')
        self.setWindowTitle('Select a DCCT')
        self.setWindowIcon(
            qta.icon('mdi.current-dc', color=util.get_appropriate_color('SI')))
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
    from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    device = 'BO-35D:DI-DCCT'
    window = DCCTMain(None, prefix=_VACA_PREFIX, device=device)
    window.show()
    _sys.exit(app.exec_())
