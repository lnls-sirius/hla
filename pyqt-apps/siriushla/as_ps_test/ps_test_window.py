"""Window to test power supplies."""
import sys
import re as _re
from functools import partial as _part

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLineEdit, \
    QPushButton, QListWidget, QLabel, QApplication, QMessageBox

from siriushla.sirius_application import SiriusApplication
from siriuspy.search import PSSearch, MASearch
from siriuspy.csdevice.pwrsupply import Const as _PSC

from siriushla.widgets import SiriusMainWindow, PVNameTree
from siriushla.widgets.dialog import ProgressDialog
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from .tasks import ResetIntlk, CheckIntlk, \
    SetOpModeSlowRef, CheckOpModeSlowRef, \
    SetPwrState, CheckPwrState, \
    SetCtrlLoop, CheckCtrlLoop, \
    SetCapBankVolt, SetCurrent
from .dclinks_data import DEFAULT_CAP_BANK_VOLT


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
        lay = QHBoxLayout()
        self.central_widget.setLayout(lay)
        self.central_widget.setStyleSheet("""
            #OkList {
                background-color: #eafaea;
            }
            #NokList {
                background-color: #ffebe6;
            }
            QLabel {
                font-weight: bold;
            }""")
        self.setCentralWidget(self.central_widget)

        # magnets selection and control
        self.search_le = QLineEdit()
        self.search_le.setPlaceholderText('Filter...')
        self.search_le.editingFinished.connect(self._filter_manames)

        self.tree = PVNameTree(items=self._get_tree_names(),
                               tree_levels=('sec', 'mag_group'), parent=self)
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(1)
        self.tree.doubleClicked.connect(self._open_detail)

        self.resetps_bt = QPushButton('Reset', self)
        self.resetps_bt.pressed.connect(_part(self._reset_intlk, 'ps'))

        self.resetdclink_bt = QPushButton('Reset DCLinks', self)
        self.resetdclink_bt.pressed.connect(_part(self._reset_intlk, 'dclink'))

        self.setslowref_bt = QPushButton('Set OpMode to SlowRef', self)
        self.setslowref_bt.pressed.connect(self._set_check_opmode)

        self.turnoff_bt = QPushButton('Turn Off', self)
        self.turnoff_bt.pressed.connect(_part(self._set_check_pwrstate, 'off'))

        self.turnondclink_bt = QPushButton('Turn On DCLinks', self)
        self.turnondclink_bt.pressed.connect(self._turn_on_dclinks)

        self.turnon_bt = QPushButton('Turn On', self)
        self.turnon_bt.pressed.connect(_part(self._set_check_pwrstate, 'on'))

        self.test_bt = QPushButton('Test', self)
        self.test_bt.pressed.connect(self._test_ps)

        self.currzero_bt = QPushButton('Zero Current', self)
        self.currzero_bt.pressed.connect(self._zero_current)

        magnets_layout = QVBoxLayout()
        magnets_layout.addWidget(QLabel('Select power supplies to test:'))
        magnets_layout.addWidget(self.search_le)
        magnets_layout.addWidget(self.tree)
        magnets_layout.addWidget(self.resetps_bt)
        magnets_layout.addWidget(self.resetdclink_bt)
        magnets_layout.addWidget(self.setslowref_bt)
        magnets_layout.addWidget(self.turnoff_bt)
        magnets_layout.addWidget(self.turnondclink_bt)
        magnets_layout.addWidget(self.turnon_bt)
        magnets_layout.addWidget(self.test_bt)
        magnets_layout.addWidget(self.currzero_bt)
        lay.addLayout(magnets_layout, stretch=1)

        # lists
        self.ok_ps = QListWidget(self)
        self.ok_ps.setObjectName('OkList')
        self.ok_ps.doubleClicked.connect(self._open_detail)
        ok_layout = QVBoxLayout()
        ok_layout.addWidget(QLabel('Ok Power Supplies', self,
                                   alignment=Qt.AlignCenter))
        ok_layout.addWidget(self.ok_ps)
        lay.addLayout(ok_layout, stretch=1)

        self.nok_ps = QListWidget(self)
        self.nok_ps.setObjectName('NokList')
        self.nok_ps.doubleClicked.connect(self._open_detail)
        nok_layout = QVBoxLayout()
        nok_layout.addWidget(QLabel('Failed Power Supplies', self,
                                    alignment=Qt.AlignCenter))
        nok_layout.addWidget(self.nok_ps)
        lay.addLayout(nok_layout, stretch=1)

    def _reset_intlk(self, pstype=''):
        self.ok_ps.clear()
        self.nok_ps.clear()
        powersupplies = self._get_selected_ps()
        if not powersupplies:
            return
        if pstype == 'dclink':
            devices = self._get_ps_related_dclinks(powersupplies).keys()
        else:
            devices = powersupplies

        task1 = ResetIntlk(devices, self)
        task2 = CheckIntlk(devices, self)
        task2.itemDone.connect(self._log)

        labels = ['Reseting PS...', 'Checking PS Interlocks...']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_opmode(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_selected_ps()
        if not devices:
            return

        task1 = SetOpModeSlowRef(devices, self)
        task2 = CheckOpModeSlowRef(devices, self)
        task2.itemDone.connect(self._log)

        labels = ['Setting PS OpMode to SlowRef...', 'Checking PS OpMode...']
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
        self.ok_ps.clear()
        self.nok_ps.clear()
        pwrsupplies = self._get_selected_ps()
        if not pwrsupplies:
            return
        dev2params = self._get_ps_related_dclinks(pwrsupplies)
        if not dev2params:
            return

        # turn on dclinks
        task1 = SetPwrState(dev2params.keys(), 'on', self)
        task2 = CheckPwrState(dev2params.keys(), 'on', self)
        task2.itemDone.connect(self._log)
        labels = ['Turning DCLinks On...', 'Checking DCLinks powered on...']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()
        if self.nok_ps.count() > 0:
            return

        # wait untill dclinks initialize
        self.ok_ps.clear()
        task = CheckOpModeSlowRef(dev2params.keys(), self)
        task.itemDone.connect(self._log)
        dlg = ProgressDialog(
            'Wait DCLinks OpMode turn to SlowRef...', task, self)
        dlg.exec_()
        if self.nok_ps.count() > 0:
            return

        # set dclinks ctrlloop
        self.ok_ps.clear()
        task1 = SetCtrlLoop(dev2params, self)
        task2 = CheckCtrlLoop(dev2params, self)
        task2.itemDone.connect(self._log)
        labels = ['Setting DCLinks CtrlLoop...',
                  'Checking DCLinks CtrlLoop state...']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()
        if self.nok_ps.count() > 0:
            return

        # set capacitor bank voltage
        self.ok_ps.clear()
        task = SetCapBankVolt(dev2params, self)
        task.itemDone.connect(self._log)
        dlg = ProgressDialog('Setting capacitor bank voltage...', task, self)
        dlg.exec_()
        if self.nok_ps.count() > 0:
            return

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

    def _get_ps_related_dclinks(self, tree_names):
        alldclinks = dict()
        for name in tree_names:
            if 'LI' in name:
                continue
            psnames = MASearch.conv_maname_2_psnames(name)
            dclinkparams = dict()
            for ps in psnames:
                dclinks = PSSearch.conv_psname_2_dclink(ps)
                if dclinks:
                    for dcl in dclinks:
                        if PSSearch.conv_psname_2_psmodel(dcl) == 'FBP_DCLink':
                            ctrlloop = _PSC.OpenLoop.Open
                            capvolt = DEFAULT_CAP_BANK_VOLT['Default']
                        else:
                            ctrlloop = _PSC.OpenLoop.Closed
                            capvolt = DEFAULT_CAP_BANK_VOLT[ps]
                        dclinkparams.update({dcl: [ctrlloop, capvolt]})
            alldclinks.update(dclinkparams)
        return alldclinks

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
