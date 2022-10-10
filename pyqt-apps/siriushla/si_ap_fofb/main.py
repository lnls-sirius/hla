"""High level FOFB main module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton, QWidget, QGridLayout, \
    QLabel, QVBoxLayout, QGroupBox, QMenuBar, QAction
import qtawesome as qta

from pydm.widgets import PyDMPushButton

from siriuspy.fofb.csdev import ETypes as _FOFBEnums
from siriushla.widgets.led import SiriusLedState

from ..util import connect_window, get_appropriate_color
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    PyDMLogLabel, SiriusMainWindow, PyDMStateButton

from .base import BaseObject
from .custom_widgets import RefOrbWidget, StatusDialog, AuxCommDialog
from .respmat import RespMatWidget


class MainWindow(BaseObject, SiriusMainWindow):
    """FOFB RespMat widget."""

    def __init__(self, parent=None, prefix='', device=''):
        BaseObject.__init__(self, device, prefix=prefix)
        SiriusMainWindow.__init__(self, parent)
        self.setWindowTitle('SI - FOFB')
        self.setObjectName('SIApp')
        self.setWindowIcon(
            qta.icon(
                'fa5s.hammer', 'fa5s.signal',
                options=[
                    dict(scale_factor=0.85, offset=(0.15, 0.0)),
                    dict(scale_factor=0.7, offset=(0.0, 0.25),
                         rotated=90, vflip=True)],
                color=get_appropriate_color('SI')))
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        # layout
        self.status = self._setupStatusWidget()

        self.reforb = self._setupRefOrbWidget()

        self.respmat = RespMatWidget(self, self.device, self.prefix)

        self.loop = self._setupLoopWidget()

        self.log = self._setupLogWidget()

        cwid = QWidget()
        layout = QGridLayout(cwid)
        layout.addWidget(self.log, 0, 0, 4, 1)
        layout.addWidget(self.status, 0, 1)
        layout.addWidget(self.loop, 1, 1)
        layout.addWidget(self.reforb, 2, 1)
        layout.addWidget(self.respmat, 3, 1)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)
        self.setCentralWidget(cwid)

        # menu
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        auxcomm_act = QAction('Auxiliary commands', menubar)
        connect_window(
            auxcomm_act, AuxCommDialog, parent=self,
            device=self.device, prefix=self.prefix)
        menubar.addAction(auxcomm_act)

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
            self, self.devpref.substitute(propty='FOFBCtrlStatus-Mon'))
        sts_ctrl = QPushButton('', self)
        sts_ctrl.setIcon(qta.icon('fa5s.list-ul'))
        sts_ctrl.setToolTip('Open Detailed Status View')
        sts_ctrl.setObjectName('sts')
        sts_ctrl.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        pvname = self.devpref.substitute(propty='FOFBCtrlStatus-Mon')
        labels = _FOFBEnums.STS_LBLS_FOFBCTRL
        cmds = [None]*len(labels)
        cmds[2] = self.devpref.substitute(propty='FOFBCtrlSyncNet-Cmd')
        cmds[4] = self.devpref.substitute(propty='FOFBCtrlSyncRefOrb-Cmd')
        cmds[5] = self.devpref.substitute(propty='FOFBCtrlConfTFrameLen-Cmd')
        cmds[6] = self.devpref.substitute(propty='FOFBCtrlConfBPMLogTrg-Cmd')
        connect_window(
            sts_ctrl, StatusDialog, parent=self, pvname=pvname, labels=labels,
            cmds=cmds, title='FOFB Controller Status')

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

        ld_gain = QLabel(
            'Gain: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_gain = SiriusSpinbox(
            self, self.devpref.substitute(propty='LoopGain-SP'))
        sb_gain.showStepExponent = False
        lb_gain = SiriusLabel(
            self, self.devpref.substitute(propty='LoopGain-RB'))

        ld_gain_mon = QLabel(
            'Impl.Gain: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lb_gain_mon = SiriusLabel(
            self, self.devpref.substitute(propty='LoopGain-Mon'))

        wid = QGroupBox('Loop')
        lay = QGridLayout(wid)
        lay.addWidget(ld_enbl, 0, 0)
        lay.addWidget(sb_enbl, 0, 1)
        lay.addWidget(lb_enbl, 0, 2, alignment=Qt.AlignLeft)
        lay.addWidget(ld_gain, 1, 0)
        lay.addWidget(sb_gain, 1, 1)
        lay.addWidget(lb_gain, 1, 2)
        lay.addWidget(ld_gain_mon, 2, 0)
        lay.addWidget(lb_gain_mon, 2, 1)
        return wid

    def _setupLogWidget(self):
        loglabel = PyDMLogLabel(
            self, init_channel=self.devpref.substitute(propty='Log-Mon'))
        loglabel.setAlternatingRowColors(True)
        loglabel.maxCount = 2000

        bt_clear = QPushButton('Clear Log', self)
        bt_clear.clicked.connect(loglabel.clear)

        wid = QWidget()
        lay = QVBoxLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(loglabel)
        lay.addWidget(bt_clear, alignment=Qt.AlignCenter)
        return wid
