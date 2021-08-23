"""ID Control Module."""

from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QVBoxLayout, QWidget, QGroupBox, QGridLayout, \
    QLabel, QAction, QMenu
from pydm.connection_inspector import ConnectionInspector

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName

from siriushla.widgets import SiriusMainWindow

from .apu_control import APUSummaryHeader, APUSummaryWidget
from .util import get_id_icon


class IDControl(SiriusMainWindow):
    """IDs Control Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix):
        super().__init__(parent)
        self._prefix = prefix
        self.setObjectName('IDApp')
        self.setWindowTitle('ID Controls')
        self.setWindowIcon(get_id_icon())
        self._setupUi()
        self._create_actions()

    def _setupUi(self):
        cw = QWidget()
        self.setCentralWidget(cw)

        label = QLabel('<h3>IDs Control Window</h3>',
                       self, alignment=Qt.AlignCenter)
        label.setStyleSheet('max-height: 1.29em;')

        self._gbox_apu = QGroupBox('APU', self)
        self._gbox_apu.setLayout(self._setupAPULayout())

        lay = QGridLayout(cw)
        lay.addWidget(label, 0, 0)
        lay.addWidget(self._gbox_apu, 1, 0)

    def _setupAPULayout(self):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)

        self._apu_header = APUSummaryHeader(self)
        lay.addWidget(self._apu_header)

        self._apu_widgets = list()
        idlist = ['SI-06SB:ID-APU22', 'SI-07SP:ID-APU22',
                  'SI-08SB:ID-APU22', 'SI-09SA:ID-APU22',
                  'SI-11SP:ID-APU58']
        for idname in idlist:
            idname = _PVName(idname)
            apu_wid = APUSummaryWidget(self, self._prefix, idname)
            lay.addWidget(apu_wid)
            self._apu_widgets.append(apu_wid)

        return lay

    def _create_actions(self):
        self.blctrl_enbl_act = QAction("Enable Beamline Control", self)
        self.blctrl_enbl_act.triggered.connect(
            lambda: self._set_beamline_control(True))
        self.blctrl_dsbl_act = QAction("Disable Beamline Control", self)
        self.blctrl_dsbl_act.triggered.connect(
            lambda: self._set_beamline_control(False))
        self.park_act = QAction("Go to Parking Position", self)
        self.park_act.triggered.connect(self._cmd_park)

    @Slot(bool)
    def _set_beamline_control(self, state):
        """Execute enable/disable beamline control actions."""
        for widget in self._apu_widgets:
            try:
                if state:
                    widget.enable_beamline_control()
                else:
                    widget.disable_beamline_control()
            except TypeError:
                pass

    @Slot(bool)
    def _cmd_park(self, state):
        """Execute park actions."""
        for widget in self._apu_widgets:
            try:
                if state:
                    widget.park()
            except TypeError:
                pass

    def contextMenuEvent(self, event):
        """Show a custom context menu."""
        point = event.pos()
        menu = QMenu("Actions", self)
        menu.addAction(self.blctrl_enbl_act)
        menu.addAction(self.blctrl_dsbl_act)
        menu.addAction(self.park_act)
        menu.addSeparator()
        action = menu.addAction('Show Connections...')
        action.triggered.connect(self.show_connections)
        menu.popup(self.mapToGlobal(point))

    def show_connections(self, checked):
        """."""
        _ = checked
        c = ConnectionInspector(self)
        c.show()
