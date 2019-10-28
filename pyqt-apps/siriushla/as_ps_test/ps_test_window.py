"""Window to test power supplies."""
import sys
import re as _re
from functools import partial as _part
from threading import Thread as _Thread, Lock as _Lock

from qtpy.QtCore import Qt, Signal, QThread
from qtpy.QtWidgets import QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QLineEdit, QGroupBox, QPushButton, QListWidget, QLabel, QApplication, \
    QMessageBox, QSizePolicy

from siriuspy.search import PSSearch
from siriuspy.namesys import SiriusPVName as PVName

from siriushla.widgets import SiriusMainWindow, PVNameTree
from siriushla.widgets.dialog import ProgressDialog
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from .tasks import ResetIntlk, CheckIntlk, \
    SetOpModeSlowRef, CheckOpModeSlowRef, \
    SetPwrState, CheckPwrState, CheckInitOk, \
    SetCtrlLoop, CheckCtrlLoop, \
    SetCapBankVolt, CheckCapBankVolt, \
    SetCurrent, CheckCurrent
from .conn import TesterDCLink, TesterDCLinkFBP, TesterPS, TesterPSLinac

_lock = _Lock()
_testers = dict()


class PSTestWindow(SiriusMainWindow):
    """PS test window."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setWindowTitle('Power Supply Test')
        self.setObjectName('ASApp')
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
            }""")
        self.setCentralWidget(self.central_widget)

        # power supplies selection
        self.search_le = QLineEdit()
        self.search_le.setPlaceholderText('Filter...')
        self.search_le.editingFinished.connect(self._filter_psnames)

        self.tree = PVNameTree(items=self._get_tree_names(),
                               tree_levels=('sec', 'mag_group'), parent=self)
        self.tree.setHeaderHidden(True)
        self.tree.setObjectName('tree')
        self.tree.setStyleSheet('#tree {max-width:15em; max-height:25em;}')
        self.tree.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.tree.setColumnCount(1)
        self.tree.doubleClicked.connect(self._open_detail)
        gbox_select = QGroupBox('Select power supplies: ', self)
        select_layout = QVBoxLayout()
        select_layout.addWidget(self.search_le)
        select_layout.addWidget(self.tree)
        gbox_select.setLayout(select_layout)

        # commands
        self.setslowref_bt = QPushButton(
            'Set PS and DCLinks to SlowRef', self)
        self.setslowref_bt.clicked.connect(self._set_lastcomm)
        self.setslowref_bt.clicked.connect(self._set_check_opmode)

        self.reset_bt = QPushButton('Reset PS and DCLinks', self)
        self.reset_bt.clicked.connect(self._set_lastcomm)
        self.reset_bt.clicked.connect(self._reset_intlk)

        self.turnoff_ps_bt = QPushButton('Turn PS Off', self)
        self.turnoff_ps_bt.clicked.connect(self._set_lastcomm)
        self.turnoff_ps_bt.clicked.connect(
            _part(self._set_check_pwrstate, 'off'))

        self.turnon_dcl_bt = QPushButton('Turn DCLinks On', self)
        self.turnon_dcl_bt.clicked.connect(self._set_lastcomm)
        self.turnon_dcl_bt.clicked.connect(self._turn_on_dclinks)

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
            _part(self._set_check_pwrstate, 'on'))

        self.test_bt = QPushButton('Test PS', self)
        self.test_bt.clicked.connect(self._set_lastcomm)
        self.test_bt.clicked.connect(self._test_ps)

        self.currzero_bt = QPushButton('Set PS Current to zero', self)
        self.currzero_bt.clicked.connect(self._set_lastcomm)
        self.currzero_bt.clicked.connect(self._zero_current)

        gbox_comm = QGroupBox('Commands', self)
        comm_layout = QVBoxLayout()
        comm_layout.setContentsMargins(20, 9, 20, 9)
        comm_layout.addWidget(QLabel(''))
        comm_layout.addWidget(QLabel('<h4>Prepare</h4>', self,
                                     alignment=Qt.AlignCenter))
        comm_layout.addWidget(self.setslowref_bt)
        comm_layout.addWidget(self.reset_bt)
        comm_layout.addWidget(self.turnoff_ps_bt)
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
        comm_layout.addWidget(self.currzero_bt)
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

        # layout
        lay = QGridLayout()
        lay.setHorizontalSpacing(15)
        lay.addWidget(QLabel('<h3>Power Supplies Test</h3>', self,
                             alignment=Qt.AlignCenter), 0, 0, 1, 3)
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

    def _set_check_opmode(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return
        dclinks = self._get_related_dclinks(devices)
        devices.extend(dclinks)
        devices = [dev for dev in devices if 'LI-' not in dev]

        testers = self._get_testers(devices)
        if not self._check_testers_conn(testers):
            return

        task1 = SetOpModeSlowRef(testers, parent=self)
        task2 = CheckOpModeSlowRef(testers, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Setting PS OpMode to SlowRef...', 'Checking PS OpMode...']
        tasks = [task1, task2]
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

        testers = self._get_testers(devices)
        if not self._check_testers_conn(testers):
            return

        testers_wth_li = {dev: tester for dev, tester in testers.items()
                          if 'LI' not in dev}
        task1 = ResetIntlk(testers_wth_li, parent=self)
        task2 = CheckIntlk(testers, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Reseting PS and DCLinks...',
                  'Checking PS and DCLinks Interlocks...']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_pwrstate(self, state):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        testers = self._get_testers(devices)
        if not self._check_testers_conn(testers):
            return

        task1 = SetPwrState(testers, state=state, parent=self)
        task2 = CheckPwrState(testers, state=state, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Turning PS '+state+'...',
                  'Checking PS powered '+state+'...']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _turn_on_dclinks(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        devices = self._get_related_dclinks(pwrsupplies)
        if not devices:
            return

        testers = self._get_testers(devices)
        if not self._check_testers_conn(testers):
            return

        task1 = SetPwrState(testers, state='on', parent=self)
        task2 = CheckPwrState(testers, state='on', parent=self)
        task3 = CheckInitOk(testers, parent=self)
        task3.itemDone.connect(self._log)
        labels = ['Turning DCLinks On...',
                  'Checking DCLinks powered on...',
                  'Wait DCLinks OpMode turn to SlowRef...']
        tasks = [task1, task2, task3]
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

        testers = self._get_testers(devices)
        if not self._check_testers_conn(testers):
            return

        task1 = SetCtrlLoop(testers, parent=self)
        task2 = CheckCtrlLoop(testers, parent=self)
        task2.itemDone.connect(self._log)
        labels = ['Setting DCLinks CtrlLoop...',
                  'Checking DCLinks CtrlLoop state...']
        tasks = [task1, task2]
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

        testers = self._get_testers(devices)
        if not self._check_testers_conn(testers):
            return

        task1 = SetCapBankVolt(testers, parent=self)
        task2 = CheckCapBankVolt(testers, parent=self)
        task2.itemDone.connect(self._log)
        labels = ['Setting capacitor bank voltage...',
                  'Checking capacitor bank voltage...']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _test_ps(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        testers = self._get_testers(devices)
        if not self._check_testers_conn(testers):
            return

        task1 = SetCurrent(testers, is_test=True, parent=self)
        task2 = CheckCurrent(testers, is_test=True, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Testing PS... Setting current...',
                  'Testing PS... Checking current value...']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _zero_current(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        testers = self._get_testers(devices)
        if not self._check_testers_conn(testers):
            return

        task1 = SetCurrent(testers, parent=self)
        task2 = CheckCurrent(testers, parent=self)
        task2.itemDone.connect(self._log)

        labels = ['Setting current to zero...',
                  'Checking current value...']
        tasks = [task1, task2]
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
        lipsnames = PSSearch.get_psnames({'sec': 'LI', 'dis': 'PS'})
        psnames = PSSearch.get_psnames({'sec': '(TB|BO|TS)', 'dis': 'PS'})
        # TODO: uncomment when using SI
        # psnames = PSSearch.get_psnames({'sec': '(TB|BO|TS|SI)', 'dis': 'PS'})
        psnames.extend(lipsnames)
        return psnames

    def _filter_psnames(self):
        text = self.search_le.text()

        try:
            pattern = _re.compile(text, _re.I)
        except Exception:  # Ignore malformed patterns?
            pattern = _re.compile("malformed")

        for node in self.tree._leafs:
            if pattern.search(node.data(0, 0)):
                node.setHidden(False)
            else:
                node.setHidden(True)

    def _get_selected_ps(self):
        devices = self.tree.checked_items()
        if not devices:
            QMessageBox.critical(self, 'Message', 'No power supply selected!')
            return False

        self._create_testers(devices)
        return devices

    def _get_related_dclinks(self, psnames):
        alldclinks = set()
        for name in psnames:
            if 'LI' in name:
                continue
            dclinks = PSSearch.conv_psname_2_dclink(name)
            if dclinks:
                alldclinks.update(dclinks)

        alldclinks_list = list(alldclinks)
        self._create_testers(alldclinks_list)
        return alldclinks_list

    def _create_testers(self, devices):
        tester2create = list()
        for n in devices:
            if n not in _testers.keys():
                tester2create.append(n)
        if not tester2create:
            return

        task = CreateTesters(tester2create, self)
        dlg = ProgressDialog('Connecting to devices...', task, self)
        dlg.exec_()

    def _get_testers(self, devices):
        return {dev: _testers[dev] for dev in devices}

    def _check_testers_conn(self, testers):
        nok_status = list()
        for dev, t in testers.items():
            if not t.connected:
                nok_status.append(dev)

        if nok_status:
            text = 'There are not connected PVs! Verify devices:\n'
            for dev in nok_status:
                text += dev + '\n'
            QMessageBox.critical(self, 'Message', text)
            return False
        return True

    def _open_detail(self, index):
        app = QApplication.instance()
        psname = index.data()
        if PVName(psname).sec == 'LI':
            return
        elif not _re.match('.*-.*:.*-.*', psname):
            if index.model().rowCount(index) == 1:
                psname = index.child(0, 0).data()
            else:
                return
        app.open_window(PSDetailWindow, parent=self, **{'psname': psname})


class CreateTesters(QThread):
    """Create testers."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, devices, parent=None):
        super().__init__(parent)
        self._devices = devices
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._devices)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Create cyclers."""
        if not self._quit_task:
            interrupted = False
            threads = list()
            for dev in self._devices:
                self.create_tester(dev)
                t = _Thread(
                    target=self.create_tester,
                    args=(dev, ), daemon=True)
                t.start()
                threads.append(t)
                if self._quit_task:
                    interrupted = True
                    break
            for t in threads:
                t.join()
            if not interrupted:
                self.completed.emit()

    def create_tester(self, dev):
        global _testers
        with _lock:
            if dev not in _testers.keys():
                if PVName(dev).sec == 'LI':
                    t = TesterPSLinac(dev)
                elif PSSearch.conv_psname_2_psmodel(dev) == 'FBP_DCLink':
                    t = TesterDCLinkFBP(dev)
                elif 'bo-dclink' in PSSearch.conv_psname_2_pstype(dev):
                    t = TesterDCLink(dev)
                elif PVName(dev).dis == 'PS':
                    t = TesterPS(dev)
                _testers[dev] = t
                self.currentItem.emit(dev)
                self.itemDone.emit()


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication

    application = SiriusApplication()
    w = PSTestWindow()
    w.show()
    sys.exit(application.exec_())
