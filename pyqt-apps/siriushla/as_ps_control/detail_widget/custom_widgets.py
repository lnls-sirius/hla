"""Custom widget."""

from qtpy.QtCore import Signal

from pydm.widgets.base import PyDMWidget

from siriuspy.util import get_bit
from siriuspy.envars import VACA_PREFIX
from siriuspy.pwrsupply.csdev import ETypes as _PSe, \
    PS_LI_INTLK_THRS as _PS_LI_INTLK

from siriushla.widgets import QLed, PyDMLed, SiriusConnectionSignal


class LISpectIntlkLed(QLed, PyDMWidget):
    """Led to check LI Spect interlock status."""

    filterlog = Signal(str)
    warning = Signal(list)
    normal = Signal(list)

    def __init__(self, parent=None, filters=None):
        """Call super and set on/off colors."""
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self)
        self.onColor = PyDMLed.Red
        self.offColor = PyDMLed.LightGreen

        self.prefix = VACA_PREFIX
        self.devname = 'LI-01:PS-Spect'
        self.filter = filters

        self.intlkstatus_ch = SiriusConnectionSignal(
            self.prefix+self.devname+':StatusIntlk-Mon')
        self.intlkstatus_ch.connection_slot = self.connectionStateChanged
        self.intlkwarn_ch = SiriusConnectionSignal(
            self.prefix+self.devname+':IntlkWarn-Mon')
        self.intlkwarn_ch.connection_slot = self.connectionStateChanged
        self.channel = self.intlkstatus_ch.address

        self.intlkwarn_bit = _PSe.LINAC_INTLCK_WARN.index('LoadI Over Thrs')

        self.intlkstatus_val = None
        self.intlkwarn_val = None
        self.intlkstatus_conn = None
        self.intlkwarn_conn = None

        self.intlkstatus_ch.new_value_signal[int].connect(
            self._update_values)
        self.intlkwarn_ch.new_value_signal[int].connect(
            self._update_values)

    def _update_values(self, new_val):
        if 'StatusIntlk' in self.sender().address:
            self.intlkstatus_val = new_val
        else:
            self.intlkwarn_val = new_val
        self.value_changed()

    def value_changed(self, new_value=None):
        if self.intlkstatus_val is None or self.intlkwarn_val is None:
            return
        intlkval = self.intlkstatus_val
        if get_bit(int(self.intlkwarn_val), self.intlkwarn_bit):
            value = self.intlkstatus_val - 2**self.intlkwarn_bit
        else:
            value = self.intlkstatus_val
        is_desired = value < _PS_LI_INTLK
        if not is_desired:
            self.warning.emit([self.intlkstatus_ch.address, intlkval])
        else:
            self.normal.emit([self.intlkstatus_ch.address, intlkval])
        self.setState(not is_desired)

    def mouseDoubleClickEvent(self, ev):
        self.filterlog.emit(self.filter)
