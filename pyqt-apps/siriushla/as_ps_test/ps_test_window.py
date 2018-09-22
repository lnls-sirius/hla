"""Window to test power supplies."""
import time
import sys

import epics
from qtpy.QtCore import Qt, pyqtSignal, QThread
from qtpy.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QMainWindow, \
    QPushButton, QListWidget, QLabel, QApplication

from siriushla.as_ps_cycle.magnets_tree import MagnetTree
from siriushla.as_ps_cycle.progress_dialog import ProgressDialog
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from siriuspy.magnet.data import MAData
from siriuspy.envars import vaca_prefix as VACA_PREFIX


class PSTestWindow(QMainWindow):
    """PS test window."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._setup_ui()
        self.setWindowTitle('Power Supply Test')

    def _setup_ui(self):
        # Magnet tree selection widgets
        magnets_layout = QVBoxLayout()
        self.tree = MagnetTree(self)
        self.test_button = QPushButton('Test', self)
        self.test_button.setObjectName('TestButton')
        self.exit_button = QPushButton("Close", self)
        self.exit_button.setObjectName('ExitButton')
        magnets_layout.addWidget(self.tree)
        magnets_layout.addWidget(self.test_button)
        magnets_layout.addWidget(self.exit_button)
        # Text edits
        ok_layout = QVBoxLayout()
        nok_layout = QVBoxLayout()
        self.ok_ps = QListWidget(self)
        self.ok_ps.setObjectName('OkTextEdit')
        ok_layout.addWidget(
            QLabel('Ok Power Supplies', self), alignment=Qt.AlignCenter)
        ok_layout.addWidget(self.ok_ps)
        self.nok_ps = QListWidget(self)
        self.nok_ps.setObjectName('NokTextEdit')
        nok_layout.addWidget(
            QLabel('Failed Power Supplies', self), alignment=Qt.AlignCenter)
        nok_layout.addWidget(self.nok_ps)
        # Set central widget
        self.central_widget = QFrame()
        self.central_widget.layout = QHBoxLayout()
        self.central_widget.layout.addLayout(magnets_layout, stretch=1)
        self.central_widget.layout.addLayout(ok_layout, stretch=1)
        self.central_widget.layout.addLayout(nok_layout, stretch=1)
        self.central_widget.setLayout(self.central_widget.layout)
        self.setCentralWidget(self.central_widget)

        # Signals
        self.test_button.pressed.connect(self._check_power_status)
        self.exit_button.pressed.connect(self.close)
        self.nok_ps.doubleClicked.connect(self._open_detail)

    def _check_power_status(self):
        self.ok_ps.clear()
        self.nok_ps.clear()
        devices = self.tree.checked_items()
        task1 = ResetPS(devices, self)
        task2 = TurnPSOn(devices, self)
        task3 = CheckPSOn(devices, self)
        task3.isOn.connect(self._log)

        labels = ['Reseting PS', 'Turning PS on', 'Checking PS power status']
        tasks = [task1, task2, task3]

        dlg = ProgressDialog(labels, tasks, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return

        self._test_power_supply()

    def _test_power_supply(self):
        devices = [self.ok_ps.item(row).data(0)
                   for row in range(self.ok_ps.count())]
        task = TestPS(devices, self)
        task.itemTested.connect(self._log)
        self.ok_ps.clear()

        dlg = ProgressDialog('Testing PS...', task, self)
        dlg.exec_()

    def _log(self, name, status):
        if status:
            self.ok_ps.addItem(name)
        else:
            self.nok_ps.addItem(name)

    def _open_detail(self, index):
        app = QApplication.instance()
        maname = index.data()
        app.open_window(PSDetailWindow, parent=self, **{'psname': maname})


class ResetPS(QThread):
    """Reset."""

    itemDone = pyqtSignal()

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._pvs = [epics.get_pv(VACA_PREFIX + device + ':Reset-Cmd')
                     for device in devices]
        self._quit_task = False

    def size(self):
        """Task size."""
        return len(self._devices)

    def exit_task(self):
        """Set quit flag."""
        self._quit_task = True

    def run(self):
        """Execute task."""
        if not self._quit_task:
            for pv in self._pvs:
                if pv.connected:
                    pv.put(1)
                    time.sleep(5e-3)
                self.itemDone.emit()
        self.finished.emit()


class TurnPSOn(QThread):
    """Turn PS on."""

    itemDone = pyqtSignal()

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._pvs = [epics.get_pv(VACA_PREFIX + device + ':PwrState-Sel')
                     for device in devices]
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set PS on."""
        if self._quit_task:
            self.finished.emit()
        else:
            for pv in self._pvs:
                if pv.connected:
                    pv.put(1)
                    time.sleep(5e-3)
                self.itemDone.emit()
                if self._quit_task:
                    break
            time.sleep(5e-3*self.size())
            self.finished.emit()


