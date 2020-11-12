"""Conn module."""

import time as _time
import numpy as _np
from epics import PV as _PV

from siriuspy.envars import VACA_PREFIX as VACA_PREFIX
from siriuspy.search import PSSearch
from siriuspy.pwrsupply.csdev import Const as _PSC


DEFAULT_CAP_BANK_VOLT = {
    'FBP_DCLink': 100,
    'PA-RaPSE01:PS-DCLink-BO': 240,
    'PA-RaPSE02:PS-DCLink-BO': 240,
    'PA-RaPSE03:PS-DCLink-BO': 240,
    'PA-RaPSE04:PS-DCLink-BO': 240,
    'PA-RaPSE06:PS-DCLink-BO': 240,
    'PA-RaPSE07:PS-DCLink-BO': 240,
    'PA-RaPSE08:PS-DCLink-BO': 240,
    'PA-RaPSE09:PS-DCLink-BO': 240,
    'PA-RaPSF01:PS-DCLink-BO': 240,
    'PA-RaPSF02:PS-DCLink-BO': 240,
    'PA-RaPSF03:PS-DCLink-BO': 240,
    'PA-RaPSF04:PS-DCLink-BO': 240,
    'PA-RaPSF06:PS-DCLink-BO': 240,
    'PA-RaPSF07:PS-DCLink-BO': 240,
    'PA-RaPSF08:PS-DCLink-BO': 240,
    'PA-RaPSF09:PS-DCLink-BO': 240,
    'PA-RaPSC03:PS-DCLink-BO1': 300,
    'PA-RaPSC03:PS-DCLink-BO2': 300,
}


TIMEOUT_CONN = 0.05
TEST_TOLERANCE = 1e-1


class _TesterBase:
    """Tester base."""

    def __init__(self, device):
        """Init."""
        self.device = device
        self._pvs = dict()

    @property
    def connected(self):
        """Return wheter PVs are connected."""
        for pv in self._pvs.values():
            if not pv.connected:
                # print(pv.pvname)
                return False
        return True

    def wait_for_connection(self, timeout=0.5):
        for pv in self._pvs.values():
            if not pv.wait_for_connection(timeout):
                return False
        return True


class _TesterPSBase(_TesterBase):
    """Tester PS base."""

    def reset(self):
        """Reset."""
        self._pvs['Reset-Cmd'].value = 1

    def check_intlk(self):
        """Check interlocks."""
        status = (self._pvs['IntlkHard-Mon'].value == 0)
        status &= (self._pvs['IntlkSoft-Mon'].value == 0)
        return status

    def set_opmode_slowref(self):
        """Set OpMode to SlowRef."""
        self._pvs['OpMode-Sel'].value = _PSC.OpMode.SlowRef

    def check_opmode_slowref(self):
        """Check OpMode in SlowRef."""
        return (self._pvs['OpMode-Sts'].value in [_PSC.States.SlowRef,
                                                  _PSC.States.Off,
                                                  _PSC.States.Interlock])

    def check_opmode_initializing(self):
        """Check OpMode in Initializing."""
        return self._pvs['OpMode-Sts'].value == _PSC.States.Initializing

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        if state == 'on':
            state = _PSC.PwrStateSel.On
        else:
            state = _PSC.PwrStateSel.Off
        self._pvs['PwrState-Sel'].value = state

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        if state == 'on':
            ok = self._pvs['PwrState-Sts'].value == _PSC.PwrStateSts.On
            ok &= self._pvs['OpMode-Sts'].value == _PSC.States.SlowRef
        else:
            ok = self._pvs['PwrState-Sts'].value == _PSC.PwrStateSts.Off
            ok &= self._pvs['OpMode-Sts'].value == _PSC.States.Off
        return ok

    def set_ctrlloop(self):
        """Set CtrlLoop."""
        self._pvs['CtrlLoop-Sel'].value = _PSC.OpenLoop.Closed

    def check_ctrlloop(self):
        """Check CtrlLoop."""
        return self._pvs['CtrlLoop-Sts'].value == _PSC.OpenLoop.Closed


