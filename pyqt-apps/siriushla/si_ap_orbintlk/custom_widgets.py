"""BPM Interlock Buttons."""

import time as _time
import numpy as _np

from qtpy.QtCore import Qt, Signal, Slot, QSize
from qtpy.QtWidgets import QPushButton, QComboBox, QSizePolicy as QSzPlcy, \
    QWidget, QHBoxLayout, QCheckBox, QLabel, QGridLayout, QSpinBox, QGroupBox,\
    QDoubleSpinBox

from siriuspy.epics import PV as _PV
from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName

from ..widgets import PyDMLedMultiChannel, PyDMLed, SiriusLedState, QLed, \
    SelectionMatrixWidget
from ..widgets.led import MultiChannelStatusDialog
from ..widgets.dialog import ReportDialog, ProgressDialog
from ..common.epics.task import EpicsConnector, EpicsSetter, \
    EpicsChecker, EpicsWait
from ..as_ap_configdb import LoadConfigDialog
from .base import BaseObject


class FamBPMButton(BaseObject, QPushButton):
    """Button to send PV setpoint to all BPMs."""

    def __init__(self, parent=None, prefix=_vaca_prefix,
                 propty='', text='', value=1):
        """Init."""
        BaseObject.__init__(self, prefix)
        QPushButton.__init__(self, text, parent)

        self.prefix = prefix
        self.propty = propty
        self.value = value
        self.pvs, self.pvs2conn = dict(), dict()
        for bpm in self.BPM_NAMES:
            pvname = bpm.substitute(prefix=self.prefix, propty=self.propty)
            self.pvs2conn[pvname] = None
            self.pvs[pvname] = _PV(
                pvname, connection_callback=self._connection_changed,
                connection_timeout=0.05)
        self.released.connect(self._send_value)

    def _send_value(self):
        for pvo in self.pvs.values():
            if pvo.wait_for_connection():
                pvo.put(self.value)

    def _connection_changed(self, pvname, conn, **kws):
        self.pvs2conn[pvname] = conn
        connstate = all(self.pvs2conn.values())
        self.setEnabled(connstate)


class FamBPMIntlkEnblStateLed(PyDMLedMultiChannel):
    """Led to check whether several PVs are in enabled state."""

    def __init__(self, parent=None, channels2values=dict()):
        super().__init__(parent, channels2values)
        self.stateColors = [
            PyDMLed.DarkGreen, PyDMLed.LightGreen,
            PyDMLed.Yellow, PyDMLed.Gray]

    def _update_statuses(self):
        if not self._connected:
            state = 3
        else:
            status_off = 0
            for status in self._address2status.values():
                if status == 'UNDEF' or not status:
                    status_off += 1
            if status_off == len(self._address2status.values()):
                state = 0
            elif status_off > 0:
                state = 2
            else:
                state = 1
        self.setState(state)

    def mouseDoubleClickEvent(self, _):
        """Reimplement mouseDoubleClick."""
        pv_groups, texts = list(), list()
        pvs_err, pvs_und = set(), set()
        for k, val in self._address2conn.items():
            if not val:
                pvs_und.add(k)
        if pvs_und:
            pv_groups.append(pvs_und)
            texts.append('There are disconnected PVs!')
        for k, val in self._address2status.items():
            if not val and k not in pvs_und:
                pvs_err.add(k)
        if pvs_err:
            pv_groups.append(pvs_err)
            texts.append(
                'The following PVs have value\n'
                'equivalent to disabled status!')

        if pv_groups:
            msg = MultiChannelStatusDialog(
                parent=self, pvs=pv_groups,
                text=texts, fun_show_diff=self._show_diff)
            msg.exec_()


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

    def __init__(self, parent=None, title='', propty='', prefix='', **kwargs):
        """Init."""
        BaseObject.__init__(self, prefix)

        self.propty = propty
        self.prefix = prefix

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
        for idx, name in enumerate(self.BPM_NAMES):
            wid = QWidget(self.parent())
            tooltip = '{0}; Pos = {1:5.1f} m'.format(
                self.BPM_NICKNAMES[idx], self.BPM_POS[idx])
            if self.propty:
                item = SiriusLedState(self)
                item.setParent(wid)
                item.setSizePolicy(sz_polc)
                item.setToolTip(tooltip)
                pvname = SiriusPVName.from_sp2rb(
                    name.substitute(prefix=self.prefix, propty=self.propty))
                item.channel = pvname
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


