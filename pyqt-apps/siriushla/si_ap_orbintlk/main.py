"""BPM Orbit Interlock Main Window."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QGroupBox, \
    QPushButton, QSizePolicy as QSzPlcy, QVBoxLayout, QMenuBar, QAction

import qtawesome as qta

from pydm.widgets import PyDMPushButton

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.orbintlk.csdev import ETypes as _ETypes

from ..widgets import SiriusMainWindow, SiriusPushButton, SiriusLedAlert, \
    PyDMLogLabel, SiriusEnumComboBox, SiriusSpinbox, SiriusLabel, \
    SiriusLedState, PyDMStateButton
from ..widgets.dialog import StatusDetailDialog
from ..widgets.windows import create_window_from_widget
from ..util import get_appropriate_color, connect_window, connect_newprocess
from .base import BaseObject
from .custom_widgets import BPMIntlkEnblWidget, BPMIntlkLimSPWidget, \
    MonitoredDevicesDialog
from .graphics import GraphMonitorWidget


class BPMOrbIntlkMainWindow(BaseObject, SiriusMainWindow):
    """BPM Orbit Interlock Control Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix):
        """Init."""
        BaseObject.__init__(self, prefix)
        SiriusMainWindow.__init__(self, parent)

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

        # Log
        self._log = self._setupLogWidget()

        # Graphs
        self._graphs = GraphMonitorWidget(self, self.prefix)

        # high level control
        self._gb_ctrl = self._setupHLGroup()

        # layout
        lay.addWidget(self.title, 0, 0, 1, 3)
        lay.addWidget(self._log, 1, 0)
        lay.addWidget(self._graphs, 1, 1)
        lay.addWidget(self._gb_ctrl, 1, 2)

        self._create_menu()

    def _setupLogWidget(self):
        loglabel = PyDMLogLabel(
            self, init_channel=self.hlprefix.substitute(propty='Log-Mon'))
        loglabel.setObjectName('log')
        loglabel.setStyleSheet('#log{min-width: 20em;}')
        loglabel.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.MinimumExpanding)
        loglabel.setAlternatingRowColors(True)
        loglabel.maxCount = 2000

        bt_clear = QPushButton('Clear Log', self)
        bt_clear.clicked.connect(loglabel.clear)

        wid = QGroupBox('IOC Log')
        lay = QVBoxLayout(wid)
        lay.addWidget(loglabel)
        lay.addWidget(bt_clear, alignment=Qt.AlignCenter)
        return wid

    def _setupGlobStatusGroup(self):
        wid = QGroupBox('Global Status')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        for i, sts in enumerate(['BPM', 'Timing', 'LLRF']):
            lblsprop = f'STS_LBLS_{sts.upper()}'
            lbl = QLabel(
                f'{sts}: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            pvname = self.hlprefix.substitute(propty=f'{sts}Status-Mon')
            led = SiriusLedAlert(self, pvname)
            pbt = self._create_detail_button()
            connect_window(
                pbt, StatusDetailDialog, parent=self, pvname=pvname,
                labels=getattr(_ETypes, lblsprop), title=f'{sts} Status')
            lay.addWidget(lbl, i, 1)
            lay.addWidget(led, i, 2)
            lay.addWidget(pbt, i, 3)

            if sts != 'LLRF':
                pbt = QPushButton('', self)
                pbt.setIcon(qta.icon('fa5s.ellipsis-v'))
                pbt.setObjectName('sts')
                pbt.setStyleSheet(
                    '#sts{min-width:18px; max-width:18px; icon-size:20px;}')
                connect_window(
                    pbt, MonitoredDevicesDialog, parent=self,
                    prefix=self.prefix, propty=f'{sts}MonitoredDevices-Mon')
                lay.addWidget(pbt, i, 0)

        return wid

    def _setupGlobSettingsGroup(self):
        wid = QGroupBox('Global Settings')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        ld_enbl = QLabel(
            'Enable: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_enbl = PyDMStateButton(
            self, self.hlprefix.substitute(propty='Enable-Sel'))
        lb_enbl = SiriusLedState(
            self, self.hlprefix.substitute(propty='Enable-Sts'))
        lay.addWidget(ld_enbl, 0, 0)
        lay.addWidget(sb_enbl, 0, 1)
        lay.addWidget(lb_enbl, 0, 2)

        lbl_rst = QLabel(
            'Reset all interlocks: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        pvname = self.hlprefix.substitute(propty='Reset-Cmd')
        pb_rst = PyDMPushButton(self, pressValue=1, init_channel=pvname)
        pb_rst.setToolTip('Send reset for BPM flags, EVG and LLRF')
        pb_rst.setIcon(qta.icon('fa5s.sync'))
        pb_rst.setObjectName('rst')
        pb_rst.setStyleSheet(
            '#rst{min-width:25px; max-width:25px; icon-size:20px;}')
        lay.addWidget(lbl_rst, 1, 0)
        lay.addWidget(pb_rst, 1, 1)

        desc2propty = {
            'Reset Timing Lock Latches': 'ResetTimingLockLatches-Cmd',
            'Configure EVG interlock': 'ConfigEVG-Cmd',
            'Configure Fout RxEnbl': 'ConfigFouts-Cmd',
            'Configure Delta EVR': 'ConfigDeltaRedunEVR-Cmd',
            'Configure AFC Timing RTM Loop': 'ConfigAFCTiming-Cmd',
            'Reset AFC Timing RTM Clocks': 'ResetAFCTimingRTMClk-Cmd', 
            'Configure HL triggers': 'ConfigHLTriggers-Cmd',
            'Configure LLRF interlocks': 'ConfigLLRFIntlk-Cmd',
            'Configure BPMs': 'ConfigBPMs-Cmd',
            'Configure AFC Phys.Triggers': 'ConfigAFCPhyTrigs-Cmd',
        }
        row = 2
        for desc, propty in desc2propty.items():
            pvname = self.hlprefix.substitute(propty=propty)
            pbt = PyDMPushButton(
                self, pressValue=1, init_channel=pvname, label=desc)
            lay.addWidget(pbt, row, 0, 1, 3)
            row += 1

        return wid

    def _setupBPMIntlkSettingsGroup(self):
        intlk2pvstr = {
            'Min.Sum.': 'MinSum',
            'Pos.': 'Pos',
            'Ang.': 'Ang',
        }
        ld_enblsel = QLabel(
            'Enable: ', alignment=Qt.AlignRight | Qt.AlignVCenter)
        ld_lim = QLabel(
            'Thresholds: ', alignment=Qt.AlignRight | Qt.AlignVCenter)
        ld_clr = QLabel(
            'Reset: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)

        wid = QGroupBox('BPM Settings')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop | Qt.AlignRight)
        lay.addWidget(ld_enblsel, 1, 0)
        lay.addWidget(ld_lim, 2, 0)
        lay.addWidget(ld_clr, 3, 0)

        col = 1
        for intlktype, pvstr in intlk2pvstr.items():
            lblcol = QLabel(
                f'<h4>{intlktype}</h4>', self,
                alignment=Qt.AlignRight | Qt.AlignVCenter)
            lay.addWidget(lblcol, 0, col, alignment=Qt.AlignCenter)

            if intlktype.startswith(('Min', 'Pos', 'Ang')):
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
                    propty=pvstr+'EnblList-SP', title=intlktype + ' Enable',
                    prefix=self.prefix)
                lay.addWidget(bt_enblsel, 1, col, alignment=Qt.AlignCenter)

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
                lay.addWidget(bt_lim, 2, col, alignment=Qt.AlignCenter)

            if 'Sum' not in intlktype:
                propty = f'ResetBPM{pvstr}-Cmd'
                bt_clr = SiriusPushButton(
                    parent=self, pressValue=1, icon=qta.icon('fa5s.sync'),
                    init_channel=self.hlprefix.substitute(
                        prefix=self.prefix, propty=propty))
                bt_clr.setObjectName('clr')
                bt_clr.setStyleSheet(
                    '#clr{min-width:25px; max-width:25px; icon-size:20px;}')
                lay.addWidget(bt_clr, 3, col, alignment=Qt.AlignCenter)

            col += 1

        return wid

    def _setupBPMAcqSettingsGroup(self):
        wid = QGroupBox('BPM Acq. Settings')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        props = [
            'PsMtmAcqChannel-Sel',
            'PsMtmAcqSamplesPre-SP',
            'PsMtmAcqSamplesPost-SP',
        ]
        for row, prop in enumerate(props):
            desc = prop.split('-')[0].split('Acq')[1]+':'
            spn = self.hlprefix.substitute(prefix=self.prefix, propty=prop)
            rbn = spn.substitute(
                propty=prop.replace('Sel', 'Sts').replace('SP', 'RB'))

            ldw = QLabel(desc, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            spw = SiriusEnumComboBox if spn.endswith('Sel') else SiriusSpinbox
            widsp = spw(self, spn)
            widrb = SiriusLabel(self, rbn)
            lay.addWidget(ldw, row, 0)
            lay.addWidget(widsp, row, 1)
            lay.addWidget(widrb, row, 2)

        ld_config = QLabel(
            'Send Acq. Config.', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        bt_config = SiriusPushButton(
            parent=self, pressValue=1, icon=qta.icon('fa5s.sync'),
            init_channel=self.hlprefix.substitute(
                prefix=self.prefix, propty='PsMtmAcqConfig-Cmd'))
        lay.addWidget(ld_config, 3, 0)
        lay.addWidget(bt_config, 3, 1, alignment=Qt.AlignCenter)

        return wid

    def _setupHLGroup(self):
        wid = QGroupBox('IOC Control')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Global Status
        self._gb_globsts = self._setupGlobStatusGroup()

        # Global Settings
        self._gb_globsett = self._setupGlobSettingsGroup()

        # BPM Interlock Settings
        self._gb_bpmintlk = self._setupBPMIntlkSettingsGroup()

        # BPM Acquisition Settings
        self._gb_bpmacq = self._setupBPMAcqSettingsGroup()

        lay.addWidget(self._gb_globsts)
        lay.addWidget(self._gb_globsett)
        lay.addWidget(self._gb_bpmintlk)
        lay.addWidget(self._gb_bpmacq)

        return wid

    def _create_detail_button(self):
        pbt = QPushButton('', self)
        pbt.setIcon(qta.icon('fa5s.list-ul'))
        pbt.setObjectName('sts')
        pbt.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        return pbt

    def _create_menu(self):
        menubar = QMenuBar(self)
        timon = QAction('Open Timing Monitor', menubar)
        connect_newprocess(
            timon, [f'sirius-hla-as-ti-control.py', '-t', 'monitor'])
        menubar.addAction(timon)
        self.layout().setMenuBar(menubar)
