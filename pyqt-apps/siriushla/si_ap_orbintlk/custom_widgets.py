"""BPM Interlock Buttons."""

import time as _time
import numpy as _np

from qtpy.QtCore import Qt, Signal, Slot, QSize
from qtpy.QtWidgets import QPushButton, QComboBox, QSizePolicy as QSzPlcy, \
    QWidget, QHBoxLayout, QCheckBox, QLabel, QGridLayout, QSpinBox, QGroupBox,\
    QDoubleSpinBox, QDialog, QVBoxLayout, QScrollArea

from pydm.widgets.base import PyDMWidget

from ..widgets import SiriusLedState, QLed, SelectionMatrixWidget, \
    SiriusConnectionSignal, SiriusLabel
from ..widgets.dialog import ReportDialog, ProgressDialog
from ..common.epics.task import EpicsConnector, EpicsSetter, \
    EpicsChecker, EpicsWait
from ..as_ap_configdb import LoadConfigDialog
from .base import BaseObject


class RefOrbComboBox(QComboBox):
    """Reference Orbit Selection ComboBox."""

    refOrbChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSzPlcy.Expanding, QSzPlcy.Preferred)
        self.setMaxVisibleItems(10)
        self._choose_reforb = [
            'Zero', 'ref_orb', 'bba_orb', 'other...']
        for item in self._choose_reforb:
            self.addItem(item)
        self.setCurrentText('ref_orb')
        self.activated.connect(self._add_reforb_entry)

    @Slot(int)
    def _add_reforb_entry(self, index):
        text = self.itemText(index)
        if not text.startswith('other'):
            self.refOrbChanged.emit(text)
            return
        win = LoadConfigDialog('si_orbit', self)
        confname, status = win.exec_()
        if not status:
            self.setCurrentIndex(0)
            return
        self.insertItem(index, confname)
        self.setCurrentIndex(index)
        self.refOrbChanged.emit(confname)


class _BPMSelectionWidget(BaseObject, SelectionMatrixWidget):
    """BPM Base Selection Widget."""

    def __init__(
            self, parent=None, title='', propty='', prefix='', **kwargs):
        """Init."""
        BaseObject.__init__(self, prefix)

        self.propty = propty

        SelectionMatrixWidget.__init__(
            self, parent=parent, title=title, **kwargs)

    def sizeHint(self):
        """Return the base size of the widget."""
        return QSize(500, 1200)

    def get_headers(self):
        nicks = self.BPM_NICKNAMES
        top_headers = sorted({nick[2:] for nick in nicks})
        top_headers = top_headers[-2:] + top_headers[:-2]
        side_headers = sorted({nick[:2] for nick in nicks})
        side_headers.append(side_headers[0])
        return top_headers, side_headers

    def get_widgets(self):
        widgets = list()
        sz_polc = QSzPlcy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        for idx, nick in enumerate(self.BPM_NICKNAMES):
            wid = QWidget(self.parent())
            tooltip = '{0}; Pos = {1:5.1f} m'.format(
                nick, self.BPM_POS[idx])
            if self.propty:
                item = SiriusLedState(self)
                item.setParent(wid)
                item.setSizePolicy(sz_polc)
                item.setToolTip(tooltip)
            else:
                item = QCheckBox(self)
                item.setSizePolicy(sz_polc)
            hbl = QHBoxLayout(wid)
            hbl.setContentsMargins(0, 0, 0, 0)
            hbl.addWidget(item)
            widgets.append(wid)
        return widgets

    def get_positions(self):
        top_headers, _ = self.headers
        positions = list()
        for idx, nick in enumerate(self.BPM_NICKNAMES):
            i = (idx + 1) // len(top_headers)
            j = top_headers.index(nick[2:])
            positions.append((i, j))
        return positions


