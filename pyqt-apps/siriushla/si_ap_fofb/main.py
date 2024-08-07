"""High level FOFB main module."""

import time as _time

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton, QWidget, QGridLayout, QMenu, \
    QLabel, QVBoxLayout, QGroupBox, QMenuBar, QAction, QHBoxLayout, \
    QSizePolicy as QSzPlcy, QDockWidget, QTabWidget
import qtawesome as qta

from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.fofb.csdev import ETypes as _FOFBEnums

from ..util import connect_window, connect_newprocess
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, CALabel, \
    PyDMLogLabel, SiriusMainWindow, PyDMStateButton, SiriusLedState, \
    SiriusConnectionSignal as _ConnSignal, CAPushButton, SiriusEnumComboBox

from .base import BaseObject, get_fofb_icon
from .custom_widgets import RefOrbWidget, StatusDialog, BPMSwModeWidget, \
    ControllersDetailDialog, PSConfigWidget
from .respmat import RespMatWidget
from .graphics import KickWidget


class MainWindow(BaseObject, SiriusMainWindow):
    """FOFB Main Window."""

    def __init__(self, parent=None, prefix='', device=''):
        BaseObject.__init__(self, device, prefix=prefix)
        SiriusMainWindow.__init__(self, parent)
        self.setWindowTitle('SI - FOFB')
        self.setObjectName('SIApp')
        self.setWindowIcon(get_fofb_icon())
        self._enblrule = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.devpref.substitute(propty='LoopState-Sts') +
            '", "trigger": true}]}]')
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        # layout
        self.log = self._setupLogWidget()

        self.kicks_view = KickWidget(self, self.device, self.prefix)

        self.control = self._setupControlWidget()

        self.setDocumentMode(False)
        self.setDockNestingEnabled(True)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.log)
        self.setCentralWidget(self.kicks_view)
        self.addDockWidget(Qt.RightDockWidgetArea, self.control)

        # menu
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        menuopen = QMenu('Open', menubar)
        actions = (
            ('&FOFB Control', 'FOFB Control', '', True, self.control),
            ('FOFB &Log', 'FOFB Log', '', True, self.log),
        )
        for name, tool, short, check, doc in actions:
            action = QAction(name, self)
            action.setToolTip(tool)
            action.setShortcut(short)
            action.setCheckable(check)
            action.setChecked(check)
            action.setEnabled(True)
            action.setVisible(True)
            action.toggled.connect(doc.setVisible)
            doc.visibilityChanged.connect(action.setChecked)
            menuopen.addAction(action)
        menubar.addAction(menuopen.menuAction())

        acq2cmd = {
            'SYSID': 'sirius-hla-si-bs-fofbsysid.py',
            'LAMP': 'sirius-hla-si-ps-fastcorracq.py',
        }
        for acq, cmd in acq2cmd.items():
            acq_menu = menubar.addMenu(acq+' Acq.')
            acq_menu.setObjectName('SIApp')
            for i in range(1, 21):
                txt = f'SI-{i:02}'
                dev = f'IA-{i:02}RaBPM:BS-FOFBCtrl'
                act = QAction(txt, acq_menu)
                connect_newprocess(act, [cmd, dev])
                acq_menu.addAction(act)

    def _setupStatusWidget(self):
        # correctors
        lbl_corr = QLabel(
            'Correctors: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)

        led_corr = SiriusLedAlert(
            self, self.devpref.substitute(propty='CorrStatus-Mon'))
        sts_corr = QPushButton('', self)
        sts_corr.setIcon(qta.icon('fa5s.list-ul'))
        sts_corr.setToolTip('Open Detailed Status View')
        sts_corr.setObjectName('sts')
        sts_corr.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        pvname = self.devpref.substitute(propty='CorrStatus-Mon')
        labels = _FOFBEnums.STS_LBLS_CORR
        cmds = [None]*len(labels)
        connect_window(
            sts_corr, StatusDialog, parent=self, pvname=pvname, labels=labels,
            cmds=cmds, title='Corrector Status')

        cnf_corr = PyDMPushButton(
            self, pressValue=1,
            init_channel=self.devpref.substitute(propty='CorrConfig-Cmd'))
        cnf_corr.setToolTip('Send OpMode, AccFreeze, Coefficients and Gains')
        cnf_corr.setIcon(qta.icon('fa5s.sync'))
        cnf_corr.setObjectName('conf')
        cnf_corr.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')

        # controllers
        lbl_ctrl = QLabel(
            'Controllers: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)

        led_ctrl = SiriusLedAlert(
            self, self.devpref.substitute(propty='CtrlrStatus-Mon'))
        sts_ctrl = QPushButton('', self)
        sts_ctrl.setIcon(qta.icon('fa5s.list-ul'))
        sts_ctrl.setToolTip('Open Detailed Status View')
        sts_ctrl.setObjectName('sts')
        sts_ctrl.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        pvname = self.devpref.substitute(propty='CtrlrStatus-Mon')
        labels = _FOFBEnums.STS_LBLS_FOFBCTRL
        cmds = [None]*len(labels)
        cmds[1] = self.devpref.substitute(propty='CtrlrConfBPMId-Cmd')
        sofbpvname = _PVName('SI-Glob:AP-SOFB').substitute(prefix=self.prefix)
        cmds[2] = sofbpvname.substitute(propty='SyncBPMs-Cmd')
        cmds[4] = self.devpref.substitute(propty='CtrlrSyncRefOrb-Cmd')
        cmds[5] = self.devpref.substitute(propty='CtrlrSyncTFrameLen-Cmd')
        cmds[6] = self.devpref.substitute(propty='CtrlrConfBPMLogTrg-Cmd')
        cmds[7] = self.devpref.substitute(propty='CtrlrSyncMaxOrbDist-Cmd')
        cmds[8] = self.devpref.substitute(
            propty='CtrlrSyncPacketLossDetec-Cmd')
        cmds[9] = self.devpref.substitute(propty='CtrlrReset-Cmd')
        cmds[10] = self.devpref.substitute(propty='CtrlrDsblSYSIDExc-Cmd')
        dtl_ctrl = QPushButton('Details')
        dtl_ctrl.setDefault(False)
        dtl_ctrl.setAutoDefault(False)
        dtl_ctrl.setIcon(qta.icon('fa5s.ellipsis-h'))
        dtl_ctrl.setToolTip('Open Controllers Details')
        dtl_ctrl.setObjectName('sts')
        dtl_ctrl.setStyleSheet('#sts{icon-size:20px;}')
        connect_window(
            dtl_ctrl, ControllersDetailDialog, parent=self,
            device=self.device, prefix=self.prefix)
        connect_window(
            sts_ctrl, StatusDialog, parent=self, pvname=pvname, labels=labels,
            cmds=cmds, title='FOFB Controller Status', detail_button=dtl_ctrl)

        cnf_ctrl = PyDMPushButton(
            self, pressValue=1,
            init_channel=self.devpref.substitute(propty='CtrlrReset-Cmd'))
        cnf_ctrl.setToolTip('Send Reset command to controllers')
        cnf_ctrl.setIcon(qta.icon('fa5s.sync'))
        cnf_ctrl.setObjectName('conf')
        cnf_ctrl.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')

        wid = QGroupBox('Status')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_corr, 0, 0)
        lay.addWidget(led_corr, 0, 1)
        lay.addWidget(sts_corr, 0, 2)
        lay.addWidget(cnf_corr, 0, 3)
        lay.addWidget(lbl_ctrl, 1, 0)
        lay.addWidget(led_ctrl, 1, 1)
        lay.addWidget(sts_ctrl, 1, 2)
        lay.addWidget(cnf_ctrl, 1, 3)
        return wid

    def _setupRefOrbWidget(self):
        widget = RefOrbWidget(self, self.device, self.prefix)

        wid = QGroupBox('Ref.Orb.')
        lay = QVBoxLayout(wid)
        lay.addWidget(widget)
        return wid

    def _setupLoopWidget(self):
        ld_enbl = QLabel(
            'Enable: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_enbl = PyDMStateButton(
            self, self.devpref.substitute(propty='LoopState-Sel'))
        lb_enbl = SiriusLedState(
            self, self.devpref.substitute(propty='LoopState-Sts'))

        ld_gain_h = QLabel(
            'Gain H: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_gain_h = SiriusSpinbox(
            self, self.devpref.substitute(propty='LoopGainH-SP'))
        lb_gain_h = SiriusLabel(
            self, self.devpref.substitute(propty='LoopGainH-RB'))
        lb_gain_mon_h = SiriusLabel(
            self, self.devpref.substitute(propty='LoopGainH-Mon'))

        ld_gain_v = QLabel(
            'Gain V: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_gain_v = SiriusSpinbox(
            self, self.devpref.substitute(propty='LoopGainV-SP'))
        lb_gain_v = SiriusLabel(
            self, self.devpref.substitute(propty='LoopGainV-RB'))
        lb_gain_mon_v = SiriusLabel(
            self, self.devpref.substitute(propty='LoopGainV-Mon'))

        wid = QGroupBox('Loop')
        lay = QGridLayout(wid)
        lay.addWidget(QLabel('<h4>SP</h4>'), 0, 1, alignment=Qt.AlignCenter)
        lay.addWidget(QLabel('<h4>RB</h4>'), 0, 2, alignment=Qt.AlignCenter)
        lay.addWidget(QLabel('<h4>Mon</h4>'), 0, 3, alignment=Qt.AlignCenter)
        lay.addWidget(ld_enbl, 1, 0)
        lay.addWidget(sb_enbl, 1, 1)
        lay.addWidget(lb_enbl, 1, 2)
        lay.addWidget(ld_gain_h, 2, 0)
        lay.addWidget(sb_gain_h, 2, 1)
        lay.addWidget(lb_gain_h, 2, 2)
        lay.addWidget(lb_gain_mon_h, 2, 3)
        lay.addWidget(ld_gain_v, 3, 0)
        lay.addWidget(sb_gain_v, 3, 1)
        lay.addWidget(lb_gain_v, 3, 2)
        lay.addWidget(lb_gain_mon_v, 3, 3)
        return wid

    def _setupAuxCommWidget(self):
        ld_orbdist = QLabel(
            'Orbit Dist. Detec.: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_orbdist = PyDMStateButton(
            self, self.devpref.substitute(
                propty='LoopMaxOrbDistortionEnbl-Sel'))
        lb_orbdist = SiriusLedState(
            self, self.devpref.substitute(
                propty='LoopMaxOrbDistortionEnbl-Sts'))

        self.ch_currzero = _ConnSignal(
            self.devpref.substitute(propty='CorrSetCurrZero-Cmd'))
        self.ch_clearacc = _ConnSignal(
            self.devpref.substitute(propty='CorrSetAccClear-Cmd'))
        btn_zero = CAPushButton('Reset Correctors current and Acc', self)
        btn_zero.setDefault(False)
        btn_zero.setAutoDefault(False)
        btn_zero.rules = self._enblrule
        btn_zero.clicked.connect(self._handle_reset_correctors)

        wid = QGroupBox('Aux. Commands')
        lay = QGridLayout(wid)
        lay.addWidget(btn_zero, 0, 0, 1, 3)
        lay.addWidget(ld_orbdist, 1, 0)
        lay.addWidget(sb_orbdist, 1, 1)
        lay.addWidget(lb_orbdist, 1, 2)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 1)
        lay.setColumnStretch(2, 1)
        return wid

    def _setupDetailsWidget(self):
        group2cmd = {
            'Correctors': {
                'Set all current to zero': 'CorrSetCurrZero-Cmd',
                'Clear all Acc': 'CorrSetAccClear-Cmd',
                'Set all PwrState to On': 'CorrSetPwrStateOn-Cmd',
                'Set all PwrState to Off': 'CorrSetPwrStateOff-Cmd',
                'Set all OpMode to Manual': 'CorrSetOpModeManual-Cmd',
                'Set all AccFreeze to Enbl': 'CorrSetAccFreezeEnbl-Cmd',
                'Set all AccFreeze to Dsbl': 'CorrSetAccFreezeDsbl-Cmd',
            },
            'Controllers': {
                'Sync Net': 'CtrlrSyncNet-Cmd',
                'Sync RefOrb': 'CtrlrSyncRefOrb-Cmd',
            },
            'BPMs': {
                'Configure BPM Log.Trigs.': 'CtrlrConfBPMLogTrg-Cmd',
            },
        }
        wid = QWidget()
        lay = QVBoxLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        for group, commands in group2cmd.items():
            gbox = QGroupBox(group)
            glay = QVBoxLayout(gbox)

            if 'Corr' in group:
                glay2 = QGridLayout()
                glay2.setContentsMargins(0, 0, 0, 0)

                for row, dev in enumerate(['CH', 'CV']):
                    lbl = QLabel(
                        dev+' Sat. Limit [A]: ', self,
                        alignment=Qt.AlignRight | Qt.AlignVCenter)
                    pref = self.devpref
                    spw = SiriusSpinbox(
                        self, pref.substitute(propty=dev+'AccSatMax-SP'))
                    rbw = SiriusLabel(
                        self, pref.substitute(propty=dev+'AccSatMax-RB'))
                    glay2.addWidget(lbl, row, 0)
                    glay2.addWidget(spw, row, 1)
                    glay2.addWidget(rbw, row, 2)

                lbl = QLabel(
                    'Curr. Ramp Down Dur. [s]: ', self,
                    alignment=Qt.AlignRight | Qt.AlignVCenter)
                pref = self.devpref
                spw = SiriusSpinbox(
                    self, pref.substitute(propty='CorrSetCurrZeroDuration-SP'))
                rbw = SiriusLabel(
                    self, pref.substitute(propty='CorrSetCurrZeroDuration-RB'))
                glay2.addWidget(lbl, 2, 0)
                glay2.addWidget(spw, 2, 1)
                glay2.addWidget(rbw, 2, 2)

                lbl = QLabel(
                    'Decimation [count]: ', self,
                    alignment=Qt.AlignRight | Qt.AlignVCenter)
                pref = self.devpref
                visrule = (
                    '[{"name": "VisRule", "property": "Visible", ' +
                    '"expression": "ch[0] == 2", "channels": ' +
                    '[{"channel": "' +
                    pref.substitute(propty='FOFBAccDecimation-Sel') +
                    '", "trigger": true}]}]')
                selw = SiriusEnumComboBox(
                    self, pref.substitute(propty='FOFBAccDecimation-Sel'))
                stsw = SiriusLabel(
                    self, pref.substitute(propty='FOFBAccDecimation-Sts'))
                stsw.rules = visrule.replace('==', '!=')
                lbldiv = CALabel(':')
                lbldiv.rules = visrule
                spw = SiriusSpinbox(
                    self, pref.substitute(propty='FOFBAccDecimation-SP'))
                spw.rules = visrule
                spw.setVisible(False)
                lblpro = CALabel('(')
                lblpro.rules = visrule.replace('==', '!=')
                rbw = SiriusLabel(
                    self, pref.substitute(propty='FOFBAccDecimation-RB'))
                rbw.setStyleSheet('min-width: 4em;')
                rbw.setAlignment(Qt.AlignCenter)
                lblprc = CALabel(')')
                lblprc.rules = visrule.replace('==', '!=')
                hbox = QHBoxLayout()
                hbox.addWidget(selw)
                hbox.addWidget(stsw)
                hbox.addWidget(lbldiv)
                hbox.addWidget(spw)
                hbox.addWidget(lblpro)
                hbox.addWidget(rbw)
                hbox.addWidget(lblprc)
                glay2.addWidget(lbl, 3, 0)
                glay2.addLayout(hbox, 3, 1, 1, 2)

                ld_psconfig = QLabel(
                    'PS Config. Matrix: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
                wid_psconfig = PSConfigWidget(self, self.device, prefix=self.prefix)
                glay2.addWidget(ld_psconfig, 4, 0)
                glay2.addWidget(wid_psconfig, 4, 1, 2, 2)

                glay.addLayout(glay2)

            elif 'Control' in group:
                glay2 = QGridLayout()
                glay2.setContentsMargins(0, 0, 0, 0)

                pref = self.devpref
                lbl = QLabel(
                    'TimeFrameLen: ', self,
                    alignment=Qt.AlignRight | Qt.AlignVCenter)
                spw = SiriusSpinbox(
                    self, pref.substitute(propty='TimeFrameLen-SP'))
                rbw = SiriusLabel(
                    self, pref.substitute(propty='TimeFrameLen-RB'))
                glay2.addWidget(lbl, 0, 0)
                glay2.addWidget(spw, 0, 1)
                glay2.addWidget(rbw, 0, 2)

                lbl = QLabel(
                    'Consider EnblList in Sync: ', self,
                    alignment=Qt.AlignRight | Qt.AlignVCenter)
                pvn = pref.substitute(propty='CtrlrSyncUseEnblList-Sel')
                sbt = PyDMStateButton(self, pvn)
                sbt.rules = self._enblrule
                led = SiriusLedState(self, pvn.substitute(propty_suffix='Sts'))
                glay2.addWidget(lbl, 1, 0)
                glay2.addWidget(sbt, 1, 1)
                glay2.addWidget(led, 1, 2)

                lbl = QLabel(
                    'Orbit Dist. Thres. [um]: ', self,
                    alignment=Qt.AlignRight | Qt.AlignVCenter)
                spw = SiriusSpinbox(
                    self, pref.substitute(propty='LoopMaxOrbDistortion-SP'))
                rbw = SiriusLabel(
                    self, pref.substitute(propty='LoopMaxOrbDistortion-RB'))
                glay2.addWidget(lbl, 2, 0)
                glay2.addWidget(spw, 2, 1)
                glay2.addWidget(rbw, 2, 2)

                lbl = QLabel(
                    'Enable Orbit Dist. Detec.: ', self,
                    alignment=Qt.AlignRight | Qt.AlignVCenter)
                pvn = pref.substitute(propty='LoopMaxOrbDistortionEnbl-Sel')
                sbt = PyDMStateButton(self, pvn)
                led = SiriusLedState(self, pvn.substitute(propty_suffix='Sts'))
                glay2.addWidget(lbl, 3, 0)
                glay2.addWidget(sbt, 3, 1)
                glay2.addWidget(led, 3, 2)

                lbl = QLabel(
                    'Enable Packet Loss Detec.: ', self,
                    alignment=Qt.AlignRight | Qt.AlignVCenter)
                pvn = pref.substitute(propty='LoopPacketLossDetecEnbl-Sel')
                sbt = PyDMStateButton(self, pvn)
                led = SiriusLedState(self, pvn.substitute(propty_suffix='Sts'))
                glay2.addWidget(lbl, 4, 0)
                glay2.addWidget(sbt, 4, 1)
                glay2.addWidget(led, 4, 2)

                glay.addLayout(glay2)
            elif 'BPM' in group:
                swbpm = BPMSwModeWidget(self, self.device, self.prefix)
                glay.addWidget(swbpm)

            for desc, cmd in commands.items():
                btn = PyDMPushButton(
                    self, label=desc, pressValue=1,
                    init_channel=self.devpref.substitute(propty=cmd))
                btn.setDefault(False)
                btn.setAutoDefault(False)
                btn.rules = self._enblrule
                glay.addWidget(btn)
            lay.addWidget(gbox)
        return wid

    def _setupControlWidget(self):
        self.controltabs = QTabWidget()
        self.controltabs.setObjectName('SITab')

        # tab main
        self.status = self._setupStatusWidget()

        self.loop = self._setupLoopWidget()

        self.auxcmd = self._setupAuxCommWidget()

        self.reforb = self._setupRefOrbWidget()

        self.respmat = RespMatWidget(self, self.device, self.prefix)

        maintab = QWidget()
        lay = QVBoxLayout(maintab)
        lay.addWidget(self.status)
        lay.addWidget(self.loop)
        lay.addWidget(self.auxcmd)
        lay.addWidget(self.reforb)
        lay.addWidget(self.respmat)
        self.controltabs.addTab(maintab, 'Main')

        # tab aux
        self.details = self._setupDetailsWidget()

        dettab = QWidget()
        lay = QVBoxLayout(dettab)
        lay.addWidget(self.details)
        self.controltabs.addTab(dettab, 'Details')

        wid = QWidget()
        lay = QVBoxLayout(wid)
        lay.addWidget(self.controltabs)

        # dock widget
        dockwid = QDockWidget(self)
        dockwid.setObjectName('SIApp')
        dockwid.setWindowTitle('FOFB Control')
        sz_pol = QSzPlcy(QSzPlcy.Preferred, QSzPlcy.Preferred)
        sz_pol.setVerticalStretch(1)
        dockwid.setSizePolicy(sz_pol)
        dockwid.setFloating(False)
        dockwid.setFeatures(QDockWidget.AllDockWidgetFeatures)
        dockwid.setAllowedAreas(Qt.AllDockWidgetAreas)
        dockwid.setWidget(wid)
        return dockwid

    def _setupLogWidget(self):
        loglabel = PyDMLogLabel(
            self, init_channel=self.devpref.substitute(propty='Log-Mon'))
        loglabel.setObjectName('log')
        loglabel.setStyleSheet('#log{min-width: 20em;}')
        loglabel.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.MinimumExpanding)
        loglabel.setAlternatingRowColors(True)
        loglabel.maxCount = 2000

        bt_clear = QPushButton('Clear Log', self)
        bt_clear.clicked.connect(loglabel.clear)

        wid = QWidget()
        lay = QVBoxLayout(wid)
        lay.addWidget(loglabel)
        lay.addWidget(bt_clear, alignment=Qt.AlignCenter)

        dockwid = QDockWidget(self)
        dockwid.setObjectName('SIApp')
        dockwid.setWindowTitle("FOFB Log")
        sz_pol = QSzPlcy(QSzPlcy.Preferred, QSzPlcy.Preferred)
        sz_pol.setVerticalStretch(1)
        dockwid.setSizePolicy(sz_pol)
        dockwid.setFloating(False)
        dockwid.setFeatures(QDockWidget.AllDockWidgetFeatures)
        dockwid.setAllowedAreas(Qt.AllDockWidgetAreas)
        dockwid.setWidget(wid)
        return dockwid

    def _handle_reset_correctors(self):
        self.ch_clearacc.send_value_signal[float].emit(1)
        _time.sleep(0.5)
        self.ch_currzero.send_value_signal[float].emit(1)
