"""Magnet cycle window."""

import re as _re
import time as _time
from threading import Thread as _Thread, Lock as _Lock
from datetime import datetime as _datetime
from functools import partial as _part

from qtpy.QtGui import QColor, QPalette
from qtpy.QtCore import Signal, QThread, Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, \
    QPushButton, QLabel, QMessageBox, QLineEdit, QApplication, \
    QListWidget, QListWidgetItem, QProgressBar, QGroupBox

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.namesys import Filter, SiriusPVName as PVName
from siriuspy.cycle import get_manames, get_manames_from_same_udc, \
    Timing, MagnetCycler, LinacMagnetCycler, CycleController

from siriushla.widgets import SiriusMainWindow, \
    PyDMLedMultiConnection as PyDMLedMultiConn
from siriushla.widgets.pvnames_tree import PVNameTree
from siriushla.widgets.dialog import ProgressDialog
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from .cycle_status_list import MagnetsListDialog

_cyclers = dict()
_lock = _Lock()

errorcolor = QColor(255, 0, 0)
warncolor = QColor(200, 200, 0)


class CycleWindow(SiriusMainWindow):
    """Magnet cycle window."""

    def __init__(self, parent=None, checked_accs=()):
        """Constructor."""
        super().__init__(parent)
        self.setObjectName('ASApp')
        # Data structs
        self._timing = Timing()
        self._magnets2cycle = list()
        self._magnets_ready = list()
        self._magnets_failed = list()
        self._checked_accs = checked_accs
        # Flags
        self._is_preparing = ''
        self._prepared = {'timing': False,
                          'mag_params': False,
                          'mag_opmode': False}
        # Setup UI
        self._setup_ui()
        self.setWindowTitle('Magnet Cycling')

    def _setup_ui(self):
        # central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # treeview
        gb_tree = QGroupBox('Select magnets:')
        self.search_le = QLineEdit()
        self.search_le.setPlaceholderText('Filter...')
        self.search_le.editingFinished.connect(self._filter_manames)
        self.magnets_tree = PVNameTree(get_manames(), ('sec', 'mag_group'),
                                       tuple(), self)
        self.magnets_tree.setHeaderHidden(True)
        self.magnets_tree.setColumnCount(1)
        self.magnets_tree.setObjectName('magtree')
        self.magnets_tree.setStyleSheet(
            '#magtree{min-width:15em; max-width:15em;}')
        glay_tree = QVBoxLayout(gb_tree)
        glay_tree.addWidget(self.search_le)
        glay_tree.addWidget(self.magnets_tree)

        # status
        gb_status = QGroupBox('Connection Status', self)
        tipvs = [VACA_PREFIX + pv
                 for pv in self._timing.get_pvnames_by_section()]
        label_ticonn = QLabel('<h4>Timing</h4>', self,
                              alignment=Qt.AlignBottom | Qt.AlignHCenter)
        self.ticonn_led = PyDMLedMultiConn(self, channels=tipvs)
        self.ticonn_led.shape = 2
        label_maconn = QLabel('<h4>Selected Magnets</h4>', self,
                              alignment=Qt.AlignBottom | Qt.AlignHCenter)
        self.maconn_led = PyDMLedMultiConn(self)
        self.maconn_led.shape = 2
        lay_status = QGridLayout(gb_status)
        lay_status.addWidget(label_ticonn, 0, 0)
        lay_status.addWidget(self.ticonn_led, 1, 0)
        lay_status.addWidget(label_maconn, 0, 1)
        lay_status.addWidget(self.maconn_led, 1, 1)

        # cycle
        self.prepare_timing_bt = QPushButton('1. Prepare\nTiming', self)
        self.prepare_timing_bt.setToolTip('Prepare EVG, triggers and events')
        self.prepare_timing_bt.clicked.connect(
            _part(self._prepare, 'timing'))
        self.prepare_magnets_params_bt = QPushButton(
            '2. Prepare Magnets\nParameters', self)
        self.prepare_magnets_params_bt.setToolTip(
            'Set magnets current to zero and \n'
            'configure cycle parameters or waveform.')
        self.prepare_magnets_params_bt.clicked.connect(
            _part(self._prepare, 'magnets', 'params'))
        self.prepare_magnets_opmode_bt = QPushButton(
            '3. Prepare Magnets\nOpMode', self)
        self.prepare_magnets_opmode_bt.setToolTip(
            'Set magnets OpMode to Cycle or RmpWfm.')
        self.prepare_magnets_opmode_bt.clicked.connect(
            _part(self._prepare, 'magnets', 'opmode'))
        self.cycle_bt = QPushButton('4. Cycle', self)
        self.cycle_bt.setToolTip('Check all configurations and trigger cycle.')
        self.cycle_bt.clicked.connect(self._cycle)
        self.cycle_bt.setEnabled(False)
        self.progress_list = QListWidget(self)
        self.progress_list.setObjectName('progresslist')
        self.progress_list.setStyleSheet("""
            #progresslist{min-width:28em; max-width:28em;}""")
        self.progress_bar = MyProgressBar(self)
        cyclelay = QGridLayout()
        cyclelay.addWidget(self.prepare_timing_bt, 0, 0)
        cyclelay.addWidget(self.prepare_magnets_params_bt, 0, 1)
        cyclelay.addWidget(self.prepare_magnets_opmode_bt, 0, 2)
        cyclelay.addWidget(self.cycle_bt, 0, 3)
        cyclelay.addWidget(self.progress_list, 1, 0, 1, 4)
        cyclelay.addWidget(self.progress_bar, 2, 0, 1, 4)

        # commands
        gb_comm = QGroupBox('Auxiliar Commands', self)
        self.restore_ti_bt = QPushButton('Restore Initial State')
        self.restore_ti_bt.clicked.connect(self._restore_timing)
        self.set_ma_2_slowref_bt = QPushButton('Set OpMode\nto SlowRef')
        self.set_ma_2_slowref_bt.clicked.connect(self._set_magnets_2_slowref)
        self.zero_ma_curr_bt = QPushButton('Set currents\nto zero', self)
        self.zero_ma_curr_bt.clicked.connect(self._set_magnets_current_2_zero)
        lay_comm = QGridLayout(gb_comm)
        lay_comm.addWidget(QLabel('<h4>Timing</h4>'), 0, 0)
        lay_comm.addWidget(self.restore_ti_bt, 1, 0)
        lay_comm.addWidget(QLabel(''), 0, 1)
        lay_comm.addWidget(QLabel('<h4>Selected Magnets</h4>'), 0, 2, 1, 2)
        lay_comm.addWidget(self.set_ma_2_slowref_bt, 1, 2)
        lay_comm.addWidget(self.zero_ma_curr_bt, 1, 3)
        lay_comm.setColumnStretch(0, 15)
        lay_comm.setColumnStretch(1, 1)
        lay_comm.setColumnStretch(2, 7)
        lay_comm.setColumnStretch(3, 7)

        # connect tree signals
        self.magnets_tree.doubleClicked.connect(self._open_magnet_detail)
        self.magnets_tree.itemChanged.connect(
            self._check_manames_from_same_udc)
        self.magnets_tree.check_requested_levels(self._checked_accs)

        # layout
        layout = QGridLayout()
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(10)
        layout.addWidget(QLabel('<h3>Magnet Cycling</h3>', self,
                                alignment=Qt.AlignCenter), 0, 0, 1, 3)
        layout.addWidget(gb_tree, 1, 0, 5, 1)
        layout.addWidget(gb_status, 1, 1)
        layout.addWidget(QLabel(''), 2, 2)
        layout.addLayout(cyclelay, 3, 1)
        layout.addWidget(QLabel(''), 4, 2)
        layout.addWidget(gb_comm, 5, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 3)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 15)
        layout.setRowStretch(4, 1)
        layout.setRowStretch(5, 3)
        self.central_widget.setLayout(layout)
        self.central_widget.setStyleSheet("""
            QPushButton{min-height:2em;}
            QLabel{qproperty-alignment: AlignCenter;}""")

    def _check_connected(self, subsystem, without_linac=False):
        led = self.ticonn_led if subsystem == 'timing' else self.maconn_led
        pvs_disconnected = set()
        for ch, v in led.channels2conn.items():
            if 'LI' in ch and without_linac:
                continue
            if not v:
                pvs_disconnected.add(ch)
        if pvs_disconnected:
            sttr = ''
            for item in pvs_disconnected:
                sttr += item + '\n'
            QMessageBox.information(
                self, 'Message', 'The following PVs are not connected:\n'+sttr)
            return False
        return True

    def _prepare(self, subsystem='magnets', ppty='params'):
        if not self._check_connected(subsystem):
            return
        magnets = self._get_magnets_list()
        if not magnets:
            return

        self._allButtons_setEnabled(False)
        self.progress_list.clear()

        sections = self._get_sections()
        if 'BO' in sections and len(sections) > 1:
            QMessageBox.critical(
                self, 'Error',
                'Can not prepare Booster with other accelerators!')
            self._allButtons_setEnabled(True)
            return False

        if subsystem == 'magnets':
            self._magnets_failed = set()
            verify_task = VerifyMagnet(magnets, self)
            verify_task.itemDone.connect(self._get_magnets_not_ready_2_cycle)
            dlg = ProgressDialog(
                'Verifying magnets initial state...', verify_task, self)
            ret = dlg.exec_()
            if ret == dlg.Rejected:
                self._allButtons_setEnabled(True)
                return False
            if self._magnets_failed:
                text = 'Verify power state and interlocks' \
                       ' of the following magnets'
                dlg = MagnetsListDialog(self._magnets_failed, text, self)
                dlg.exec_()
                self._allButtons_setEnabled(True)
                return False

            self._is_preparing = 'mag_' + ppty
            prepare_task = PrepareMagnets(magnets, self._timing, ppty, self)
        else:
            self._is_preparing = 'timing'
            prepare_task = PrepareTiming(magnets, self._timing, self)

        prepare_task.updated.connect(self._update_progress)
        duration = prepare_task.duration()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(duration)
        self.progress_bar.setValue(0)
        pal = self.progress_bar.palette()
        pal.setColor(QPalette.Highlight, self.progress_bar.default_color)
        self.progress_bar.setPalette(pal)
        self.update_bar = UpdateProgressBar(duration, self)
        self.update_bar.increment.connect(self.progress_bar.increment)

        prepare_task.start()
        self.update_bar.start()

    def _cycle(self):
        if not self._check_connected('timing'):
            return
        if not self._check_connected('magnets'):
            return

        magnets = self._get_magnets_list()
        if not magnets:
            return

        self._allButtons_setEnabled(False)
        self.progress_list.clear()

        sections = self._get_sections()
        if 'BO' in sections and len(sections) > 1:
            QMessageBox.critical(
                self, 'Error',
                'Can not cycle Booster with other accelerators!')
            self._allButtons_setEnabled(True)
            return

        self._is_preparing = ''
        self.cycle_bt.setEnabled(False)
        cycle_task = Cycle(magnets, self._timing, self)
        cycle_task.updated.connect(self._update_progress)
        duration = cycle_task.duration()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(duration)
        self.progress_bar.setValue(0)
        pal = self.progress_bar.palette()
        pal.setColor(QPalette.Highlight, self.progress_bar.default_color)
        self.progress_bar.setPalette(pal)
        self.update_bar = UpdateProgressBar(duration, self)
        self.update_bar.increment.connect(self.progress_bar.increment)

        cycle_task.start()
        self.update_bar.start()

    def _set_magnets_current_2_zero(self):
        if not self._check_connected('magnets'):
            return
        magnets = self._get_magnets_list()
        if not magnets:
            return False
        task = ZeroMagnetsCurrent(magnets, self)
        dlg = ProgressDialog('Setting currents to zero...', task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

    def _set_magnets_2_slowref(self):
        if not self._check_connected('magnets', without_linac=True):
            return
        magnets = self._get_magnets_list(without_linac=True)
        if not magnets:
            return False
        task = ResetMagnetsOpMode(magnets, self)
        dlg = ProgressDialog('Setting OpMode to SlowRef...', task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

    def _restore_timing(self):
        if not self._check_connected('timing'):
            return
        self._timing.restore_initial_state()

    def _get_magnets_list(self, without_linac=False):
        """Return list of magnets to cycle."""
        # Get magnets list
        magnets = self.magnets_tree.checked_items()
        if not magnets:
            QMessageBox.critical(self, 'Message', 'No magnet selected!')

        if without_linac:
            magnets = [ma for ma in magnets if 'LI' not in ma]

        # Create new cyclers if needed
        self._create_cyclers(magnets)
        return magnets

    def _get_sections(self):
        sections = list()
        magnets2cycle = self.magnets_tree.checked_items()
        for s in ['TB', 'BO', 'TS', 'SI']:
            if Filter.process_filters(magnets2cycle, filters={'sec': s}):
                sections.append(s)
        return sections

    def _create_cyclers(self, manames):
        """Create new cyclers, if necessary."""
        ma2create = list()
        for maname in manames:
            if maname not in _cyclers.keys():
                ma2create.append(maname)
        if not ma2create:
            return

        task = CreateCyclers(ma2create)
        dlg = ProgressDialog('Connecting to magnets...', task, self)
        dlg.exec_()

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
        if len(maname) == 2 or PVName(maname).sec == 'LI':
            return
        app.open_window(PSDetailWindow, parent=self, **{'psname': maname})

    def _check_manames_from_same_udc(self, item):
        maname = item.data(0, Qt.DisplayRole)
        if len(maname) == 2 or PVName(maname).sec == 'LI':
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
        self._update_led_channels()

    def _get_magnets_not_ready_2_cycle(self, maname, status):
        if not status:
            self._magnets_failed.add(maname)

    def _update_progress(self, text, done, warning=False, error=False):
        """Update automated cycle progress list and bar."""
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
                self.update_bar.exit_task()
                pal = self.progress_bar.palette()
                pal.setColor(QPalette.Highlight,
                             self.progress_bar.warning_color)
                self.progress_bar.setPalette(pal)
                if self._is_preparing:
                    self._prepared[self._is_preparing] = False
                else:
                    self._prepared = {k: False for k in self._prepared.keys()}
                self._allButtons_setEnabled(True)
            elif warning:
                item.setForeground(warncolor)
            elif 'finished' in text:
                self.update_bar.exit_task()
                self.progress_bar.setValue(self.progress_bar.maximum())
                if self._is_preparing:
                    self._prepared[self._is_preparing] = True
                    cycle = all(self._prepared.values())
                else:
                    self._prepared = {k: False for k in self._prepared.keys()}
                    self.cycle_bt.setEnabled(False)
                    cycle = False
                self._allButtons_setEnabled(True, cycle)

            self.progress_list.addItem(item)
            self.progress_list.scrollToBottom()

    def _update_led_channels(self):
        sections = self._get_sections()
        ti_ch = [VACA_PREFIX + name
                 for name in self._timing.get_pvnames_by_section(sections)]
        self.ticonn_led.set_channels(ti_ch)

        ma_ch = list()
        for name in self.magnets_tree.checked_items():
            ppty = ':Version-Cte' if PVName(name).sec != 'LI' else ':setpwm'
            ma_ch.append(VACA_PREFIX + name + ppty)
        self.maconn_led.set_channels(ma_ch)

    def _allButtons_setEnabled(self, enable, cycle=False):
        self.prepare_timing_bt.setEnabled(enable)
        self.prepare_magnets_params_bt.setEnabled(enable)
        self.prepare_magnets_opmode_bt.setEnabled(enable)
        self.restore_ti_bt.setEnabled(enable)
        self.set_ma_2_slowref_bt.setEnabled(enable)
        self.zero_ma_curr_bt.setEnabled(enable)
        if cycle:
            self.cycle_bt.setEnabled(enable)


# Auxiliar progress monitoring classes

class MyProgressBar(QProgressBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        pal = self.palette()
        self.default_color = pal.color(QPalette.Highlight)
        self.warning_color = Qt.red

    def increment(self):
        current_val = self.value()
        max_val = self.maximum()
        if max_val > current_val:
            self.setValue(current_val+1)


class UpdateProgressBar(QThread):

    increment = Signal()

    def __init__(self, duration, parent=None):
        super().__init__(parent)
        self._duration = duration
        self._quit_task = False

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        t0 = _time.time()
        while _time.time() - t0 < self._duration:
            if self._quit_task:
                break
            _time.sleep(1)
            self.increment.emit()


# Tasks

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
                threads[maname] = _Thread(
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
        if maname in _cyclers.keys():
            pass
        else:
            if PVName(maname).sec == 'LI':
                c = LinacMagnetCycler(maname)
            else:
                c = MagnetCycler(maname)
            with _lock:
                _cyclers[maname] = c
        self.currentItem.emit(maname)
        self.itemDone.emit()


class VerifyMagnet(QThread):
    """Verify magnet initial state."""

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
                threads[maname] = _Thread(
                    target=self.check_magnet, args=(maname, ), daemon=True)
                threads[maname].start()
                if self._quit_task:
                    interrupted = True
                    break
            for t in threads.values():
                if interrupted:
                    t.stop()
                t.join()
            if not interrupted:
                self.completed.emit()

    def check_magnet(self, maname):
        global _cyclers
        cycler = _cyclers[maname]
        status = cycler.connected
        if not status:
            print(maname, 'connection')
        status &= cycler.check_on()
        if not status:
            print(maname, 'off')
        status &= cycler.check_intlks()
        if not status:
            print(maname, 'intlk')
        self.currentItem.emit(maname)
        self.itemDone.emit(maname, status)


class ZeroMagnetsCurrent(QThread):
    """Set magnet current to zero."""

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
        """Set magnets current to zero."""
        if self._quit_task:
            pass
        else:
            interrupted = False
            threads = dict()
            for maname in self._manames:
                threads[maname] = _Thread(
                    target=self.set_magnet_current_zero,
                    args=(maname, ), daemon=True)
                threads[maname].start()
                if self._quit_task:
                    interrupted = True
                    break
            for t in threads.values():
                t.join()
            if not interrupted:
                self.completed.emit()

    def set_magnet_current_zero(self, maname):
        global _cyclers
        done = _cyclers[maname].set_current_zero()
        self.currentItem.emit(maname)
        self.itemDone.emit(maname, done)


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
                threads[maname] = _Thread(
                    target=self.set_magnet_opmode_slowref,
                    args=(maname, ), daemon=True)
                threads[maname].start()
                if self._quit_task:
                    interrupted = True
                    break
            for t in threads.values():
                t.join()
            if not interrupted:
                self.completed.emit()

    def set_magnet_opmode_slowref(self, maname):
        global _cyclers
        done = _cyclers[maname].set_opmode_slowref()
        self.currentItem.emit(maname)
        self.itemDone.emit(maname, done)


class PrepareMagnets(QThread):
    """Cycle."""

    updated = Signal(str, bool, bool, bool)

    def __init__(self, manames, timing, ppty, parent=None):
        super().__init__(parent)
        cyclers = dict()
        for ma in manames:
            cyclers[ma] = _cyclers[ma]
        self._controller = CycleController(
            cyclers=cyclers, timing=timing, logger=self)
        self._ppty = ppty
        self._quit_thread = False

    def size(self):
        return self._controller.prepare_magnets_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_magnets_max_duration

    def exit_thread(self):
        self._quit_thread = True

    def run(self):
        if not self._quit_thread:
            if self._ppty == 'params':
                self._controller.prepare_magnets_parameters()
            else:
                self._controller.prepare_magnets_opmode()
            self._quit_thread = True

    def update(self, message, done, warning, error):
        now = _datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
        self.updated.emit(now+'  '+message, done, warning, error)


class PrepareTiming(QThread):
    """Cycle."""

    updated = Signal(str, bool, bool, bool)

    def __init__(self, manames, timing, parent=None):
        super().__init__(parent)
        cyclers = dict()
        for ma in manames:
            cyclers[ma] = _cyclers[ma]
        self._controller = CycleController(
            cyclers=cyclers, timing=timing, logger=self)
        self._quit_thread = False

    def size(self):
        return self._controller.prepare_timing_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.prepare_timing_max_duration

    def exit_thread(self):
        self._quit_thread = True

    def run(self):
        if not self._quit_thread:
            self._controller.prepare_timing()
            self._quit_thread = True

    def update(self, message, done, warning, error):
        now = _datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
        self.updated.emit(now+'  '+message, done, warning, error)


class Cycle(QThread):
    """Cycle."""

    updated = Signal(str, bool, bool, bool)

    def __init__(self, manames, timing, parent=None):
        super().__init__(parent)
        cyclers = dict()
        for ma in manames:
            cyclers[ma] = _cyclers[ma]
        self._controller = CycleController(
            cyclers=cyclers, timing=timing, logger=self)
        self._quit_thread = False

    def size(self):
        return self._controller.cycle_size

    def duration(self):
        """Return task maximum duration."""
        return self._controller.cycle_max_duration

    def exit_thread(self):
        self._quit_thread = True

    def run(self):
        if not self._quit_thread:
            self._controller.cycle()
            self._quit_thread = True

    def update(self, message, done, warning, error):
        now = _datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
        self.updated.emit(now+'  '+message, done, warning, error)


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    application = SiriusApplication()

    w = CycleWindow()
    w.show()

    sys.exit(application.exec_())
