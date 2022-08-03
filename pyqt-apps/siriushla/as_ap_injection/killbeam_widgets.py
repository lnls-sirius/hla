"""RF Kill Beam widgets."""

import qtawesome as qta

from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName
from siriuspy.injctrl.csdev import Const as _Const

from ..widgets import SiriusConnectionSignal as _ConnSignal


class RFKillBeamButton(PyDMPushButton):
    """Button to kill beam with RF."""

    def __init__(self, parent=None, prefix=''):

        self.prefix = prefix
        self._inj_prefix = SiriusPVName(
            'AS-Glob:AP-InjCtrl').substitute(prefix=prefix)

        super().__init__(
            parent=parent,
            init_channel=self._inj_prefix.substitute(propty='RFKillBeam-Cmd'),
            icon=qta.icon('mdi.skull-outline'), label='',
            pressValue=1)
        self.initial_icon = self.icon()

        self.showConfirmDialog = True
        self.confirmMessage = \
            'This action will kill the stored beam.\n' \
            'Are you sure you want to proceed?'

        self.setObjectName('rfkill')
        self.setStyleSheet("""
            #rfkill{
                min-width:30px; max-width:30px;
                min-height:30px; max-height:30px;
                icon-size:25px;}""")

        self._pv_mon = _ConnSignal(
            self._inj_prefix.substitute(propty='RFKillBeam-Mon'))
        self._pv_mon.new_value_signal[int].connect(self._handle_enable_state)

    def _handle_enable_state(self, value):
        if value == _Const.RFKillBeamMon.Idle:
            self.setIcon(self.initial_icon)
            self.setEnabled(True)
        elif value == _Const.RFKillBeamMon.Kill:
            self.setEnabled(False)
            self.setIcon(
                qta.icon('fa5s.spinner', animation=qta.Spin(self)))
        else:
            raise ValueError('strange RFKillBeam-Mon value')
