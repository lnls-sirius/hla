"""DCCT Monitor Windows."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, \
    QPushButton, QHBoxLayout
import qtawesome as qta
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName
from siriushla.widgets import SiriusMainWindow
from siriushla import util
from siriushla.as_di_dccts.graphics import DCCTMonitor, EffMonitor
from siriushla.as_di_dccts.settings import DCCTSettings


def get_dcct_list(sec):
    if sec == 'SI':
        return ['SI-13C4:DI-DCCT', 'SI-14C4:DI-DCCT']
    else:
        return ['BO-35D:DI-DCCT', ]


class DCCTMain(SiriusMainWindow):
    """DCCT Main Window."""

    def __init__(self, parent=None, prefix='', device=''):
        """Initialize."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = SiriusPVName(device)
        self.section = self.device.sec
        self.setObjectName(self.section+'App')
        self.setWindowTitle(device)
        self.setWindowIcon(
            qta.icon('mdi.current-dc',
                     color=util.get_appropriate_color(self.section)))
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        self.title = QLabel('<h3>'+self.device+'</h3>',
                            alignment=Qt.AlignCenter)

        self.curr_graph = DCCTMonitor(self, self.prefix, self.device)
        self.settings = DCCTSettings(self, self.prefix, self.device)
        hbox_dcct = QHBoxLayout()
        hbox_dcct.addWidget(self.curr_graph)
        hbox_dcct.addWidget(self.settings)

        self.pb_showsett = QPushButton('<', self)
        self.pb_showsett.setObjectName('showsett')
        self.pb_showsett.setToolTip('Hide settings')
        self.pb_showsett.setStyleSheet(
            '#showsett{min-width:0.7em;max-width:0.7em;}')
        self.pb_showsett.released.connect(self._handle_settings_vis)

        self.pb_showeff = QPushButton('v', self)
        self.pb_showeff.setObjectName('showeff')
        self.pb_showeff.setToolTip('Show efficiency graph')
        self.pb_showeff.setStyleSheet(
            '#showeff{min-width:0.7em;max-width:0.7em;}')
        self.pb_showeff.released.connect(self._handle_efficiency_vis)

        hbox_visi = QHBoxLayout()
        hbox_visi.addStretch()
        hbox_visi.addWidget(self.pb_showsett)
        hbox_visi.addWidget(self.pb_showeff)

        self.eff_graph = EffMonitor(self, self.prefix, self.section)
        self.eff_graph.setVisible(False)

        cw = QWidget()
        self.setCentralWidget(cw)
        lay = QVBoxLayout(cw)
        lay.setSpacing(10)
        lay.addWidget(self.title)
        lay.addLayout(hbox_dcct)
        lay.addLayout(hbox_visi)
        lay.addWidget(self.eff_graph)

    def _handle_settings_vis(self):
        vis = self.settings.isVisible()
        text = '>' if vis else '<'
        ttip = 'Show' if vis else 'Hide'
        self.pb_showsett.setText(text)
        self.pb_showsett.setToolTip(ttip+' settings')
        self.settings.setVisible(not vis)
        self.sender().parent().adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()

    def _handle_efficiency_vis(self):
        vis = self.eff_graph.isVisible()
        text = 'v' if vis else '^'
        ttip = 'Show' if vis else 'Hide'
        self.pb_showeff.setText(text)
        self.pb_showeff.setToolTip(ttip+' efficiency graph')
        self.eff_graph.setVisible(not vis)
        self.sender().parent().adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()


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
