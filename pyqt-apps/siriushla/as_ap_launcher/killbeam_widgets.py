import time as _time
from epics import PV as _PV

from qtpy.QtCore import Qt, QThread, Signal
from qtpy.QtWidgets import QPushButton, QMessageBox
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX as _vaca_prefix


class RFKillBeamHandler:
    """RF Kill Beam Action Handler."""

    TIMEOUT_WAIT = 3.0  # s
    INCRATE_VALUE = 14  # 50 mV/s
    REFMIN_VALUE = 60  # Minimum Amplitude Reference

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
            'SR-RF-DLLRF-01:mV:AL:REF-RB',
            'SR-RF-DLLRF-01:mV:AL:REF-SP'}
        for pvn in pvnames:
            _pvs[pvn] = _PV(_vaca_prefix+pvn, connection_timeout=0.05)

        RFKillBeamHandler._pvs.update(_pvs)

    def _get_pv(self, pvname):
        """Get PV value."""
        pvo = RFKillBeamHandler._pvs[pvname]
        if pvo.wait_for_connection():
            return pvo.get()
        return None

    def _set_pv(self, pvname, value):
        """Set PV to value."""
        pvo = RFKillBeamHandler._pvs[pvname]
        if pvo.wait_for_connection():
            return pvo.put(value)
        return False

    def _wait_pv(self, pvname, value):
        """Wait for PV to reach value."""
        pvo = RFKillBeamHandler._pvs[pvname]
        _time0 = _time.time()
        while _time.time() - _time0 < RFKillBeamHandler.TIMEOUT_WAIT:
            if pvo.value == value:
                return True
            _time.sleep(0.1)
        return False

    def kill_beam(self):
        """Kill beam."""
        # get initial Amplitude Increase Rate
        AIncRate_init = self._get_pv('SR-RF-DLLRF-01:AMPREF:INCRATE')
        if AIncRate_init is None:
            return [False, 'Could not read RF Amplitude Increase Rate PV\n'
                           '(SR-RF-DLLRF-01:AMPREF:INCRATE)!']

        # get initial Amplitude Reference
        ALRef_init = self._get_pv('SR-RF-DLLRF-01:mV:AL:REF-RB')
        if ALRef_init is None:
            return [False, 'Could not read Amplitude Reference PV\n'
                           '(SR-RF-DLLRF-01:mV:AL:REF-RB)!']

        # set Amplitude Increase Rate to 50 mV/s and wait
        self._set_pv('SR-RF-DLLRF-01:AMPREF:INCRATE:S',
                     RFKillBeamHandler.INCRATE_VALUE)

        if not self._wait_pv('SR-RF-DLLRF-01:AMPREF:INCRATE:S',
                             RFKillBeamHandler.INCRATE_VALUE):
            return [False, 'Could not set RF Amplitude Increase Rate PV\n'
                           '(SR-RF-DLLRF-01:AMPREF:INCRATE:S)!']

        # waiting time
        wait_time = int((ALRef_init - RFKillBeamHandler.REFMIN_VALUE)/50)

        # set Amplitude Reference to 60mV and wait for wait_time seconds
        if not self._set_pv('SR-RF-DLLRF-01:mV:AL:REF-SP',
                            RFKillBeamHandler.REFMIN_VALUE):
            return [False, 'Could not set Amplitude Reference PV\n'
                           '(SR-RF-DLLRF-01:mV:AL:REF-SP)!']
        _time.sleep(wait_time)

        # set Amplitude Reference to initial value
        if not self._set_pv('SR-RF-DLLRF-01:mV:AL:REF-SP', ALRef_init):
            return [False, 'Could not set Amplitude Reference PV\n'
                           '(SR-RF-DLLRF-01:mV:AL:REF-SP)!']
        _time.sleep(wait_time)

        # set Amplitude Increase Rate to initial value
        if not self._set_pv('SR-RF-DLLRF-01:AMPREF:INCRATE:S', AIncRate_init):
            return [False, 'Could not set RF Amplitude Increase Rate PV\n'
                           '(SR-RF-DLLRF-01:AMPREF:INCRATE:S)!']

        return [True, '']


class RFKillBeamButton(QPushButton):
    """Button to kill beam with RF."""

    def __init__(self, parent=None):
        super().__init__(qta.icon('mdi.skull-outline'), '', parent)
        self.initial_icon = self.icon()
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

        self._show_wait_icon()

        thread = RFKillBeamSender(self._rf_handler, self)
        thread.sendMessage.connect(self._show_popup)
        thread.finished.connect(self._show_init_icon)
        thread.start()

    def _show_popup(self, title, message):
        if 'Error' in title:
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    def _show_wait_icon(self):
        self.setEnabled(False)
        self.setIcon(
            qta.icon('fa5s.spinner', animation=qta.Spin(self)))

    def _show_init_icon(self):
        self.setIcon(self.initial_icon)
        self.setEnabled(True)


class RFKillBeamSender(QThread):
    """Thread to send Kill Beam command."""

    sendMessage = Signal(str, str)

    def __init__(self, handler, parent=None):
        """Initialize."""
        super().__init__(parent)
        self._handler = handler

    def run(self):
        """Run."""
        retval = self._handler.kill_beam()
        if not retval[0]:
            self.sendMessage.emit('Error', retval[1])
        else:
            self.sendMessage.emit('Done!', 'Beam was killed!')
