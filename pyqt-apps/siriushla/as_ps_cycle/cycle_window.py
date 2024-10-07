"""Power supplies cycle window."""

import re as _re
import time as _time
from functools import partial as _part

from qtpy.QtGui import QColor, QPalette, QKeySequence
from qtpy.QtCore import Signal, QThread, Qt, QTimer, QSize
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QPushButton, QLabel, QMessageBox, QGroupBox, QListWidget, QSpacerItem, \
    QListWidgetItem, QProgressBar, QSizePolicy as QSzPlcy, QApplication, \
    QAbstractItemView
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX as VACA_PREFIX
from siriuspy.namesys import Filter, SiriusPVName as PVName
from siriuspy.cycle import get_psnames, Timing, get_sections
from siriuspy.search import PSSearch

from ..util import get_appropriate_color, run_newprocess
from ..widgets import SiriusMainWindow, \
    PyDMLedMultiConnection as PyDMLedMultiConn
from ..widgets.pvnames_tree import PVNameTree
from ..widgets.dialog import ProgressDialog, PSStatusDialog
from .tasks import CreateCyclers, VerifyPS, \
    SaveTiming, PrepareTiming, RestoreTiming, \
    PreparePSSOFBMode, PreparePSOpModeSlowRef, PreparePSCurrentZero, \
    PreparePSParams, PreparePSOpModeCycle, Cycle, CycleTrims


errorcolor = QColor(255, 0, 0)
warncolor = QColor(200, 200, 0)