class BPMIntlkEnblWidget(_BPMSelectionWidget, PyDMWidget):
    """BPM Orbit Interlock Enable Widget."""

    def __init__(self, parent=None, propty='', title='', prefix=''):
        """Init."""
        _BPMSelectionWidget.__init__(
            self, parent=parent, propty=propty, title=title, prefix=prefix)

        address = self.hlprefix.substitute(prefix=self.prefix, propty=propty)
        PyDMWidget.__init__(self, init_channel=address.replace('-SP', '-RB'))

        # initialize auxiliary attributes
        self.propty = propty

        # create channels
        self.pv_sel = SiriusConnectionSignal(address)

        self.setObjectName('SIApp')
        self.setStyleSheet('#SIApp{min-width: 27em; max-width: 27em;}')

        # connect signals and slots
        self.applyChangesClicked.connect(self.send_value)

    def send_value(self):
        """Send new value."""
        val = self.pv_sel.getvalue()
        if val is None:
            return
        for idx, wid in enumerate(self.widgets):
            led = wid.findChild(QLed)
            if led.isSelected():
                val[idx] = int(not led.state)
                led.setSelected(False)
        self.pv_sel.send_value_signal[_np.ndarray].emit(val)

    def value_changed(self, new_val):
        if not isinstance(new_val, _np.ndarray):
            return
        super(BPMIntlkEnblWidget, self).value_changed(new_val)
        for i, wid in enumerate(self.widgets):
            led = wid.findChild(QLed)
            led.state = self.value[i]
        self.adjustSize()
        parent = self.parent()
        while parent is not None:
            parent.adjustSize()
            if isinstance(parent, QDialog):
                break
            parent = parent.parent()

    def connection_changed(self, new_conn):
        super(BPMIntlkEnblWidget, self).connection_changed(new_conn)
        for wid in self.widgets:
            led = wid.findChild(QLed)
            led.setEnabled(new_conn)


