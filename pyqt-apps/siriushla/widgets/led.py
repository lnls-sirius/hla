"""Led widgets."""

from qtpy.QtWidgets import QListWidget, QVBoxLayout, QLabel, QPushButton, \
    QGridLayout, QCheckBox
from qtpy.QtCore import Qt
from copy import deepcopy as _dcopy
import logging as _log
import numpy as _np
from qtpy.QtGui import QColor
from qtpy.QtCore import Property, Slot, Signal
from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel
from .waveformplot import SiriusWaveformPlot
from .windows import SiriusDialog
from .QLed import QLed


class PyDMLed(QLed, PyDMWidget):
    """
    A QLed with support for Channels and more from PyDM.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the led.
    init_channel : str, optional
        The channel to be used by the widget.
    bit : int
        Bit of the PV value to be handled.
    color_list : int
        List of QColor objects for each state the channel can assume.
    """

    default_colorlist = [
        QLed.DarkGreen, QLed.LightGreen, QLed.Yellow, QLed.Red]

    def __init__(self, parent=None, init_channel=None, bit=-1,
                 color_list=None):
        """Init."""
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.pvbit = bit
        self.stateColors = color_list or self.default_colorlist

    @Property(int)
    def pvbit(self):
        """PV bit to be handled by the led."""
        return self._bit

    @pvbit.setter
    def pvbit(self, bit):
        if bit >= 0:
            self._bit = int(bit)
            self._mask = 1 << bit
        else:
            self._bit = -1
            self._mask = None

    def value_changed(self, new_val):
        """
        Receive new value and set led color accordingly.

        For int or float data type the standard led behaviour is to be red when
        the value is 0, and green otherwise.

        If a :attr:`bit` is set the value received will be treated as an int
        and the bit value is extracted using a mask. The led represents the
        value of the chosen bit.
        """
        PyDMWidget.value_changed(self, new_val)
        if new_val is None:
            return
        if isinstance(new_val, _np.ndarray):
            _log.warning('PyDMLed received a numpy array to ' +
                         self.channel+' ('+str(new_val)+')!')
            return
        value = int(new_val)
        if self._bit < 0:  # Led represents value of PV
            self.setState(value)
        else:  # Led represents specific bit of PV
            bit_val = (value & self._mask) >> self._bit
            self.setState(bit_val)


class SiriusLedState(PyDMLed):
    """PyDMLed specialization to represent 2 states in dark/light green."""

    def __init__(self, parent=None, init_channel=None, bit=-1):
        """Call super and set on/off colors."""
        super().__init__(parent, init_channel, bit)
        self.setOffColor(PyDMLed.DarkGreen)
        self.setOnColor(PyDMLed.LightGreen)

    def value_changed(self, new_val):
        """Reimplement value_changed to filter bug."""
        if isinstance(new_val, _np.ndarray):
            _log.warning('SiriusLedState received a numpy array to ' +
                         self.channel+' ('+str(new_val)+')!')
            return
        super().value_changed(new_val)


class SiriusLedAlert(PyDMLed):
    """PyDMLed specialization to represent 2 states in red/light green."""

    def __init__(self, parent=None, init_channel=None, bit=-1):
        """Call super and set on/off colors."""
        super().__init__(parent, init_channel, bit)
        self.setOnColor(PyDMLed.Red)
        self.setOffColor(PyDMLed.LightGreen)

    def value_changed(self, new_val):
        """If no bit is set, treat new_val as 2 states, zero and non-zero."""
        if isinstance(new_val, _np.ndarray):
            _log.warning('SiriusLedAlert received a numpy array to ' +
                         self.channel+' ('+str(new_val)+')!')
            return
        value = int(new_val != 0) if self._bit < 0 else new_val
        super().value_changed(value)


