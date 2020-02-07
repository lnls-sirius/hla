"""Window to test power supplies."""
import sys
import re as _re
from functools import partial as _part

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QSizePolicy, QGroupBox, QPushButton, QListWidget, QLabel, QApplication, \
    QMessageBox
import qtawesome as qta

from siriuspy.search import PSSearch
from siriuspy.namesys import SiriusPVName as PVName

from siriushla.util import get_appropriate_color, connect_newprocess
from siriushla.widgets import SiriusMainWindow, PVNameTree
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets.dialog import ProgressDialog
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from siriushla.as_ti_control import HLTriggerDetailed
from .tasks import CreateTesters, \
    CheckStatus, \
    ResetIntlk, CheckIntlk, \
    SetOpModeSlowRef, CheckOpModeSlowRef, \
    SetPwrState, CheckPwrState, CheckInitOk, \
    SetCtrlLoop, CheckCtrlLoop, \
    SetCapBankVolt, CheckCapBankVolt, \
    SetCurrent, CheckCurrent, \
    SetTriggerState, CheckTriggerState


class PSTestWindow(SiriusMainWindow):
    """PS test window."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setWindowTitle('PS Test')
        self.setObjectName('ASApp')
        cor = get_appropriate_color(section='AS')
        self.setWindowIcon(qta.icon('mdi.test-tube', color=cor))
        self._setup_ui()

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
            }""")
        self.setCentralWidget(self.central_widget)

        # power supplies selection
        self.tree = PVNameTree(
            items=self._get_tree_names(),
            tree_levels=('sec', 'mag_group'), parent=self)
        self.tree.tree.setHeaderHidden(True)
        self.tree.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.tree.tree.setColumnCount(1)
        self.tree.tree.doubleClicked.connect(self._open_detail)
        gbox_select = QGroupBox('Select power supplies: ', self)
        select_layout = QVBoxLayout()
        select_layout.addWidget(self.tree)
        gbox_select.setLayout(select_layout)

        # commands
        self.checkstatus_bt = QPushButton('Check Status', self)
        self.checkstatus_bt.clicked.connect(self._set_lastcomm)
        self.checkstatus_bt.clicked.connect(self._check_status)
        self.checkstatus_bt.setToolTip(
            'Check interlock status and, if powered on, '
            'check if it is following reference')

        self.dsbltrigger_bt = QPushButton('Disable triggers', self)
        self.dsbltrigger_bt.clicked.connect(self._set_lastcomm)
        self.dsbltrigger_bt.clicked.connect(self._disable_triggers)

        self.setslowref_bt = QPushButton(
            'Set PS and DCLinks to SlowRef', self)
        self.setslowref_bt.clicked.connect(self._set_lastcomm)
        self.setslowref_bt.clicked.connect(self._set_check_opmode)

        self.currzero_bt1 = QPushButton('Set PS Current to zero', self)
        self.currzero_bt1.clicked.connect(self._set_lastcomm)
        self.currzero_bt1.clicked.connect(self._zero_current)

        self.reset_bt = QPushButton('Reset PS and DCLinks', self)
        self.reset_bt.clicked.connect(self._set_lastcomm)
        self.reset_bt.clicked.connect(self._reset_intlk)

        self.turnon_dcl_bt = QPushButton('Turn DCLinks On', self)
        self.turnon_dcl_bt.clicked.connect(self._set_lastcomm)
        self.turnon_dcl_bt.clicked.connect(
            _part(self._set_check_pwrstate_dclinks, 'on'))

        self.setctrlloop_dcl_bt = QPushButton('Set DCLinks CtrlLoop', self)
        self.setctrlloop_dcl_bt.clicked.connect(self._set_lastcomm)
        self.setctrlloop_dcl_bt.clicked.connect(
            self._set_check_dclinks_ctrlloop)

        self.setvolt_dcl_bt = QPushButton('Set DCLinks Voltage', self)
        self.setvolt_dcl_bt.clicked.connect(self._set_lastcomm)
        self.setvolt_dcl_bt.clicked.connect(
            self._set_check_dclinks_capvolt)

        self.turnon_ps_bt = QPushButton('Turn PS On', self)
        self.turnon_ps_bt.clicked.connect(self._set_lastcomm)
        self.turnon_ps_bt.clicked.connect(
            _part(self._set_check_pwrstate_ps, 'on'))

        self.test_bt = QPushButton('Set PS Current to test value', self)
        self.test_bt.clicked.connect(self._set_lastcomm)
        self.test_bt.clicked.connect(self._test_ps)

        self.currzero_bt2 = QPushButton('Set PS Current to zero', self)
        self.currzero_bt2.clicked.connect(self._set_lastcomm)
        self.currzero_bt2.clicked.connect(self._zero_current)

        self.restoretrigger_bt = QPushButton('Restore triggers', self)
        self.restoretrigger_bt.clicked.connect(self._set_lastcomm)
        self.restoretrigger_bt.clicked.connect(self._restore_triggers_state)

        gbox_comm = QGroupBox('Commands', self)
        comm_layout = QVBoxLayout()
        comm_layout.setContentsMargins(20, 9, 20, 9)
        comm_layout.addWidget(QLabel(''))
        comm_layout.addWidget(QLabel('<h4>Check</h4>', self,
                                     alignment=Qt.AlignCenter))
        comm_layout.addWidget(self.checkstatus_bt)
        comm_layout.addWidget(QLabel(''))
        comm_layout.addWidget(QLabel('<h4>Prepare</h4>', self,
                                     alignment=Qt.AlignCenter))
        comm_layout.addWidget(self.dsbltrigger_bt)
        comm_layout.addWidget(self.setslowref_bt)
        comm_layout.addWidget(self.currzero_bt1)
        comm_layout.addWidget(self.reset_bt)
        comm_layout.addWidget(QLabel(''))
        comm_layout.addWidget(QLabel('<h4>Config DCLinks</h4>', self,
                                     alignment=Qt.AlignCenter))
        comm_layout.addWidget(self.turnon_dcl_bt)
        comm_layout.addWidget(self.setctrlloop_dcl_bt)
        comm_layout.addWidget(self.setvolt_dcl_bt)
        comm_layout.addWidget(QLabel(''))
        comm_layout.addWidget(QLabel('<h4>Test</h4>', self,
                                     alignment=Qt.AlignCenter))
        comm_layout.addWidget(self.turnon_ps_bt)
        comm_layout.addWidget(self.test_bt)
        comm_layout.addWidget(self.currzero_bt2)
        comm_layout.addWidget(QLabel(''))
        comm_layout.addWidget(QLabel('<h4>Restore</h4>', self,
                                     alignment=Qt.AlignCenter))
        comm_layout.addWidget(self.restoretrigger_bt)
        comm_layout.addWidget(QLabel(''))
        gbox_comm.setLayout(comm_layout)

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
        self.aux_comm = self.menu.addMenu('Auxiliar commands')
        self.act_turnoff_ps = self.aux_comm.addAction('Turn PS Off')
        self.act_turnoff_ps.triggered.connect(self._set_lastcomm)
        self.act_turnoff_ps.triggered.connect(
            _part(self._set_check_pwrstate_ps, 'off'))
        self.act_turnoff_dclink = self.aux_comm.addAction('Turn DCLinks Off')
        self.act_turnoff_dclink.triggered.connect(self._set_lastcomm)
        self.act_turnoff_dclink.triggered.connect(
            _part(self._set_check_pwrstate_dclinks, 'off'))

        # layout
        lay = QGridLayout()
        lay.setHorizontalSpacing(15)
        lay.setVerticalSpacing(5)
        lay.addWidget(QLabel(
            '<h3>Power Supplies Test</h3>', self, alignment=Qt.AlignCenter),
            0, 0, 1, 3)
        lay.addWidget(gbox_select, 1, 0)
        lay.addWidget(gbox_comm, 1, 1)
        lay.addLayout(list_layout, 1, 2)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 1)
        lay.setColumnStretch(2, 2)
        lay.setRowStretch(0, 2)
        lay.setRowStretch(1, 18)
        self.central_widget.setLayout(lay)

    # ---------- commands ------------

    def _check_status(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return
        dclinks = self._get_related_dclinks(devices)
        devices.extend(dclinks)

        task0 = CreateTesters(devices, parent=self)
        task1 = CheckStatus(devices, parent=self)
        task1.itemDone.connect(self._log)

        labels = ['Connecting to devices...',
                  'Checking PS and DCLinks Status...']
        tasks = [task0, task1]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _disable_triggers(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        task1 = SetTriggerState(parent=self)
        task2 = CheckTriggerState(parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task1, task2]
        labels = ['Disabling triggers...', 'Checking trigger states...']
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

    def _reset_intlk(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return
        dclinks = self._get_related_dclinks(devices)
        devices.extend(dclinks)

        devices_wth_li = {dev for dev in devices if 'LI' not in dev}
        task0 = CreateTesters(devices, parent=self)
        task1 = ResetIntlk(devices_wth_li, parent=self)
        task2 = CheckIntlk(devices, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Connecting to devices...',
                  'Reseting PS and DCLinks...',
                  'Checking PS and DCLinks Interlocks...']
        tasks = [task0, task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_pwrstate_ps(self, state):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetPwrState(devices, state=state, parent=self)
        task2 = CheckPwrState(devices, state=state, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Connecting to devices...',
                  'Turning PS '+state+'...',
                  'Checking PS powered '+state+'...']
        tasks = [task0, task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_pwrstate_dclinks(self, state='on'):
        self.ok_ps.clear()
        self.nok_ps.clear()
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        devices = self._get_related_dclinks(pwrsupplies)
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetPwrState(devices, state=state, parent=self)
        task2 = CheckPwrState(devices, state=state, parent=self)
        labels = ['Connecting to devices...',
                  'Turning DCLinks '+state+'...',
                  'Checking DCLinks powered '+state+'...']
        tasks = [task0, task1, task2]

        if state == 'on':
            task3 = CheckInitOk(devices, parent=self)
            task3.itemDone.connect(self._log)
            tasks.append(task3)
            labels.append('Wait DCLinks OpMode turn to SlowRef...')
        else:
            task2.itemDone.connect(self._log)

        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_dclinks_ctrlloop(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        devices = self._get_related_dclinks(pwrsupplies)
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetCtrlLoop(devices, parent=self)
        task2 = CheckCtrlLoop(devices, parent=self)
        task2.itemDone.connect(self._log)
        labels = ['Connecting to devices...',
                  'Setting DCLinks CtrlLoop...',
                  'Checking DCLinks CtrlLoop state...']
        tasks = [task0, task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_dclinks_capvolt(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        devices = self._get_related_dclinks(pwrsupplies)
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetCapBankVolt(devices, parent=self)
        task2 = CheckCapBankVolt(devices, parent=self)
        task2.itemDone.connect(self._log)
        labels = ['Connecting to devices...',
                  'Setting capacitor bank voltage...',
                  'Checking capacitor bank voltage...']
        tasks = [task0, task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _test_ps(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetCurrent(devices, is_test=True, parent=self)
        task2 = CheckCurrent(devices, is_test=True, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Connecting to devices...',
                  'Testing PS... Setting current...',
                  'Testing PS... Checking current value...']
        tasks = [task0, task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _zero_current(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        task0 = CreateTesters(devices, parent=self)
        task1 = SetCurrent(devices, parent=self)
        task2 = CheckCurrent(devices, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Connecting to devices...',
                  'Setting current to zero...',
                  'Checking current value...']
        tasks = [task0, task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _restore_triggers_state(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        task1 = SetTriggerState(restore_initial_value=True, parent=self)
        task2 = CheckTriggerState(restore_initial_value=True, parent=self)
        task2.itemDone.connect(self._log)
        tasks = [task1, task2]
        labels = ['Restoring trigger states...', 'Checking trigger states...']
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    # ---------- log updates -----------

    def _set_lastcomm(self):
        sender_text = self.sender().text()
        self.label_lastcomm.setText('Last Command: '+sender_text)

    def _clear_lastcomm(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        self.label_lastcomm.setText('Last Command: ')

    def _log(self, name, status):
        if status:
            self.ok_ps.addItem(name)
        else:
            self.nok_ps.addItem(name)

    # ---------- devices control ----------

    def _get_tree_names(self):
        psnames = PSSearch.get_psnames({'sec': '(LI|TB|BO|TS)', 'dis': 'PS'})
        psnames.extend(PSSearch.get_psnames(
            {'sec': 'SI', 'sub': 'Fam', 'dis': 'PS', 'dev': '(B|Q.*|S.*)'}))
        psnames.extend(PSSearch.get_psnames(
            {'sec': 'SI', 'sub': '[0-2][0-9].*', 'dis': 'PS',
             'dev': '(CH|CV)'}))
        # psnames.extend(PSSearch.get_psnames(
        #     {'sec': 'SI', 'sub': '[0-2][0-9].*', 'dis': 'PS',
        #      'dev': '(QD.*|QF.*|Q[1-4])'}))
        # psnames.extend(PSSearch.get_psnames(
        #     {'sec': 'SI', 'sub': '[0-2][0-9](M1|M2|C1|C3)', 'dis': 'PS',
        #      'dev': 'QS'}))
        return psnames

    def _get_selected_ps(self):
        devices = self.tree.checked_items()
        if not devices:
            QMessageBox.critical(self, 'Message', 'No power supply selected!')
            return False
        return devices

    def _get_related_dclinks(self, psnames):
        alldclinks = set()
        for name in psnames:
            if 'LI' in name:
                continue
            dclinks = PSSearch.conv_psname_2_dclink(name)
            if dclinks:
                dclink_type = PSSearch.conv_psname_2_psmodel(dclinks[0])
                if dclink_type != 'REGATRON_DCLink':
                    alldclinks.update(dclinks)
        return list(alldclinks)

    def _open_detail(self, index):
        app = QApplication.instance()
        name = PVName(index.data())
        if name.dis == 'TI':
            wind = create_window_from_widget(HLTriggerDetailed, title=name,
                                             is_main=True)
            app.open_window(wind, parent=self, **{'prefix': name})
            return
        elif not _re.match('.*-.*:.*-.*', name):
            if index.model().rowCount(index) == 1:
                name = index.child(0, 0).data()
            else:
                return
        app.open_window(PSDetailWindow, parent=self, **{'psname': name})


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication

    application = SiriusApplication()
    w = PSTestWindow()
    w.show()
    sys.exit(application.exec_())