class BPMIntlkLimSPWidget(BaseObject, QWidget):
    """BPM Orbit Interlock Limit Setpoint Widget."""

    def __init__(self, parent=None, metric='', prefix=''):
        """Init."""
        BaseObject.__init__(self, prefix)
        QWidget.__init__(self, parent)

        # initialize auxiliary attributes
        self.metric = metric.lower()
        if 'sum' in self.metric:
            self.lim_sp = ['MinSumLim-SP', ]
            self.title = 'Min.Sum. Thresholds'
        elif 'pos' in self.metric:
            self.lim_sp = [
                'PosXMinLim-SP', 'PosXMaxLim-SP',
                'PosYMinLim-SP', 'PosYMaxLim-SP']
            self.title = 'Position Thresholds'
        elif 'ang' in self.metric:
            self.lim_sp = [
                'AngXMinLim-SP', 'AngXMaxLim-SP',
                'AngYMinLim-SP', 'AngYMaxLim-SP']
            self.title = 'Angulation Thresholds'
        else:
            raise ValueError(metric)

        if 'sum' in self.metric:
            self._create_pvs('SlowSumRaw-Mon')
            self._summon = _np.zeros(len(self.BPM_NAMES), dtype=float)
        else:
            self._set_ref_orb('ref_orb')

        self.lim_pvs = {
            p: SiriusConnectionSignal(self.hlprefix.substitute(propty=p))
            for p in self.lim_sp}

        # initialize super
        self.setObjectName('SIApp')

        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        title = QLabel(self.title, self, alignment=Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold;")
        title.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)

        # limit setpoints
        self._wid_lims = QGroupBox('Select Thresholds: ')
        lay_lims = QGridLayout(self._wid_lims)
        lay_lims.setAlignment(Qt.AlignTop)

        row = 0
        if 'sum' in self.metric:
            text = '\nThresholds must be set in FAcq rate counts,\n'\
                'considering polynomial calibration disabled.\n'\
                'Here we make available you to read Sum-Mon\n'\
                'values, in Monit rate counts, and convert them\n'\
                'to orbit interlock counts using Monit/FAcq\n'\
                'ratio. You can also apply a scale factor to the\n'\
                'values read.\n\n'
            self._label_help = QLabel(text, self)
            lay_lims.addWidget(self._label_help, row, 0, 1, 2)

            row += 1
            self._pb_get = QPushButton('Get current Sum-Mon', self)
            self._pb_get.released.connect(self._get_new_sum)
            lay_lims.addWidget(self._pb_get, row, 0, 1, 2)
            row += 1
            self._label_getsts = QLabel('\n', self)
            lay_lims.addWidget(self._label_getsts, row, 0, 1, 2)

            row += 1
            self._label_scl = QLabel('Scale: ', self)
            lay_lims.addWidget(self._label_scl, row, 0)
            self._spin_scl = QDoubleSpinBox(self)
            self._spin_scl.setDecimals(2)
            self._spin_scl.setValue(1.00)
            self._spin_scl.setMinimum(-100.00)
            self._spin_scl.setMaximum(+100.00)
            lay_lims.addWidget(self._spin_scl, row, 1)
        else:
            self._head_value = QLabel('Value', self, alignment=Qt.AlignCenter)
            lay_lims.addWidget(self._head_value, 0, 1)
            self._head_send = QLabel('Apply', self, alignment=Qt.AlignCenter)
            lay_lims.addWidget(self._head_send, 0, 2)

            self._spins, self._checks = dict(), dict()
            for lsp in self.lim_sp:
                row += 1
                text = lsp.split('-')[0].split('Lim')[0]+' [nm]: '
                label = QLabel(text, self, alignment=Qt.AlignRight)
                lay_lims.addWidget(label, row, 0)
                spin = QSpinBox(self)
                self._spins[lsp] = spin
                spin.setValue(0)
                spin.setMinimum(-1e9)
                spin.setMaximum(1e9)
                lay_lims.addWidget(spin, row, 1)
                check = QCheckBox(self)
                self._checks[lsp] = check
                lay_lims.addWidget(check, row, 2, alignment=Qt.AlignCenter)

            row += 1
            self._label_reforb = QLabel(
                '\nChoose Ref.Orb. to calculate reference\n' +
                self.title.lower()+' around which we\napply the values above:')
            lay_lims.addWidget(self._label_reforb, row, 0, 1, 3)

            row += 1
            self._cb_reforb = RefOrbComboBox(self)
            self._cb_reforb.refOrbChanged.connect(self._set_ref_orb)
            lay_lims.addWidget(self._cb_reforb, row, 0, 1, 3)

            if 'pos' in self.metric:
                text = '\n\nBPM calculation consider the position\n' \
                    'estimative:' \
                    '\n\n(pos@downstream+pos@upstream)/2\n\n' \
                    'where the pairs upstream/downstream\nfolow:\n' \
                    '    - M1/M2\n' \
                    '    - C1-1/C1-2\n' \
                    '    - C2/C3-1\n' \
                    '    - C3-2/C4\n'
            elif 'ang' in self.metric:
                text = '\n\nBPM calculation consider the angulation\n' \
                    'estimative:' \
                    '\n\n(pos@downstream - pos@upstream)\n\n' \
                    'where the pairs upstream/downstream\nfolow:\n' \
                    '    - M1/M2\n' \
                    '    - C1-1/C1-2\n' \
                    '    - C2/C3-1\n' \
                    '    - C3-2/C4\n'
            row += 1
            self._label_help = QLabel(text, self)
            lay_lims.addWidget(self._label_help, row, 0, 1, 3)

        # BPM selection
        groupsel = QGroupBox('Select BPMs:')
        groupsel.setObjectName('groupsel')
        groupsel.setStyleSheet(
            '#groupsel{min-width: 27em; max-width: 27em;}')
        self._bpm_sel = _BPMSelectionWidget(
            self, show_toggle_all_false=False,
            toggle_all_true_text='Select All', prefix=self.prefix)
        lay_groupsel = QGridLayout(groupsel)
        lay_groupsel.addWidget(self._bpm_sel)

        # connect signals and slots
        self._bpm_sel.applyChangesClicked.connect(self.send_value)

        lay = QGridLayout(self)
        lay.addWidget(title, 0, 0, 1, 2)
        lay.addWidget(self._wid_lims, 1, 0)
        lay.addWidget(groupsel, 1, 1)

    def _set_ref_orb(self, text):
        self._reforb = dict()
        if text.lower() == 'zero':
            self._reforb['x'] = _np.zeros(len(self.BPM_NAMES), dtype=float)
            self._reforb['y'] = _np.zeros(len(self.BPM_NAMES), dtype=float)
        else:
            data = self.get_ref_orb(text)
            self._reforb['x'] = data['x']
            self._reforb['y'] = data['y']

    def _get_new_sum(self):
        self._summon = _np.array(
            self._get_values('SlowSumRaw-Mon'), dtype=float)
        text = 'Read at ' + _time.strftime(
            '%d/%m/%Y %H:%M:%S\n', _time.localtime(_time.time()))
        self._label_getsts.setText(text)

    def send_value(self):
        """Send new value."""
        idxsel = list()
        for idx, wid in enumerate(self._bpm_sel.widgets):
            check = wid.findChild(QCheckBox)
            if check.isChecked():
                idxsel.append(idx)
                check.setChecked(False)
        idxsel = _np.array(idxsel, dtype=int)
        if not idxsel.size:
            return

        if 'sum' in self.metric:
            sumintlk = self._summon * self.monitsum2intlksum_factor
            allvals = self.lim_pvs[self.lim_sp[0]].getvalue().astype(_np.int_)
            allvals[idxsel] = self._spin_scl.value() * sumintlk[idxsel]
            reso = self.MINSUM_RESO
            allvals[idxsel] = _np.ceil(allvals[idxsel] / reso) * reso
            allvals[idxsel] = self.calc_intlk_metric(
                allvals, operation='min')[idxsel]
            values = [allvals, ]
            pvs = [self.hlprefix.substitute(propty=self.lim_sp[0]), ]
        else:
            pvs, values = list(), list()
            for lsp in self.lim_sp:
                if not self._checks[lsp].isChecked():
                    continue
                lval = self._spins[lsp].value()
                plan = 'y' if 'y' in lsp.lower() else 'x'
                metric = self.calc_intlk_metric(
                    self._reforb[plan], metric=self.metric)
                allvals = self.lim_pvs[lsp].getvalue()
                allvals[idxsel] = _np.round(metric[idxsel] + lval)
                values.append(allvals)
                pvs.append(self.hlprefix.substitute(propty=lsp))

        delays = [0.0, ] * len(pvs)

        self._items_success = list()
        self._items_fail = list()
        conn = EpicsConnector(pvs, parent=self)
        task_set = EpicsSetter(pvs, values, delays, parent=self)
        task_sleep = EpicsWait([None, ]*10, wait_time=2.0, parent=self)
        task_check = EpicsChecker(pvs, values, delays, parent=self)
        task_check.itemChecked.connect(self._check_status)

        dlg = ProgressDialog(
            ['Connecting...', 'Setting...', 'Waiting...', 'Checking...'],
            [conn, task_set, task_sleep, task_check], parent=self)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return

        if self._items_fail:
            report = ReportDialog(self._items_fail, self)
            report.exec_()
            return

    @Slot(str, bool)
    def _check_status(self, item, status):
        if status:
            self._items_success.append((item, True))
        else:
            self._items_fail.append(item)


