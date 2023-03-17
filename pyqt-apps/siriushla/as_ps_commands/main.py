"""Window to test power supplies."""

import re as _re
from functools import partial as _part

from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QSizePolicy, QGroupBox, QPushButton, QListWidget, QLabel, QApplication, \
    QMessageBox, QTabWidget, QWidget, QInputDialog, QAbstractItemView, \
    QComboBox, QStackedLayout
from qtpy.QtGui import QKeySequence
import qtawesome as qta

from siriuspy.search import PSSearch
from siriuspy.namesys import SiriusPVName as PVName
from siriuspy.pwrsupply.csdev import Const as _PSC, ETypes as _PSE

from ..util import get_appropriate_color, connect_newprocess, \
    run_newprocess
from ..widgets import SiriusMainWindow, PVNameTree
from ..widgets.windows import create_window_from_widget
from ..widgets.dialog import ProgressDialog
from ..as_ti_control import HLTriggerDetailed

from .tasks import CreateTesters, \
    CheckComm, CheckStatus, \
    ResetIntlk, CheckIntlk, \
    SetSOFBMode, CheckSOFBMode, \
    SetOpMode, CheckOpMode, \
    SetPwrState, CheckPwrState, CheckInitOk, \
    SetPulse, CheckPulse, \
    CheckCtrlLoop, \
    SetCapBankVolt, CheckCapBankVolt, \
    SetCurrent, CheckCurrent, \
    SetVoltage, CheckVoltage, \
    SetTriggerState, CheckTriggerState


