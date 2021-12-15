"""Timing widgets."""

import qtawesome as qta

from pydm.widgets import PyDMPushButton

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName
from siriuspy.search import LLTimeSearch as _LLTimeSearch

from ..widgets import PyDMStateButton, PyDMLed, SiriusLedAlert

EVG_NAME = _LLTimeSearch.get_evg_name()


class EVGContinuousLed(PyDMLed):
    """EVG Continuous Led."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        pref_dev = SiriusPVName(EVG_NAME).substitute(prefix=prefix)
        color_list = 7*[self.LightGreen, ]
        color_list[0] = self.DarkGreen  # Initializing
        color_list[1] = self.DarkGreen  # Stopped
        color_list[4] = self.Yellow  # Preparing Continuous
        color_list[6] = self.Yellow  # Restarting Continuous
        super().__init__(
            parent=parent,
            init_channel=pref_dev.substitute(propty_name='STATEMACHINE'),
            color_list=color_list)


class EVGContinuousButton(PyDMStateButton):
    """EVG Continuous State Button."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        pref_dev = SiriusPVName(EVG_NAME).substitute(prefix=prefix)
        super().__init__(
            parent=parent,
            init_channel=pref_dev.substitute(propty='ContinuousEvt-Sel'))


class EVGInjectionLed(PyDMLed):
    """EVG Injection Led."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        pref_dev = SiriusPVName(EVG_NAME).substitute(prefix=prefix)
        color_list = 7*[self.DarkGreen, ]
        color_list[3] = self.LightGreen  # Injection
        color_list[5] = self.Yellow  # Preparing Injection
        super().__init__(
            parent=parent,
            init_channel=pref_dev.substitute(propty_name='STATEMACHINE'),
            color_list=color_list)


class EVGInjectionButton(PyDMStateButton):
    """EVG Injection State Button."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        pref_dev = SiriusPVName(EVG_NAME).substitute(prefix=prefix)
        super().__init__(
            parent=parent,
            init_channel=pref_dev.substitute(propty='InjectionEvt-Sel'))


class EVGUpdateEvtLed(SiriusLedAlert):
    """EVG Update Events Led."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        pref_dev = SiriusPVName(EVG_NAME).substitute(prefix=prefix)
        super().__init__(
            parent=parent,
            init_channel=pref_dev.substitute(propty='EvtSyncStatus-Mon'))
        self.setOffColor(self.Red)
        self.setOnColor(self.LightGreen)


class EVGUpdateEvtButton(PyDMPushButton):
    """EVG Update Events Button."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        super().__init__(
            parent, label='', icon=qta.icon('fa5s.sync'), pressValue=1)
        pref_dev = SiriusPVName(EVG_NAME).substitute(prefix=prefix)
        self.setToolTip('Update Events Table')
        self.channel = pref_dev.substitute(propty='UpdateEvt-Cmd')
        self.setObjectName('but')
        self.setStyleSheet(
            '#but{min-width:25px; max-width:25px; icon-size:20px;}')