class MonitoredDevicesDialog(BaseObject, QDialog):
    """Monitored Devices Detail Dialog."""

    def __init__(self, parent=None, prefix='', propty=''):
        """Init."""
        BaseObject.__init__(self, prefix)
        QWidget.__init__(self, parent)
        title = 'Monitored Devices'
        self.setObjectName('SIApp')
        self.setWindowTitle(title)

        self._desc = QLabel('<h4>'+title+'</h4>')
        self._desc.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        self._label = SiriusLabel(
            self, self.hlprefix.substitute(propty=propty))
        self._label.displayFormat = SiriusLabel.DisplayFormat.String

        scarea = QScrollArea(self)
        scarea.setStyleSheet(
            '.QScrollArea{min-height: 30em;}')
        scarea.setSizeAdjustPolicy(scarea.AdjustToContents)
        scarea.setWidgetResizable(True)

        scr_ar_wid = QWidget()
        scr_ar_wid.setObjectName('scrollarea')
        scr_ar_wid.setStyleSheet(
            '#scrollarea {background-color: transparent;}')
        gdl = QGridLayout(scr_ar_wid)
        gdl.addWidget(self._desc)
        gdl.addWidget(self._label)
        scarea.setWidget(scr_ar_wid)

        lay = QVBoxLayout(self)
        lay.addWidget(scarea)
