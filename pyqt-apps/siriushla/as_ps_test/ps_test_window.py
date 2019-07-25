"""Window to test power supplies."""
import sys
import re as _re
from functools import partial as _part

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFrame, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QLineEdit, QGroupBox, QPushButton, QListWidget, QLabel, QApplication, \
    QMessageBox, QSizePolicy

from siriushla.sirius_application import SiriusApplication
from siriuspy.search import PSSearch, MASearch

from siriushla.widgets import SiriusMainWindow, PVNameTree
from siriushla.widgets.dialog import ProgressDialog
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from .tasks import ResetIntlk, CheckIntlk, \
    SetOpModeSlowRef, CheckOpModeSlowRef, \
    SetPwrState, CheckPwrState, \
    SetCtrlLoop, CheckCtrlLoop, \
    SetCapBankVolt, SetCurrent
from .dclinks_data import get_related_dclinks_data as _get_related_dclinks_data


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

        # magnets selection
        self.search_le = QLineEdit()
        self.search_le.setPlaceholderText('Filter...')
        self.search_le.editingFinished.connect(self._filter_manames)

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
        self.setslowref_bt.pressed.connect(self._set_lastcomm_label_text)
        self.setslowref_bt.pressed.connect(self._set_check_opmode)

        self.reset_bt = QPushButton('Reset PS and DCLinks', self)
        self.reset_bt.pressed.connect(self._set_lastcomm_label_text)
        self.reset_bt.pressed.connect(self._reset_intlk)

        self.turnoff_ps_bt = QPushButton('Turn PS Off', self)
        self.turnoff_ps_bt.pressed.connect(self._set_lastcomm_label_text)
        self.turnoff_ps_bt.pressed.connect(
            _part(self._set_check_pwrstate, 'off'))

        self.turnon_dcl_bt = QPushButton('Turn DCLinks On', self)
        self.turnon_dcl_bt.pressed.connect(self._set_lastcomm_label_text)
        self.turnon_dcl_bt.pressed.connect(self._turn_on_dclinks)

        self.setctrlloop_dcl_bt = QPushButton('Set DCLinks CtrlLoop', self)
        self.setctrlloop_dcl_bt.pressed.connect(self._set_lastcomm_label_text)
        self.setctrlloop_dcl_bt.pressed.connect(
            self._set_check_dclinks_ctrlloop)

        self.setvolt_dcl_bt = QPushButton('Set DCLinks Voltage', self)
        self.setvolt_dcl_bt.pressed.connect(self._set_lastcomm_label_text)
        self.setvolt_dcl_bt.pressed.connect(
            self._set_check_dclinks_capvolt)

        self.turnon_ps_bt = QPushButton('Turn PS On', self)
        self.turnon_ps_bt.pressed.connect(self._set_lastcomm_label_text)
        self.turnon_ps_bt.pressed.connect(
            _part(self._set_check_pwrstate, 'on'))

        self.test_bt = QPushButton('Test PS', self)
        self.test_bt.pressed.connect(self._set_lastcomm_label_text)
        self.test_bt.pressed.connect(self._test_ps)

        self.currzero_bt = QPushButton('Set PS Current to zero', self)
        self.currzero_bt.pressed.connect(self._set_lastcomm_label_text)
        self.currzero_bt.pressed.connect(self._zero_current)

        gbox_comm = QGroupBox('Commands', self)
        comm_layout = QVBoxLayout()
        comm_layout.setContentsMargins(20, 9, 20, 9)
        comm_layout.addWidget(QLabel(''))
        comm_layout.addWidget(self.setslowref_bt)
        comm_layout.addWidget(self.reset_bt)
        comm_layout.addWidget(self.turnoff_ps_bt)
        comm_layout.addWidget(QLabel(''))
        comm_layout.addWidget(self.turnon_dcl_bt)
        comm_layout.addWidget(self.setctrlloop_dcl_bt)
        comm_layout.addWidget(self.setvolt_dcl_bt)
        comm_layout.addWidget(QLabel(''))
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
        self.clearlists_bt.pressed.connect(self._clear_lastcomm)
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

    def _set_check_opmode(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return
        dclinks = _get_related_dclinks_data(devices).keys()
        devices.extend(dclinks)

        task1 = SetOpModeSlowRef(devices, self)
        task2 = CheckOpModeSlowRef(devices, self)
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
        dclinks = _get_related_dclinks_data(devices).keys()
        devices.extend(dclinks)

        task1 = ResetIntlk(devices, self)
        task2 = CheckIntlk(devices, self)
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

        task1 = SetPwrState(devices, state, self)
        task2 = CheckPwrState(devices, state, self)
        task2.itemDone.connect(self._log)

        labels = ['Turning PS '+state+'...',
                  'Checking PS powered '+state+'...']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _turn_on_dclinks(self):
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        dev2params = _get_related_dclinks_data(pwrsupplies)
        if not dev2params:
            return
        devices = dev2params.keys()

        self.ok_ps.clear()
        self.nok_ps.clear()
        task1 = SetPwrState(devices, 'on', self)
        task2 = CheckPwrState(devices, 'on', self)
        task3 = CheckOpModeSlowRef(devices, 'dclinks', self)
        task3.itemDone.connect(self._log)
        labels = ['Turning DCLinks On...',
                  'Checking DCLinks powered on...',
                  'Wait DCLinks OpMode turn to SlowRef...']
        tasks = [task1, task2, task3]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_dclinks_ctrlloop(self):
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        dev2params = _get_related_dclinks_data(pwrsupplies)
        if not dev2params:
            return

        self.ok_ps.clear()
        task1 = SetCtrlLoop(dev2params, self)
        task2 = CheckCtrlLoop(dev2params, self)
        task2.itemDone.connect(self._log)
        labels = ['Setting DCLinks CtrlLoop...',
                  'Checking DCLinks CtrlLoop state...']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_dclinks_capvolt(self):
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        dev2params = _get_related_dclinks_data(pwrsupplies)
        if not dev2params:
            return

        self.ok_ps.clear()
        task = SetCapBankVolt(dev2params, self)
        task.itemDone.connect(self._log)
        dlg = ProgressDialog('Setting capacitor bank voltage...', task, self)
        dlg.exec_()

    def _test_ps(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        task = SetCurrent(devices, is_test=True, parent=self)
        task.itemDone.connect(self._log)

        dlg = ProgressDialog('Testing PS...', task, self)
        dlg.exec_()

    def _zero_current(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        task = SetCurrent(devices, parent=self)
        task.itemDone.connect(self._log)

        dlg = ProgressDialog('Setting current to zero PS...', task, self)
        dlg.exec_()

    def _get_selected_ps(self):
        devices = self.tree.checked_items()
        if not devices:
            QMessageBox.critical(self, 'Message', 'No magnet selected!')
            return False
        return devices

    def _set_lastcomm_label_text(self):
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

    def _get_tree_names(self):
        lipsnames = PSSearch.get_psnames({'sec': 'LI', 'dis': 'PS'})
        manames = MASearch.get_manames({'sec': '(TB|BO)', 'dis': 'MA'})
        # TODO: uncomment when using TS and SI
        # manames = MASearch.get_manames({'sec': '(TB|BO|TS|SI)', 'dis': 'MA'})
        manames.extend(lipsnames)
        return manames

    def _filter_manames(self):
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

    def _open_detail(self, index):
        app = QApplication.instance()
        maname = index.data()
        if 'LI' in maname or maname in ['TB', 'BO', 'TS', 'SI']:
            return
        app.open_window(PSDetailWindow, parent=self, **{'psname': maname})


if __name__ == '__main__':
    application = SiriusApplication()
    w = PSTestWindow()
    w.show()
    sys.exit(application.exec_())
