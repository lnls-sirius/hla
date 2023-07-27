"""Custom widgets for RaBPM monitor."""

import numpy as np

from qtpy.QtCore import Signal

from pydm.widgets.base import PyDMWidget
from pydm.widgets.channel import PyDMChannel

from siriuspy.namesys import SiriusPVName
from siriuspy.devices import FamFOFBControllers as _FamFOFBCtrls

from ..util import connect_newprocess
from ..widgets import PyDMLedMultiChannel, QLed


class _BaseMonLed(PyDMLedMultiChannel):
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
        self.set_channels2values(c2v)
        self.command = command
        connect_newprocess(
            self, [self.command, self.device], parent=self,
            signal=self.doubleClicked)

    def mouseDoubleClickEvent(self, _):
        """Reimplement mouseDoubleClickEvent."""
        self.doubleClicked.emit()


class BPMMonLed(_BaseMonLed):
    """BPM monitor led."""

    def __init__(self, parent=None, device='', prefix=''):
        p2v = {'ADCAD9510PllStatus-Mon': 1}
        super().__init__(
            parent, device=device, propties2values=p2v, prefix=prefix,
            command='sirius-hla-as-di-bpm.py')


class RFFEMonLed(_BaseMonLed):
    """BPM monitor led."""

    def __init__(self, parent=None, device='', prefix=''):
        p2v = {'RFFEasyn.CNCT': 1}
        super().__init__(
            parent, device=device, propties2values=p2v, prefix=prefix,
            command='sirius-hla-as-di-bpm.py')


class PBPMMonLed(_BaseMonLed):
    """Photon BPM monitor led."""

    def __init__(self, parent=None, device='', prefix=''):
        p2v = {'asyn.CNCT': 1}
        super().__init__(
            parent, device=device, propties2values=p2v, prefix=prefix,
            command='sirius-hla-as-di-bpm.py')


class EVRMonLed(_BaseMonLed):
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
            self, ['sirius-hla-si-ap-fofb.py', '--lowleveldetails'], parent=self,
            signal=self.doubleClicked)

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

        self.setOnColor(self.LightGreen)
        self.setOffColor(self.Red)

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