class PyDMLedMultiChannel(QLed, PyDMWidget):
    """
    A QLed with support for checking values of several Channels.

    The led state notify if a set of PVs is in a desired state or not.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the led.
    channels2values: dict
        A dict with channels as keys and desired PVs values as values.
        Values can be either a scalar, to simple comparision, or a dict.
        This dict can have as keys:
            - 'value' (the value to use in comparision);
            - 'comp' (a string that select the type of comparision, can be
                      'eq', 'ne', 'gt', 'lt', 'ge', 'le');
            - and 'bit' (select a bit of the pv to compare to 'value').
    """

    warning = Signal(list)
    normal = Signal(list)

    default_colorlist = [PyDMLed.Red, PyDMLed.LightGreen, PyDMLed.Gray]

    def __init__(self, parent=None, channels2values=dict(), color_list=None):
        """Init."""
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.stateColors = _dcopy(color_list) or self.default_colorlist
        self._connected = False

        self._operations_dict = {'eq': self._eq,
                                 'cl': self._cl,
                                 'ne': self._ne,
                                 'gt': self._gt,
                                 'lt': self._lt,
                                 'ge': self._ge,
                                 'le': self._le,
                                 'in': self._in,
                                 'wt': self._wt,
                                 'ou': self._ou}

        self._address2values = dict()
        self._address2channel = dict()
        self._address2conn = dict()
        self._address2status = dict()
        self._address2currvals = dict()
        self.set_channels2values(_dcopy(channels2values))

    @property
    def channels2values(self):
        """Return channels2values dict."""
        return _dcopy(self._address2values)

    @property
    def channels2status(self):
        """Return channels2status dict."""
        return _dcopy(self._address2status)

    def set_channels2values(self, new_channels2values):
        """Set channels2values."""
        self._address2values = _dcopy(new_channels2values)

        if not new_channels2values:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

        # Check which channel can be removed
        address2pop = list()
        for address in self._address2channel.keys():
            if address not in new_channels2values.keys():
                address2pop.append(address)

        # Remove channels
        for address in address2pop:
            self._address2channel[address].disconnect()
            self._address2channel.pop(address)
            self._address2status.pop(address)
            self._address2conn.pop(address)
            self._address2currvals.pop(address)

        # Add new channels
        for address, value in new_channels2values.items():
            if address not in self._address2channel.keys():
                self._address2conn[address] = False
                self._address2status[address] = 'UNDEF'
                self._address2currvals[address] = 'UNDEF'
                channel = PyDMChannel(
                    address=address,
                    connection_slot=self.connection_changed,
                    value_slot=self.value_changed)
                channel.connect()
                self._address2channel[address] = channel
            self._address2values[address] = value

        self._channels = list(self._address2channel.values())

        # redo comparisions
        for ad, des in self._address2values.items():
            self._address2status[ad] = self._check_status(
                ad, des, self._address2currvals[ad])

        self._update_statuses()

    def value_changed(self, new_val):
        """Receive new value and set led color accordingly."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        desired = self._address2values[address]
        self._address2currvals[address] = new_val

        is_desired = self._check_status(address, desired, new_val)
        self._address2status[address] = is_desired
        if not is_desired:
            self.warning.emit([address, new_val])
        else:
            self.normal.emit([address, new_val])
        self._update_statuses()

    def _check_status(self, address, desired, current):
        if current is None:
            return False
        elif isinstance(current, str) and current == 'UNDEF':
            return False

        kws = dict()
        if isinstance(desired, dict):
            if 'bit' in desired.keys():
                bit = desired['bit']
                mask = 1 << bit
                current = (current & mask) >> bit
            if 'comp' in desired.keys():
                fun = self._operations_dict[desired['comp']]
            else:
                fun = self._operations_dict['eq']
            if 'abs_tol' in desired.keys():
                kws['abs_tol'] = desired['abs_tol']
            if 'rel_tol' in desired.keys():
                kws['rel_tol'] = desired['rel_tol']
            desired_value = desired['value']
        else:
            fun = self._operations_dict['eq']
            desired_value = desired
        if fun != self._wt and (desired_value is not None) and \
                (type(current) != type(desired_value)) and \
                isinstance(current, _np.ndarray):
            _log.warning('PyDMLedMultiChannel received a numpy array to ' +
                         address+' ('+str(current)+')!')
            return

        if desired_value is None:
            is_desired = True
        else:
            is_desired = fun(current, desired_value, **kws)
        return is_desired

    def _update_statuses(self):
        state = 1
        if not self._connected:
            state = 2
        else:
            for status in self._address2status.values():
                if status == 'UNDEF' or not status:
                    state = 0
                    break
        self.setState(state)

    @Slot(bool)
    def connection_changed(self, conn):
        """Reimplement connection_changed to handle all channels."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        self._address2conn[address] = conn
        allconn = True
        for conn in self._address2conn.values():
            allconn &= conn
        PyDMWidget.connection_changed(self, allconn)
        self._connected = allconn
        self._update_statuses()

    @staticmethod
    def _eq(val1, val2, **kws):
        return not PyDMLedMultiChannel._ne(val1, val2, **kws)

    @staticmethod
    def _cl(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        if val1.dtype != val2.dtype or val1.size != val2.size:
            return False
        atol = kws.get('abs_tol', 1e-8)
        rtol = kws.get('rel_tol', 1e-5)
        return _np.allclose(val1, val2, atol=atol, rtol=rtol)

    @staticmethod
    def _ne(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 != val2)

    @staticmethod
    def _gt(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 > val2)

    @staticmethod
    def _lt(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 < val2)

    @staticmethod
    def _ge(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 >= val2)

    @staticmethod
    def _le(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 <= val2)

    @staticmethod
    def _in(val1, val2, **kws):
        return val1 in val2

    @staticmethod
    def _wt(val1, val2, **kws):
        return val2[0] < val1 < val2[1]

    @staticmethod
    def _ou(val1, val2, **kws):
        """Whether val1 is out of range (val2[0], val2[1])."""
        return val1 < val2[0] or val1 > val2[1]

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
                'There are PVs with values different\n'
                'from the desired ones!')

        if pv_groups:
            msg = MultiChannelStatusDialog(
                parent=self, pvs=pv_groups,
                text=texts, fun_show_diff=self._show_diff)
            msg.exec_()
        super().mouseDoubleClickEvent(ev)

    def _show_diff(self, address):
        des_val = self._address2values[address]
        if isinstance(self._address2values[address], dict):
            des_val = des_val['value']
        curr_val = self._address2currvals[address]
        dialog = _DiffStatus(self, des_val, curr_val)
        dialog.exec_()


