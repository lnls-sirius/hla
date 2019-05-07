"""Magnet cycle window."""

import time as _time
import re as _re
import threading as _thread
from datetime import datetime as _datetime
from functools import partial as _part

from qtpy.QtGui import QColor
from qtpy.QtCore import Signal, QThread, Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QPushButton, QLabel, QMessageBox, QLineEdit, QApplication, QGroupBox, \
    QTabWidget, QListWidget, QListWidgetItem

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search import MASearch as _MASearch
from siriuspy.namesys import Filter

from siriushla.widgets import SiriusMainWindow, \
    PyDMLedMultiConnection as PyDMLedMultiConn
from siriushla.as_ps_cycle.cycle_status_list import CycleStatusList
from siriushla.widgets.pvnames_tree import PVNameTree
from siriushla.widgets.dialog import ProgressDialog
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow

from .util import MagnetCycler, Timing, get_manames, \
    get_manames_from_same_udc, AutomatedCycle

_cyclers = dict()


errorcolor = QColor(255, 0, 0)
warncolor = QColor(200, 200, 0)


class CycleWindow(SiriusMainWindow):
    """Magnet cycle window."""

    auto_cycle_aborted = Signal()

    def __init__(self, parent=None, checked_accs=()):
        """Constructor."""
        super().__init__(parent)
        # Data structs
        self._timing = Timing()
        self._magnets2cycle = list()
        self._magnets_ready = list()
        self._magnets_failed = list()
        self._checked_accs = checked_accs
        # Setup UI
        self._setup_ui()
        self.setWindowTitle('Magnet Cycling')

    def _setup_ui(self):
        # central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # treeview
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

        # leds
        gb_status = QGroupBox('Status')
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
        glay_status.setAlignment(Qt.AlignBottom)
        gb_status.setLayout(glay_status)

        # tabwidget
        self._tab_widget = QTabWidget()

        self._tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border-top: 2px solid black;
                border-bottom: 2px solid gray;
                border-left: 2px solid gray;
                border-right: 2px solid gray;}""")

        # Tab Automated
        self._tab_auto = QWidget()
        # widgets
        self.auto_exec_bt = QPushButton('Execute automated cycle')
        self.auto_exec_bt.setStyleSheet('min-height:2.5em;')
        self.auto_exec_bt.clicked.connect(self._auto_cycle)
        self.progress_list = QListWidget()
        self.auto_cancel_bt = QPushButton('Cancel')
        self.auto_cancel_bt.clicked.connect(self.auto_cycle_aborted.emit)
        autolay = QVBoxLayout()
        autolay.addWidget(self.auto_exec_bt)
        autolay.addWidget(self.progress_list)
        autolay.addWidget(self.auto_cancel_bt)
        self._tab_auto.setLayout(autolay)
        self._tab_widget.addTab(self._tab_auto, 'Automated')

        # Tab Manual
        self._tab_manual = QWidget()
        gb_demag = QGroupBox('Demagnetize')
        self.prepare_demag_bt = QPushButton('Prepare', self)
        self.prepare_demag_bt.clicked.connect(
            _part(self._prepare_to_cycle, 'Cycle'))
        self.demag_bt = QPushButton('Demagnetize', self)
        self.demag_bt.setEnabled(False)
        self.demag_bt.clicked.connect(_part(self._cycle, 'Cycle'))
        vlay_demag = QVBoxLayout()
        vlay_demag.addWidget(self.prepare_demag_bt)
        vlay_demag.addWidget(self.demag_bt)
        gb_demag.setLayout(vlay_demag)

        gb_cycle = QGroupBox('Cycle')
        self.prepare_cycle_bt = QPushButton('Prepare', self)
        # self.prepare_cycle_bt.setEnabled(False)
        self.prepare_cycle_bt.clicked.connect(
            _part(self._prepare_to_cycle, 'Ramp'))
        self.cycle_bt = QPushButton('Cycle', self)
        self.cycle_bt.setEnabled(False)
        self.cycle_bt.clicked.connect(_part(self._cycle, 'Ramp'))
        vlay_cycle = QVBoxLayout()
        vlay_cycle.addWidget(self.prepare_cycle_bt)
        vlay_cycle.addWidget(self.cycle_bt)
        gb_cycle.setLayout(vlay_cycle)

        self.status_list = CycleStatusList()
        vlay_failed = QVBoxLayout()
        vlay_failed.addWidget(QLabel(''))
        vlay_failed.addWidget(QLabel('List of failed magnets:'))
        vlay_failed.addWidget(self.status_list)

        manuallay = QGridLayout()
        manuallay.addWidget(gb_demag, 0, 0)
        manuallay.addWidget(gb_cycle, 0, 1)
        manuallay.addLayout(vlay_failed, 2, 0, 1, 2)
        manuallay.setRowStretch(0, 5)
        manuallay.setRowStretch(1, 1)
        manuallay.setRowStretch(2, 15)
        self._tab_manual.setLayout(manuallay)
        self._tab_widget.addTab(self._tab_manual, 'Manual')

        # reset
        gb_reset = QGroupBox('Turn Off Cycle')
        self.reset_ma_bt = QPushButton('Put Magnets in SlowRef')
        self.reset_ma_bt.clicked.connect(self._reset_magnets)
        self.reset_ti_bt = QPushButton('Turn off Timing')
        self.reset_ti_bt.clicked.connect(self._reset_timing)
        glay_reset = QHBoxLayout()
        glay_reset.addWidget(self.reset_ti_bt)
        glay_reset.addWidget(self.reset_ma_bt)
        gb_reset.setLayout(glay_reset)

        # connect tree signals
        self.magnets_tree.doubleClicked.connect(self._open_magnet_detail)
        self.magnets_tree.itemChanged.connect(self._disable_cycle_buttons)
        self.magnets_tree.itemChanged.connect(
            self._check_manames_from_same_udc)

        # layout
        layout = QGridLayout()
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(10)
        layout.addWidget(QLabel('<h3>Magnet Cycling</h3>', self,
                                alignment=Qt.AlignCenter), 0, 0, 1, 2)
        layout.addWidget(gb_ma, 1, 0, 4, 1)
        layout.addWidget(gb_status, 1, 1)
        layout.addWidget(self._tab_widget, 2, 1)
        layout.addWidget(QLabel(''), 3, 1)
        layout.addWidget(gb_reset, 4, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(0, 3)
        layout.setRowStretch(1, 3)
        layout.setRowStretch(2, 30)
        layout.setRowStretch(3, 1)
        layout.setRowStretch(4, 3)

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

        sections = list()
        for s in ['TB', 'BO', 'TS', 'SI']:
            if Filter.process_filters(self._magnets2cycle, filters={'sec': s}):
                sections.append(s)
        self._timing.init(mode, sections)
        return True

    def _prepare_magnets(self, mode):
        self._magnets2cycle = self._get_magnets_list(mode=mode, prepare=True)
        if not self._magnets2cycle:
            return False

        # Set magnets to proper cycling state
        self._magnets_ready = list()
        self._magnets_failed = list()
        task = SetToCycle(self._magnets2cycle, mode, self)
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
        # Prepare magnets to cycle
        status = self._prepare_magnets(mode)
        if status:
            status = self._prepare_timing(mode)

        if not status:
            self.demag_bt.setEnabled(False)
            self.cycle_bt.setEnabled(False)
        else:
            if mode == 'Cycle':
                self.demag_bt.setEnabled(True)
                self.cycle_bt.setEnabled(False)
            else:
                self.demag_bt.setEnabled(False)
                self.cycle_bt.setEnabled(True)

    def _cycle(self, mode):
        magnets = self._get_magnets_list(mode=mode)
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
            self._update_mafailed_status(mode)
            return False

        # Trigger timing and wait cyling end
        task = WaitCycle(magnets, self._timing, mode, self)
        dlg = ProgressDialog('Wait for magnets...', task, self)
        task.initValue.connect(dlg.set_value)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

        # Verify ps final state
        self._magnets_ready = list()
        self._magnets_failed = list()
        task = VerifyFinalState(magnets, mode, self)
        dlg = ProgressDialog('Verifying magnet final state...', task, self)
        task.itemDone.connect(self._update_cycling_status)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False
        self._update_mafailed_status(mode)
        if self._magnets_failed:
            QMessageBox.critical(
                self, 'Message', 'Check magnets in failed list!')
            return False

        QMessageBox.information(self, 'Message', 'Cycle finished!')

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

    def _auto_cycle(self):
        magnets = self._get_magnets_list()
        if not magnets:
            return
        self.progress_list.clear()
        auto = CycleAutomatically(magnets, self._timing, self)
        auto.updated.connect(self._update_auto_progress)
        self.auto_cycle_aborted.connect(auto.exit_thread)
        auto.start()

    def _get_magnets_list(self, mode='Cycle', prepare=False):
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

    def _update_mafailed_status(self, mode):
        self.cycle_bt.setEnabled(False)
        self.demag_bt.setEnabled(False)
        self.status_list.magnets = self._magnets_failed

    def _update_auto_progress(self, text, done, warning=False, error=False):
        if done:
            last_item = self.progress_list.item(self.progress_list.count()-1)
            curr_text = last_item.text()
            last_item.setText(curr_text+' done.')
        elif 'Remaining time' in text:
            last_item = self.progress_list.item(self.progress_list.count()-1)
            if 'Remaining time' in last_item.text():
                last_item.setText(text)
            else:
                self.progress_list.addItem(text)
                self.progress_list.scrollToBottom()
        else:
            item = QListWidgetItem(text)
            if error:
                item.setForeground(errorcolor)
            elif warning:
                item.setForeground(warncolor)
            self.progress_list.addItem(item)
            self.progress_list.scrollToBottom()

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

    def _disable_cycle_buttons(self):
        self.demag_bt.setEnabled(False)
        self.cycle_bt.setEnabled(False)

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
            interrupted = False
            threads = dict()
            for maname in self._manames:
                threads[maname] = _thread.Thread(
                    target=self.create_cycler,
                    args=(maname, ), daemon=True)
                threads[maname].start()
                if self._quit_task:
                    interrupted = True
                    break
            for t in threads.values():
                t.join()
            if not interrupted:
                self.completed.emit()

    def create_cycler(self, maname):
        global _cyclers
        self.currentItem.emit(maname)
        if maname not in _cyclers.keys():
            _cyclers[maname] = MagnetCycler(maname)
        self.itemDone.emit()


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
            interrupted = False
            threads = dict()
            for maname in self._manames:
                threads[maname] = _thread.Thread(
                    target=self.prepare_magnet,
                    args=(maname, self._mode), daemon=True)
                threads[maname].start()
                if self._quit_task:
                    interrupted = True
                    break
            for t in threads.values():
                t.join()
            if not interrupted:
                self.completed.emit()

    def prepare_magnet(self, maname, mode):
        global _cyclers
        self.currentItem.emit('Preparing '+maname+'...')
        done = _cyclers[maname].config_cycle_params(mode)
        done &= _cyclers[maname].config_cycle_opmode(mode)
        self.itemDone.emit(maname, done)


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
            interrupted = False
            threads = dict()
            for maname in self._manames:
                threads[maname] = _thread.Thread(
                    target=self.check_magnet,
                    args=(maname, self._mode), daemon=True)
                threads[maname].start()
                if self._quit_task:
                    interrupted = True
                    break
            for t in threads.values():
                t.join()
            if not interrupted:
                self.completed.emit()

    def check_magnet(self, maname, mode):
        global _cyclers
        self.currentItem.emit(maname)
        status = _cyclers[maname].is_ready(mode)
        self.itemDone.emit(maname, status)


class WaitCycle(QThread):
    """Wait cycle."""

    currentItem = Signal(str)
    itemDone = Signal()
    initValue = Signal(int)
    completed = Signal()

    def __init__(self, manames, timing_conn, mode, parent=None):
        """Build PVs."""
        super().__init__(parent)
        self._manames = manames
        self._timing_conn = timing_conn
        self._mode = mode
        self._quit_task = False
        self._init_done = False

        if mode == 'Cycle':
            size = 0
            for maname in manames:
                size = max(_cyclers[maname].cycle_duration(mode), size)
            self._size = size
        else:
            self._size = self._timing_conn.DEFAULT_RAMP_NRCYCLES

        if mode == 'Cycle':
            self._format_msg = 'Remaining time: {}s...'
        else:
            self._format_msg = 'Cycle {} of ' + str(self._size)+'...'

    def size(self):
        """Return task size."""
        return self._size

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
            self._timing_conn.wait_trigger_enable(self._mode)

            # Wait for cycling
            t0 = _time.time()
            interrupted = False
            keep_waiting = True
            while keep_waiting:
                self.currentItem.emit(self._format_msg.format(
                    self._check_curr_step(t0)))
                _time.sleep(min(1, self._size/10))
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
            count = self._timing_conn.get_cycle_count()
            if not self._init_done:
                self._init_done = True
                self.initValue.emit(count)
            return count

    def _check_keep_waiting(self, t0):
        if self._mode == 'Cycle':
            return _time.time() - t0 < self._duration
        else:
            return not self._timing_conn.check_ramp_end()


class VerifyFinalState(QThread):
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
            _time.sleep(4)
            interrupted = False
            threads = dict()
            for maname in self._manames:
                threads[maname] = _thread.Thread(
                    target=self.check_magnet_final_state,
                    args=(maname, self._mode), daemon=True)
                threads[maname].start()
                if self._quit_task:
                    interrupted = True
                    break
            for t in threads.values():
                t.join()
            if not interrupted:
                self.completed.emit()

    def check_magnet_final_state(self, maname, mode):
        global _cyclers
        self.currentItem.emit(maname)
        ans = _cyclers[maname].check_final_state(mode)
        status = False if ans != 0 else True
        self.itemDone.emit(maname, status)


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
            interrupted = False
            threads = dict()
            for maname in self._manames:
                threads[maname] = _thread.Thread(
                    target=self.reset_magnet_opmode,
                    args=(maname, ), daemon=True)
                threads[maname].start()
                if self._quit_task:
                    interrupted = True
                    break
            for t in threads.values():
                t.join()
            if not interrupted:
                self.completed.emit()

    def reset_magnet_opmode(self, maname):
        global _cyclers
        self.currentItem.emit(maname)
        done = _cyclers[maname].reset_opmode()
        self.itemDone.emit(maname, done)


class CycleAutomatically(QThread):
    """Cycle Automatically."""

    updated = Signal(str, bool, bool, bool)

    def __init__(self, manames, timing, parent=None):
        super().__init__(parent)
        cyclers = dict()
        for ma in manames:
            cyclers[ma] = _cyclers[ma]
        self._auto = AutomatedCycle(
            cyclers=cyclers, timing=timing, logger=self)
        self._quit_thread = False

    def exit_thread(self):
        self._quit_thread = True
        self._auto.aborted = True

    def run(self):
        if not self._quit_thread:
            self._auto.execute()
            self._quit_thread = True

    def update(self, message, done, warning, error):
        self.updated.emit(self._strnow+'  '+message, done, warning, error)

    @property
    def _strnow(self):
        return _datetime.now().strftime('%Y/%m/%d-%H:%M:%S')


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    application = SiriusApplication()

    w = CycleWindow()
    w.show()

    sys.exit(application.exec_())
