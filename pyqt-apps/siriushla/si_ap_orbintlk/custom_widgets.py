"""BPM Interlock Buttons."""

import numpy as _np

from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtWidgets import QPushButton, QComboBox, QSizePolicy as QSzPlcy, \
    QWidget, QHBoxLayout, QCheckBox, QLabel, QGridLayout, QSpinBox, QGroupBox

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName
from siriuspy.clientconfigdb import ConfigDBClient

from ..widgets import SiriusConnectionSignal as _ConnSignal, \
    PyDMLedMultiChannel, PyDMLed, SiriusLedState, QLed, SelectionMatrixWidget
from ..widgets.led import MultiChannelStatusDialog
from ..as_ap_configdb import LoadConfigDialog
from .base import BaseObject


class FamBPMButton(BaseObject, QPushButton):
    """Button to send PV setpoint to all BPMs."""

    def __init__(self, parent=None, prefix=_vaca_prefix,
                 propty='', text='', value=1):
        """Init."""
        BaseObject.__init__(self)
        QPushButton.__init__(self, text, parent)

        self.prefix = prefix
        self.propty = propty
        self.value = value
        _chs, _conns = dict(), dict()
        for bpm in self.BPM_NAMES:
            pvname = bpm.substitute(prefix=self.prefix, propty=self.propty)
            channel = _ConnSignal(pvname)
            channel.connection_state_signal.connect(self._connection_changed)
            _chs[pvname] = channel
            _conns[pvname] = None
        self.channels = _chs
        self.channel2conn = _conns
        self.released.connect(self._send_value)

    def _send_value(self):
        for chn in self.channels.values():
            chn.send_value_signal[int].emit(self.value)

    def _connection_changed(self, conn):
        address = self.sender().address
        self.channel2conn[address] = conn

        connstate = all(self.channel2conn.values())
        self.setEnabled(connstate)


class FamBPMIntlkEnblStateLed(PyDMLedMultiChannel):
    """Led to check whether several PVs are in enabled state."""

    def __init__(self, parent=None, channels2values=dict()):
        super().__init__(parent, channels2values)
        self.stateColors = [
            PyDMLed.DarkGreen, PyDMLed.LightGreen, PyDMLed.Yellow, PyDMLed.Gray]

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

    def mouseDoubleClickEvent(self, ev):
        pv_groups, texts = list(), list()
        pvs_err, pvs_und = set(), set()
        for k, v in self._address2conn.items():
            if not v:
                pvs_und.add(k)
        if pvs_und:
            pv_groups.append(pvs_und)
            texts.append('There are disconnected PVs!')
        for k, v in self._address2status.items():
            if not v and k not in pvs_und:
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
        BaseObject.__init__(self)

        self.propty = propty
        self.prefix = prefix

        SelectionMatrixWidget.__init__(
            self, parent=parent, title=title, **kwargs)

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
            led = SiriusLedState(self)
            led.setParent(wid)
            led.setSizePolicy(sz_polc)
            tooltip = '{0}; Pos = {1:5.1f} m'.format(
                self.BPM_NICKNAMES[idx], self.BPM_POS[idx])
            led.setToolTip(tooltip)
            if self.propty:
                pvname = SiriusPVName.from_sp2rb(
                    name.substitute(prefix=self.prefix, propty=self.propty))
                led.channel = pvname
            else:
                led.state = 1
            hbl = QHBoxLayout(wid)
            hbl.setContentsMargins(0, 0, 0, 0)
            hbl.addWidget(led)
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
            self.pvs_sel[bpm] = _ConnSignal(
                bpm.substitute(prefix=self.prefix, propty=propty))

        self.setObjectName('SIApp')

        # connect signals and slots
        self.applyChangesClicked.connect(self.send_value)

    def send_value(self):
        """Send new value."""
        for idx, wid in enumerate(self.widgets):
            name = self.BPM_NAMES[idx]
            led = wid.findChild(QLed)
            if led.isSelected():
                new_state = int(not led.state)
                self.pvs_sel[name].send_value_signal[int].emit(new_state)
                led.setSelected(False)