class CheckPSOn(QThread):
    """Check if PS is on."""

    itemDone = pyqtSignal()
    isOn = pyqtSignal(str, bool)

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._devices = devices
        self._pvs = [epics.get_pv(VACA_PREFIX + device + ':PwrState-Sts')
                     for device in devices]
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._pvs)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set PS on."""
        time.sleep(1)
        if self._quit_task:
            self.finished.emit()
        else:
            for device, pv in zip(self._devices, self._pvs):
                t = time.time()
                is_on = False
                if pv.connected:
                    while time.time() - t < 10:
                        if pv.get() == 1:
                            is_on = True
                            break
                        if self._quit_task:
                            break
                self.itemDone.emit()
                self.isOn.emit(device, is_on)
                time.sleep(5e-3)
                if self._quit_task:
                    break
            self.finished.emit()


class TestPS(QThread):
    """Set value and check if it rb is achieved."""

    itemDone = pyqtSignal()
    itemTested = pyqtSignal(str, bool)

    def __init__(self, devices, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._error = 1e-6
        self._quit_task = False
        self._devices = devices
        self._sp_pvs = [epics.get_pv(VACA_PREFIX + device + ':Current-SP')
                        for device in devices]
        self._rb_pvs = [epics.get_pv(VACA_PREFIX + device + ':Current-RB')
                        for device in devices]

    def size(self):
        """Task size."""
        return len(self._devices)

    def exit_task(self):
        """Exit flag."""
        self._quit_task = True

    def run(self):
        """Set PS Current."""
        time.sleep(0.1)
        if self._quit_task:
            self.finished.emit()
        for i in range(len(self._devices)):
            dev_name = self._devices[i]
            rb = self._rb_pvs[i]
            sp = self._sp_pvs[i]

            if not rb.connected or not sp.connected:
                self.itemTested.emit(dev_name, False)
            else:
                success = False
                splims = MAData(dev_name).splims
                # sp.put(splims['HIGH'] - 2.0)
                # # time.sleep(0.01)

                # init = time.time()
                # while time.time() - init < 5:
                #     if self._cmp(rb.get(), splims['HIGH'] - 2.0):
                #         success = True
                #         break
                #     if self._quit_task:
                #         break

                # if not success:
                #     self.itemTested.emit(dev_name, False)
                #     self.itemDone.emit()
                #     continue

                # success = False
                sp.put(splims['HIGH'] - 1.0)
                # time.sleep(0.01)

                init = time.time()
                while time.time() - init < 10:
                    if self._cmp(rb.get(), splims['HIGH'] - 1.0):
                        success = True
                        break
                    if self._quit_task:
                        break

                self.itemTested.emit(dev_name, success)

            self.itemDone.emit()

            if self._quit_task:
                break
        self.finished.emit()

    def _cmp(self, value, target, error=1e-3):
        if abs(value - target) < error:
            return True
        else:
            return False


if __name__ == '__main__':
    application = SiriusApplication()
    application.setStyleSheet("""
        * {
            font: 20pt;
        }
        #OkTextEdit {
            background-color: #eafaea;
        }
        #NokTextEdit {
            background-color: #ffebe6;
        }
        PSTestWindow #TestButton {
            color: white;
            background-color: blue;
        }
        PSTestWindow #ExitButton {
            color: white;
            background-color: red;
        }
        QLabel {
            font-weight: bold;
        }
    """)

    w = PSTestWindow()
    w.show()

    sys.exit(application.exec_())