class TesterDCLinkFBP(_TesterPSBase):
    """FBP DCLink tester."""

    properties = ['Reset-Cmd', 'IntlkSoft-Mon', 'IntlkHard-Mon',
                  'OpMode-Sel', 'OpMode-Sts',
                  'PwrState-Sel', 'PwrState-Sts',
                  'CtrlLoop-Sel', 'CtrlLoop-Sts',
                  'Voltage-SP', 'Voltage-Mon']

    def __init__(self, device):
        """Init."""
        super().__init__(device)
        for ppty in TesterDCLinkFBP.properties:
            self._pvs[ppty] = _PV(
                VACA_PREFIX + device + ':' + ppty,
                connection_timeout=TIMEOUT_CONN)

    def check_init_ok(self):
        """Check OpMode in SlowRef."""
        status = (self._pvs['OpMode-Sts'].value == _PSC.States.SlowRef)
        return status

    def set_ctrlloop(self):
        """Set CtrlLoop."""
        self._pvs['CtrlLoop-Sel'].value = _PSC.OpenLoop.Open

    def check_ctrlloop(self):
        """Check CtrlLoop."""
        return (self._pvs['CtrlLoop-Sts'].value == _PSC.OpenLoop.Open)

    def set_capvolt(self):
        """Set capacitor bank voltage."""
        self._pvs['Voltage-SP'].value = \
            DEFAULT_CAP_BANK_VOLT['FBP_DCLink']

    def check_capvolt(self):
        """Do not need to check."""
        return True

    def check_status(self):
        return self.check_intlk()


class TesterDCLink(_TesterPSBase):
    """DCLink tester."""

    properties = ['Reset-Cmd', 'IntlkSoft-Mon', 'IntlkHard-Mon',
                  'OpMode-Sel', 'OpMode-Sts',
                  'PwrState-Sel', 'PwrState-Sts',
                  'CtrlLoop-Sel', 'CtrlLoop-Sts',
                  'CapacitorBankVoltage-SP', 'CapacitorBankVoltageRef-Mon',
                  'CapacitorBankVoltage-Mon']

    def __init__(self, device):
        """Init."""
        super().__init__(device)
        for ppty in TesterDCLink.properties:
            self._pvs[ppty] = _PV(
                VACA_PREFIX + device + ':' + ppty,
                connection_timeout=TIMEOUT_CONN)

    def check_init_ok(self):
        """Check OpMode in SlowRef."""
        status = (self._pvs['OpMode-Sts'].value == _PSC.States.SlowRef)
        return status

    def set_capvolt(self):
        """Set capacitor bank voltage."""
        self._pvs['CapacitorBankVoltage-SP'].value = \
            DEFAULT_CAP_BANK_VOLT[self.device]

    def check_capvolt(self):
        """Check capacitor bank voltage."""
        return self._cmp(self._pvs['CapacitorBankVoltage-Mon'].value,
                         DEFAULT_CAP_BANK_VOLT[self.device])

    def check_status(self):
        status = True
        status &= self.check_intlk()
        if self.check_pwrstate():
            status &= _np.isclose(
                self._pvs['CapacitorBankVoltage-Mon'].value,
                self._pvs['CapacitorBankVoltageRef-Mon'].value,
                atol=1.0)
        return status

    def _cmp(self, value, target):
        return value >= target


class TesterDCLinkRegatron(_TesterBase):
    """DCLink tester."""

    properties = ['Reset-Cmd', 'GenIntlk-Mon', 'GenWarn-Mon', 'OpMode-Sts',
                  'PwrState-Sel', 'PwrState-Sts',
                  'Voltage-SP', 'VoltageRef-Mon', 'Voltage-Mon']

    _OPMODE_STS_OFF = 4  # READY
    _OPMODE_STS_ON = 8  # RUN

    def __init__(self, device):
        """Init."""
        super().__init__(device)
        for ppty in TesterDCLinkRegatron.properties:
            self._pvs[ppty] = _PV(
                VACA_PREFIX + device + ':' + ppty,
                connection_timeout=TIMEOUT_CONN)

    def reset(self):
        """Reset."""
        self._pvs['Reset-Cmd'].value = 1

    def check_intlk(self):
        """Check interlocks."""
        status = (self._pvs['GenIntlk-Mon'].value == 0)
        status &= (self._pvs['GenWarn-Mon'].value == 0)
        return status

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        self._pvs['PwrState-Sel'].value = state

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        if state == 'on':
            ok = self._pvs['PwrState-Sts'].value == _PSC.OffOn.On
            ok &= self._pvs['OpMode-Sts'].value == self._OPMODE_STS_ON
        else:
            ok = self._pvs['PwrState-Sts'].value == _PSC.OffOn.Off
            ok &= self._pvs['OpMode-Sts'].value == self._OPMODE_STS_OFF
        return ok

    def check_init_ok(self):
        """Check OpMode Ok."""
        return self._pvs['OpMode-Sts'].value == self._OPMODE_STS_ON

    def check_capvolt(self):
        """Check voltage."""
        return _np.isclose(self._pvs['Voltage-Mon'].value,
                           self._pvs['VoltageRef-Mon'].value,
                           rtol=0.05)

    def check_status(self):
        status = True
        status &= self.check_intlk()
        if self.check_pwrstate():
            status &= self.check_capvolt()
        return status


