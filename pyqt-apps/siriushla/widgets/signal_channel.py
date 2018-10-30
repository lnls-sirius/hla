#!/usr/bin/env python-sirius

import numpy as _np
from pydm.widgets.channel import PyDMChannel
from qtpy.QtCore import Signal, Slot, QObject


class SiriusConnectionSignal(QObject, PyDMChannel):
    send_value_signal = Signal(
        [int], [float], [str], [bool], [_np.ndarray], [list])
    new_value_signal = Signal(
        [int], [float], [str], [bool], [_np.ndarray], [list])
    connection_state_signal = Signal(bool)
    write_access_signal = Signal(bool)
    enum_strings_signal = Signal(tuple)
    unit_signal = Signal(str)
    prec_signal = Signal(int)
    new_severity_signal = Signal(int)
    upper_ctrl_limit_signal = Signal([float], [int])
    lower_ctrl_limit_signal = Signal([float], [int])

    def __init__(self, address):
        QObject.__init__(self)
        PyDMChannel.__init__(self, address)

        self.connection_slot = self._connection_slot
        self.value_slot = self._value_slot
        self.severity_slot = self._severity_slot
        self.write_access_slot = self._write_access_slot
        self.enum_strings_slot = self._enum_strings_slot
        self.unit_slot = self._unit_slot
        self.prec_slot = self._prec_slot
        self.upper_ctrl_limit_slot = self._upper_ctrl_limit_slot
        self.lower_ctrl_limit_slot = self._lower_ctrl_limit_slot
        self.value_signal = self.send_value_signal

        self.channeltype = None
        self._value = None
        self.connected = None
        self.connect()

    def getvalue(self):
        if self.connected and self._value is not None:
            return self._value.copy()

    value = property(fget=getvalue)

    @Slot(bool)
    def _connection_slot(self, connection):
        self.connected = connection
        self.connection_state_signal.emit(connection)

    @Slot(int)
    @Slot(str)
    @Slot(float)
    @Slot(list)
    @Slot(_np.ndarray)
    def _value_slot(self, value):
        self.channeltype = type(value)
        self._value = value
        self.new_value_signal[self.channeltype].emit(value)

    @Slot(int)
    def _severity_slot(self, severity):
        self.new_severity_signal.emit(severity)

    @Slot(bool)
    def _write_access_slot(self, write_access):
        self.write_access_signal.emit(write_access)

    @Slot(tuple)
    def _enum_strings_slot(self, enum_strings):
        self.enum_strings_signal.emit(enum_strings)

    @Slot(str)
    def _unit_slot(self, unit):
        self.unit_signal.emit(unit)

    @Slot(int)
    def _prec_slot(self, prec):
        self.prec_signal.emit(prec)

    @Slot(int)
    @Slot(float)
    def _upper_ctrl_limit_slot(self, upper_ctrl_limit):
        self.upper_ctrl_limit_signal.emit(upper_ctrl_limit)

    @Slot(int)
    @Slot(float)
    def _lower_ctrl_limit_slot(self, lower_ctrl_limit):
        self.lower_ctrl_limit_signal.emit(lower_ctrl_limit)
