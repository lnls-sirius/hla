"""Window to test power supplies."""
import sys
import re as _re
from functools import partial as _part

from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QSizePolicy, QGroupBox, QPushButton, QListWidget, QLabel, QApplication, \
    QMessageBox, QTabWidget, QWidget
import qtawesome as qta

from siriuspy.search import PSSearch
from siriuspy.namesys import SiriusPVName as PVName

from siriushla.util import get_appropriate_color, connect_newprocess, \
    run_newprocess
from siriushla.widgets import SiriusMainWindow, PVNameTree
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets.dialog import ProgressDialog
from siriushla.as_ti_control import HLTriggerDetailed

from .tasks import CreateTesters, \
    CheckStatus, \
    ResetIntlk, CheckIntlk, \
    SetSOFBMode, CheckSOFBMode, \
    SetOpModeSlowRef, CheckOpModeSlowRef, CheckOpModeInit, \
    SetPwrState, CheckPwrState, CheckInitOk, \
    SetPulse, CheckPulse, \
    CheckCtrlLoop, \
    SetCapBankVolt, CheckCapBankVolt, \
    SetCurrent, CheckCurrent, \
    SetVoltage, CheckVoltage, \
    SetTriggerState, CheckTriggerState


class PSTestWindow(SiriusMainWindow):
    """PS test window."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setWindowTitle('PS/PU Test')
        self.setObjectName('ASApp')
        cor = get_appropriate_color(section='AS')
        self.setWindowIcon(qta.icon('mdi.test-tube', color=cor))

        self._si_fam_psnames = PSSearch.get_psnames(
            filters={'sec': 'SI', 'sub': 'Fam', 'dis': 'PS'})
        self._needs_update_setup = False
        self._setup_ui()
        self._update_setup_timer = QTimer(self)
        self._update_setup_timer.timeout.connect(self._update_setup)
        self._update_setup_timer.setInterval(250)
        self._update_setup_timer.start()

    def _setup_ui(self):
        # setup central widget
        self.central_widget = QFrame()
        self.central_widget.setStyleSheet("""
            #OkList {
                background-color: #eafaea;
            }
            #NokList {
                background-color: #ffebe6;
            }
            QLabel{
                max-height: 1.29em;
            }
            QTabWidget::pane {
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        self.setCentralWidget(self.central_widget)

        self.tab = QTabWidget(self)
        self.tab.setObjectName('ASTab')

        # # PS
        self.ps_wid = QWidget(self)
        lay_ps = QGridLayout(self.ps_wid)
        lay_ps.setContentsMargins(0, 9, 0, 0)
        lay_ps.setHorizontalSpacing(0)

        # PS selection
        self.ps_tree = PVNameTree(
            items=self._get_ps_tree_names(),
            tree_levels=('sec', 'mag_group'), parent=self)
        self.ps_tree.tree.setHeaderHidden(True)
        self.ps_tree.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.ps_tree.tree.setColumnCount(1)
        self.ps_tree.tree.doubleClicked.connect(self._open_detail)
        self.ps_tree.tree.itemChanged.connect(
            self._handle_checked_items_changed)

        gbox_ps_select = QGroupBox('Select PS: ', self)
        gbox_ps_select.setObjectName('select')
        gbox_ps_select.setStyleSheet("""
            #select{
                border-top: 0px solid transparent;
                border-left: 0px solid transparent;
                border-bottom: 0px solid transparent;
            }""")
        lay_ps_select = QVBoxLayout(gbox_ps_select)
        lay_ps_select.addWidget(self.ps_tree)
        lay_ps.addWidget(gbox_ps_select, 0, 0)
        lay_ps.setColumnStretch(0, 1)

        # PS commands
        self.checkstatus_ps_bt = QPushButton('Show Status Summary', self)
        self.checkstatus_ps_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.checkstatus_ps_bt.clicked.connect(_part(self._check_status, 'PS'))
        self.checkstatus_ps_bt.setToolTip(
            'Check PS and DCLinks interlock status and, if powered on, '
            'check if it is following reference')

        self.dsbltrigger_ps_bt = QPushButton('Disable PS triggers', self)
        self.dsbltrigger_ps_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.dsbltrigger_ps_bt.clicked.connect(
            _part(self._set_check_trigger_state, 'PS', 'dsbl'))

        self.setsofbmode_ps_bt = QPushButton('Turn Off SOFBMode', self)
        self.setsofbmode_ps_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.setsofbmode_ps_bt.clicked.connect(
            _part(self._set_check_fbp_sofmode, 'off'))

        self.setslowref_ps_bt = QPushButton(
            'Set PS and DCLinks to SlowRef', self)
        self.setslowref_ps_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.setslowref_ps_bt.clicked.connect(self._set_check_opmode)

        self.currzero_ps_bt1 = QPushButton('Set PS Current to zero', self)
        self.currzero_ps_bt1.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.currzero_ps_bt1.clicked.connect(self._set_zero_ps)

        self.reset_ps_bt = QPushButton('Reset PS and DCLinks', self)
        self.reset_ps_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.reset_ps_bt.clicked.connect(_part(self._reset_intlk, 'PS'))

        self.init_sips_bt = QPushButton('Initialize SI Fam PS', self)
        self.init_sips_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.init_sips_bt.clicked.connect(self._set_check_pwrstateinit)
        self.init_sips_bt.setVisible(False)

        self.turnon_dcl_bt = QPushButton('Turn DCLinks On', self)
        self.turnon_dcl_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.turnon_dcl_bt.clicked.connect(
            _part(self._set_check_pwrstate_dclinks, 'on'))

        self.checkctrlloop_dcl_bt = QPushButton('Check DCLinks CtrlLoop', self)
        self.checkctrlloop_dcl_bt.clicked.connect(
            _part(self._set_lastcomm, 'PS'))
        self.checkctrlloop_dcl_bt.clicked.connect(
            _part(self._check_ctrlloop, 'dclink'))

        self.setvolt_dcl_bt = QPushButton('Set DCLinks Voltage', self)
        self.setvolt_dcl_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.setvolt_dcl_bt.clicked.connect(
            self._set_check_dclinks_capvolt)

        self.turnon_ps_bt = QPushButton('Turn PS On', self)
        self.turnon_ps_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.turnon_ps_bt.clicked.connect(
            _part(self._set_check_pwrstate, 'PS', 'on'))

        self.checkctrlloop_ps_bt = QPushButton('Check PS CtrlLoop', self)
        self.checkctrlloop_ps_bt.clicked.connect(
            _part(self._set_lastcomm, 'PS'))
        self.checkctrlloop_ps_bt.clicked.connect(
            _part(self._check_ctrlloop, 'pwrsupply'))

        self.test_ps_bt = QPushButton('Set PS Current to test value', self)
        self.test_ps_bt.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.test_ps_bt.clicked.connect(self._set_test_ps)

        self.currzero_ps_bt2 = QPushButton('Set PS Current to zero', self)
        self.currzero_ps_bt2.clicked.connect(_part(self._set_lastcomm, 'PS'))
        self.currzero_ps_bt2.clicked.connect(self._set_zero_ps)

        self.restoretrigger_ps_bt = QPushButton('Restore PS triggers', self)
        self.restoretrigger_ps_bt.clicked.connect(
            _part(self._set_lastcomm, 'PS'))
        self.restoretrigger_ps_bt.clicked.connect(
            _part(self._restore_triggers_state, 'PS'))

        gbox_ps_comm = QGroupBox('Commands', self)
        gbox_ps_comm.setObjectName('comm')
        gbox_ps_comm.setStyleSheet('#comm{border: 0px solid transparent;}')
        lay_ps_comm = QVBoxLayout(gbox_ps_comm)
        lay_ps_comm.setContentsMargins(20, 9, 20, 9)
        lay_ps_comm.addWidget(QLabel(''))
        lay_ps_comm.addWidget(QLabel('<h4>Check</h4>', self,
                                     alignment=Qt.AlignCenter))
        lay_ps_comm.addWidget(self.checkstatus_ps_bt)
        lay_ps_comm.addWidget(QLabel(''))
        lay_ps_comm.addWidget(QLabel('<h4>Prepare</h4>', self,
                                     alignment=Qt.AlignCenter))
        lay_ps_comm.addWidget(self.dsbltrigger_ps_bt)
        lay_ps_comm.addWidget(self.setsofbmode_ps_bt)
        lay_ps_comm.addWidget(self.setslowref_ps_bt)
        lay_ps_comm.addWidget(self.currzero_ps_bt1)
        lay_ps_comm.addWidget(self.reset_ps_bt)
        lay_ps_comm.addWidget(self.init_sips_bt)
        lay_ps_comm.addWidget(QLabel(''))
        lay_ps_comm.addWidget(QLabel('<h4>Config DCLinks</h4>', self,
                                     alignment=Qt.AlignCenter))
        lay_ps_comm.addWidget(self.turnon_dcl_bt)
        lay_ps_comm.addWidget(self.checkctrlloop_dcl_bt)
        lay_ps_comm.addWidget(self.setvolt_dcl_bt)
        lay_ps_comm.addWidget(QLabel(''))
        lay_ps_comm.addWidget(QLabel('<h4>Test</h4>', self,
                                     alignment=Qt.AlignCenter))
        lay_ps_comm.addWidget(self.turnon_ps_bt)
        lay_ps_comm.addWidget(self.checkctrlloop_ps_bt)
        lay_ps_comm.addWidget(self.test_ps_bt)
        lay_ps_comm.addWidget(self.currzero_ps_bt2)
        lay_ps_comm.addWidget(QLabel(''))
        lay_ps_comm.addWidget(QLabel('<h4>Restore</h4>', self,
                                     alignment=Qt.AlignCenter))
        lay_ps_comm.addWidget(self.restoretrigger_ps_bt)
        lay_ps_comm.addWidget(QLabel(''))
        lay_ps.addWidget(gbox_ps_comm, 0, 1)
        lay_ps.setColumnStretch(1, 1)

        self.tab.addTab(self.ps_wid, 'PS')

        # # PU
        self.pu_wid = QWidget(self)
        lay_pu = QGridLayout(self.pu_wid)
        lay_pu.setContentsMargins(0, 9, 0, 0)
        lay_pu.setHorizontalSpacing(0)

        # PU selection
        self.pu_tree = PVNameTree(
            items=self._get_pu_tree_names(),
            tree_levels=('sec', ), parent=self)
        self.pu_tree.tree.setHeaderHidden(True)
        self.pu_tree.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.pu_tree.tree.setColumnCount(1)
        self.pu_tree.tree.doubleClicked.connect(self._open_detail)

        gbox_pu_select = QGroupBox('Select PU: ', self)
        gbox_pu_select.setObjectName('select')
        gbox_pu_select.setStyleSheet("""
            #select{
                border-top: 0px solid transparent;
                border-left: 0px solid transparent;
                border-bottom: 0px solid transparent;
            }""")
        lay_pu_select = QVBoxLayout(gbox_pu_select)
        lay_pu_select.addWidget(self.pu_tree)
        lay_pu.addWidget(gbox_pu_select, 0, 0)
        lay_pu.setColumnStretch(0, 1)

        # PU commands
        self.checkstatus_pu_bt = QPushButton('Show Status Summary', self)
        self.checkstatus_pu_bt.clicked.connect(_part(self._set_lastcomm, 'PU'))
        self.checkstatus_pu_bt.clicked.connect(_part(self._check_status, 'PU'))
        self.checkstatus_pu_bt.setToolTip(
            'Check PU interlock status and, if powered on, '
            'check if it is following voltage setpoint')

        self.voltzero_pu_bt1 = QPushButton('Set PU Voltage to zero', self)
        self.voltzero_pu_bt1.clicked.connect(_part(self._set_lastcomm, 'PU'))
        self.voltzero_pu_bt1.clicked.connect(_part(self._set_zero_pu, False))

        self.reset_pu_bt = QPushButton('Reset PU', self)
        self.reset_pu_bt.clicked.connect(_part(self._set_lastcomm, 'PU'))
        self.reset_pu_bt.clicked.connect(_part(self._reset_intlk, 'PU'))

        self.turnon_pu_bt = QPushButton('Turn PU On', self)
        self.turnon_pu_bt.clicked.connect(_part(self._set_lastcomm, 'PU'))
        self.turnon_pu_bt.clicked.connect(
            _part(self._set_check_pwrstate, 'PU', 'on'))

        self.enblpulse_pu_bt = QPushButton('Enable PU Pulse', self)
        self.enblpulse_pu_bt.clicked.connect(_part(self._set_lastcomm, 'PU'))
        self.enblpulse_pu_bt.clicked.connect(
            _part(self._set_check_pulse, 'on'))

        self.enbltrigger_pu_bt = QPushButton('Enable PU triggers', self)
        self.enbltrigger_pu_bt.clicked.connect(_part(self._set_lastcomm, 'PU'))
        self.enbltrigger_pu_bt.clicked.connect(
            _part(self._set_check_trigger_state, 'PU', 'on'))

        self.test_pu_bt = QPushButton('Set PU Voltage to test value', self)
        self.test_pu_bt.clicked.connect(_part(self._set_lastcomm, 'PU'))
        self.test_pu_bt.clicked.connect(self._set_test_pu)

        self.voltzero_pu_bt2 = QPushButton('Set PU Voltage to zero', self)
        self.voltzero_pu_bt2.clicked.connect(_part(self._set_lastcomm, 'PU'))
        self.voltzero_pu_bt2.clicked.connect(_part(self._set_zero_pu, True))

        self.restoretrigger_pu_bt = QPushButton('Restore PU triggers', self)
        self.restoretrigger_pu_bt.clicked.connect(
            _part(self._set_lastcomm, 'PU'))
        self.restoretrigger_pu_bt.clicked.connect(
            _part(self._restore_triggers_state, 'PU'))

        gbox_pu_comm = QGroupBox('Commands', self)
        gbox_pu_comm.setObjectName('comm')
        gbox_pu_comm.setStyleSheet('#comm{border: 0px solid transparent;}')
        lay_pu_comm = QVBoxLayout(gbox_pu_comm)
        lay_pu_comm.setContentsMargins(20, 9, 20, 9)
        lay_pu_comm.addWidget(QLabel(''))
        lay_pu_comm.addWidget(QLabel('<h4>Check</h4>', self,
                                     alignment=Qt.AlignCenter))
        lay_pu_comm.addWidget(self.checkstatus_pu_bt)
        lay_pu_comm.addWidget(QLabel(''))
        lay_pu_comm.addWidget(QLabel('<h4>Prepare</h4>', self,
                                     alignment=Qt.AlignCenter))
        lay_pu_comm.addWidget(self.voltzero_pu_bt1)
        lay_pu_comm.addWidget(self.reset_pu_bt)
        lay_pu_comm.addWidget(QLabel(''))
        lay_pu_comm.addWidget(QLabel('<h4>Test</h4>', self,
                                     alignment=Qt.AlignCenter))
        lay_pu_comm.addWidget(self.turnon_pu_bt)
        lay_pu_comm.addWidget(self.enblpulse_pu_bt)
        lay_pu_comm.addWidget(self.enbltrigger_pu_bt)
        lay_pu_comm.addWidget(self.test_pu_bt)
        lay_pu_comm.addWidget(self.voltzero_pu_bt2)
        lay_pu_comm.addWidget(QLabel(''))
        lay_pu_comm.addWidget(QLabel('<h4>Restore</h4>', self,
                                     alignment=Qt.AlignCenter))
        lay_pu_comm.addWidget(self.restoretrigger_pu_bt)
        lay_pu_comm.addWidget(QLabel(''))
        lay_pu.addWidget(gbox_pu_comm, 0, 1)
        lay_pu.setColumnStretch(1, 1)

        self.tab.addTab(self.pu_wid, 'PU')

        # lists
        self.label_lastcomm = QLabel('Last Command: ', self)
        self.ok_ps = QListWidget(self)
        self.ok_ps.setObjectName('OkList')
        self.ok_ps.doubleClicked.connect(self._open_detail)
        self.nok_ps = QListWidget(self)
        self.nok_ps.setObjectName('NokList')
        self.nok_ps.doubleClicked.connect(self._open_detail)
        self.clearlists_bt = QPushButton('Clear', self)
        self.clearlists_bt.clicked.connect(self._clear_lastcomm)
        self.ok_ps_aux_list = list()
        self.nok_ps_aux_list = list()
        hbox = QHBoxLayout()
        hbox.addWidget(self.label_lastcomm)
        hbox.addWidget(self.clearlists_bt, alignment=Qt.AlignRight)
        list_layout = QGridLayout()
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setVerticalSpacing(6)
        list_layout.setHorizontalSpacing(9)
        list_layout.addLayout(hbox, 0, 0, 1, 2)
        list_layout.addWidget(QLabel('<h4>Ok</h4>', self,
                                     alignment=Qt.AlignCenter), 1, 0)
        list_layout.addWidget(self.ok_ps, 2, 0)
        list_layout.addWidget(QLabel('<h4>Failed</h4>', self,
                                     alignment=Qt.AlignCenter), 1, 1)
        list_layout.addWidget(self.nok_ps, 2, 1)

        # menu
        self.menu = self.menuBar()
        self.act_cycle = self.menu.addAction('Open Cycle Window')
        connect_newprocess(
            self.act_cycle, 'sirius-hla-as-ps-cycle.py', parent=self)
        self.aux_comm = self.menu.addMenu('Auxiliary commands')

        self.act_turnoff_ps = self.aux_comm.addAction('Turn PS Off')
        self.act_turnoff_ps.triggered.connect(_part(self._set_lastcomm, 'PS'))
        self.act_turnoff_ps.triggered.connect(
            _part(self._set_check_pwrstate, 'PS', 'off'))

        self.act_turnoff_dclink = self.aux_comm.addAction('Turn DCLinks Off')
        self.act_turnoff_dclink.triggered.connect(
            _part(self._set_lastcomm, 'PS'))
        self.act_turnoff_dclink.triggered.connect(
            _part(self._set_check_pwrstate_dclinks, 'off'))

        self.act_turnoff_pu = self.aux_comm.addAction('Turn PU Off')
        self.act_turnoff_pu.triggered.connect(
            _part(self._set_lastcomm, 'PU'))
        self.act_turnoff_pu.triggered.connect(
            _part(self._set_check_pwrstate, 'PU', 'off'))

        self.act_dsblpulse_pu = self.aux_comm.addAction('Disable PU Pulse')
        self.act_dsblpulse_pu.triggered.connect(
            _part(self._set_lastcomm, 'PU'))
        self.act_dsblpulse_pu.triggered.connect(
            _part(self._set_check_pulse, 'off'))

        # layout
        lay = QGridLayout()
        lay.setHorizontalSpacing(15)
        lay.setVerticalSpacing(5)
        lay.addWidget(QLabel(
            '<h3>Power Supplies Test</h3>', self, alignment=Qt.AlignCenter),
            0, 0, 1, 3)
        lay.addWidget(self.tab, 1, 0)
        lay.addLayout(list_layout, 1, 1)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 2)
        lay.setRowStretch(0, 2)
        lay.setRowStretch(1, 18)
        self.central_widget.setLayout(lay)

    # ---------- commands ------------

    def _check_status(self, dev_type):
        self.ok_ps.clear()
        self.nok_ps.clear()
        if dev_type == 'PS':
            devices = self._get_selected_ps()
            if not devices:
                return
            dclinks = self._get_related_dclinks(
                devices, include_regatrons=True)
            devices.extend(dclinks)
            label1 = 'Reading PS and DCLinks Status...'
        elif dev_type == 'PU':
            devices = self._get_selected_pu()
            if not devices:
                return
            label1 = 'Reading PU Status...'

        task0 = CreateTesters(devices, parent=self)
        task1 = CheckStatus(devices, parent=self)
        task1.itemDone.connect(self._log)

        labels = ['Connecting to devices...', label1]
        tasks = [task0, task1]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_trigger_state(self, dev_type, state):
        self.ok_ps.clear()
        self.nok_ps.clear()
        if dev_type == 'PS':
            devices = self._get_selected_ps()
        elif dev_type == 'PU':
            devices = self._get_selected_pu()
        if not devices:
            return

        task1 = SetTriggerState(
            parent=self, dis=dev_type, state=state, devices=devices)
        task2 = CheckTriggerState(
            parent=self, dis=dev_type, state=state, devices=devices)
        task2.itemDone.connect(self._log)
        tasks = [task1, task2]

        labels = ['Disabling '+dev_type+' triggers...',
                  'Checking '+dev_type+' trigger states...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_opmode(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return
        dclinks = self._get_related_dclinks(devices)
        devices.extend(dclinks)
        devices = [dev for dev in devices if 'LI-' not in dev]

        task0 = CreateTesters(devices, parent=self)
        task1 = SetOpModeSlowRef(devices, parent=self)
        task2 = CheckOpModeSlowRef(devices, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Connecting to devices...',
                  'Setting PS OpMode to SlowRef...',
                  'Checking PS OpMode...']
        tasks = [task0, task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _reset_intlk(self, dev_type):
        self.ok_ps.clear()
        self.nok_ps.clear()
        if dev_type == 'PS':
            devices = self._get_selected_ps()
            if not devices:
                return
            dclinks = self._get_related_dclinks(
                devices, include_regatrons=True)
            devices.extend(dclinks)
            dev_label = 'PS and DCLinks'
        elif dev_type == 'PU':
            devices = self._get_selected_pu()
            if not devices:
                return
            dev_label = 'PU'
        devices_wth_li = {dev for dev in devices if 'LI' not in dev}

        task0 = CreateTesters(devices, parent=self)
        task1 = ResetIntlk(devices_wth_li, parent=self)
        task2 = CheckIntlk(devices, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Reseting '+dev_label+'...',
                  'Checking '+dev_label+' Interlocks...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_pwrstate(self, dev_type, state):
        self.ok_ps.clear()
        self.nok_ps.clear()
        if dev_type == 'PS':
            devices = self._get_selected_ps()
            devices_wth_sifam = list(
                set(devices) - set(self._si_fam_psnames))
        elif dev_type == 'PU':
            devices = self._get_selected_pu()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetPwrState(devices_wth_sifam, state=state, parent=self)
        task2 = CheckPwrState(devices, state=state, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Turning '+dev_type+' '+state+'...',
                  'Checking '+dev_type+' powered '+state+'...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_pwrstateinit(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        selected = self._get_selected_ps()
        devices = [ps for ps in selected if ps in self._si_fam_psnames]
        dclinks = self._get_related_dclinks(devices, include_regatrons=True)
        if not devices:
            return

        # if power state is on, do nothing
        self._check_pwrstate(devices, state='on', show=False)
        if len(self.ok_ps_aux_list) == len(devices):
            for dev in self.ok_ps_aux_list:
                self._log(dev, True)
            self.ok_ps_aux_list = list()
            self.nok_ps_aux_list = list()
            return

        # if need initializing, check if DCLinks are turned off before continue
        self._check_pwrstate(dclinks, state='off', show=False)
        if len(self.nok_ps_aux_list) > 0:
            for dev in self.ok_ps_aux_list:
                self._log(dev, True)
            for dev in self.nok_ps_aux_list:
                self._log(dev, False)
            self.ok_ps_aux_list = list()
            self.nok_ps_aux_list = list()
            QMessageBox.critical(
                self, 'Message',
                'Make sure related DCLinks are turned\n'
                'off before initialize SI Fam PS!')
            return

        # then, initialize SI Fam PS
        task0 = CreateTesters(devices, parent=self)
        task1 = SetPwrState(devices, parent=self)
        task2 = CheckOpModeInit(devices, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Initializing SI Fam PS...',
                  'Checking SI Fam PS initilized...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_pulse(self, state):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_pu()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetPulse(devices, state=state, parent=self)
        task2 = CheckPulse(devices, state=state, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Turning PU Pulse '+state+'...',
                  'Checking PU Pulse '+state+'...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_pwrstate_dclinks(self, state):
        self.ok_ps.clear()
        self.nok_ps.clear()
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        devices, pwrsupplies2check = self._get_related_dclinks(
            pwrsupplies, include_regatrons=True, return_psnames=True)
        if not devices:
            return

        if state == 'off':
            self._check_pwrstate(pwrsupplies2check, state='off', show=False)
            if len(self.nok_ps_aux_list) > 0:
                for dev in self.ok_ps_aux_list:
                    self._log(dev, True)
                for dev in self.nok_ps_aux_list:
                    self._log(dev, False)
                self.ok_ps_aux_list = list()
                self.nok_ps_aux_list = list()
                QMessageBox.critical(
                    self, 'Message',
                    'Make sure all related power supplies\n'
                    'are turned off before turning DCLinks off!')
                return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetPwrState(devices, state=state, parent=self)
        task2 = CheckPwrState(devices, state=state, parent=self)
        tasks = [task0, task1, task2]

        labels = ['Connecting to DCLinks...',
                  'Turning DCLinks '+state+'...',
                  'Checking DCLinks powered '+state+'...']

        if state == 'on':
            task3 = CheckInitOk(devices, parent=self)
            task3.itemDone.connect(self._log)
            tasks.append(task3)
            labels.append('Wait DCLinks initialize...')
        else:
            task2.itemDone.connect(self._log)

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _check_pwrstate(self, devices, state, show=True):
        self.ok_ps.clear()
        self.nok_ps.clear()

        task0 = CreateTesters(devices, parent=self)
        task1 = CheckPwrState(devices, state=state, parent=self)
        task1.itemDone.connect(_part(self._log, show=show))
        tasks = [task0, task1]

        labels = ['Connecting to devices...',
                  'Checking devices powered '+state+'...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _check_ctrlloop(self, dev_type='pwrsupply'):
        self.ok_ps.clear()
        self.nok_ps.clear()
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        if dev_type == 'pwrsupply':
            devices = {dev for dev in pwrsupplies if 'LI' not in dev}
        else:
            devices = self._get_related_dclinks(pwrsupplies)
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = CheckCtrlLoop(devices, parent=self)
        task1.itemDone.connect(self._log)
        labels = ['Connecting to devices...',
                  'Checking CtrlLoop state...']
        tasks = [task0, task1]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_dclinks_capvolt(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        devices = self._get_related_dclinks(
            pwrsupplies, include_regatrons=True)
        dev_exc_regatrons = {
            dev for dev in devices
            if PSSearch.conv_psname_2_psmodel(dev) != 'REGATRON_DCLink'}
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetCapBankVolt(dev_exc_regatrons, parent=self)
        task2 = CheckCapBankVolt(devices, parent=self)
        task2.itemDone.connect(self._log)
        labels = ['Connecting to devices...',
                  'Setting capacitor bank voltage...',
                  'Checking capacitor bank voltage...']
        tasks = [task0, task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_fbp_sofmode(self, state):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        devices = [dev for dev in devices
                   if PSSearch.conv_psname_2_psmodel(dev) == 'FBP']
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetSOFBMode(devices, state=state, parent=self)
        task2 = CheckSOFBMode(devices, state=state, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Turning PS SOFBMode '+state+'...',
                  'Checking PS SOFBMode '+state+'...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_test_ps(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetCurrent(devices, is_test=True, parent=self)
        task2 = CheckCurrent(devices, is_test=True, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Testing PS... Setting current...',
                  'Testing PS... Checking current value...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_zero_ps(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetCurrent(devices, parent=self)
        task2 = CheckCurrent(devices, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Setting current to zero...',
                  'Checking current value...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_test_pu(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_pu()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetVoltage(devices, is_test=True, parent=self)
        task2 = CheckVoltage(devices, is_test=True, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Testing PU... Setting voltage...',
                  'Testing PU... Checking voltage value...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_zero_pu(self, check=True):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_pu()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetVoltage(devices, parent=self)
        tasks = [task0, task1]

        labels = ['Connecting to devices...',
                  'Setting voltage to zero...']

        if check:
            task2 = CheckVoltage(devices, parent=self)
            task2.itemDone.connect(self._log)
            tasks.append(task2)
            labels.append('Checking voltage value...')
        else:
            task1.itemDone.connect(self._log)

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _restore_triggers_state(self, dev_type):
        self.ok_ps.clear()
        self.nok_ps.clear()
        if dev_type == 'PS':
            devices = self._get_selected_ps()
        elif dev_type == 'PU':
            devices = self._get_selected_pu()
        if not devices:
            return

        task1 = SetTriggerState(
            parent=self, restore_initial_value=True, dis=dev_type,
            devices=devices)
        task2 = CheckTriggerState(
            parent=self, restore_initial_value=True, dis=dev_type,
            devices=devices)
        task2.itemDone.connect(self._log)
        tasks = [task1, task2]

        labels = ['Restoring '+dev_type+' trigger states...',
                  'Checking '+dev_type+' trigger states...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    # ---------- log updates -----------

    def _set_lastcomm(self, dev_type):
        sender_text = self.sender().text()
        self.label_lastcomm.setText(
            'Last Command: '+dev_type+' - '+sender_text)

    def _clear_lastcomm(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        self.label_lastcomm.setText('Last Command: ')

    def _log(self, name, status, show=True):
        if show:
            if status:
                self.ok_ps.addItem(name)
            else:
                self.nok_ps.addItem(name)
        else:
            if status:
                self.ok_ps_aux_list.append(name)
            else:
                self.nok_ps_aux_list.append(name)

    # ---------- devices control ----------

    def _get_ps_tree_names(self):
        # add LI, TB, BO, TS
        psnames = PSSearch.get_psnames({'sec': '(LI|TB|BO|TS)', 'dis': 'PS'})
        # add SI Fams
        psnames.extend(PSSearch.get_psnames(
            {'sec': 'SI', 'sub': 'Fam', 'dis': 'PS', 'dev': '(B.*|Q.*|S.*)'}))
        # add SI Corrs
        psnames.extend(PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '[0-2][0-9].*', 'dis': 'PS',
             'dev': '(CH|CV)'}))
        # add SI QTrims
        psnames.extend(PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '[0-2][0-9].*', 'dis': 'PS',
             'dev': '(QD.*|QF.*|Q[1-4])'}))
        # add SI QSkews
        psnames.extend(PSSearch.get_psnames(
            {'sec': 'SI', 'dis': 'PS', 'dev': 'QS'}))
        return psnames

    def _get_pu_tree_names(self):
        punames = PSSearch.get_psnames(
            {'sec': '(TB|BO|TS|SI)', 'dis': 'PU', 'dev': '.*(Kckr|Sept).*'})
        return punames

    def _get_selected_ps(self):
        devices = self.ps_tree.checked_items()
        if not devices:
            QMessageBox.critical(self, 'Message', 'No power supply selected!')
            return False
        return devices

    def _get_selected_pu(self):
        devices = self.pu_tree.checked_items()
        if not devices:
            QMessageBox.critical(
                self, 'Message', 'No pulsed power supply selected!')
            return False
        return devices

    def _get_related_dclinks(self, psnames, include_regatrons=False,
                             return_psnames=False):
        alldclinks = set()
        relpsnames = set()
        for name in psnames:
            if 'LI' in name:
                continue
            dclinks = PSSearch.conv_psname_2_dclink(name)
            if dclinks:
                dclink_model = PSSearch.conv_psname_2_psmodel(dclinks[0])
                if dclink_model != 'REGATRON_DCLink':
                    relpsnames.add(name)
                    alldclinks.update(dclinks)
                elif include_regatrons:
                    for dcl in dclinks:
                        dcl_typ = PSSearch.conv_psname_2_pstype(dcl)
                        if dcl_typ == 'as-dclink-regatron-master':
                            relpsnames.add(name)
                            alldclinks.add(dcl)
        if return_psnames:
            return list(alldclinks), list(relpsnames)
        else:
            return list(alldclinks)

    def _open_detail(self, index):
        name = PVName(index.data())
        if name.dis == 'TI':
            app = QApplication.instance()
            wind = create_window_from_widget(HLTriggerDetailed, title=name,
                                             is_main=True)
            app.open_window(wind, parent=self, **{'prefix': name})
            return
        elif not _re.match('.*-.*:.*-.*', name):
            if index.model().rowCount(index) == 1:
                name = PVName(index.child(0, 0).data())
            else:
                return
        if name.dis == 'PS':
            run_newprocess(['sirius-hla-as-ps-detail.py', name])
        elif name.dis == 'PU':
            run_newprocess(['sirius-hla-as-pu-detail.py', name])

    # ---------- update setup ----------

    def _handle_checked_items_changed(self, item):
        self._needs_update_setup = True

    def _update_setup(self):
        if not self._needs_update_setup:
            return
        self._needs_update_setup = False

        has_sifam = False
        for psn in self._si_fam_psnames:
            item = self.ps_tree._item_map[psn]
            has_sifam |= item.checkState(0) != 0

        self.init_sips_bt.setVisible(has_sifam)


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication

    application = SiriusApplication()
    w = PSTestWindow()
    w.show()
    sys.exit(application.exec_())
