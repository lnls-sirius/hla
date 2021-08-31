"""ID Control Module."""

import os as _os
from qtpy.QtGui import QMovie
from qtpy.QtCore import Qt, Slot, QSize
from qtpy.QtWidgets import QVBoxLayout, QWidget, QGroupBox, QGridLayout, \
    QLabel, QAction, QMenu
from pydm.connection_inspector import ConnectionInspector

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName

from ..widgets import SiriusMainWindow, SiriusConnectionSignal

from .apu_control import APUSummaryHeader, APUSummaryWidget
from .util import get_id_icon


class IDControl(SiriusMainWindow):
    """ID Control Window."""

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

        label = QLabel('<h3>ID Control Window</h3>',
                       self, alignment=Qt.AlignCenter)
        label.setStyleSheet('QLabel{min-height: 3em; max-height: 3em;}')

        self.label_mov1 = QLabel(self)
        self.label_mov1.setVisible(False)
        self.label_mov1.setStyleSheet(
            'QLabel{min-height: 3em; max-height: 3em;}')
        self.label_mov2 = QLabel(self)
        self.label_mov2.setVisible(False)
        self.label_mov2.setStyleSheet(
            'QLabel{min-height: 3em; max-height: 3em;}')
        self.movie_mov = QMovie(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), 'hula.gif'))
        self.movie_mov.setScaledSize(QSize(50, 50))
        self.label_mov1.setMovie(self.movie_mov)
        self.label_mov2.setMovie(self.movie_mov)

        self._gbox_apu = QGroupBox('APU', self)
        self._gbox_apu.setLayout(self._setupAPULayout())

        lay = QGridLayout(cw)
        lay.addWidget(self.label_mov1, 0, 0)
        lay.addWidget(label, 0, 1)
        lay.addWidget(self.label_mov2, 0, 2)
        lay.addWidget(self._gbox_apu, 1, 0, 1, 3)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 15)
        lay.setColumnStretch(2, 1)

    def _setupAPULayout(self):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)

        self._apu_header = APUSummaryHeader(self)
        lay.addWidget(self._apu_header)

        self._apu_widgets = list()
        self._channels_mov = list()
        idlist = ['SI-06SB:ID-APU22', 'SI-07SP:ID-APU22',
                  'SI-08SB:ID-APU22', 'SI-09SA:ID-APU22',
                  'SI-11SP:ID-APU58']
        for idname in idlist:
            idname = _PVName(idname)
            apu_wid = APUSummaryWidget(self, self._prefix, idname)
            lay.addWidget(apu_wid)
            self._apu_widgets.append(apu_wid)
            ch_mov = SiriusConnectionSignal(idname+':Moving-Mon')
            ch_mov.new_value_signal[float].connect(self._handle_moving_vis)
            self._channels_mov.append(ch_mov)

        return lay

    def _create_actions(self):
        self.blctrl_enbl_act = QAction("Enable Beamline Control", self)
        self.blctrl_enbl_act.triggered.connect(
            lambda: self._set_beamline_control(True))
        self.blctrl_dsbl_act = QAction("Disable Beamline Control", self)
        self.blctrl_dsbl_act.triggered.connect(
            lambda: self._set_beamline_control(False))

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

    def contextMenuEvent(self, event):
        """Show a custom context menu."""
        point = event.pos()
        menu = QMenu("Actions", self)
        menu.addAction(self.blctrl_enbl_act)
        menu.addAction(self.blctrl_dsbl_act)
        menu.addSeparator()
        action = menu.addAction('Show Connections...')
        action.triggered.connect(self.show_connections)
        menu.popup(self.mapToGlobal(point))

    def show_connections(self, checked):
        """Show connections."""
        _ = checked
        c = ConnectionInspector(self)
        c.show()

    def _handle_moving_vis(self, value):
        """Handle visualization of moving state label."""
        show = any([ch.value != 0 for ch in self._channels_mov])
        self.label_mov1.setVisible(show)
        self.label_mov2.setVisible(show)
        if show:
            self.movie_mov.start()
        else:
            self.movie_mov.stop()