class CycleWindow(SiriusMainWindow):
    """Power supplies cycle window."""

    def __init__(self, parent=None, checked_accs=(), adv_mode=False):
        """Constructor."""
        super().__init__(parent)
        self.setObjectName('ASApp')
        cor = get_appropriate_color(section='AS')
        self.setWindowIcon(qta.icon('mdi.recycle', color=cor))
        self._is_adv_mode = adv_mode
        # Data structs
        self._psnames = Filter.process_filters(
            get_psnames(isadv=self._is_adv_mode),
            filters={'sub': '((?!SB).)*'})
        self._timing = Timing()
        self._ps2cycle = list()
        self._ps_ready = list()
        self._ps_failed = list()
        self._checked_accs = checked_accs
        # Flags
        self._is_preparing = ''
        self._prepared_init_vals = {
            'timing': False,
            'ps_sofbmode': False,
            'ps_om_slowref': False,
            'ps_current': False,
            'ps_params': False,
            'ps_om_cycle': False,
            'trims': True}
        self._prepared = self._prepared_init_vals.copy()
        self._icon_check = qta.icon('fa5s.check')
        self._pixmap_check = self._icon_check.pixmap(
            self._icon_check.actualSize(QSize(16, 16)))
        self._icon_not = qta.icon('fa5s.times')
        self._pixmap_not = self._icon_not.pixmap(
            self._icon_not.actualSize(QSize(16, 16)))
        # Tasks
        self._step_2_task = {
            'save_timing': SaveTiming,
            'timing': PrepareTiming,
            'ps_sofbmode': PreparePSSOFBMode,
            'ps_om_slowref': PreparePSOpModeSlowRef,
            'ps_current': PreparePSCurrentZero,
            'ps_params': PreparePSParams,
            'ps_om_cycle': PreparePSOpModeCycle,
            'trims': CycleTrims,
            'cycle': Cycle,
            'restore_timing': RestoreTiming,
        }
        # Setup UI
        self._needs_update_setup = False
        self._setup_ui()
        self._update_setup_timer = QTimer(self)
        self._update_setup_timer.timeout.connect(self._update_setup)
        self._update_setup_timer.setInterval(250)
        self._update_setup_timer.start()
        self.setWindowTitle('PS Cycle')

    def _setup_ui(self):
        # central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # tree
        gb_tree = QGroupBox('Select power supplies:')
        self.pwrsupplies_tree = PVNameTree(
            self._psnames, ('sec', 'mag_group'), tuple(), self)
        self.pwrsupplies_tree.tree.setHeaderHidden(True)
        self.pwrsupplies_tree.tree.setColumnCount(1)
        glay_tree = QVBoxLayout(gb_tree)
        glay_tree.addWidget(self.pwrsupplies_tree)

        # commands
        lb_prep_ti = QLabel('<h4>Prepare Timing</h4>', self,
                            alignment=Qt.AlignCenter)
        ti_ch = [PVName(name).substitute(prefix=VACA_PREFIX)
                 for name in self._timing.get_pvnames_by_psnames()]
        self.ticonn_led = PyDMLedMultiConn(self, channels=ti_ch)

        self.save_timing_bt = QPushButton(
            '1. Save Timing Initial State', self)
        self.save_timing_bt.setToolTip(
            'Save timing current state as initial state.')
        self.save_timing_bt.clicked.connect(
            _part(self._run_task, 'save_timing'))
        self.save_timing_bt.clicked.connect(self._set_lastcomm)

        self.prepare_timing_bt = QPushButton(
            '2. Prepare Timing', self)
        self.prepare_timing_bt.setToolTip(
            'Prepare EVG, triggers and events')
        self.prepare_timing_bt.clicked.connect(
            _part(self._run_task, 'timing'))
        self.prepare_timing_bt.clicked.connect(self._set_lastcomm)

        self.prepare_timing_lb = QLabel(self)
        self.prepare_timing_lb.setPixmap(self._pixmap_not)

        lb_prep_ps = QLabel('<h4>Prepare PS</h4>', self,
                            alignment=Qt.AlignCenter)
        self.psconn_led = PyDMLedMultiConn(self)

        self.set_ps_sofbmode_off_bt = QPushButton(
            '3. Turn off PS SOFBMode', self)
        self.set_ps_sofbmode_off_bt.setToolTip(
            'Turn off power supplies SOFBMode.')
        self.set_ps_sofbmode_off_bt.clicked.connect(
            _part(self._run_task, 'ps_sofbmode'))
        self.set_ps_sofbmode_off_bt.clicked.connect(self._set_lastcomm)

        self.set_ps_sofbmode_off_lb = QLabel(self)
        self.set_ps_sofbmode_off_lb.setPixmap(self._pixmap_not)

        self.set_ps_opmode_slowref_bt = QPushButton(
            '4. Set PS OpMode to SlowRef', self)
        self.set_ps_opmode_slowref_bt.setToolTip(
            'Set power supplies OpMode to SlowRef.')
        self.set_ps_opmode_slowref_bt.clicked.connect(
            _part(self._run_task, 'ps_om_slowref'))
        self.set_ps_opmode_slowref_bt.clicked.connect(self._set_lastcomm)

        self.set_ps_opmode_slowref_lb = QLabel(self)
        self.set_ps_opmode_slowref_lb.setPixmap(self._pixmap_not)

        self.set_ps_current_zero_bt = QPushButton(
            '5. Set PS current to zero', self)
        self.set_ps_current_zero_bt.setToolTip(
            'Set power supplies current to zero.')
        self.set_ps_current_zero_bt.clicked.connect(
            _part(self._run_task, 'ps_current'))
        self.set_ps_current_zero_bt.clicked.connect(self._set_lastcomm)

        self.set_ps_current_zero_lb = QLabel(self)
        self.set_ps_current_zero_lb.setPixmap(self._pixmap_not)

        self.prepare_ps_params_bt = QPushButton(
            '6. Prepare PS Parameters', self)
        self.prepare_ps_params_bt.setToolTip(
            'Check power supplies OpMode in SlowRef, check\n'
            'current is zero and configure cycle parameters.')
        self.prepare_ps_params_bt.clicked.connect(
            _part(self._run_task, 'ps_params'))
        self.prepare_ps_params_bt.clicked.connect(self._set_lastcomm)

        self.prepare_ps_params_lb = QLabel(self)
        self.prepare_ps_params_lb.setPixmap(self._pixmap_not)

        self.prepare_ps_opmode_bt = QPushButton(
            '7. Prepare PS OpMode', self)
        self.prepare_ps_opmode_bt.setToolTip(
            'Set power supplies OpMode to Cycle.')
        self.prepare_ps_opmode_bt.clicked.connect(
            _part(self._run_task, 'ps_om_cycle'))
        self.prepare_ps_opmode_bt.clicked.connect(self._set_lastcomm)

        self.prepare_ps_opmode_lb = QLabel(self)
        self.prepare_ps_opmode_lb.setPixmap(self._pixmap_not)

        lb_cycle = QLabel('<h4>Cycle</h4>', self,
                          alignment=Qt.AlignCenter)

        self.cycle_trims_bt = QPushButton('8. Cycle Trims', self)
        self.cycle_trims_bt.setToolTip(
            'Cycle trims:\nStep 1) CH, QS and QTrims\nStep 2) CV')
        self.cycle_trims_bt.clicked.connect(
            _part(self._run_task, 'trims'))
        self.cycle_trims_bt.clicked.connect(self._set_lastcomm)
        self.cycle_trims_bt.setVisible(False)

        self.cycle_trims_lb = QLabel(self)
        self.cycle_trims_lb.setPixmap(self._pixmap_check)
        self.cycle_trims_lb.setVisible(False)

        self.cycle_bt = QPushButton('8. Cycle', self)
        self.cycle_bt.setToolTip(
            'Check all configurations,\nenable triggers and run cycle.')
        self.cycle_bt.clicked.connect(
            _part(self._run_task, 'cycle'))
        self.cycle_bt.clicked.connect(self._set_lastcomm)
        self.cycle_bt.setEnabled(False)

        lb_rest_ti = QLabel('<h4>Restore Timing</h4>', self,
                            alignment=Qt.AlignCenter)
        self.restore_timing_bt = QPushButton(
            '9. Restore Timing Initial State', self)
        self.restore_timing_bt.setToolTip(
            'Restore timing initial state.')
        self.restore_timing_bt.clicked.connect(
            _part(self._run_task, 'restore_timing'))
        self.restore_timing_bt.clicked.connect(self._set_lastcomm)

        self._prepared_labels = {
            'timing': self.prepare_timing_lb,
            'ps_sofbmode': self.set_ps_sofbmode_off_lb,
            'ps_om_slowref': self.set_ps_opmode_slowref_lb,
            'ps_current': self.set_ps_current_zero_lb,
            'ps_params': self.prepare_ps_params_lb,
            'ps_om_cycle': self.prepare_ps_opmode_lb,
            'trims': self.cycle_trims_lb}

        gb_commsts = QGroupBox()
        gb_commsts.setStyleSheet("""
            QPushButton{min-height:1.5em;}
            QLabel{qproperty-alignment: AlignCenter;}""")
        lay_commsts = QGridLayout(gb_commsts)
        lay_commsts.addItem(
            QSpacerItem(1, 1, QSzPlcy.Ignored, QSzPlcy.Expanding), 0, 0, 1, 2)
        lay_commsts.addWidget(lb_prep_ti, 1, 0)
        lay_commsts.addWidget(self.ticonn_led, 1, 1)
        lay_commsts.addWidget(self.save_timing_bt, 2, 0)
        lay_commsts.addWidget(self.prepare_timing_bt, 3, 0)
        lay_commsts.addWidget(self.prepare_timing_lb, 3, 1)
        lay_commsts.addItem(
            QSpacerItem(1, 1, QSzPlcy.Ignored, QSzPlcy.Expanding), 4, 0)
        lay_commsts.addWidget(lb_prep_ps, 5, 0)
        lay_commsts.addWidget(self.psconn_led, 5, 1)
        lay_commsts.addWidget(self.set_ps_sofbmode_off_bt, 6, 0)
        lay_commsts.addWidget(self.set_ps_sofbmode_off_lb, 6, 1)
        lay_commsts.addWidget(self.set_ps_opmode_slowref_bt, 7, 0)
        lay_commsts.addWidget(self.set_ps_opmode_slowref_lb, 7, 1)
        lay_commsts.addWidget(self.set_ps_current_zero_bt, 8, 0)
        lay_commsts.addWidget(self.set_ps_current_zero_lb, 8, 1)
        lay_commsts.addWidget(self.prepare_ps_params_bt, 9, 0)
        lay_commsts.addWidget(self.prepare_ps_params_lb, 9, 1)
        lay_commsts.addWidget(self.prepare_ps_opmode_bt, 10, 0)
        lay_commsts.addWidget(self.prepare_ps_opmode_lb, 10, 1)
        lay_commsts.addItem(
            QSpacerItem(1, 1, QSzPlcy.Ignored, QSzPlcy.Expanding), 11, 0)
        lay_commsts.addWidget(lb_cycle, 12, 0)
        lay_commsts.addWidget(self.cycle_trims_bt, 13, 0)
        lay_commsts.addWidget(self.cycle_trims_lb, 13, 1)
        lay_commsts.addWidget(self.cycle_bt, 14, 0)
        lay_commsts.addItem(
            QSpacerItem(1, 1, QSzPlcy.Ignored, QSzPlcy.Expanding), 15, 0)
        lay_commsts.addWidget(lb_rest_ti, 16, 0)
        lay_commsts.addWidget(self.restore_timing_bt, 17, 0)
        lay_commsts.addItem(
            QSpacerItem(1, 1, QSzPlcy.Ignored, QSzPlcy.Expanding), 18, 0)
        lay_commsts.setColumnStretch(0, 10)
        lay_commsts.setColumnStretch(1, 1)
        lay_commsts.setVerticalSpacing(12)
        lay_commsts.setHorizontalSpacing(6)

        self.label_lastcomm = QLabel('Last Command: ', self)
        self.clearhist_bt = QPushButton('Clear', self)
        self.clearhist_bt.clicked.connect(self._clear_lastcomm)
        lay_lc = QHBoxLayout()
        lay_lc.setContentsMargins(0, 0, 0, 0)
        lay_lc.addWidget(self.label_lastcomm, alignment=Qt.AlignLeft)
        lay_lc.addWidget(self.clearhist_bt, alignment=Qt.AlignRight)
        lay_lc.setStretch(0, 10)
        lay_lc.setStretch(1, 1)

        self.progress_list = QListWidget(self)
        self.progress_list.setObjectName('progresslist')
        self.progress_list.setStyleSheet('#progresslist{min-width:20em;}')
        self.progress_list.itemDoubleClicked.connect(self._open_ps_detail)
        self.progress_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.progress_list.setToolTip(
            'Select rows and press Ctrl+C to copy and Esc to deselect.')

        self.progress_bar = MyProgressBar(self)

        lay_log = QVBoxLayout()
        lay_log.addLayout(lay_lc)
        lay_log.addWidget(self.progress_list)
        lay_log.addWidget(self.progress_bar)

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
        layout.addWidget(gb_tree, 1, 0)
        layout.addWidget(gb_commsts, 1, 1)
        layout.addLayout(lay_log, 1, 2)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 15)
        layout.setColumnStretch(0, 5)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 8)
        self.central_widget.setLayout(layout)

    # --- handle tasks ---

    def _run_task(self, control=''):
        if not self._check_connected(control):
            return
        pwrsupplies = self._get_ps_list()
        if not pwrsupplies:
            return

        if 'ps' in control and not self._verify_ps(pwrsupplies):
            return

        if control in self._step_2_task:
            task_class = self._step_2_task[control]
        else:
            raise NotImplementedError(
                "Task not defined for control '{}'".format(control))
        self._is_preparing = control

        self._handle_buttons_enabled(False)
        self.progress_list.clear()

        task = task_class(
            parent=self, psnames=pwrsupplies, timing=self._timing,
            isadv=self._is_adv_mode)
        task.updated.connect(self._update_progress)
        duration = task.duration()

        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(duration)
        self.progress_bar.setValue(0)
        pal = self.progress_bar.palette()
        pal.setColor(QPalette.Highlight, self.progress_bar.default_color)
        self.progress_bar.setPalette(pal)

        self.update_bar = UpdateProgressBar(duration, self)
        self.update_bar.increment.connect(self.progress_bar.increment)

        task.start()
        self.update_bar.start()

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
        elif 'Sent ' in text:
            last_item = self.progress_list.item(self.progress_list.count()-1)
            if 'Sent ' in last_item.text():
                last_item.setText(text)
            else:
                self.progress_list.addItem(text)
                self.progress_list.scrollToBottom()
        elif 'Successfully checked ' in text:
            last_item = self.progress_list.item(self.progress_list.count()-1)
            if 'Successfully checked ' in last_item.text():
                last_item.setText(text)
            else:
                self.progress_list.addItem(text)
                self.progress_list.scrollToBottom()
        elif 'Created connections ' in text:
            last_item = self.progress_list.item(self.progress_list.count()-1)
            if 'Created connections ' in last_item.text():
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
                if self._is_preparing in self._prepared.keys():
                    self._prepared[self._is_preparing] = False
                cycle = all(self._prepared.values())
                self._handle_buttons_enabled(True, cycle=cycle)
            elif warning:
                item.setForeground(warncolor)
            elif 'finished' in text:
                self.update_bar.exit_task()
                self.progress_bar.setValue(self.progress_bar.maximum())
                if self._is_preparing == 'cycle':
                    self._prepared = {k: False for k in self._prepared.keys()}
                    if not self.cycle_trims_bt.isVisible():
                        self._prepared['trims'] = True
                    cycle = False
                else:
                    if self._is_preparing in self._prepared.keys():
                        self._prepared[self._is_preparing] = True
                    cycle = all(self._prepared.values())
                self._handle_buttons_enabled(True, cycle=cycle)

            self._handle_stslabels_content()

            self.progress_list.addItem(item)
            self.progress_list.scrollToBottom()

    def _handle_buttons_enabled(self, enable, cycle=False):
        self.save_timing_bt.setEnabled(enable)
        self.prepare_timing_bt.setEnabled(enable)
        self.set_ps_sofbmode_off_bt.setEnabled(enable)
        self.set_ps_opmode_slowref_bt.setEnabled(enable)
        self.set_ps_current_zero_bt.setEnabled(enable)
        self.prepare_ps_params_bt.setEnabled(enable)
        self.prepare_ps_opmode_bt.setEnabled(enable)
        self.cycle_trims_bt.setEnabled(enable)
        self.cycle_bt.setEnabled(cycle)
        self.restore_timing_bt.setEnabled(enable)
        self.clearhist_bt.setEnabled(enable)
        self.pwrsupplies_tree.setEnabled(enable)

    def _handle_stslabels_content(self):
        for prep, value in self._prepared.items():
            pixmap = self._pixmap_check if value else self._pixmap_not
            self._prepared_labels[prep].setPixmap(pixmap)

    def _set_lastcomm(self):
        sender_text = self.sender().text()
        self.label_lastcomm.setText('Last Command: '+sender_text)

    def _clear_lastcomm(self):
        self.progress_bar.setValue(0)
        self.progress_list.clear()
        self.label_lastcomm.setText('Last Command: ')

    # --- handle ps selection ---

    def _get_ps_list(self):
        """Return list of power supplies to cycle."""
        # Get power supplies list
        pwrsupplies = self.pwrsupplies_tree.checked_items()
        if not pwrsupplies:
            QMessageBox.critical(self, 'Message', 'No power supply selected!')
            return False

        sections = get_sections(pwrsupplies)
        if 'BO' in sections and len(sections) > 1:
            QMessageBox.critical(
                self, 'Error', 'Can not cycle Booster with other sectors!')
            return False

        create_task = CreateCyclers(parent=self, psnames=pwrsupplies)
        dlg = ProgressDialog('Creating cycles...', create_task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return False

        return pwrsupplies

    def _handle_checked_items_changed(self, item):
        psname = PVName(item.data(0, Qt.DisplayRole))
        if not _re.match('.*-.*:.*-.*', psname):
            return

        if not self._is_adv_mode and psname.sec == 'SI' and \
                not psname.dev.startswith('FC'):
            psname2check = Filter.process_filters(
                self._psnames, filters={'sec': 'SI', 'dev': '(?!FC)'})
            psname2check.remove(psname)
            state2set = item.checkState(0)
            self.pwrsupplies_tree.tree.blockSignals(True)
            for psn in psname2check:
                item2check = self.pwrsupplies_tree._item_map[psn]
                if item2check.checkState(0) != state2set:
                    item2check.setData(0, Qt.CheckStateRole, state2set)
            self.pwrsupplies_tree.tree.blockSignals(False)
        else:
            if (psname.sec in ['BO', 'SI'] and psname.dev in ['B', 'B1B2']):
                psname2check = PSSearch.get_psnames(
                    {'sec': psname.sec, 'dev': 'B.*'})
                psname2check.remove(psname)
                item2check = self.pwrsupplies_tree._item_map[psname2check[0]]

                state2set = item.checkState(0)
                state2change = item2check.checkState(0)
                if state2change != state2set:
                    self.pwrsupplies_tree.tree.blockSignals(True)
                    item2check.setData(0, Qt.CheckStateRole, state2set)
                    self.pwrsupplies_tree.tree.blockSignals(False)

        self._prepared.update(self._prepared_init_vals)
        self._needs_update_setup = True

    def _update_setup(self):
        if not self._needs_update_setup:
            return
        self._needs_update_setup = False

        # update leds
        psnames = self.pwrsupplies_tree.checked_items()
        ti_ch = [PVName(name).substitute(prefix=VACA_PREFIX)
                 for name in self._timing.get_pvnames_by_psnames(psnames)]
        self.ticonn_led.set_channels(ti_ch)

        ps_ch = list()
        for name in psnames:
            ps_ch.append(PVName(name).substitute(
                prefix=VACA_PREFIX, propty='PwrState-Sts'))
        self.psconn_led.set_channels(ps_ch)

        # update buttons and self._prepared dict if not in advanced mode
        if not self._is_adv_mode:
            has_sifam = False
            sifamfilt = {'sec': 'SI', 'sub': 'Fam', 'dis': 'PS'}
            for psn in PSSearch.get_psnames(sifamfilt):
                if psn not in self.pwrsupplies_tree._item_map:
                    continue
                item = self.pwrsupplies_tree._item_map[psn]
                has_sifam |= item.checkState(0) != 0

            if not has_sifam:
                self.cycle_bt.setText('8. Cycle')
                self.restore_timing_bt.setText(
                    '9. Restore Timing Initial State')
                self.cycle_trims_bt.setVisible(False)
                self.cycle_trims_lb.setVisible(False)
                self._prepared['trims'] = True
            else:
                self.cycle_bt.setText('9. Cycle')
                self.restore_timing_bt.setText(
                    '10. Restore Timing Initial State')
                self.cycle_trims_bt.setVisible(True)
                self.cycle_trims_lb.setVisible(True)
                self._prepared['trims'] = False

        self._handle_stslabels_content()
        self._handle_buttons_enabled(True)

    # --- auxiliary checks ---

    def _check_connected(self, control):
        if control in ['trims', 'cycle']:
            leds = [self.ticonn_led, self.psconn_led]
        elif 'timing' in control:
            leds = [self.ticonn_led, ]
        else:
            leds = [self.psconn_led, ]

        for led in leds:
            pvs_disconnected = set()
            for ch, v in led.channels2conn.items():
                if not v:
                    pvs_disconnected.add(ch)
            if pvs_disconnected:
                sttr = ''
                for item in pvs_disconnected:
                    sttr += item + '\n'
                QMessageBox.information(
                    self, 'Message',
                    'The following PVs are not connected:\n'+sttr)
                return False
        return True

    def _verify_ps(self, pwrsupplies):
        self._ps_failed = set()

        task = VerifyPS(parent=self, psnames=pwrsupplies)
        task.itemDone.connect(self._get_ps_not_ready_2_cycle)

        dlg = ProgressDialog(
            'Verifying power supplies initial state...', task, self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            self._handle_buttons_enabled(True)
            return False

        if self._ps_failed:
            text = 'Verify power state and interlocks' \
                ' of the following power supplies'
            dlg = PSStatusDialog(self._ps_failed, text, self)
            dlg.exec_()
            self._handle_buttons_enabled(True)
            return False

        return True

    def _get_ps_not_ready_2_cycle(self, psname, status):
        if not status:
            self._ps_failed.add(psname)

    def _open_ps_detail(self, item):
        if self.sender() == self.progress_list:
            text_split = item.data(Qt.DisplayRole).split(' ')
            psname = ''
            for text in text_split:
                if _re.match('.*-.*:.*-.*', text):
                    psname = text
            if not psname:
                return
        else:
            psname = item.data()
        if not _re.match('.*-.*:.*-.*', psname):
            if item.model().rowCount(item) == 1:
                psname = item.child(0, 0).data()
            else:
                return
        run_newprocess(['sirius-hla-as-ps-detail.py', psname])

    # --- events ---

    def keyPressEvent(self, evt):
        """Implement keyPressEvent."""
        if evt.matches(QKeySequence.Copy) and self.progress_list.underMouse():
            items = self.progress_list.selectedItems()
            items = '\n'.join([i.text() for i in items])
            QApplication.clipboard().setText(items)
        if evt.key() == Qt.Key_Escape and self.progress_list.underMouse():
            items = self.progress_list.clearSelection()
        super().keyPressEvent(evt)

    def closeEvent(self, ev):
        self._update_setup_timer.stop()
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
