import time as _time
from epics import PV as _PV

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton, QMessageBox
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX as _vaca_prefix


class RFKillBeamHandler:
    """RF Kill Beam Action Handler."""

    TIMEOUT_WAIT = 0.5
    TIMEOUT_ACT = 1.0

    _pvs = dict()

    def __init__(self):
        """Init."""
        self._create_pvs()

    def _create_pvs(self):
        """Create PVs."""
        _pvs = dict()

        pvnames = {
            'SR-RF-DLLRF-01:AMPREF:INCRATE',
            'SR-RF-DLLRF-01:AMPREF:INCRATE:S',
            'SR-RF-DLLRF-01:mV:AL:REF',
            'SR-RF-DLLRF-01:mV:AL:REF:S'}
        for pvn in pvnames:
            _pvs[pvn] = _PV(_vaca_prefix+pvn, connection_timeout=0.05)

        RFKillBeamHandler._pvs.update(_pvs)

    def _get_pv(self, pvname):
        """Get PV value."""
        pv = RFKillBeamHandler._pvs[pvname]
        if pv.wait_for_connection():
            return pv.get()
        return None

    def _set_pv(self, pvname, value):
        """Set PV to value."""
        pv = RFKillBeamHandler._pvs[pvname]
        if pv.wait_for_connection():
            return pv.put(value)
        return False

    def kill_beam(self):
        """Kill beam."""
        # get initial Amplitude Increase Rate
        AIncRate_init = self._get_pv('SR-RF-DLLRF-01:AMPREF:INCRATE')
        if AIncRate_init is None:
            return [False, 'Could not read RF Amplitude Increase Rate PV\n'
                           '(SR-RF-DLLRF-01:AMPREF:INCRATE)!']

        # get initial Amplitude Reference
        ALRef_init = self._get_pv('SR-RF-DLLRF-01:mV:AL:REF')
        if ALRef_init is None:
            return [False, 'Could not read Amplitude Reference PV\n'
                           '(SR-RF-DLLRF-01:mV:AL:REF)!']

        # set Amplitude Increase Rate to Immediately
        if not self._set_pv('SR-RF-DLLRF-01:AMPREF:INCRATE:S', 7):
            return [False, 'Could not set RF Amplitude Increase Rate PV\n'
                           '(SR-RF-DLLRF-01:AMPREF:INCRATE:S)!']
        _time.sleep(RFKillBeamHandler.TIMEOUT_WAIT)

        # set Amplitude Reference to 60mV and wait for 0.2 seconds
        if not self._set_pv('SR-RF-DLLRF-01:mV:AL:REF:S', 60):
            return [False, 'Could not set Amplitude Reference PV\n'
                           '(SR-RF-DLLRF-01:mV:AL:REF:S)!']
        _time.sleep(RFKillBeamHandler.TIMEOUT_ACT)

        # set Amplitude Reference to initial value
        if not self._set_pv('SR-RF-DLLRF-01:mV:AL:REF:S', ALRef_init):
            return [False, 'Could not set Amplitude Reference PV\n'
                           '(SR-RF-DLLRF-01:mV:AL:REF:S)!']
        _time.sleep(RFKillBeamHandler.TIMEOUT_WAIT)

        # set Amplitude Increase Rate to initial value
        if not self._set_pv('SR-RF-DLLRF-01:AMPREF:INCRATE:S', AIncRate_init):
            return [False, 'Could not set RF Amplitude Increase Rate PV\n'
                           '(SR-RF-DLLRF-01:AMPREF:INCRATE:S)!']

        return [True, '']


class RFKillBeamButton(QPushButton):
    """Button to kill beam with RF."""

    def __init__(self, parent=None):
        super().__init__(qta.icon('mdi.skull-outline'), '', parent)
        self.setObjectName('rfkill')
        self.setStyleSheet("""
            #rfkill{
                min-width:30px; max-width:30px;
                min-height:30px; max-height:30px;
                icon-size:25px;}""")
        self.released.connect(self.kill_beam)

        self._rf_handler = RFKillBeamHandler()

    def kill_beam(self):
        """Kill beam using RF."""
        dlg = QMessageBox(self)
        dlg.setIcon(QMessageBox.Warning)
        dlg.setWindowTitle('Are you sure?')
        dlg.setText('This action will kill the stored beam.\n'
                    'Are you sure you want to proceed?')
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setDefaultButton(QMessageBox.No)
        dlg.setEscapeButton(QMessageBox.No)
        dlg.buttons()[0].setFocusPolicy(Qt.ClickFocus)
        dlg.buttons()[1].setFocusPolicy(Qt.ClickFocus)
        ans = dlg.exec_()
        if ans == QMessageBox.No:
            return

        retval = self._rf_handler.kill_beam()
        if not retval[0]:
            QMessageBox.critical(self, 'Error', retval[1])
            return
        else:
            QMessageBox.information(self, 'Done!', 'Beam was killed!')
