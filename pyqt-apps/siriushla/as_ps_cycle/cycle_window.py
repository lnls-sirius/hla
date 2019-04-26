"""Magnet cycle window."""

import time as _time
import re as _re
from functools import partial as _part

from qtpy.QtCore import Signal, QThread, Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QGroupBox, \
    QPushButton, QLabel, QMessageBox, QLineEdit, QApplication

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search import MASearch as _MASearch

from siriushla.widgets import SiriusMainWindow, \
    PyDMLedMultiConnection as PyDMLedMultiConn
from siriushla.as_ps_cycle.cycle_status_list import CycleStatusList
from siriushla.widgets.pvnames_tree import PVNameTree
from siriushla.widgets.dialog import ProgressDialog
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow

from .util import MagnetCycler, Timing, get_manames, \
    get_manames_from_same_udc

_cyclers = dict()


class CycleWindow(SiriusMainWindow):
    """Magnet cycle window."""

    def __init__(self, parent=None, checked_accs=()):
        """Constructor."""
        super().__init__(parent)
        # Data structs
        self._timing = Timing()
        self._magnets_ready = list()
        self._magnets_failed = list()
        self._checked_accs = checked_accs
        # Setup UI
        self._setup_ui()
        self.setWindowTitle('Magnet Cycling')

    def _setup_ui(self):
        # central widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName('CentralWidget')
        self.central_widget.setStyleSheet("""
            #CentralWidget {
                min-width: 30em;
                min-height: 40em;
            }""")
        self.setCentralWidget(self.central_widget)

        # widgets
        gb_ma = QGroupBox('Select magnets:')
        self.search_le = QLineEdit()
        self.search_le.setPlaceholderText('Filter...')
        self.search_le.editingFinished.connect(self._filter_manames)
        self.magnets_tree = PVNameTree(get_manames(), ('sec', 'mag_group'),
                                       self._checked_accs, self)
        self.magnets_tree.setHeaderHidden(True)
        self.magnets_tree.setColumnCount(1)
        glay_ma = QVBoxLayout()
        glay_ma.addWidget(self.search_le)
        glay_ma.addWidget(self.magnets_tree)
        gb_ma.setLayout(glay_ma)

        gb_demag = QGroupBox('Demagnetize')
        self.prepare_demag_bt = QPushButton('Prepare', self)
        self.prepare_demag_bt.pressed.connect(
            _part(self._prepare_to_cycle, 'Cycle'))
        self.demag_bt = QPushButton('Demagnetize', self)
        self.demag_bt.setEnabled(False)
        self.demag_bt.pressed.connect(_part(self._cycle, 'Cycle'))
        vlay_demag = QVBoxLayout()
        vlay_demag.addWidget(self.prepare_demag_bt)
        vlay_demag.addWidget(self.demag_bt)
        gb_demag.setLayout(vlay_demag)

        gb_cycle = QGroupBox('Cycle')
        self.prepare_cycle_bt = QPushButton('Prepare', self)
        # self.prepare_cycle_bt.setEnabled(False)
        self.prepare_cycle_bt.pressed.connect(
            _part(self._prepare_to_cycle, 'Ramp'))
        self.cycle_bt = QPushButton('Cycle', self)
        self.cycle_bt.setEnabled(False)
        self.cycle_bt.pressed.connect(_part(self._cycle, 'Ramp'))
        vlay_cycle = QVBoxLayout()
        vlay_cycle.addWidget(self.prepare_cycle_bt)
        vlay_cycle.addWidget(self.cycle_bt)
        gb_cycle.setLayout(vlay_cycle)

        gb_status = QGroupBox('Status')
        self.status_list = CycleStatusList()
        tipvs = list()
        for cycletype in self._timing.properties:
            for pvname in self._timing.properties[cycletype].keys():
                tipvs.append(VACA_PREFIX + pvname)
        self.ticonn_led = PyDMLedMultiConn(self, tipvs)
        self.ticonn_led.shape = 2
        self.maconn_led = PyDMLedMultiConn()
        self.maconn_led.shape = 2
        glay_status = QGridLayout()
        glay_status.addWidget(QLabel('Timing conn?', self,
                              alignment=Qt.AlignCenter), 0, 0)
        glay_status.addWidget(self.ticonn_led, 1, 0)
        glay_status.addWidget(QLabel('Selected magnets conn?', self,
                              alignment=Qt.AlignCenter), 0, 1)
        glay_status.addWidget(self.maconn_led, 1, 1)
        glay_status.addWidget(QLabel('List of failed magnets:'), 3, 0, 1, 2)
        glay_status.addWidget(self.status_list, 4, 0, 1, 2)
        glay_status.setRowStretch(0, 2)
        glay_status.setRowStretch(1, 2)
        glay_status.setRowStretch(2, 1)
        glay_status.setRowStretch(3, 2)
        glay_status.setRowStretch(4, 30)
        gb_status.setLayout(glay_status)

        # connect tree signals
        self.magnets_tree.doubleClicked.connect(self._open_magnet_detail)
        self.magnets_tree.itemChanged.connect(
            self._check_manames_from_same_udc)

        # layout
        layout = QGridLayout()
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(10)
        layout.addWidget(QLabel('<h3>Magnet Cycling</h3>', self,
                                alignment=Qt.AlignCenter), 0, 0, 1, 3)
        layout.addWidget(gb_ma, 1, 0, 2, 1)
        layout.addWidget(gb_demag, 1, 1)
        layout.addWidget(gb_cycle, 1, 2)
        layout.addWidget(gb_status, 2, 1, 1, 2)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 3)
        layout.setRowStretch(2, 15)

        self.central_widget.setLayout(layout)

    def _prepare_timing(self, mode):
        if not self._timing.connected:
            pvs_disconnected = self._timing.status_nok
            sttr = ''
            for item in pvs_disconnected:
                sttr += item + '\n'
            QMessageBox.information(
                self, 'Message', 'Timing PVs are not connected!\n'+sttr)
            return False
        self._timing.init(mode)
        return True

    def _prepare_magnets(self, mode):
        magnets = self._get_magnets_list(mode, prepare=True)
        if not magnets:
            return False

        # Set magnets to proper cycling state
        self._magnets_ready = list()
        self._magnets_failed = list()
        task = SetToCycle(magnets, mode, self)
        task.itemDone.connect(self._update_cycling_status)
        dlg = ProgressDialog('Setting magnets...', task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

        # Show failed magnets
        if not self._magnets_failed:
            self.status_list.magnets = []
            return True
        else:
            self.status_list.magnets = self._magnets_failed
            return False

    def _prepare_to_cycle(self, mode):
        # Prepare timing to cycle
        status = self._prepare_timing(mode)
        if not status:
            return

        status = self._prepare_magnets(mode)
        if not status:
            self.demag_bt.setEnabled(False)
            self.cycle_bt.setEnabled(False)
        else:
            if mode == 'Cycle':
                self.demag_bt.setEnabled(True)
            else:
                self.cycle_bt.setEnabled(True)

    def _cycle(self, mode):
        magnets = self._get_magnets_list(mode)
        if not magnets:
            return False

        self._magnets_ready = list()
        self._magnets_failed = list()
        task = VerifyCycle(magnets, mode, self)
        task.itemDone.connect(self._update_cycling_status)
        dlg = ProgressDialog('Checking magnets...', task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

        if self._magnets_failed:
            self.cycle_bt.setEnabled(False)
            if mode == 'Cycle':
                self.demag_bt.setEnabled(False)
            self.status_list.magnets = self._magnets_failed
            return False

        # Trigger timing and wait cyling end
        task = WaitCycle(magnets, self._timing, mode, self)
        dlg = ProgressDialog('Wait for magnets...', task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False
        QMessageBox.information(self, 'Message', 'Cycle finished sucessfully!')

    def _reset_magnets(self):
        magnets = self._get_magnets_list()
        if not magnets:
            return False
        task = ResetMagnetsOpMode(magnets, self)
        dlg = ProgressDialog('Setting OpMode to SlowRef...', task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

    def _reset_timing(self):
        self._timing.reset()

        # Get magnets list
        magnets = self.magnets_tree.checked_items()
        if mode == 'Ramp':
            bo_ma = _MASearch.get_manames(filters={'sec': 'BO', 'dis': 'MA'})
            not_bo = ''
            for name in magnets:
                if name not in bo_ma:
                    not_bo += name + '\n'
            if not_bo:
                ans = QMessageBox.question(
                    self, 'Warning',
                    'Are you sure you\'re ramping the following magnets?\n' +
                    not_bo, QMessageBox.Yes, QMessageBox.Cancel)
                if ans == QMessageBox.Cancel:
                    return False

        # Show message if no magnet is selected
        if not magnets:
            aux_str = ' Booster' if mode == 'Ramp' else ''
            btfunc_str = 'prepare to ' if prepare else ''
            mode_str = 'demagnetize' if mode == 'Cycle' else 'cycle'
            QMessageBox.about(
                self, 'Message', 'Select' + aux_str +
                ' magnets to ' + btfunc_str + mode_str + '!')
            return False

        # Create new cyclers if needed
        self._create_cyclers(magnets)
        return magnets

    def _create_cyclers(self, manames):
        """Create new cyclers, if necessary."""
        task = CreateCyclers(manames)
        dlg = ProgressDialog('Connecting to magnets...', task, self)
        dlg.exec_()

    def _update_cycling_status(self, maname, status):
        """Check magnet cycling status."""
        if status:
            self._magnets_ready.append(maname)
        else:
            self._magnets_failed.append(maname)

    def _filter_manames(self):
        text = self.search_le.text()

        try:
            pattern = _re.compile(text, _re.I)
        except Exception:  # Ignore malformed patterns?
            pattern = _re.compile("malformed")

        for node in self.magnets_tree._leafs:
            if pattern.search(node.data(0, 0)):
                node.setHidden(False)
            else:
                node.setHidden(True)

    def _open_magnet_detail(self, item):
        app = QApplication.instance()
        maname = item.data()
        if maname in ['TB', 'BO', 'TS', 'SI']:
            return
        app.open_window(PSDetailWindow, parent=self, **{'psname': maname})

    def _check_manames_from_same_udc(self, item):
        maname = item.data(0, Qt.DisplayRole)
        if maname in ['TB', 'BO', 'TS', 'SI']:
            pass
        else:
            manames2check = get_manames_from_same_udc(maname)
            manames2check.remove(maname)
            for maname in manames2check:
                item = self.magnets_tree._item_map[maname]
                state = item.checkState(0)
                state2set = Qt.Checked if state == Qt.Unchecked \
                    else Qt.Unchecked
                self.magnets_tree.blockSignals(True)
                item.setCheckState(0, state2set)
                self.magnets_tree.blockSignals(False)
        self._update_maled_channels()

    def _update_maled_channels(self):
        self.maconn_led.set_channels(
            [VACA_PREFIX + name + ':Version-Cte'
             for name in self.magnets_tree.checked_items()])


class CreateCyclers(QThread):

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, manames, parent=None):
        super().__init__(parent)
        self._manames = manames
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._manames)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Create cyclers."""
        if self._quit_task:
            pass
        else:
            global _cyclers
            for maname in self._manames:
                if maname not in _cyclers.keys():
                    self.currentItem.emit(maname)
                    _cyclers[maname] = MagnetCycler(maname)
                    self.itemDone.emit()
            self.completed.emit()


class SetToCycle(QThread):
    """Set magnet to cycle."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, manames, mode, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._manames = manames
        self._mode = mode
        self._quit_task = False

    def size(self):
        """Return task size."""
        return 2*len(self._manames)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set magnets to cycling."""
        if self._quit_task:
            pass
        else:
            # config params
            for maname in self._manames:
                cycler = _cyclers[maname]
                self.currentItem.emit('Setting '+maname+' parameters...')
                done = cycler.config_cycle_params(self._mode)
                self.itemDone.emit(maname, done)
                if self._quit_task:
                    break
            # config opmodes
            for maname in self._manames:
                cycler = _cyclers[maname]
                self.currentItem.emit('Setting '+maname+' OpMode...')
                done = cycler.config_cycle_opmode(self._mode)
                self.itemDone.emit(maname, done)
                if self._quit_task:
                    break
            else:
                self.completed.emit()


class VerifyCycle(QThread):
    """Verify cycle."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, manames, mode, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._manames = manames
        self._mode = mode
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._manames)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set magnets to cycling."""
        if self._quit_task:
            pass
        else:
            for maname in self._manames:
                cycler = _cyclers[maname]
                self.currentItem.emit(maname)
                status = cycler.is_ready(self._mode)
                self.itemDone.emit(maname, status)
                if self._quit_task:
                    break
            else:
                self.completed.emit()


class WaitCycle(QThread):
    """Wait cycle."""

    currentItem = Signal(str)
    itemDone = Signal()
    completed = Signal()

    def __init__(self, manames, timing_conn, mode, parent=None):
        """Build PVs."""
        super().__init__(parent)
        self._manames = manames
        self._timing_conn = timing_conn
        self._mode = mode
        self._quit_task = False

        self._duration = 0
        for maname in manames:
            ma_cycle_duration = _cyclers[maname].cycle_duration(mode)
            self._duration = max(ma_cycle_duration, self._duration)

        if mode == 'Cycle':
            self._format_msg = 'Missing {} seconds...'
        else:
            self._format_msg = 'Cycle {} of ' +\
                str(self._timing_conn.DEFAULT_RAMP_NRCYCLES)+'...'

    def size(self):
        """Return task size."""
        return self._duration

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Start thread."""
        if self._quit_task:
            pass
        else:
            # Trigger timing
            self._timing_conn.trigger(self._mode)

            # Wait for cycling
            t0 = _time.time()
            interrupted = False
            keep_waiting = True
            while keep_waiting:
                self.currentItem.emit(self._format_msg.format(
                    self._check_curr_step(t0)))
                _time.sleep(min(1, self._duration/10))
                keep_waiting = self._check_keep_waiting(t0)
                self.itemDone.emit()
                if self._quit_task:
                    interrupted = True
                    break

            # If ended without interruption
            if not interrupted:
                self.completed.emit()

    def _check_curr_step(self, t0):
        if self._mode == 'Cycle':
            return round(self._duration - (_time.time()-t0))
        else:
            return self._timing_conn.get_cycle_count()

    def _check_keep_waiting(self, t0):
        if self._mode == 'Cycle':
            return _time.time() - t0 < self._duration
        else:
            return not self._timing_conn.check_ramp_end()


class ResetMagnetsOpMode(QThread):
    """Set magnet to cycle."""

    currentItem = Signal(str)
    itemDone = Signal(str, bool)
    completed = Signal()

    def __init__(self, manames, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._manames = manames
        self._quit_task = False

    def size(self):
        """Return task size."""
        return len(self._manames)

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Set magnets to cycling."""
        if self._quit_task:
            pass
        else:
            for maname in self._manames:
                self.currentItem.emit(maname)
                done = _cyclers[maname].reset_opmode()
                self.itemDone.emit(maname, done)
                if self._quit_task:
                    break
            else:
                self.completed.emit()


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    application = SiriusApplication()

    w = CycleWindow()
    w.show()

    sys.exit(application.exec_())