class BPMIntlkEnblWidget(_BPMSelectionWidget):
    """BPM Orbit Interlock Enable Widget."""

    def __init__(self, parent=None, propty='', title='', prefix=''):
        """Init."""
        super().__init__(
            parent=parent, propty=propty, title=title, prefix=prefix)

        # initialize auxiliary attributes
        self.propty = propty

        # create channels
        self.pvs_sel = dict()
        for bpm in self.BPM_NAMES:
            self.pvs_sel[bpm] = _PV(
                bpm.substitute(prefix=self.prefix, propty=propty),
                connection_timeout=0.05)

        self.setObjectName('SIApp')
        self.setStyleSheet(
            '#SIApp{min-width: 27em; max-width: 27em;}')

        # connect signals and slots
        self.applyChangesClicked.connect(self.send_value)

    def send_value(self):
        """Send new value."""
        for idx, wid in enumerate(self.widgets):
            name = self.BPM_NAMES[idx]
            led = wid.findChild(QLed)
            if led.isSelected():
                new_state = int(not led.state)
                pvo = self.pvs_sel[name]
                if pvo.wait_for_connection():
                    pvo.put(int(new_state))
                    led.setSelected(False)


class BPMIntlkLimSPWidget(BaseObject, QWidget):
    """BPM Orbit Interlock Limit Setpoint Widget."""

    def __init__(self, parent=None, metric='', prefix=''):
        """Init."""
        BaseObject.__init__(self, prefix)
        QWidget.__init__(self, parent)

        # initialize auxiliary attributes
        self.metric = metric.lower()
        if 'sum' in self.metric:
            self.lim_sp = ['IntlkLmtMinSum-SP', ]
            self.title = 'Min.Sum. Thresholds'
        elif 'pos' in self.metric:
            self.lim_sp = [
                'IntlkLmtPosMinX-SP', 'IntlkLmtPosMaxX-SP',
                'IntlkLmtPosMinY-SP', 'IntlkLmtPosMaxY-SP']
            self.title = 'Position Thresholds'
        elif 'ang' in self.metric:
            self.lim_sp = [
                'IntlkLmtAngMinX-SP', 'IntlkLmtAngMaxX-SP',
                'IntlkLmtAngMinY-SP', 'IntlkLmtAngMaxY-SP']
            self.title = 'Angulation Thresholds'
        else:
            raise ValueError(metric)

        if 'sum' in self.metric:
            self._create_pvs('Sum-Mon')
            self._summon = _np.zeros(len(self.BPM_NAMES), dtype=float)
        else:
            self._set_ref_orb('ref_orb')

        self.prefix = prefix

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
                text = lsp.split('-')[0].split('Lmt')[1]+' [nm]: '
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
        self._summon = _np.array(self._get_values('Sum-Mon'), dtype=float)
        text = 'Read at ' + _time.strftime(
            '%d/%m/%Y %H:%M:%S\n', _time.localtime(_time.time()))
        self._label_getsts.setText(text)

    def send_value(self):
        """Send new value."""
        idxsel, namesel = list(), list()
        for idx, wid in enumerate(self._bpm_sel.widgets):
            name = self.BPM_NAMES[idx]
            check = wid.findChild(QCheckBox)
            if check.isChecked():
                idxsel.append(idx)
                namesel.append(name)
                check.setChecked(False)
        if not namesel:
            return

        if 'sum' in self.metric:
            summonit = self._summon
            sumintlk = summonit * self.monitsum2intlksum_factor
            allvals = self._spin_scl.value() * sumintlk
            reso = self.MINSUM_RESO
            allvals = _np.ceil(allvals / reso) * reso
            allvals = _np.array(self.calc_intlk_metric(
                allvals, operation='min'))
            values = allvals[_np.array(idxsel)]
            pvs = [b.substitute(propty=self.lim_sp[0]) for b in namesel]
        else:
            pvs, values = list(), list()
            for lsp in self.lim_sp:
                if not self._checks[lsp].isChecked():
                    continue
                lval = self._spins[lsp].value()
                plan = 'y' if 'y' in lsp.lower() else 'x'
                metric = self.calc_intlk_metric(
                    self._reforb[plan], metric=self.metric)
                allvals = _np.round(_np.array(metric) + lval)
                allvals = allvals[_np.array(idxsel)]
                values.extend(allvals)
                pvs.extend([b.substitute(propty=lsp) for b in namesel])

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
