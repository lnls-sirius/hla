"""Magnet cycle window."""

import time

from qtpy.QtCore import Signal, QThread, Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QPushButton, QDialog, QLabel, QMessageBox

from siriushla.widgets.windows import SiriusMainWindow
from siriushla.as_ps_cycle.cycle_status_list import CycleStatusList
from siriushla.widgets.pvnames_tree import PVNameTree
from siriushla.widgets.dialog import ProgressDialog

from .util import MagnetCycler, Timing, get_manames


class CycleWindow(SiriusMainWindow):
    """Magnet cycle window."""

    def __init__(self, parent=None, checked_accs=()):
        """Constructor."""
        super().__init__(parent)
        # Data structs
        self._timing = Timing()
        self._magnets = list()
        self._magnets_ready = list()
        self._magnets_failed = list()
        self._cyclers = list()
        self._checked_accs = checked_accs
        # Setup UI
        self._setup_ui()
        self.central_widget.setStyleSheet("""
            #CentralWidget {
                min-width: 30em;
                min-height: 40em;
            }
        """)
        self.setWindowTitle('Magnet Cycling')

    def _setup_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName('CentralWidget')
        self.central_widget.layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget.layout)

        self.prepare_button = QPushButton("Prepare to cycle", self)
        self.prepare_button.setObjectName('PrepareButton')
        self.magnets_tree = PVNameTree(get_manames(), ('sec', 'mag_group'),
                                       self, self._checked_accs)

        self.central_widget.layout.addWidget(
            QLabel('<h3>Magnet Cycling</h3>', self, alignment=Qt.AlignCenter))
        self.central_widget.layout.addWidget(
            QLabel('Select magnets to cycle:', self))
        self.central_widget.layout.addWidget(self.magnets_tree)
        self.central_widget.layout.addWidget(self.prepare_button)

        self.setCentralWidget(self.central_widget)

        self.prepare_button.pressed.connect(self._prepare_to_cycle)

    def _prepare_timing(self):
        self._timing.init()
        status_nok = self._timing.status_nok
        if status_nok:
            sttr = 'Disconnected timing PVs: '
            for pvname in status_nok:
                sttr += pvname + ' '
            QMessageBox.information(self, 'Message', sttr)
            return False
        return True

    def _prepare_to_cycle(self):

        self._prepare_timing()

        self._magnets = self.magnets_tree.checked_items()
        self._magnets_ready = list()
        self._magnets_failed = list()
        self._cyclers = [MagnetCycler(maname) for maname in self._magnets]

        # Set magnets to proper cycling state
        task1 = SetToCycle(self._cyclers, self)
        task2 = VerifyCycle(self._cyclers, self)
        task2.itemChecked.connect(self._check_cycling_status)

        labels = ['Setting magnets...', 'Checking magnets...']
        tasks = [task1, task2]

        dlg = ProgressDialog(labels, tasks, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return
        # Show failed magnets or ask to cycle
        dlg = CyclingDlg(self._magnets_failed, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return
        # Wait cyling end
        task = WaitCycle(self._cyclers, self)
        dlg = ProgressDialog('Wait for magnets to cycle...', task, self)
        self._cycle()
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return

        QMessageBox.information(self, 'Message', 'Cycle finished sucessfully!')
        self.close()

    def _cycle(self):
        """."""
        if self._prepare_timing():
            self._timing.trigger()

    def _check_cycling_status(self, cycler, status):
        """Check magnet cycling status."""
        row = self._cyclers.index(cycler)
        if status:
            self._magnets_ready.append(self._magnets[row])
        else:
            self._magnets_failed.append(self._magnets[row])


class CyclingDlg(QDialog):
    """Magnet cycle dialog."""

    def __init__(self, magnets, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._magnets = magnets

        self._cyclers = dict()
        for magnet in magnets:
            self._cyclers[magnet] = MagnetCycler(magnet)

        # Setup user interface
        self._setup_ui()
        self._connect_buttons()

    def _setup_ui(self):
        layout = QVBoxLayout()

        btn_group = QHBoxLayout()
        self.cycle_btn = QPushButton('Cycle', self)
        self.cancel_btn = QPushButton('Cancel', self)
        btn_group.addWidget(self.cycle_btn)
        btn_group.addWidget(self.cancel_btn)
        if not self._magnets:
            self.label = QLabel('All magnets ready to cycle', self)
            self.status_list = None
            layout.addWidget(self.label)
            layout.addLayout(btn_group)
        else:
            self.label = QLabel(
                'Failed to set {} magnets'.format(len(self._magnets)), self)
            self.cycle_btn.setEnabled(False)
            self.status_list = CycleStatusList(self._magnets)

            layout.addWidget(self.status_list)
            layout.addWidget(self.label)
            layout.addLayout(btn_group)

        self.setLayout(layout)

    def _connect_buttons(self):
        self.cycle_btn.pressed.connect(self.accept)
        self.cancel_btn.pressed.connect(self.reject)


class SetToCycle(QThread):
    """Set magnet to cycle."""

    currentItem = Signal(str)
    itemDone = Signal()

    def __init__(self, cyclers, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._cyclers = cyclers
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._cyclers)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set magnets to cycling."""
        if self._quit_task:
            self.finished.emit()
        else:
            for cycler in self._cyclers:
                self.currentItem.emit(cycler.maname)
                cycler.set_cycle()
                self.itemDone.emit()
                if self._quit_task:
                    break
            self.finished.emit()


class VerifyCycle(QThread):
    """Verify cycle."""

    currentItem = Signal(str)
    itemDone = Signal()
    itemChecked = Signal(MagnetCycler, bool)

    def __init__(self, cyclers, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._cyclers = cyclers
        self.quit_task = False

    def size(self):
        """Return task size."""
        return len(self._cyclers)

    def exit_task(self):
        """Set flag to quit thread."""
        self.quit_task = True

    def run(self):
        """Set magnets to cycling."""
        if self.quit_task:
            self.finished.emit()
        else:
            time.sleep(2)
            for cycler in self._cyclers:
                self.currentItem.emit(cycler.maname)
                status = cycler.is_ready()
                if self.quit_task:
                    break
                self.itemDone.emit()
                self.itemChecked.emit(cycler, status)
            self.finished.emit()


class WaitCycle(QThread):
    """Cycle."""

    currentItem = Signal(str)
    itemDone = Signal()

    def __init__(self, cyclers, parent=None):
        """Build PVs."""
        super().__init__(parent)
        self._cyclers = cyclers
        self.quit_task = False

        self.pvs_state = {cycler.cycleenbl_mon.pvname: 0 for cycler in cyclers}
        self.ps_count = len(self.pvs_state)
        self.ps_cycled = 0

        for cycler in cyclers:
            cycler.cycleenbl.add_callback(self.check_cycle_end)

    def size(self):
        """Return task size."""
        return len(self._cyclers)

    def exit_task(self):
        """Set flag to quit thread."""
        self.quit_task = True

    def run(self):
        """Start thread."""
        while self.ps_cycled < self.ps_count:
            time.sleep(0.1)
            if self.quit_task:
                break
        self.finished.emit()

    def check_cycle_end(self, pvname, value, **kwargs):
        """Check wether cycle finished."""
        cb_info = kwargs['cb_info']
        state = self.pvs_state[pvname]
        if state == 0:
            if value == 0:
                pass
            elif value == 1:
                self.pvs_state[pvname] = 1
        elif state == 1:
            if value == 0:
                cb_info[1].remove_callback(cb_info[0])
                self.itemDone.emit()
                self.ps_cycled += 1
            elif value == 1:
                pass


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    application = SiriusApplication()

    w = CycleWindow()
    w.show()

    sys.exit(application.exec_())