class TesterPS(_TesterPSBase):
    """PS tester."""

    properties = ['Reset-Cmd', 'IntlkSoft-Mon', 'IntlkHard-Mon',
                  'OpMode-Sel', 'OpMode-Sts',
                  'PwrState-Sel', 'PwrState-Sts',
                  'CtrlLoop-Sel', 'CtrlLoop-Sts',
                  'Current-SP', 'CurrentRef-Mon', 'Current-Mon']

    def __init__(self, device):
        """Init."""
        super().__init__(device)
        for ppty in self.properties:
            self._pvs[ppty] = _PV(
                VACA_PREFIX + device + ':' + ppty,
                connection_timeout=TIMEOUT_CONN)

        splims = PSSearch.conv_psname_2_splims(device)
        self.test_current = splims['TSTV']
        self.test_tol = splims['TSTR']

    def set_current(self, test=False):
        """Set current."""
        if test:
            self._pvs['Current-SP'].value = self.test_current
        else:
            self._pvs['Current-SP'].value = 0

    def check_current(self, test=False):
        """Check current."""
        if test:
            status = self._cmp(self._pvs['Current-Mon'].value,
                               self.test_current)
        else:
            status = self._cmp(self._pvs['Current-Mon'].value, 0)
        return status

    def check_status(self):
        status = True
        status &= self.check_intlk()
        if self.check_pwrstate():
            status &= self._cmp(
                self._pvs['Current-Mon'].value,
                self._pvs['CurrentRef-Mon'].value)
        return status

    def _cmp(self, value, target):
        return abs(value - target) < self.test_tol


class TesterPSFBP(TesterPS):
    """PS FBP Tester."""

    properties = ['Reset-Cmd', 'IntlkSoft-Mon', 'IntlkHard-Mon',
                  'OpMode-Sel', 'OpMode-Sts',
                  'PwrState-Sel', 'PwrState-Sts',
                  'CtrlLoop-Sel', 'CtrlLoop-Sts',
                  'Current-SP', 'CurrentRef-Mon', 'Current-Mon',
                  'SOFBMode-Sel', 'SOFBMode-Sts']

    def set_sofbmode(self, state='on'):
        """Set SOFBMode."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        self._pvs['SOFBMode-Sel'].value = state

    def check_sofbmode(self, state='on'):
        """Check SOFBMode."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        return (self._pvs['SOFBMode-Sts'].value == state)


class TesterPSLinac(_TesterBase):
    """Linac PS tester."""

    properties = ['StatusIntlk-Mon',
                  'PwrState-Sel', 'PwrState-Sts',
                  'Current-SP', 'Current-Mon']

    def __init__(self, device):
        super().__init__(device)
        for ppty in TesterPSLinac.properties:
            self._pvs[ppty] = _PV(
                VACA_PREFIX + device + ':' + ppty,
                connection_timeout=TIMEOUT_CONN)

        splims = PSSearch.conv_pstype_2_splims(
            PSSearch.conv_psname_2_pstype(device))
        self.test_current = splims['HIGH']/2.0
        self.test_tol = TEST_TOLERANCE

    def check_intlk(self):
        """Check interlocks."""
        return self._pvs['StatusIntlk-Mon'].value < 64

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        if state == 'on':
            state = _PSC.PwrStateSel.On
        else:
            state = _PSC.PwrStateSel.Off
        self._pvs['PwrState-Sel'].value = state

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        if state == 'on':
            state = _PSC.PwrStateSel.On
        else:
            state = _PSC.PwrStateSel.Off
        return (self._pvs['PwrState-Sts'].value == state)

    def set_current(self, test=False):
        """Set current."""
        if test:
            self._pvs['Current-SP'].value = self.test_current
        else:
            self._pvs['Current-SP'].value = 0

    def check_current(self, test=False):
        """Check current."""
        if test:
            status = self._cmp(
                self._pvs['Current-Mon'].value, self.test_current)
        else:
            status = self._cmp(self._pvs['Current-Mon'].value, 0)
        return status

    def check_status(self):
        status = True
        status &= self.check_intlk()
        if self.check_pwrstate():
            status &= self._cmp(
                self._pvs['Current-SP'].value,
                self._pvs['Current-Mon'].value)
        return status

    def _cmp(self, value, target):
        return abs(value - target) < self.test_tol


