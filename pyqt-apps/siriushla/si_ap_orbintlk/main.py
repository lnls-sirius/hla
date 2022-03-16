"""BPM Orbit Interlock Main Window."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QGroupBox, \
    QPushButton

import qtawesome as qta

from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from ..widgets import SiriusMainWindow
from ..widgets.windows import create_window_from_widget
from ..util import get_appropriate_color, connect_window
from .base import BaseObject
from .custom_widgets import FamBPMButton, FamBPMIntlkEnblStateLed, \
    BPMIntlkEnblWidget, BPMIntlkLimSPWidget
from .graphics import GraphMonitorWidget


class BPMOrbIntlkMainWindow(BaseObject, SiriusMainWindow):
    """BPM Orbit Interlock Control Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix):
        """Init."""
        BaseObject.__init__(self)
        SiriusMainWindow.__init__(self, parent)

        self.prefix = prefix

        self.setObjectName('SIApp')
        self.setWindowTitle('Orbit Interlock Control Window')
        color = get_appropriate_color('SI')
        self.setWindowIcon(qta.icon(
            'mdi.currency-sign', 'mdi.alarm-light',
            options=[
                dict(scale_factor=1, color=color),
                dict(scale_factor=0.45, color=color),
            ]))

        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        wid = QWidget(self)
        lay = QGridLayout(wid)
        self.setCentralWidget(wid)

        # title
        self.title = QLabel(
            '<h3>Orbit Interlock</h3>', self, alignment=Qt.AlignCenter)

        # General
        self._gb_gen = self._setupIntlkGroup('General')

        # Min.Sum. Threshold
        self._gb_minsum = self._setupIntlkGroup('Min.Sum.Threshold')

        # Translation
        self._gb_trans = self._setupIntlkGroup('Translation')

        # Angulation
        self._gb_ang = self._setupIntlkGroup('Angulation')

        # Graphs
        self._graphs = GraphMonitorWidget(self, self.prefix)

        # layout
        lay.addWidget(self.title, 0, 0, 1, 4)
        lay.addWidget(self._gb_gen, 1, 0)
        lay.addWidget(self._gb_minsum, 1, 1)
        lay.addWidget(self._gb_trans, 1, 2)
        lay.addWidget(self._gb_ang, 1, 3)
        lay.addWidget(self._graphs, 2, 0, 1, 4)

    def _setupIntlkGroup(self, intlktype):
        if 'General' in intlktype:
            pvstr = ''
        elif 'Sum' in intlktype:
            pvstr = 'MinSum'
        elif 'Translation' in intlktype:
            pvstr = 'Trans'
        elif 'Angulation' in intlktype:
            pvstr = 'Ang'

        wid = QGroupBox(intlktype)
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        row = 0
        ld_enblsel = QLabel(
            'Enable: ', alignment=Qt.AlignRight | Qt.AlignBottom)
        lay.addWidget(ld_enblsel, row, 0)

        sel_enbl_wind = create_window_from_widget(
            BPMIntlkEnblWidget,
            title='BPM Orbit Interlock - '+intlktype+' Enable State')
        bt_enblsel = QPushButton(qta.icon('fa5s.tasks'), '', self)
        bt_enblsel.setToolTip('Open window to set BPMs enable state.')
        bt_enblsel.setObjectName('sel')
        bt_enblsel.setStyleSheet(
            '#sel{min-width:25px; max-width:25px; icon-size:20px;}')
        connect_window(
            bt_enblsel, sel_enbl_wind, parent=self,
            propty='Intlk'+pvstr+'En-Sel', title=intlktype + ' Enable',
            prefix=self.prefix)
        lay.addWidget(bt_enblsel, row, 1)

        ch2vals = dict()
        for bpm in self.BPM_NAMES:
            chn = bpm.substitute(
                prefix=self.prefix, propty='Intlk'+pvstr+'En-Sts')
            ch2vals[chn] = 1
        led_enblsts = FamBPMIntlkEnblStateLed(self, ch2vals)
        lay.addWidget(led_enblsts, row, 2)

        if 'General' not in intlktype:
            row += 1
            ld_lim = QLabel(
                'Thresholds: ', alignment=Qt.AlignRight | Qt.AlignBottom)
            lay.addWidget(ld_lim, row, 0)

            sel_lim_wind = create_window_from_widget(
                BPMIntlkLimSPWidget,
                title='BPM Orbit Interlock - '+intlktype +
                (' Threshold' if 'Thres' not in intlktype else '') +
                ' Setpoint')
            bt_lim = QPushButton(qta.icon('fa5s.tasks'), '', self)
            bt_lim.setToolTip('Open window to set BPMs thresholds.')
            bt_lim.setObjectName('sel')
            bt_lim.setStyleSheet(
                '#sel{min-width:25px; max-width:25px; icon-size:20px;}')
            connect_window(
                bt_lim, sel_lim_wind, parent=self,
                metric=intlktype, prefix=self.prefix)
            lay.addWidget(bt_lim, row, 1)

        if 'Sum' not in intlktype:
            row += 1
            ld_clr = QLabel(
                'Clear All: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
            lay.addWidget(ld_clr, row, 0)

            bt_clr = FamBPMButton(
                self, self.prefix, 'Intlk'+pvstr+'Clr-Sel', '', value=1)
            bt_clr.setIcon(qta.icon('fa5s.sync'))
            bt_clr.setObjectName('clr')
            bt_clr.setStyleSheet(
                '#clr{min-width:25px; max-width:25px; icon-size:20px;}')
            lay.addWidget(bt_clr, row, 1)

        return wid