class BPMIntlkLimSPWidget(BaseObject, QWidget):
    """BPM Orbit Interlock Limit Setpoint Widget."""

    def __init__(self, parent=None, metric='', prefix=''):
        """Init."""
        BaseObject.__init__(self)
        QWidget.__init__(self, parent)

        # initialize auxiliary attributes
        self.metric = metric.lower()
        if 'sum' in self.metric:
            self.lim_sp = ['IntlkLmtMinSum-SP', ]
            self.has_reforb = False
            self.title = 'Min.Sum. Thresholds'
        elif 'trans' in self.metric:
            self.lim_sp = [
                'IntlkLmtTransMinX-SP', 'IntlkLmtTransMaxX-SP',
                'IntlkLmtTransMinY-SP', 'IntlkLmtTransMaxY-SP']
            self.has_reforb = True
            self.title = 'Translation Thresholds'
        elif 'ang' in self.metric:
            self.lim_sp = [
                'IntlkLmtAngMinX-SP', 'IntlkLmtAngMaxX-SP',
                'IntlkLmtAngMinY-SP', 'IntlkLmtAngMaxY-SP']
            self.has_reforb = True
            self.title = 'Angulation Thresholds'
        else:
            raise ValueError(metric)

        if self.has_reforb:
            self._reforb = dict()
            self._reforb['x'] = _np.zeros(len(self.BPM_NAMES))
            self._reforb['y'] = _np.zeros(len(self.BPM_NAMES))
            self._client = ConfigDBClient(config_type='si_orbit')

        self.prefix = prefix

        # create channels
        self.pvs_sp = dict()
        for lsp in self.lim_sp:
            self.pvs_sp[lsp] = dict()
            for bpm in self.BPM_NAMES:
                self.pvs_sp[lsp][bpm] = _ConnSignal(
                    bpm.substitute(prefix=self.prefix, propty=lsp))

        # initialize super
        self.setObjectName('SIApp')

        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        title = QLabel(self.title, self, alignment=Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold;")

        # limit setpoints
        self._wid_lims = QGroupBox('Select Limits: ')
        lay_lims = QGridLayout(self._wid_lims)
        lay_lims.setAlignment(Qt.AlignTop)

        row = 0
        self._head_value = QLabel('Value', self, alignment=Qt.AlignCenter)
        lay_lims.addWidget(self._head_value, 0, 1)
        self._head_send = QLabel('Apply', self, alignment=Qt.AlignCenter)
        lay_lims.addWidget(self._head_send, 0, 2)
        if len(self.pvs_sp) == 1:
            self._head_send.setVisible(False)

        self._spins, self._checks = dict(), dict()
        for lsp in self.lim_sp:
            row += 1
            label = QLabel(lsp.split('-')[0].split('Lmt')[1], self)
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
            if len(self.pvs_sp) == 1:
                check.setChecked(True)
                check.setVisible(False)

        if self.has_reforb:
            row += 1
            self._label_reforb = QLabel(
                '\nChoose Ref.Orb. to calculate reference\n' +
                self.title.lower()+' around which we\napply the values above:')
            lay_lims.addWidget(self._label_reforb, row, 0, 1, 3)

            row += 1
            self._cb_reforb = RefOrbComboBox(self)
            self._cb_reforb.refOrbChanged.connect(self._set_ref_orb)
            lay_lims.addWidget(self._cb_reforb, row, 0, 1, 3)

        # BPM selection
        groupsel = QGroupBox('Select BPMs:')
        self._bpm_sel = _BPMSelectionWidget(
            self, show_toggle_all_true=False,
            toggle_all_false_text='Select All', prefix=self.prefix)
        lay_groupsel = QGridLayout(groupsel)
        lay_groupsel.addWidget(self._bpm_sel)

        # connect signals and slots
        self._bpm_sel.applyChangesClicked.connect(self.send_value)

        lay = QGridLayout(self)
        lay.addWidget(title, 0, 0, 1, 2)
        lay.addWidget(self._wid_lims, 1, 0)
        lay.addWidget(groupsel, 1, 1)

    def _set_ref_orb(self, text):
        if text.lower() == 'zero':
            self._reforb['x'] = _np.zeros(len(self.BPM_NAMES))
            self._reforb['y'] = _np.zeros(len(self.BPM_NAMES))
        else:
            data = self.get_ref_orb(text)
            self._reforb['x'] = _np.array(data['x']) * self.CONV_UM2NM
            self._reforb['y'] = _np.array(data['y']) * self.CONV_UM2NM

    def send_value(self):
        """Send new value."""
        selected = list()
        for idx, wid in enumerate(self._bpm_sel.widgets):
            name = self.BPM_NAMES[idx]
            led = wid.findChild(QLed)
            if led.isSelected():
                selected.append(name)
                led.setSelected(False)
        if not selected:
            return

        for lsp in self.lim_sp:
            if not self._checks[lsp].isChecked():
                continue
            lval = self._spins[lsp].value()
            if self.has_reforb:
                plan = 'x' if 'x' in lsp.lower() else 'y'
                ref = self._reforb[plan]
                metric = self.get_intlk_metric(ref, metric=self.metric)
                value = _np.array(metric) + lval
            else:
                value = _np.ones(len(self.BPM_NAMES)) * lval
            for name in selected:
                idx = self.BPM_NAMES.index(name)
                self.pvs_sp[lsp][name].send_value_signal[int].emit(
                    round(value[idx]))