class PSCmdWindow(SiriusMainWindow):
    """PS commands window."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setWindowTitle('Power Supply Commands')
        self.setObjectName('ASApp')
        cor = get_appropriate_color(section='AS')
        self.setWindowIcon(qta.icon('mdi.format-list-numbered', color=cor))

        # auxiliar data for initializing SI Fam PS
        self._si_fam_psnames = PSSearch.get_psnames(
            filters={'sec': 'SI', 'sub': 'Fam', 'dis': 'PS'})

        # auxiliary data for SI fast correctors
        self._si_fastcorrs = PSSearch.get_psnames(
            filters={'sec': 'SI', 'dis': 'PS', 'dev': 'FC.*'})

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

        self.title = QLabel(
            '<h3>Power Supply Commands</h3>', self, alignment=Qt.AlignCenter)

        # data
        cmddata = {
            'PS': {
                'Selection': {
                    'devices': self._get_ps_tree_names(),
                    'levels': ('sec', 'mag_group'),
                },
                'Test': {
                    'Check': {
                        'Check Communication': {
                            'cmd': self._check_comm,
                            'tooltip': 'Check PS and DCLinks communication '
                                       'status (verify invalid alarms and, '
                                       'if LI, the value of Connected-Mon PV)',
                        },
                    },
                    'Prepare': {
                        'Disable PS triggers': {
                            'cmd': _part(
                                self._set_check_trigger_state, 'PS', 'dsbl'),
                        },
                        'Turn Off SOFBMode': {
                            'cmd': _part(self._set_check_fbp_sofbmode, 'off'),
                        },
                        'Set PS and DCLinks to SlowRef': {
                            'cmd': self._set_check_opmode_slowref,
                        },
                        'Set PS Current to zero': {
                            'cmd': self._set_zero_ps,
                        },
                        'Reset PS and DCLinks': {
                            'cmd': _part(self._reset_intlk, 'PS'),
                        },
                        'Prepare SI Fam DCLinks': {
                            'cmd': self._prepare_sidclinks,
                        },
                        'Initialize SI Fam PS': {
                            'cmd': self._set_check_pwrstateinit,
                        },
                    },
                    'Config DCLinks': {
                        'Turn DCLinks On': {
                            'cmd': _part(
                                self._set_check_pwrstate_dclinks, 'on'),
                        },
                        'Check DCLinks CtrlLoop': {
                            'cmd': _part(self._check_ctrlloop, 'dclink'),
                        },
                        'Set DCLinks Voltage': {
                            'cmd': self._set_check_dclinks_capvolt,
                        },
                    },
                    'Test': {
                        'Turn PS On': {
                            'cmd': _part(
                                self._set_check_pwrstate, 'PS', 'on', True),
                        },
                        'Check PS CtrlLoop': {
                            'cmd': _part(self._check_ctrlloop, 'pwrsupply'),
                        },
                        'Set PS Current to test value': {
                            'cmd': self._set_test_ps,
                        },
                        'Set PS Current to zero': {
                            'cmd': self._set_zero_ps,
                        },
                    },
                    'Restore': {
                        'Restore PS triggers': {
                            'cmd': _part(self._restore_triggers_state, 'PS'),
                        },
                    },
                },
                'Turn Off': {
                    'Check': {
                        'Check Communication': {
                            'cmd': self._check_comm,
                            'tooltip': 'Check PS and DCLinks communication '
                                       'status (verify invalid alarms and, '
                                       'if LI, the value of Connected-Mon PV)',
                        },
                    },
                    'Prepare': {
                        'Disable PS triggers': {
                            'cmd': _part(
                                self._set_check_trigger_state, 'PS', 'dsbl'),
                        },
                        'Turn Off SOFBMode': {
                            'cmd': _part(self._set_check_fbp_sofbmode, 'off'),
                        },
                        'Set PS and DCLinks to SlowRef': {
                            'cmd': self._set_check_opmode_slowref,
                        },
                        'Set PS Current to zero': {
                            'cmd': self._set_zero_ps,
                        },
                        'Reset PS and DCLinks': {
                            'cmd': _part(self._reset_intlk, 'PS'),
                        },
                    },
                    'Turn Off': {
                        'Turn PS Off': {
                            'cmd': _part(
                                self._set_check_pwrstate, 'PS', 'off', True),
                        },
                        'Turn DCLinks Off': {
                            'cmd': _part(
                                self._set_check_pwrstate_dclinks, 'off'),
                        },
                    },
                },
                'Turn On': {
                    'Check': {
                        'Check Communication': {
                            'cmd': self._check_comm,
                            'tooltip': 'Check PS and DCLinks communication '
                                       'status (verify invalid alarms and, '
                                       'if LI, the value of Connected-Mon PV)',
                        },
                    },
                    'Prepare': {
                        'Disable PS triggers': {
                            'cmd': _part(
                                self._set_check_trigger_state, 'PS', 'dsbl'),
                        },
                        'Turn Off SOFBMode': {
                            'cmd': _part(self._set_check_fbp_sofbmode, 'off'),
                        },
                        'Reset PS and DCLinks': {
                            'cmd': _part(self._reset_intlk, 'PS'),
                        },
                        'Prepare SI Fam DCLinks': {
                            'cmd': self._prepare_sidclinks,
                        },
                        'Initialize SI Fam PS': {
                            'cmd': self._set_check_pwrstateinit,
                        },
                    },
                    'Config DCLinks': {
                        'Turn DCLinks On': {
                            'cmd': _part(
                                self._set_check_pwrstate_dclinks, 'on'),
                        },
                        'Check DCLinks CtrlLoop': {
                            'cmd': _part(self._check_ctrlloop, 'dclink'),
                        },
                        'Set DCLinks Voltage': {
                            'cmd': self._set_check_dclinks_capvolt,
                        },
                    },
                    'Turn On': {
                        'Turn PS On': {
                            'cmd': _part(
                                self._set_check_pwrstate, 'PS', 'on', True),
                        },
                        'Check PS CtrlLoop': {
                            'cmd': _part(self._check_ctrlloop, 'pwrsupply'),
                        },
                    },
                    'Restore': {
                        'Restore PS triggers': {
                            'cmd': _part(self._restore_triggers_state, 'PS'),
                        },
                    },
                },
                'Auxiliary Commands': {
                    'Show Status Summary': {
                        'cmd': _part(self._check_status, 'PS'),
                        'tooltip': 'Check PS and DCLinks interlock status'
                                   ' and, if powered on, check if it is '
                                   'following reference',
                    },
                    'Set PS Current': {
                        'cmd': self._set_check_current,
                    },
                    'Set PS OpMode': {
                        'cmd': self._set_check_opmode,
                    },
                },
            },
            'PU': {
                'Selection': {
                    'devices': self._get_pu_tree_names(),
                    'levels': ('sec', ),
                },
                'Test': {
                    'Prepare': {
                        'Set PU Voltage to zero': {
                            'cmd': _part(self._set_zero_pu, False),
                        },
                        'Reset PU': {
                            'cmd': _part(self._reset_intlk, 'PU'),
                        },
                    },
                    'Test': {
                        'Turn PU On': {
                            'cmd': _part(
                                self._set_check_pwrstate, 'PU', 'on', True),
                        },
                        'Enable PU Pulse': {
                            'cmd': _part(self._set_check_pulse, 'on'),
                        },
                        'Enable PU triggers': {
                            'cmd': _part(
                                self._set_check_trigger_state, 'PU', 'on'),
                        },
                        'Set PU Voltage to test value': {
                            'cmd': self._set_test_pu,
                        },
                        'Set PU Voltage to zero': {
                            'cmd': _part(self._set_zero_pu, True),
                        },
                    },
                    'Restore': {
                        'Restore PU triggers': {
                            'cmd': _part(self._restore_triggers_state, 'PU'),
                        },
                    },
                },
                'Turn Off': {
                    'Prepare': {
                        'Set PU Voltage to zero': {
                            'cmd': _part(self._set_zero_pu, False),
                        },
                        'Reset PU': {
                            'cmd': _part(self._reset_intlk, 'PU'),
                        },
                    },
                    'Turn Off': {
                        'Disable PU Pulse': {
                            'cmd': _part(self._set_check_pulse, 'off'),
                        },
                        'Turn PU Off': {
                            'cmd': _part(
                                self._set_check_pwrstate, 'PU', 'off', True),
                        },
                    },
                },
                'Turn On': {
                    'Prepare': {
                        'Reset PU': {
                            'cmd': _part(self._reset_intlk, 'PU'),
                        },
                    },
                    'Turn On': {
                        'Turn PU On': {
                            'cmd': _part(
                                self._set_check_pwrstate, 'PU', 'on', True),
                        },
                        'Enable PU Pulse': {
                            'cmd': _part(self._set_check_pulse, 'on'),
                        },
                    },
                },
                'Auxiliary Commands': {
                    'Show Status Summary': {
                        'cmd': _part(self._check_status, 'PU'),
                        'tooltip': 'Check PU interlock status and, if '
                                   'powered on, check if it is following '
                                   'voltage setpoint'
                    },
                }
            },
        }
        procedures = sorted(
            {proc for data in cmddata.values() for proc in data})
        procedures.remove('Selection')
        procedures.remove('Auxiliary Commands')
        init_index = procedures.index('Test')

        # menu
        self.menu = self.menuBar()

        self.act_cycle = self.menu.addAction('Open Cycle Window')
        connect_newprocess(
            self.act_cycle, 'sirius-hla-as-ps-cycle.py', parent=self)

        self.aux_comm = self.menu.addMenu('Auxiliary Commands')
        for group, props in cmddata.items():
            menu = self.aux_comm.addMenu(group)
            for cmd, data in props['Auxiliary Commands'].items():
                act = menu.addAction(cmd)
                act.triggered.connect(_part(self._set_lastcomm, group))
                act.triggered.connect(data['cmd'])
                if 'tooltip' in data:
                    act.setToolTip(data['tooltip'])

        # selection and commands
        self.wid_procs = QWidget(self)

        self.ld_procs = QLabel(
            'Select a procedure: ', self, alignment=Qt.AlignRight)
        self.cb_procs = QComboBox(self)
        self.cb_procs.addItems(procedures)
        self.cb_procs.setCurrentIndex(init_index)
        self.tab = QTabWidget(self)
        self.tab.setObjectName('ASTab')

        lay_procs = QGridLayout(self.wid_procs)
        lay_procs.addWidget(self.ld_procs, 0, 0, alignment=Qt.AlignRight)
        lay_procs.addWidget(self.cb_procs, 0, 1, alignment=Qt.AlignLeft)
        lay_procs.addWidget(self.tab, 1, 0, 1, 2)

        self.seltrees = dict()
        self.buttons = dict()
        for group, props in cmddata.items():
            self.buttons[group] = dict()

            # select
            selection = props['Selection']
            tree = PVNameTree(
                items=selection['devices'],
                tree_levels=selection['levels'],
                parent=self,
            )
            tree.setStyleSheet(".QLabel{min-width: 8.5em;}")
            tree.tree.setHeaderHidden(True)
            tree.setSizePolicy(
                QSizePolicy.Preferred, QSizePolicy.Preferred)
            tree.tree.setColumnCount(1)
            tree.tree.doubleClicked.connect(self._open_detail)
            tree.tree.itemChanged.connect(
                self._handle_checked_items_changed)
            self.seltrees[group] = tree

            gbox_select = QGroupBox('Select '+group+': ', self)
            gbox_select.setObjectName('select')
            gbox_select.setStyleSheet("""
                #select{
                    border-top: 0px solid transparent;
                    border-left: 0px solid transparent;
                    border-bottom: 0px solid transparent;
                }""")
            lay_select = QVBoxLayout(gbox_select)
            lay_select.addWidget(tree)

            # commands
            gbox_comm = QGroupBox('Commands', self)
            gbox_comm.setObjectName('comm')
            gbox_comm.setStyleSheet(
                '#comm{border: 0px solid transparent;}')
            stack_procs = QStackedLayout(gbox_comm)
            self.cb_procs.currentIndexChanged.connect(
                stack_procs.setCurrentIndex)
            for proc in procedures:
                wid_comm = QWidget()
                lay_comm = QVBoxLayout(wid_comm)
                lay_comm.setContentsMargins(20, 9, 20, 9)
                cmdidx, cmdbuttons = 1, list()
                for cmdgroup, cmdlist in props[proc].items():
                    label = QLabel(
                        '<h4>'+cmdgroup+'</h4>', self,
                        alignment=Qt.AlignCenter)
                    lay_comm.addWidget(label)
                    for cmd, data in cmdlist.items():
                        btn = QPushButton(str(cmdidx) + '. ' + cmd, self)
                        btn.setSizePolicy(
                            QSizePolicy.Minimum, QSizePolicy.Maximum)
                        btn.clicked.connect(_part(self._set_lastcomm, group))
                        btn.clicked.connect(data['cmd'])
                        if 'tooltip' in data:
                            btn.setToolTip(data['tooltip'])
                        cmdbuttons.append(btn)
                        if 'SI Fam' in cmd:
                            btn.setVisible(False)
                        else:
                            cmdidx += 1
                        lay_comm.addWidget(btn)
                    lay_comm.addWidget(QLabel(''))
                self.buttons[group][proc] = cmdbuttons
                stack_procs.addWidget(wid_comm)
            stack_procs.setCurrentIndex(init_index)

            wid = QWidget(self)
            lay = QGridLayout(wid)
            lay.setContentsMargins(0, 9, 0, 0)
            lay.setHorizontalSpacing(0)
            lay.addWidget(gbox_select, 0, 0)
            lay.addWidget(gbox_comm, 0, 1)
            lay.setColumnStretch(0, 1)
            lay.setColumnStretch(1, 1)
            self.tab.addTab(wid, group)

        # lists
        self.label_lastcomm = QLabel('Last Command: ', self)
        self.ok_ps = QListWidget(self)
        self.ok_ps.setObjectName('OkList')
        self.ok_ps.doubleClicked.connect(self._open_detail)
        self.ok_ps.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ok_ps.setToolTip(
            'Select rows and press Ctrl+C to copy and Esc to deselect.')
        self.nok_ps = QListWidget(self)
        self.nok_ps.setObjectName('NokList')
        self.nok_ps.doubleClicked.connect(self._open_detail)
        self.nok_ps.setSelectionMode(QAbstractItemView.MultiSelection)
        self.nok_ps.setToolTip(
            'Select rows and press Ctrl+C to copy and Esc to deselect.')
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

        # layout
        lay = QGridLayout()
        lay.setHorizontalSpacing(15)
        lay.setVerticalSpacing(5)
        lay.addWidget(self.title, 0, 0, 1, 3)
        lay.addWidget(self.wid_procs, 1, 0)
        lay.addLayout(list_layout, 1, 1)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 2)
        lay.setRowStretch(0, 2)
        lay.setRowStretch(1, 18)
        self.central_widget.setLayout(lay)

    # ---------- commands ------------

    def _check_comm(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return
        dclinks = self._get_related_dclinks(
            devices, include_regatrons=True)
        devices.extend(dclinks)

        task0 = CreateTesters(devices, parent=self)
        task1 = CheckComm(devices, parent=self)
        task1.itemDone.connect(self._log)

        labels = ['Connecting to devices...',
                  'Checking PS and DCLinks Comm. Status...']
        tasks = [task0, task1]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

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

    def _set_check_opmode_slowref(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return
        dclinks = self._get_related_dclinks(devices)
        devices.extend(dclinks)
        devices = [dev for dev in devices if 'LI-' not in dev]
        devsot = [dev for dev in devices if dev.dev not in ('FCH', 'FCV')]
        devsfc = [dev for dev in devices if dev.dev in ('FCH', 'FCV')]

        task0 = CreateTesters(devices, parent=self)
        task1 = SetOpMode(devsot, state=_PSC.OpMode.SlowRef, parent=self)
        task2 = SetOpMode(devsfc, state=_PSC.OpModeFOFBSel.manual, parent=self)
        task3 = CheckOpMode(
            devsot,
            state=[_PSC.States.SlowRef, _PSC.States.Off,
                   _PSC.States.Interlock, _PSC.States.Initializing],
            parent=self)
        task3.itemDone.connect(self._log)
        task4 = CheckOpMode(
            devsfc, state=_PSC.OpModeFOFBSts.manual, parent=self)
        task4.itemDone.connect(self._log)

        labels = ['Connecting to devices...',
                  'Setting PS OpMode to SlowRef...',
                  'Setting FC PS OpMode to manual...',
                  'Checking PS OpMode...',
                  'Checking FC PS OpMode...']
        tasks = [task0, task1, task2, task3, task4]
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
        devices_rst = {
            dev for dev in devices if dev.sec != 'LI' and
            dev.dev not in ('FCH', 'FCV')}

        task0 = CreateTesters(devices, parent=self)
        task1 = ResetIntlk(devices_rst, parent=self)
        task2 = CheckIntlk(devices, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Reseting '+dev_label+'...',
                  'Checking '+dev_label+' Interlocks...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_pwrstate(self, dev_type, state, show=True):
        self.ok_ps.clear()
        self.nok_ps.clear()
        if isinstance(dev_type, list):
            devices = list(dev_type)
            dev_type = PVName(devices[0]).dis
        else:
            if dev_type == 'PS':
                devices = self._get_selected_ps()
            elif dev_type == 'PU':
                devices = self._get_selected_pu()
        if not devices:
            return

        if state == 'on' and dev_type == 'PS':
            dev2ctrl = list(set(devices) - set(self._si_fam_psnames))
        else:
            dev2ctrl = devices

        task0 = CreateTesters(devices, parent=self)
        task1 = SetPwrState(dev2ctrl, state=state, parent=self)
        task2 = CheckPwrState(devices, state=state, is_test=True, parent=self)
        task2.itemDone.connect(_part(self._log, show=show))
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Turning '+dev_type+' '+state+'...',
                  'Checking '+dev_type+' powered '+state+'...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _prepare_sidclinks(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        selected = self._get_selected_ps()
        ps2check = [ps for ps in selected if ps in self._si_fam_psnames]
        dclinks = self._get_related_dclinks(ps2check, include_regatrons=True)
        if not ps2check:
            return

        # if power state is on, do nothing
        self.ok_ps_aux_list.clear()
        self.nok_ps_aux_list.clear()
        self._check_pwrstate(ps2check, state='on', is_test=False, show=False)
        if set(self.ok_ps_aux_list) == set(ps2check):
            for dev in dclinks:
                self._log(dev, True)
            return

        ps2act = list(self.nok_ps_aux_list)  # act in PS off
        dcl2act = self._get_related_dclinks(ps2act, include_regatrons=True)
        # print('act', ps2act, dcl2act)

        # if need initializing, check if DCLinks are turned off
        self.ok_ps_aux_list.clear()
        self.nok_ps_aux_list.clear()
        self._check_pwrstate(dcl2act, state='off', is_test=False, show=False)
        if not self.nok_ps_aux_list:
            for dev in dclinks:
                self._log(dev, True)
            return

        dcl2ctrl = list(self.nok_ps_aux_list)  # control DCLink on
        dcl_ok = set(dclinks) - set(dcl2ctrl)
        ps2ctrl = set()  # get related psnames
        for dcl in dcl2ctrl:
            pss = PSSearch.conv_dclink_2_psname(dcl)
            ps2ctrl.update(pss)
        # print('ctrl', ps2ctrl, dcl2ctrl)

        # if some DCLink is on, make sure related PS are turned off
        self.ok_ps_aux_list.clear()
        self.nok_ps_aux_list.clear()
        self._check_pwrstate(ps2ctrl, state='off', is_test=False, show=False)
        if self.nok_ps_aux_list:
            ps2ctrl = list(self.nok_ps_aux_list)

            self.ok_ps_aux_list.clear()
            self.nok_ps_aux_list.clear()
            self._set_zero_ps(ps2ctrl, show=False)

            self.ok_ps_aux_list.clear()
            self.nok_ps_aux_list.clear()
            self._set_check_pwrstate(dev_type=ps2ctrl, state='off', show=False)

            if self.nok_ps_aux_list:
                for dev in self.ok_ps_aux_list:
                    self._log(dev, True)
                for dev in self.nok_ps_aux_list:
                    self._log(dev, False)
                text = 'The listed PS seems to be taking too\n'\
                    'long to turn off.\n'\
                    'Try to execute this step once again.'
                QMessageBox.warning(self, 'Message', text)
                return

        # finally, turn DCLinks off
        self._set_check_pwrstate_dclinks(
            state='off', devices=dcl2ctrl, ps2check=ps2ctrl)
        # log DCLinks Ok
        for dev in dcl_ok:
            self._log(dev, True)

    def _set_check_pwrstateinit(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        selected = self._get_selected_ps()
        devices = [ps for ps in selected if ps in self._si_fam_psnames]
        if not devices:
            return

        # if power state is on, do nothing
        self.ok_ps_aux_list.clear()
        self.nok_ps_aux_list.clear()
        self._check_pwrstate(devices, state='on', is_test=False, show=False)
        if len(self.ok_ps_aux_list) == len(devices):
            for dev in self.ok_ps_aux_list:
                self._log(dev, True)
            return

        # if need initializing, check if DCLinks are turned off before continue
        ps_ok = list(self.ok_ps_aux_list)
        ps2ctrl = list(self.nok_ps_aux_list)  # check PS off
        dcl2check = self._get_related_dclinks(ps2ctrl, include_regatrons=True)
        # print('set_check_pwrstateinit', ps2ctrl)

        self.ok_ps_aux_list.clear()
        self.nok_ps_aux_list.clear()
        self._check_pwrstate(dcl2check, state='off', is_test=False, show=False)
        if self.nok_ps_aux_list:
            for dev in self.ok_ps_aux_list:
                self._log(dev, True)
            for dev in self.nok_ps_aux_list:
                self._log(dev, False)
            QMessageBox.critical(
                self, 'Message',
                'Make sure related DCLinks are turned\n'
                'off before initialize SI Fam PS!')
            return

        # list in Ok PS already on
        for dev in ps_ok:
            self._log(dev, True)

        # then, initialize SI Fam PS
        task0 = CreateTesters(ps2ctrl, parent=self)
        task1 = SetPwrState(ps2ctrl, state='on', parent=self)
        task2 = CheckOpMode(
            ps2ctrl, state=_PSC.States.Initializing, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Initializing SI Fam PS...',
                  'Checking SI Fam PS initialized...']

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

    def _set_check_pwrstate_dclinks(self, state, devices=list(),
                                    ps2check=list()):
        self.ok_ps.clear()
        self.nok_ps.clear()
        if not devices:
            pwrsupplies = self._get_selected_ps()
            if not pwrsupplies:
                return
            devices = self._get_related_dclinks(
                pwrsupplies, include_regatrons=True)
            ps2check = set()
            for dev in devices:
                ps2check.update(PSSearch.conv_dclink_2_psname(dev))
        if not devices:
            return

        if state == 'off':
            self.ok_ps_aux_list.clear()
            self.nok_ps_aux_list.clear()
            self._check_pwrstate(ps2check, state='offintlk', show=False)
            if self.nok_ps_aux_list:
                for dev in self.ok_ps_aux_list:
                    self._log(dev, True)
                for dev in self.nok_ps_aux_list:
                    self._log(dev, False)
                QMessageBox.critical(
                    self, 'Message',
                    'Make sure all related power supplies\n'
                    'are turned off before turning DCLinks off!')
                return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetPwrState(devices, state=state, parent=self)
        task2 = CheckPwrState(devices, state=state, is_test=True, parent=self)
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

    def _check_pwrstate(self, devices, state, is_test=True, show=True):
        self.ok_ps.clear()
        self.nok_ps.clear()

        task0 = CreateTesters(devices, parent=self)

        if state == 'offintlk':
            text = 'off or interlock'
            task1 = CheckOpMode(
                devices, state=[_PSC.States.Off, _PSC.States.Interlock],
                parent=self)
        else:
            text = state
            task1 = CheckPwrState(
                devices, state=state, is_test=is_test, parent=self)
        task1.itemDone.connect(_part(self._log, show=show))
        tasks = [task0, task1]

        labels = ['Connecting to devices...',
                  'Checking devices powered '+text+'...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _check_ctrlloop(self, dev_type='pwrsupply'):
        self.ok_ps.clear()
        self.nok_ps.clear()
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        if dev_type == 'pwrsupply':
            devices = {
                dev for dev in pwrsupplies if dev.sec != 'LI' and
                dev.dev not in ('FCH', 'FCV')}
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

    def _set_check_fbp_sofbmode(self, state):
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

    def _set_zero_ps(self, devices=list(), show=True):
        self.ok_ps.clear()
        self.nok_ps.clear()
        if not devices:
            devices = self._get_selected_ps()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetCurrent(devices, parent=self)
        task2 = CheckCurrent(devices, parent=self)
        task2.itemDone.connect(_part(self._log, show=show))
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Setting current to zero...',
                  'Checking current value...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_current(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        value, res = QInputDialog.getDouble(
            self, "Setpoint Input", "Insert current setpoint: ")
        if not res:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetCurrent(devices, value=value, parent=self)
        task2 = CheckCurrent(devices, value=value, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task0, task1, task2]

        labels = ['Connecting to devices...',
                  'Setting current...',
                  'Checking current value...']

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_opmode(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        devices = [
            dev for dev in devices if dev.sec != 'LI' and
            dev.dev not in ('FCH', 'FCV')]
        if not devices:
            return

        state, res = QInputDialog.getItem(
            self, "OpMode Input", "Select OpMode: ",
            _PSE.OPMODES, editable=False)
        if not res:
            return
        state2set = getattr(_PSC.OpMode, state)
        state2check = getattr(_PSC.States, state)

        task0 = CreateTesters(devices, parent=self)
        task1 = SetOpMode(devices, state=state2set, parent=self)
        task2 = CheckOpMode(devices, state=state2check, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Connecting to devices...',
                  'Setting PS OpMode to '+state+'...',
                  'Checking PS OpMode in '+state+'...']
        tasks = [task0, task1, task2]
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

    # ---------- device control ----------

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
        # add SI Fast Corrs
        psnames.extend(PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '(?!01M).*', 'dis': 'PS', 'dev': 'FC.*'}))
        # add SI SeptaFF Corrs
        psnames.extend(PSSearch.get_psnames(
            {'sec': 'SI', 'dis': 'PS', 'dev': 'FFC.*'}))
        return psnames

    def _get_pu_tree_names(self):
        punames = PSSearch.get_psnames(
            {'sec': '(TB|BO|TS|SI)', 'dis': 'PU', 'dev': '.*(Kckr|Sept)',
             'propty_name': '(?!:CCoil).*'})
        return punames

    def _get_selected_ps(self):
        devices = self.seltrees['PS'].checked_items()
        if not devices:
            QMessageBox.critical(self, 'Message', 'No power supply selected!')
            return False
        devices = [PVName(dev) for dev in devices]
        return devices

    def _get_selected_pu(self):
        devices = self.seltrees['PU'].checked_items()
        if not devices:
            QMessageBox.critical(
                self, 'Message', 'No pulsed power supply selected!')
            return False
        devices = [PVName(dev) for dev in devices]
        return devices

    def _get_related_dclinks(self, psnames, include_regatrons=False):
        if isinstance(psnames, str):
            psnames = [psnames, ]
        alldclinks = set()
        for name in psnames:
            if 'LI' in name:
                continue
            dclinks = PSSearch.conv_psname_2_dclink(name)
            if dclinks:
                dclink_model = PSSearch.conv_psname_2_psmodel(dclinks[0])
                if dclink_model != 'REGATRON_DCLink':
                    alldclinks.update(dclinks)
                elif include_regatrons:
                    for dcl in dclinks:
                        dcl_typ = PSSearch.conv_psname_2_pstype(dcl)
                        if dcl_typ == 'as-dclink-regatron-master':
                            alldclinks.add(dcl)
        alldclinks = [PVName(dev) for dev in alldclinks]
        return alldclinks

    def _open_detail(self, index):
        name = PVName(index.data())
        if name.dis == 'TI':
            app = QApplication.instance()
            wind = create_window_from_widget(
                HLTriggerDetailed, title=name, is_main=True)
            app.open_window(wind, parent=self, **{'device': name})
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
        devname = PVName(item.data(0, Qt.DisplayRole))
        if not _re.match('.*-.*:.*-.*', devname):
            return
        state2set = item.checkState(0)

        # ensure power supplies that share dclinks are checked together
        if devname in self._si_fam_psnames:
            dclinks = PSSearch.conv_psname_2_dclink(devname)
            if dclinks:
                psname2check = set()
                for dcl in dclinks:
                    relps = PSSearch.conv_dclink_2_psname(dcl)
                    relps.remove(devname)
                    psname2check.update(relps)
                self.seltrees['PS'].tree.blockSignals(True)
                for psn in psname2check:
                    item2check = self.seltrees['PS']._item_map[psn]
                    if item2check.checkState(0) != state2set:
                        item2check.setData(0, Qt.CheckStateRole, state2set)
                self.seltrees['PS'].tree.blockSignals(False)

        self._needs_update_setup = True

    def _update_setup(self):
        if not self._needs_update_setup:
            return
        self._needs_update_setup = False

        # show/hide buttons to initialize SI Fam PS
        has_sifam = False
        for psn in self._si_fam_psnames:
            item = self.seltrees['PS']._item_map[psn]
            has_sifam |= item.checkState(0) != 0

        for proc in self.buttons['PS']:
            index = 1
            for but in self.buttons['PS'][proc]:
                if 'SI Fam' in but.text():
                    but.setVisible(has_sifam)
                    if not has_sifam:
                        continue
                oldtext = but.text()
                newtext = str(index) + '.' + oldtext.split('.')[1]
                but.setText(newtext)
                index += 1

    # ---------- events ----------

    def keyPressEvent(self, evt):
        """Implement keyPressEvent."""
        if evt.matches(QKeySequence.Copy):
            if self.ok_ps.underMouse():
                items = self.ok_ps.selectedItems()
            elif self.nok_ps.underMouse():
                items = self.nok_ps.selectedItems()
            items = '\n'.join([i.text() for i in items])
            QApplication.clipboard().setText(items)
        if evt.key() == Qt.Key_Escape:
            if self.ok_ps.underMouse():
                items = self.ok_ps.clearSelection()
            elif self.nok_ps.underMouse():
                items = self.nok_ps.clearSelection()
        super().keyPressEvent(evt)
