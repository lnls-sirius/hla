"""Base module."""

from qtpy.QtWidgets import QWidget

import qtawesome as qta

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.fofb.csdev import HLFOFBConst

from ..util import get_appropriate_color
from ..as_ap_sofb.ioc_control.base import BaseObject as _BaseObject, \
    BaseWidget as _BaseWidget


class BaseObject(_BaseObject):
    """Base object."""

    UM2M = 1e-6
    UM2NM = 1e3
    URAD2RAD = 1e-6

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


def get_fofb_icon(color=True):
    """Return default icon."""
    iconcolor = color if isinstance(color, str) else \
        get_appropriate_color('SI') if color else None
    return qta.icon(
        'fa5s.hammer', 'fa5s.signal', options=[
            dict(scale_factor=0.85, offset=(0.15, 0.0)),
            dict(scale_factor=0.7, offset=(0.0, 0.25), rotated=90,
                 vflip=True)], color=iconcolor)
