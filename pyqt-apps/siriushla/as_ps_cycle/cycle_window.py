"""Power supplies cycle window."""

import re as _re
import time as _time
from functools import partial as _part

from qtpy.QtGui import QColor, QPalette
from qtpy.QtCore import Signal, QThread, Qt, QTimer
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, \
    QPushButton, QLabel, QMessageBox, QApplication, QGroupBox, \
    QListWidget, QListWidgetItem, QProgressBar
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX as VACA_PREFIX
from siriuspy.namesys import Filter, SiriusPVName as PVName
from siriuspy.cycle import get_psnames, Timing
from siriuspy.search import PSSearch

from siriushla.util import get_appropriate_color
from siriushla.widgets import SiriusMainWindow, \
    PyDMLedMultiConnection as PyDMLedMultiConn
from siriushla.widgets.pvnames_tree import PVNameTree
from siriushla.widgets.dialog import ProgressDialog, PSStatusDialog
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from siriushla.as_ps_cycle.tasks import CreateCyclers, VerifyPS, \
    ZeroPSCurrent, ResetPSOpMode, RestoreTiming, PreparePSParams, \
    PreparePSOpMode, PrepareTiming, Cycle


errorcolor = QColor(255, 0, 0)
warncolor = QColor(200, 200, 0)