class PyDMLedTwoChannel(QLed, PyDMWidget):
    """
    A QLed with support for comparing values of two Channels.

    The led state notify if the two PV values are not equal.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the led.
    channels: list
        A list with channels to be compared.
    """

    default_colorlist = [PyDMLed.Red, PyDMLed.LightGreen]

    def __init__(
        self,
        channel1,
        channel2,
        parent=None,
        operation='eq',
        color_list=None
    ):
        """Init."""
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.stateColors = _dcopy(color_list) or self.default_colorlist
        self._connected = False

        _operations_dict = {
            'eq': self._eq,
            'cl': self._cl,
            'ne': self._ne,
            'gt': self._gt,
            'lt': self._lt,
            'ge': self._ge,
            'le': self._le,
            'in': self._in,
            'wt': self._wt,
            'ou': self._ou
        }
        self._operation = _operations_dict[operation]

        self._addresses = {channel1, channel2}
        self._address2channel = {add: None for add in self._addresses}
        self._address2conn = {add: False for add in self._addresses}
        self._address2values = {add: 'UNDEF' for add in self._addresses}
        self.set_channels2values(self._addresses)

    @property
    def channels2values(self):
        """Return channels2values dict."""
        return _dcopy(self._address2values)

    def set_channels2values(self, new_channels):
        """Set channels2values."""
        if not new_channels:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

        # Check which channel can be removed
        address2pop = list()
        for address in self._address2channel:
            if address not in new_channels:
                address2pop.append(address)

        # Remove channels
        for address in address2pop:
            self._address2channel[address].disconnect()
            self._address2channel.pop(address)
            self._address2conn.pop(address)

        # Add new channels
        for address in new_channels:
            if address not in self._address2channel.keys():
                self._address2conn[address] = False
                channel = PyDMChannel(
                    address=address,
                    connection_slot=self.connection_changed,
                    value_slot=self.value_changed
                )
                channel.connect()
                self._address2channel[address] = channel

        self._channels = list(self._address2channel.values())

    def value_changed(self, new_val):
        """Receive new value and set led color accordingly."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        other = (self._addresses - {address}).pop()
        other_val = self._address2values[other]
        self._address2values[address] = new_val

        self.setState(self._check_status(other_val, new_val))

    def _check_status(self, other_val, new_val):
        if new_val is None:
            return False
        elif isinstance(other_val, str) and other_val == 'UNDEF':
            return False

        return self._operation(new_val, other_val)

    @Slot(bool)
    def connection_changed(self, conn):
        """Reimplement connection_changed to handle all channels."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        self._address2conn[address] = conn
        allconn = True
        for conn in self._address2conn.values():
            allconn &= conn
        PyDMWidget.connection_changed(self, allconn)
        self._connected = allconn

    @staticmethod
    def _eq(val1, val2, **kws):
        return not PyDMLedMultiChannel._ne(val1, val2, **kws)

    @staticmethod
    def _cl(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        if val1.dtype != val2.dtype or val1.size != val2.size:
            return False
        atol = kws.get('abs_tol', 1e-8)
        rtol = kws.get('rel_tol', 1e-5)
        return _np.allclose(val1, val2, atol=atol, rtol=rtol)

    @staticmethod
    def _ne(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 != val2)

    @staticmethod
    def _gt(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 > val2)

    @staticmethod
    def _lt(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 < val2)

    @staticmethod
    def _ge(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 >= val2)

    @staticmethod
    def _le(val1, val2, **kws):
        val1 = _np.asarray(val1)
        val2 = _np.asarray(val2)
        return _np.all(val1 <= val2)

    @staticmethod
    def _in(val1, val2, **kws):
        return val1 in val2

    @staticmethod
    def _wt(val1, val2, **kws):
        return val2[0] < val1 < val2[1]

    @staticmethod
    def _ou(val1, val2, **kws):
        """Whether val1 is out of range (val2[0], val2[1])."""
        return val1 < val2[0] or val1 > val2[1]


class PyDMLedMultiConnection(QLed, PyDMWidget):
    """
    A QLed with support for checking connection of several Channels.

    The led state notify if a set of PVs is connected.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the led.
    channels: list
        A list of channels.
    """

    warning = Signal(list)
    normal = Signal(list)

    default_colorlist = [PyDMLed.Red, PyDMLed.LightGreen]

    def __init__(self, parent=None, channels=list(), color_list=None):
        """Init."""
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.stateColors = color_list or self.default_colorlist

        self._address2conn = dict()
        self._address2channel = dict()
        self.set_channels(channels)

    @property
    def channels2conn(self):
        """Return dict with connection state of each channel."""
        return _dcopy(self._address2conn)

    def set_channels(self, new_channels):
        if not new_channels:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

        # Check which channel can be removed
        address2pop = list()
        for address in self._address2channel.keys():
            if address not in new_channels:
                address2pop.append(address)
            else:
                new_channels.remove(address)

        # Remove channels
        for address in address2pop:
            self._address2channel[address].disconnect()
            self._address2channel.pop(address)
            self._address2conn.pop(address)

        # Add new channels
        for address in new_channels:
            self._address2conn[address] = False
            channel = PyDMChannel(
                address=address, connection_slot=self.connection_changed)
            channel.connect()
            self._address2channel[address] = channel

        self._channels = list(self._address2channel.values())

        self._update_state()

    @Slot(bool)
    def connection_changed(self, conn):
        """Reimplement connection_changed to handle all channels."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        if not conn:
            self.warning.emit([address, conn])
        else:
            self.normal.emit([address, conn])
        self._address2conn[address] = conn
        self._update_state()

    def _update_state(self):
        allconn = True
        for conn in self._address2conn.values():
            allconn &= conn
        self.setState(allconn)
        self._connected = allconn

    def mouseDoubleClickEvent(self, ev):
        pvs = set()
        for k, v in self._address2conn.items():
            if not v:
                pvs.add(k)
        if pvs:
            msg = MultiChannelStatusDialog(
                parent=self, pvs=pvs,
                text='There are disconnected PVs!')
            msg.exec_()
        super().mouseDoubleClickEvent(ev)


class MultiChannelStatusDialog(SiriusDialog):

    def __init__(self, parent=None, text='', pvs=set(), fun_show_diff=None):
        super().__init__(parent)
        self.setWindowTitle('Channels Status')
        self._fun_show_diff = fun_show_diff
        if isinstance(pvs, set):
            pvs = [pvs, ]
            text = [text, ]

        lay = QVBoxLayout(self)
        for pvg, txt in zip(pvs, text):
            label = QLabel(txt, self)
            pv_list = _PVList(pvg, self)
            if fun_show_diff:
                pv_list.clicked_item_data.connect(fun_show_diff)
            lay.addWidget(label)
            lay.addWidget(pv_list)

        self._ok_bt = QPushButton('Ok', self)
        self._ok_bt.clicked.connect(self.close)
        lay.addWidget(self._ok_bt)


class _PVList(QListWidget):
    """PV List."""

    clicked_item_data = Signal(str)

    def __init__(self, pvs=set(), parent=None):
        """Constructor."""
        super().__init__(parent)
        self.addItems(pvs)
        self.doubleClicked.connect(self.emit_item_data)

    def emit_item_data(self, index):
        self.clicked_item_data.emit(index.data())


class _DiffStatus(SiriusDialog):

    def __init__(self, parent=None, desired=None, current=None):
        super().__init__(parent)
        self.setWindowTitle('Diff Status')
        self._desired = desired
        self._current = current
        self._setupUi()

    def _setupUi(self):
        self._text = 'It is all ok!'
        self._plot = None
        if isinstance(self._desired, type(self._current)):
            if isinstance(self._desired, (_np.ndarray, tuple, list)):
                if len(self._desired) != len(self._current):
                    self._text = \
                        'Implemented and desired values have different\n'\
                        'lenghts: {} and {}, respectively!'.format(
                            len(self._current), len(self._desired))
                else:
                    self._text = 'Difference: '
                    self._plot = SiriusWaveformPlot()
                    self._plot.addChannel(y_channel='DES', color='blue')
                    self._plot.addChannel(y_channel='CURR', color='black')
                    self._plot.addChannel(y_channel='DIFF', color='magenta')
                    self._plot.autoRangeX = True
                    self._plot.autoRangeY = True
                    self._plot.setLabel('left', '')
                    self._plot.setBackgroundColor(QColor(255, 255, 255))
                    self._desired_curve = self._plot.curveAtIndex(0)
                    self._desired_curve.receiveYWaveform(self._desired)
                    self._desired_curve.redrawCurve()
                    self._current_curve = self._plot.curveAtIndex(1)
                    self._current_curve.receiveYWaveform(self._current)
                    self._current_curve.redrawCurve()
                    self._diff_curve = self._plot.curveAtIndex(2)
                    diff = self._current-self._desired
                    self._diff_curve.receiveYWaveform(diff)
                    self._diff_curve.redrawCurve()
            elif isinstance(self._desired, (int, float, str)):
                self._text = 'Implemented: {}\nDesired: {}'.format(
                    self._current, self._desired)
        elif self._current == 'UNDEF':
            self._text = 'PV is disconnected!'
        elif isinstance(self._desired, (tuple, list)):
            self._text = 'Implemented value ({}) is not within\n' \
                         'desired interval ({})!'.format(
                             self._current, self._desired)
        else:
            self._text = 'Implemented value (of type {}) has type\n' \
                         'different from desired ({})!'.format(
                             type(self._current), type(self._desired))

        lay = QGridLayout(self)
        self._label = QLabel(self._text, self, alignment=Qt.AlignCenter)
        self._label.setStyleSheet("min-width: 20em;")
        lay.addWidget(self._label, 0, 0, 1, 3)
        if self._plot:
            lay.addWidget(self._plot, 1, 0, 1, 3)
            self.show_des = QCheckBox('Desired')
            self.show_des.setChecked(True)
            self.show_des.setStyleSheet('color: blue;')
            self.show_des.stateChanged.connect(self._desired_curve.setVisible)
            lay.addWidget(self.show_des, 2, 0)
            self.show_cur = QCheckBox('Implemented')
            self.show_cur.setChecked(True)
            self.show_cur.setStyleSheet('color: black;')
            self.show_cur.stateChanged.connect(self._current_curve.setVisible)
            lay.addWidget(self.show_cur, 2, 1)
            self.show_dif = QCheckBox('Diff')
            self.show_dif.setChecked(True)
            self.show_dif.setStyleSheet('color: magenta;')
            self.show_dif.stateChanged.connect(self._diff_curve.setVisible)
            lay.addWidget(self.show_dif, 2, 2)
        self._ok_bt = QPushButton('Ok', self)
        self._ok_bt.clicked.connect(self.close)
        lay.addWidget(self._ok_bt, 3, 1)
