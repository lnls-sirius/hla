"""Base module."""

from qtpy.QtWidgets import QWidget

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.fofb.csdev import HLFOFBConst

from ..as_ap_sofb.ioc_control.base import BaseObject as _BaseObject, \
    BaseWidget as _BaseWidget


class BaseObject(_BaseObject):
    """Base object."""

    def __init__(self, device, prefix=''):
        """Init."""
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self._csorb = HLFOFBConst()

    @property
    def acc(self):
        """Accelerator."""
        return 'SI'

    @property
    def acc_idx(self):
        """Accelerator index."""
        return 0

    @property
    def isring(self):
        """Whether accelerator is a ring."""
        return True


class BaseWidget(_BaseWidget, BaseObject):
    """Base widget."""

    def __init__(self, parent, device, prefix=''):
        """Init."""
        BaseObject.__init__(self, device, prefix)
        QWidget.__init__(self, parent)
        self.setObjectName('SIApp')
