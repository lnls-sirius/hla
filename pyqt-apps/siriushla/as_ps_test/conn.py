
from epics import PV as _PV

from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search import MASearch, PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSC


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


class _Tester:
    """Tester base."""

    def __init__(self, device):
        """Init."""
        self.device = device

    @property
    def connected(self):
        """Return wheter PVs are connected."""
        for pv in self._pvs.values():
            if not pv.connected:
                # print(pv.pvname)
                return False
        return True

    def reset(self):
        """Reset."""
        self._pvs['Reset-Cmd'].value = 1

    def check_intlk(self):
        """Check interlocks."""
        status = (self._pvs['IntlkHard-Mon'].value == 0)
        status &= (self._pvs['IntlkSoft-Mon'].value == 0)
        return status

    def set_slowref(self):
        """Set OpMode to SlowRef."""
        self._pvs['OpMode-Sel'].value = _PSC.OpMode.SlowRef

    def check_slowref(self):
        """Check OpMode in SlowRef."""
        return (self._pvs['OpMode-Sts'].value in [_PSC.States.SlowRef,
                                                  _PSC.States.Off,
                                                  _PSC.States.Interlock])

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


class TesterDCLinkFBP(_Tester):
    """FBP DCLink tester."""

    properties = ['Reset-Cmd', 'IntlkSoft-Mon', 'IntlkHard-Mon',
                  'OpMode-Sel', 'OpMode-Sts',
                  'PwrState-Sel', 'PwrState-Sts',
                  'CtrlLoop-Sel', 'CtrlLoop-Sts',
                  'Voltage-SP', 'Voltage-Mon']

    def __init__(self, device):
        """Init."""
        super().__init__(device)
        self._pvs = dict()
        for ppty in TesterDCLinkFBP.properties:
            self._pvs[ppty] = _PV(VACA_PREFIX + device + ':' + ppty,
                                  connection_timeout=TIMEOUT_CONN)
            self._pvs[ppty].get()

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


class TesterDCLink(_Tester):
    """DCLink tester."""

    properties = ['Reset-Cmd', 'IntlkSoft-Mon', 'IntlkHard-Mon',
                  'OpMode-Sel', 'OpMode-Sts',
                  'PwrState-Sel', 'PwrState-Sts',
                  'CtrlLoop-Sel', 'CtrlLoop-Sts',
                  'CapacitorBankVoltage-SP', 'CapacitorBankVoltage-Mon']

    def __init__(self, device):
        """Init."""
        super().__init__(device)
        self._pvs = dict()
        for ppty in TesterDCLink.properties:
            self._pvs[ppty] = _PV(VACA_PREFIX + device + ':' + ppty,
                                  connection_timeout=TIMEOUT_CONN)
            self._pvs[ppty].get()

    def check_init_ok(self):
        """Check OpMode in SlowRef."""
        status = (self._pvs['OpMode-Sts'].value == _PSC.States.SlowRef)
        return status

    def set_ctrlloop(self):
        """Set CtrlLoop."""
        self._pvs['CtrlLoop-Sel'].value = _PSC.OpenLoop.Closed

    def check_ctrlloop(self):
        """Check CtrlLoop."""
        return (self._pvs['CtrlLoop-Sts'].value == _PSC.OpenLoop.Closed)

    def set_capvolt(self):
        """Set capacitor bank voltage."""
        self._pvs['CapacitorBankVoltage-SP'].value = \
            DEFAULT_CAP_BANK_VOLT[self.device]

    def check_capvolt(self):
        """Check capacitor bank voltage."""
        return self._cmp(self._pvs['CapacitorBankVoltage-Mon'].value,
                         DEFAULT_CAP_BANK_VOLT[self.device])

    def _cmp(self, value, target):
        if value >= target:
            return True
        else:
            return False


class TesterPS(_Tester):
    """PS tester."""

    properties = ['Reset-Cmd', 'IntlkSoft-Mon', 'IntlkHard-Mon',
                  'OpMode-Sel', 'OpMode-Sts',
                  'PwrState-Sel', 'PwrState-Sts',
                  'Current-SP', 'Current-Mon']

    def __init__(self, device):
        """Init."""
        super().__init__(device)
        self._pvs = dict()
        for ppty in TesterPS.properties:
            self._pvs[ppty] = _PV(VACA_PREFIX + device + ':' + ppty,
                                  connection_timeout=TIMEOUT_CONN)
            self._pvs[ppty].get()

        maname = MASearch.conv_psname_2_psmaname(device)
        splims = MASearch.conv_maname_2_splims(maname)
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

    def _cmp(self, value, target):
        if abs(value - target) < self.test_tol:
            return True
        else:
            return False


class TesterPSLinac:
    """Linac PS tester."""

    properties = ['interlock',
                  'setpwm', 'rdpwm',
                  'seti', 'rdi']

    def __init__(self, device):
        self.device = device
        self._pvs = dict()
        for ppty in TesterPSLinac.properties:
            self._pvs[ppty] = _PV(VACA_PREFIX + device + ':' + ppty,
                                  connection_timeout=TIMEOUT_CONN)
            self._pvs[ppty].get()

        splims = PSSearch.conv_pstype_2_splims(
            PSSearch.conv_psname_2_pstype(device))
        self.test_current = splims['HIGH']/2.0
        self.test_tol = TEST_TOLERANCE

    @property
    def connected(self):
        """Return wheter PVs are connected."""
        return all([pv.connected for pv in self._pvs.values()])

    def check_intlk(self):
        """Check interlocks."""
        return self._pvs['interlock'].value < 55

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        if state == 'on':
            state = _PSC.PwrStateSel.On
        else:
            state = _PSC.PwrStateSel.Off
        self._pvs['setpwm'].value = state

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        if state == 'on':
            state = _PSC.PwrStateSel.On
        else:
            state = _PSC.PwrStateSel.Off
        return (self._pvs['rdpwm'].value == state)

    def set_current(self, test=False):
        """Set current."""
        if test:
            self._pvs['seti'].value = self.test_current
        else:
            self._pvs['seti'].value = 0

    def check_current(self, test=False):
        """Check current."""
        if test:
            status = self._cmp(self._pvs['rdi'].value, self.test_current)
        else:
            status = self._cmp(self._pvs['rdi'].value, 0)
        return status

    def _cmp(self, value, target):
        if abs(value - target) < self.test_tol:
            return True
        else:
            return False
