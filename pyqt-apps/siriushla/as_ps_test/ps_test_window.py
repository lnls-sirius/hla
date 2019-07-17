"""Window to test power supplies."""
import sys
import re as _re
from functools import partial as _part

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLineEdit, \
    QPushButton, QListWidget, QLabel, QApplication, QMessageBox

from siriuspy.search import PSSearch, MASearch

from siriushla.widgets import SiriusMainWindow, PVNameTree
from siriushla.widgets.dialog import ProgressDialog
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from .tasks import ResetIntlk, CheckIntlk, \
    SetPwrState, CheckPwrState, SetCurrent


class PSTestWindow(SiriusMainWindow):
    """PS test window."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._setup_ui()
        self.setWindowTitle('Power Supply Test')

    def _setup_ui(self):
        # setup central widget
        self.central_widget = QFrame()
        self.central_widget.setObjectName("CentralWidget")
        lay = QHBoxLayout()
        self.central_widget.setLayout(lay)
        self.central_widget.setStyleSheet("""
            #CentralWidget {
                min-width: 70em;
            }
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
        self.reset_bt = QPushButton('Reset', self)
        self.reset_bt.pressed.connect(self._reset_interlocks)
        self.turnoff_bt = QPushButton('Turn Off', self)
        self.turnoff_bt.pressed.connect(_part(self._set_check_pwrstate, 'off'))
        self.turnon_bt = QPushButton('Turn On', self)
        self.turnon_bt.pressed.connect(_part(self._set_check_pwrstate, 'on'))
        self.test_bt = QPushButton('Test', self)
        self.test_bt.pressed.connect(self._test_ps)
        self.currzero_bt = QPushButton('Zero Current', self)
        self.currzero_bt.pressed.connect(self._zero_current)
        magnets_layout = QVBoxLayout()
        magnets_layout.addWidget(self.search_le)
        magnets_layout.addWidget(self.tree)
        magnets_layout.addWidget(self.reset_bt)
        magnets_layout.addWidget(self.turnoff_bt)
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

    def _reset_interlocks(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_manames()
        if not devices:
            return

        task1 = ResetIntlk(devices, self)
        task2 = CheckIntlk(devices, self)
        task2.itemDone.connect(self._log)

        labels = ['Reseting PS', 'Checking PS Interlocks']
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _set_check_pwrstate(self, state):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_manames()
        if not devices:
            return

        task1 = SetPwrState(devices, state, self)
        task2 = CheckPwrState(devices, state, self)
        task2.itemDone.connect(self._log)

        labels = ['Turning PS '+state, 'Checking PS power '+state]
        tasks = [task1, task2]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.exec_()

    def _test_ps(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_manames()
        if not devices:
            return

        task = SetCurrent(devices, is_test=True, parent=self)
        task.itemDone.connect(self._log)

        dlg = ProgressDialog('Testing PS...', task, self)
        dlg.exec_()

    def _zero_current(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self._get_manames()
        if not devices:
            return

        task = SetCurrent(devices, parent=self)
        task.itemDone.connect(self._log)

        dlg = ProgressDialog('Setting current to zero PS...', task, self)
        dlg.exec_()

    def _get_manames(self):
        devices = self.tree.checked_items()

        if not devices:
            QMessageBox.critical(self, 'Message', 'No magnet selected!')
            return False
        return devices

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