class _TesterPUBase(_TesterBase):
    """Tester PU base."""

    properties = []

    def __init__(self, device):
        """Init."""
        super().__init__(device)
        for ppty in self.properties:
            self._pvs[ppty] = _PV(
                VACA_PREFIX + device + ':' + ppty,
                connection_timeout=TIMEOUT_CONN)

        splims = PSSearch.conv_psname_2_splims(device)
        self.test_voltage = splims['TSTV']
        self.test_tol = splims['TSTR']

    def reset(self):
        """Reset."""
        self._pvs['Reset-Cmd'].value = 1

    def check_intlk(self):
        """Check interlocks."""
        raise NotImplementedError

    def set_pulse(self, state='on'):
        """Set Pulse."""
        # if pulsed magnet was in interlock state and was reset,
        # we need to send a Pulse-Sel = Off before continue
        if self._pvs['Pulse-Sel'].value == _PSC.OffOn.On \
                and self.check_pulse('off'):
            self._pvs['Pulse-Sel'].value = _PSC.OffOn.Off
            _time.sleep(0.5)

        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        self._pvs['Pulse-Sel'].value = state

    def check_pulse(self, state='on'):
        """Check Pulse."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        return self._pvs['Pulse-Sts'].value == state

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        # if pulsed magnet was in interlock state and was reset,
        # we need to send a PwrState-Sel = Off before continue
        if self._pvs['PwrState-Sel'].value == _PSC.OffOn.On \
                and self.check_pwrstate('off'):
            self._pvs['PwrState-Sel'].value = _PSC.OffOn.Off
            _time.sleep(0.5)

        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        self._pvs['PwrState-Sel'].value = state

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        return self._pvs['PwrState-Sts'].value == state

    def set_voltage(self, test=False):
        """Set voltage."""
        if test:
            self._pvs['Voltage-SP'].value = self.test_voltage
        else:
            self._pvs['Voltage-SP'].value = 0

    def check_voltage(self, test=False):
        """Check voltage."""
        if test:
            status = self._cmp(self._pvs['Voltage-Mon'].value,
                               self.test_voltage)
        else:
            status = self._cmp(self._pvs['Voltage-Mon'].value, 0)
        return status

    def check_status(self):
        status = True
        status &= self.check_intlk()
        if self.check_pwrstate():
            status &= self._cmp(
                self._pvs['Voltage-Mon'].value,
                self._pvs['Voltage-RB'].value)
        return status

    def _cmp(self, value, target):
        return abs(value - target) < self.test_tol


class TesterPUKckr(_TesterPUBase):
    """Kicker tester."""

    properties = [
        'Reset-Cmd',
        'Intlk1-Mon', 'Intlk2-Mon', 'Intlk3-Mon', 'Intlk4-Mon',
        'Intlk5-Mon', 'Intlk6-Mon', 'Intlk7-Mon', 'Intlk8-Mon',
        'PwrState-Sel', 'PwrState-Sts',
        'Pulse-Sel', 'Pulse-Sts',
        'Voltage-SP', 'Voltage-RB', 'Voltage-Mon']

    def check_intlk(self):
        """Check interlocks."""
        status = (self._pvs['Intlk1-Mon'].value == 1)
        status &= (self._pvs['Intlk2-Mon'].value == 1)
        status &= (self._pvs['Intlk3-Mon'].value == 1)
        status &= (self._pvs['Intlk4-Mon'].value == 1)
        status &= (self._pvs['Intlk5-Mon'].value == 1)
        status &= (self._pvs['Intlk6-Mon'].value == 1)
        status &= (self._pvs['Intlk7-Mon'].value == 1)
        status &= (self._pvs['Intlk8-Mon'].value == 1)
        return status


class TesterPUSept(_TesterPUBase):
    """Septum tester."""

    properties = [
        'Reset-Cmd',
        'Intlk1-Mon', 'Intlk2-Mon', 'Intlk3-Mon', 'Intlk4-Mon',
        'Intlk5-Mon', 'Intlk6-Mon', 'Intlk7-Mon',
        'PwrState-Sel', 'PwrState-Sts',
        'Pulse-Sel', 'Pulse-Sts',
        'Voltage-SP', 'Voltage-RB', 'Voltage-Mon']

    def check_intlk(self):
        """Check interlocks."""
        status = (self._pvs['Intlk1-Mon'].value == 1)
        status &= (self._pvs['Intlk2-Mon'].value == 1)
        status &= (self._pvs['Intlk3-Mon'].value == 1)
        status &= (self._pvs['Intlk4-Mon'].value == 1)
        status &= (self._pvs['Intlk5-Mon'].value == 1)
        status &= (self._pvs['Intlk6-Mon'].value == 1)
        status &= (self._pvs['Intlk7-Mon'].value == 1)
        return status
