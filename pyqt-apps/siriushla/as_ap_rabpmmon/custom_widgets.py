"""Custom widgets for RaBPM monitor."""

import numpy as np

from qtpy.QtCore import Signal

from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel

from siriuspy.namesys import SiriusPVName
from siriuspy.devices import FamFOFBControllers as _FamFOFBCtrls

from ..util import connect_newprocess
from ..widgets import PyDMLedMultiChannel, QLed, PyDMLedMultiConnection


def get_base_class(led_class):
    """Generate base class for MonLed.

    Args:
        led_class (PyDMLed class):
            led class for base, can be PyDMLedMultiChannel or
            PyDMLedMultiConnection.

    Returns:
        _BaseMonLed: base class for MonLed.
    """
    class _BaseMonLed(led_class):
        """Base monitor led."""

        doubleClicked = Signal()

        def __init__(
                self, parent=None, device='', propties2values=None, prefix='',
                command=None):
            super().__init__(parent)
            self.device = SiriusPVName(device).device_name
            self.setToolTip(device)
            c2v = {
                self.device.substitute(propty=p, prefix=prefix): v
                for p, v in propties2values.items()}
            if led_class == PyDMLedMultiChannel:
                self.set_channels2values(c2v)
            elif led_class == PyDMLedMultiConnection:
                self.set_channels(list(c2v.keys()))
            else:
                raise ValueError(
                    f'base class not defined for class {led_class}'
                )
            self.command = command
            connect_newprocess(
                self, [self.command, self.device], parent=self,
                signal=self.doubleClicked)

        def mouseDoubleClickEvent(self, _):
            """Reimplement mouseDoubleClickEvent."""
            self.doubleClicked.emit()

    return _BaseMonLed

_BaseMonLedMultiChan = get_base_class(PyDMLedMultiChannel)
_BaseMonLedMultiConn = get_base_class(PyDMLedMultiConnection)



class BPMMonLed(_BaseMonLedMultiChan):
    """BPM monitor led."""

    def __init__(self, parent=None, device='', prefix=''):
        p2v = {'ADCAD9510PllStatus-Mon': 1}
        super().__init__(
            parent, device=device, propties2values=p2v, prefix=prefix,
            command='sirius-hla-as-di-bpm.py')


class RFFEMonLed(_BaseMonLedMultiChan):
    """BPM monitor led."""

    def __init__(self, parent=None, device='', prefix=''):
        p2v = {'RFFEasyn.CNCT': 1}
        super().__init__(
            parent, device=device, propties2values=p2v, prefix=prefix,
            command='sirius-hla-as-di-bpm.py')


class PBPMMonLed(_BaseMonLedMultiConn):
    """Photon BPM monitor led."""

    def __init__(self, parent=None, device='', prefix=''):
        p2v = {'PosX-Mon': 'connected'}
        super().__init__(
            parent, device=device, propties2values=p2v, prefix=prefix,
            command='sirius-hla-as-di-bpm.py')


class EVRMonLed(_BaseMonLedMultiChan):
    """BPM monitor led."""

    def __init__(self, parent=None, device='', prefix=''):
        p2v = {'RefClkLocked-Mon': 1}
        super().__init__(
            parent, device=device, propties2values=p2v, prefix=prefix,
            command='sirius-hla-as-ti-afc.py')


class FOFBCtrlMonLed(QLed, PyDMWidget):
    """FOFBCtrl device monitor led."""

    doubleClicked = Signal()

    FOFBCTRL_BPMID = np.array(
        [_FamFOFBCtrls.FOFBCTRL_BPMID_OFFSET - 1 + i for i in range(1, 21)])
    FOFBCTRL_UPLINK = np.roll(FOFBCTRL_BPMID, 1)
    FOFBCTRL_DWLINK = np.roll(FOFBCTRL_BPMID, -1)
    PROPTIES = (
        'DCCFMCLinkPartnerCH0-Mon',
        'DCCFMCLinkPartnerCH1-Mon',
        'DCCFMCLinkPartnerCH2-Mon',
        'DCCFMCLinkPartnerCH3-Mon',
    )

    def __init__(self, parent=None, device='', prefix=''):
        QLed.__init__(self, parent)
        PyDMWidget.__init__(self)

        self.device = SiriusPVName(device)
        self.setToolTip(device)
        connect_newprocess(
            self, ['sirius-hla-si-ap-fofb.py', '--lowleveldetails'],
            parent=self, signal=self.doubleClicked)

        idx = int(self.device.sub[:2]) - 1
        self._values = set([
            FOFBCtrlMonLed.FOFBCTRL_UPLINK[idx],
            FOFBCtrlMonLed.FOFBCTRL_DWLINK[idx]])
        self._status = False

        self._address2channel = dict()
        self._address2conn = dict()
        self._address2currvals = dict()
        for propty in FOFBCtrlMonLed.PROPTIES:
            address = self.device.substitute(propty=propty, prefix=prefix)
            self._address2conn[address] = False
            self._address2currvals[address] = 'UNDEF'
            channel = PyDMChannel(
                address=address,
                connection_slot=self.connection_changed,
                value_slot=self.value_changed)
            channel.connect()
            self._address2channel[address] = channel

        self._channels = list(self._address2channel.values())

        self.stateColors = [self.Red, self.LightGreen, self.Gray]

    def value_changed(self, new_val):
        """Receive new value and set led color accordingly."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        self._address2currvals[address] = new_val

        linked = set(self._address2currvals.values())
        self._status = len(linked & self._values) == len(self._values)
        self._update_statuses()

    def connection_changed(self, connected):
        """Reimplement connection_changed to handle all channels."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        self._address2conn[address] = connected

        PyDMWidget.connection_changed(self, all(self._address2conn.values()))
        self._update_statuses()

    def _update_statuses(self):
        state = 2 if not self._connected else 1 if self._status else 0
        self.setState(state)

    def mouseDoubleClickEvent(self, _):
        """Reimplement mouseDoubleClickEvent."""
        self.doubleClicked.emit()