class CycleWindow(SiriusMainWindow):
    """Power supplies cycle window."""

    def __init__(self, parent=None, checked_accs=()):
        """Constructor."""
        super().__init__(parent)
        self.setObjectName('ASApp')
        cor = get_appropriate_color(section='AS')
        self.setWindowIcon(qta.icon('mdi.recycle', color=cor))
        # Data structs
        self._timing = Timing()
        self._ps2cycle = list()
        self._ps_ready = list()
        self._ps_failed = list()
        self._checked_accs = checked_accs
        # Flags
        self._is_preparing = ''
        self._prepared = {
            'timing': False, 'ps_params': False, 'ps_opmode': False}
        # Setup UI
        self._needs_update_leds = False
        self._setup_ui()
        self._update_led_timer = QTimer(self)
        self._update_led_timer.timeout.connect(self._update_led_channels)
        self._update_led_timer.setInterval(500)
        self._update_led_timer.start()
        self.setWindowTitle('PS Cycle')

    def _setup_ui(self):
        # central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # treeview
        gb_tree = QGroupBox('Select power supplies:')
        self.pwrsupplies_tree = PVNameTree(
            get_psnames(), ('sec', 'mag_group'), tuple(), self)
        self.pwrsupplies_tree.tree.setHeaderHidden(True)
        self.pwrsupplies_tree.tree.setColumnCount(1)
        glay_tree = QVBoxLayout(gb_tree)
        glay_tree.addWidget(self.pwrsupplies_tree)

        # status
        gb_status = QGroupBox('Connection Status', self)
        ti_ch = [VACA_PREFIX + name
                 for name in self._timing.get_pvnames_by_psnames()]
        label_ticonn = QLabel('<h4>Timing</h4>', self,
                              alignment=Qt.AlignBottom | Qt.AlignHCenter)
        self.ticonn_led = PyDMLedMultiConn(self, channels=ti_ch)
        self.ticonn_led.shape = 2
        label_psconn = QLabel('<h4>Selected Power Supplies</h4>', self,
                              alignment=Qt.AlignBottom | Qt.AlignHCenter)
        self.psconn_led = PyDMLedMultiConn(self)
        self.psconn_led.shape = 2
        lay_status = QGridLayout(gb_status)
        lay_status.addWidget(label_ticonn, 0, 0)
        lay_status.addWidget(self.ticonn_led, 1, 0)
        lay_status.addWidget(label_psconn, 0, 1)
        lay_status.addWidget(self.psconn_led, 1, 1)

        # cycle
        self.prepare_timing_bt = QPushButton('1. Prepare\nTiming', self)
        self.prepare_timing_bt.setToolTip('Prepare EVG, triggers and events')
        self.prepare_timing_bt.clicked.connect(
            _part(self._prepare, 'timing'))
        self.prepare_ps_params_bt = QPushButton(
            '2. Prepare PS\nParameters', self)
        self.prepare_ps_params_bt.setToolTip(
            'Set power supplies current to zero and \n'
            'configure cycle parameters or waveform.')
        self.prepare_ps_params_bt.clicked.connect(
            _part(self._prepare, 'ps', 'params'))
        self.prepare_ps_opmode_bt = QPushButton(
            '3. Prepare PS\nOpMode', self)
        self.prepare_ps_opmode_bt.setToolTip(
            'Set power supplies OpMode to Cycle or RmpWfm.')
        self.prepare_ps_opmode_bt.clicked.connect(
            _part(self._prepare, 'ps', 'opmode'))
        self.cycle_bt = QPushButton('4. Cycle', self)
        self.cycle_bt.setToolTip('Check all configurations and trigger cycle.')
        self.cycle_bt.clicked.connect(self._cycle)
        self.cycle_bt.setEnabled(False)
        self.progress_list = QListWidget(self)
        self.progress_bar = MyProgressBar(self)
        cyclelay = QGridLayout()
        cyclelay.addWidget(self.prepare_timing_bt, 0, 0)
        cyclelay.addWidget(self.prepare_ps_params_bt, 0, 1)
        cyclelay.addWidget(self.prepare_ps_opmode_bt, 0, 2)
        cyclelay.addWidget(self.cycle_bt, 0, 3)
        cyclelay.addWidget(self.progress_list, 1, 0, 1, 4)
        cyclelay.addWidget(self.progress_bar, 2, 0, 1, 4)

        # commands
        gb_comm = QGroupBox('Auxiliar Commands', self)
        self.restore_ti_bt = QPushButton('Restore Initial State')
        self.restore_ti_bt.clicked.connect(self._restore_timing)
        self.set_ps_2_slowref_bt = QPushButton('Set OpMode\nto SlowRef')
        self.set_ps_2_slowref_bt.clicked.connect(self._set_ps_2_slowref)
        self.zero_ps_curr_bt = QPushButton('Set currents\nto zero', self)
        self.zero_ps_curr_bt.clicked.connect(self._set_ps_current_2_zero)
        lay_comm = QGridLayout(gb_comm)
        lay_comm.addWidget(QLabel('<h4>Timing</h4>'), 0, 0)
        lay_comm.addWidget(self.restore_ti_bt, 1, 0)
        lay_comm.addWidget(QLabel(''), 0, 1)
        lay_comm.addWidget(QLabel('<h4>Selected Power Supplies</h4>'),
                           0, 2, 1, 2)
        lay_comm.addWidget(self.set_ps_2_slowref_bt, 1, 2)
        lay_comm.addWidget(self.zero_ps_curr_bt, 1, 3)
        lay_comm.setColumnStretch(0, 15)
        lay_comm.setColumnStretch(1, 1)
        lay_comm.setColumnStretch(2, 7)
        lay_comm.setColumnStretch(3, 7)

        # connect tree signals
        self.pwrsupplies_tree.tree.doubleClicked.connect(self._open_ps_detail)
        self.pwrsupplies_tree.tree.itemChanged.connect(
            self._handle_checked_items_changed)
        self.pwrsupplies_tree.check_requested_levels(self._checked_accs)

        # layout
        layout = QGridLayout()
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(10)
        layout.addWidget(QLabel('<h3>PS Cycle</h3>', self,
                                alignment=Qt.AlignCenter), 0, 0, 1, 3)
        layout.addWidget(gb_tree, 1, 0, 5, 1)
        layout.addWidget(gb_status, 1, 1)
        layout.addWidget(QLabel(''), 2, 1)
        layout.addLayout(cyclelay, 3, 1)
        layout.addWidget(QLabel(''), 4, 1)
        layout.addWidget(gb_comm, 5, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 3)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 15)
        layout.setRowStretch(4, 1)
        layout.setRowStretch(5, 3)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        self.central_widget.setLayout(layout)
        self.central_widget.setStyleSheet("""
            QPushButton{min-height:2em;}
            QLabel{qproperty-alignment: AlignCenter;}""")

    def _check_connected(self, subsystem, without_linac=False):
        led = self.ticonn_led if subsystem == 'timing' else self.psconn_led
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

    def _prepare(self, subsystem='ps', ppty='params'):
        if not self._check_connected(subsystem):
            return
        pwrsupplies = self._get_ps_list()
        if not pwrsupplies:
            QMessageBox.critical(self, 'Message', 'No power supply selected!')
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

        create_task = CreateCyclers(parent=self, psnames=pwrsupplies)
        dlg = ProgressDialog('Creating cycles...', create_task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            self._allButtons_setEnabled(True)
            return False

        if subsystem == 'ps':
            self._ps_failed = set()
            verify_task = VerifyPS(parent=self, psnames=pwrsupplies)
            verify_task.itemDone.connect(self._get_ps_not_ready_2_cycle)
            dlg = ProgressDialog(
                'Verifying power supplies initial state...', verify_task, self)
            ret = dlg.exec_()
            if ret == dlg.Rejected:
                self._allButtons_setEnabled(True)
                return False
            if self._ps_failed:
                text = 'Verify power state and interlocks' \
                       ' of the following power supplies'
                dlg = PSStatusDialog(self._ps_failed, text, self)
                dlg.exec_()
                self._allButtons_setEnabled(True)
                return False

            self._is_preparing = 'ps_' + ppty
            if ppty == 'params':
                prepare_task = PreparePSParams(
                    parent=self, psnames=pwrsupplies, timing=self._timing)
            else:
                prepare_task = PreparePSOpMode(
                    parent=self, psnames=pwrsupplies, timing=self._timing)
        else:
            self._is_preparing = 'timing'
            prepare_task = PrepareTiming(
                parent=self, psnames=pwrsupplies, timing=self._timing)

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
        if not self._check_connected('ps'):
            return

        pwrsupplies = self._get_ps_list()
        if not pwrsupplies:
            QMessageBox.critical(self, 'Message', 'No power supply selected!')
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

        create_task = CreateCyclers(parent=self, psnames=pwrsupplies)
        dlg = ProgressDialog('Creating cyclers...', create_task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            self._allButtons_setEnabled(True)
            return

        cycle_task = Cycle(parent=self, psnames=pwrsupplies,
                           timing=self._timing)
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

    def _set_ps_current_2_zero(self):
        if not self._check_connected('ps'):
            return
        pwrsupplies = self._get_ps_list()
        if not pwrsupplies:
            QMessageBox.critical(self, 'Message', 'No power supply selected!')
            return False

        task0 = CreateCyclers(parent=self, psnames=pwrsupplies)
        task1 = ZeroPSCurrent(parent=self, psnames=pwrsupplies)
        labels = ['Creating cycles...', 'Setting currents to zero...']
        tasks = [task0, task1]
        dlg = ProgressDialog(labels, tasks, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

    def _set_ps_2_slowref(self):
        if not self._check_connected('ps', without_linac=True):
            return
        pwrsupplies = self._get_ps_list(without_linac=True)
        if not pwrsupplies:
            QMessageBox.critical(self, 'Message', 'No power supply selected!')
            return False

        task0 = CreateCyclers(parent=self, psnames=pwrsupplies)
        task1 = ResetPSOpMode(parent=self, psnames=pwrsupplies)
        labels = ['Creating cycles...', 'Setting OpMode to SlowRef...']
        tasks = [task0, task1]
        dlg = ProgressDialog(labels, tasks, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

    def _restore_timing(self):
        if not self._check_connected('timing'):
            return
        task = RestoreTiming(parent=self, timing=self._timing)
        dlg = ProgressDialog('Restoring timing initial state...', task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

    def _get_ps_list(self, without_linac=False):
        """Return list of power supplies to cycle."""
        # Get power supplies list
        pwrsupplies = self.pwrsupplies_tree.checked_items()
        if not pwrsupplies:
            return False

        if without_linac:
            pwrsupplies = [ps for ps in pwrsupplies if 'LI' not in ps]

        return pwrsupplies

    def _get_sections(self):
        sections = list()
        ps2cycle = self.pwrsupplies_tree.checked_items()
        for s in ['LI', 'TB', 'BO', 'TS', 'SI']:
            if Filter.process_filters(ps2cycle, filters={'sec': s}):
                sections.append(s)
        return sections

    def _open_ps_detail(self, item):
        app = QApplication.instance()
        psname = item.data()
        if not _re.match('.*-.*:.*-.*', psname):
            if item.model().rowCount(item) == 1:
                psname = item.child(0, 0).data()
            else:
                return
        app.open_window(PSDetailWindow, parent=self, **{'psname': psname})

    def _handle_checked_items_changed(self, item):
        psname = PVName(item.data(0, Qt.DisplayRole))
        if (psname.sec in ['BO', 'SI'] and psname.dev in ['B', 'B1B2']):
            psname2check = PSSearch.get_psnames(
                {'sec': psname.sec, 'dev': 'B.*'})
            psname2check.remove(psname)
            item2check = self.pwrsupplies_tree._item_map[psname2check[0]]

            state2set = item.checkState(0)
            state2change = item2check.checkState(0)
            if state2change != state2set:
                item2check.setCheckState(0, state2set)
        self._needs_update_leds = True

    def _get_ps_not_ready_2_cycle(self, psname, status):
        if not status:
            self._ps_failed.add(psname)

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
        if not self._needs_update_leds:
            return

        psnames = self.pwrsupplies_tree.checked_items()
        ti_ch = [VACA_PREFIX + name
                 for name in self._timing.get_pvnames_by_psnames(psnames)]
        self.ticonn_led.set_channels(ti_ch)

        ps_ch = list()
        for name in psnames:
            ppty = ':Version-Cte'
            ps_ch.append(VACA_PREFIX + name + ppty)
        self.psconn_led.set_channels(ps_ch)

        self._needs_update_leds = False

    def _allButtons_setEnabled(self, enable, cycle=False):
        self.prepare_timing_bt.setEnabled(enable)
        self.prepare_ps_params_bt.setEnabled(enable)
        self.prepare_ps_opmode_bt.setEnabled(enable)
        self.restore_ti_bt.setEnabled(enable)
        self.set_ps_2_slowref_bt.setEnabled(enable)
        self.zero_ps_curr_bt.setEnabled(enable)
        if cycle:
            self.cycle_bt.setEnabled(enable)

    def closeEvent(self, ev):
        self._update_led_timer.stop()
        super().closeEvent(ev)


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


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    application = SiriusApplication()

    w = CycleWindow()
    w.show()

    sys.exit(application.exec_())
