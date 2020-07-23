import time as _time
from epics import PV as _PV

from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMessageBox
from qtpy.QtCore import Slot
import qtawesome as qta

import pydm
from pydm.widgets.base import PyDMWidget, PyDMWritableWidget
from pydm.widgets.channel import PyDMChannel

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch, HLTimeSearch
from siriuspy.timesys.csdev import Const as TIConst
from siriuspy.pwrsupply.csdev import Const as PSConst

from siriushla.widgets import PyDMLedMultiChannel, PyDMLed, QLed
from siriushla.widgets.led import MultiChannelStatusDialog
from siriushla.widgets.dialog import PSStatusDialog

TIMEOUT_WAIT = 2
TRG_ENBL_VAL = TIConst.DsblEnbl.Enbl
TRG_DSBL_VAL = TIConst.DsblEnbl.Dsbl
PU_ENBL_VAL = PSConst.DsblEnbl.Enbl
PU_DSBL_VAL = PSConst.DsblEnbl.Dsbl
PS_OPM_SLWREF = PSConst.OpMode.SlowRef
PS_STS_SLWREF = PSConst.States.SlowRef
PS_OPM_RMPWFM = PSConst.OpMode.RmpWfm
PS_STS_RMPWFM = PSConst.States.RmpWfm

CHANNELS_2_VALUES_BUTTON = {
    # PU Pulse and PwrState
    'TB-04:PU-InjSept:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TB-04:PU-InjSept:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'BO-01D:PU-InjKckr:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'BO-01D:PU-InjKckr:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'BO-48D:PU-EjeKckr:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'BO-48D:PU-EjeKckr:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-01:PU-EjeSeptF:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-01:PU-EjeSeptF:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-01:PU-EjeSeptG:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-01:PU-EjeSeptG:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptF:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptF:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptG-1:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptG-1:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptG-2:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'TS-04:PU-InjSeptG-2:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'SI-01SA:PU-InjNLKckr:Pulse-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'SI-01SA:PU-InjNLKckr:PwrState-Sel': (PU_DSBL_VAL, PU_ENBL_VAL),
    'SI-01SA:PU-InjDpKckr:Pulse-Sel': (PU_DSBL_VAL, None),
    'SI-01SA:PU-InjDpKckr:PwrState-Sel': (PU_DSBL_VAL, None),
    # BO RF ramp enable
    'BR-RF-DLLRF-01:RmpEnbl-Sel': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    # BO PS trigger
    'BO-Glob:TI-Mags-Fams:State-Sel': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'BO-Glob:TI-Mags-Corrs:State-Sel': (TRG_DSBL_VAL, TRG_ENBL_VAL),
}
CHANNELS_2_VALUES_LED = CHANNELS_2_VALUES_BUTTON.copy()
CHANNELS_2_VALUES_LED.update({
    # PU triggers
    'TB-04:TI-InjSept:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-01:TI-EjeSeptF:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-01:TI-EjeSeptG:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-04:TI-InjSeptF:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-04:TI-InjSeptG-1:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'TS-04:TI-InjSeptG-2:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'SI-01SA:TI-InjNLKckr:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    # BO RF trigger and ramp ready
    'BO-Glob:TI-LLRF-Rmp:State-Sts': (TRG_DSBL_VAL, TRG_ENBL_VAL),
    'BR-RF-DLLRF-01:RmpReady-Mon': (TRG_DSBL_VAL, TRG_ENBL_VAL),
})
# BO PS opmode and current
for psn in PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'}):
    CHANNELS_2_VALUES_LED[psn+':OpMode-Sts'] = (PS_STS_SLWREF, PS_STS_RMPWFM)


class BoRampStandbyHandler:
    """Booster PS Ramp Standby Mode Handler."""

    _pvs = dict()

    def __init__(self):
        """Init."""
        self._psnames = PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})
        self._triggers = HLTimeSearch.get_hl_triggers(
            {'sec': 'BO', 'dev': 'Mags'})
        self._create_pvs()

    def _create_pvs(self):
        """Create PVs."""
        _pvs = dict()
        for psn in self._psnames:
            for propty in ['OpMode-Sel', 'OpMode-Sts', 'Current-SP']:
                pvname = psn+':'+propty
                _pvs[pvname] = _PV(
                    _vaca_prefix+pvname, connection_timeout=0.05)

        for trg in self._triggers:
            pvname = trg+':State-Sts'
            _pvs[pvname] = _PV(_vaca_prefix+pvname, connection_timeout=0.05)

        BoRampStandbyHandler._pvs.update(_pvs)

    def _set_pvs(self, pvnames, value):
        """Set PVs to value."""
        for pvname in pvnames:
            pv = BoRampStandbyHandler._pvs[pvname]
            if pv.wait_for_connection():
                pv.put(value)

    def _wait_pvs(self, pvnames, value):
        """Wait for PVs to reach value."""
        need_check = {pvn: True for pvn in pvnames}

        _time0 = _time.time()
        while any(need_check.values()):
            for pvn, tocheck in need_check.items():
                if not tocheck:
                    continue
                pv = BoRampStandbyHandler._pvs[pvn]
                need_check[pvn] = not pv.value == value
            _time.sleep(0.1)
            if _time.time() - _time0 > TIMEOUT_WAIT:
                break

        prob = [str(_PVName(psn).device_name) for psn,
                val in need_check.items() if val]
        if prob:
            return False, prob
        return True, []

    def turn_off(self):
        # wait for triggers disable
        pvs2wait = [trg+':State-Sts' for trg in self._triggers]
        retval = self._wait_pvs(pvs2wait, TRG_DSBL_VAL)
        if not retval[0]:
            text = 'Check for BO Triggers to be disabled\n'\
                   'timed out without sucess!\nVerify BO Mags Triggers!'
            return [False, text, retval[1]]

        # wait duration of a ramp for PS change opmode
        _time.sleep(0.5)

        # set slowref
        pvs2set = [psn+':OpMode-Sel' for psn in self._psnames]
        self._set_pvs(pvs2set, PS_OPM_SLWREF)

        # wait for PS change opmode
        pvs2wait = [psn+':OpMode-Sts' for psn in self._psnames]
        retval = self._wait_pvs(pvs2wait, PS_STS_SLWREF)
        if not retval[0]:
            text = 'Check for BO PS to be in OpMode SlowRef\n'\
                   'timed out without sucess!\nVerify BO PS!'
            return [False, text, retval[1]]

        # set current to zero
        pvs2set = [psn+':Current-SP' for psn in self._psnames]
        self._set_pvs(pvs2set, 0.0)

        return True, '', []

    def turn_on(self):
        # set rmpwfm
        pvs2set = [psn+':OpMode-Sel' for psn in self._psnames]
        self._set_pvs(pvs2set, PS_OPM_RMPWFM)

        # wait for PS change opmode
        pvs2wait = [psn+':OpMode-Sts' for psn in self._psnames]
        retval = self._wait_pvs(pvs2wait, PS_STS_RMPWFM)
        if not retval[0]:
            text = 'Check for BO PS to be in OpMode RmpWfm\n'\
                   'timed out without sucess!\nVerify BO PS!'
            return [False, text, retval[1]]

        return True, '', []


class InjSysStandbyButton(PyDMWritableWidget, QPushButton):
    """Button to set several PVs to standby state."""

    def __init__(self, parent=None, label='', icon=None, pressValue=1,
                 booster_handler=None):
        if not icon:
            QPushButton.__init__(self, label, parent)
        else:
            QPushButton.__init__(self, icon, label, parent)
        PyDMWritableWidget.__init__(self)
        self._alarm_sensitive_border = False
        self._pressvalue = pressValue
        self._address2values = dict()
        self._address2channel = dict()
        self._address2conn = dict()
        for address, values in CHANNELS_2_VALUES_BUTTON.items():
            self._address2conn[address] = False
            channel = PyDMChannel(
                address=address,
                connection_slot=self.connection_changed,
                value_signal=self.send_value_signal)
            channel.connect()
            self._address2channel[address] = channel
            self._address2values[address] = values[pressValue]
        self.released.connect(self.sendValue)

        self._booster_handler = booster_handler

    def sendValue(self):
        """Send values to PVs."""
        if not self._connected:
            return

        if self._pressvalue == 1:
            retval = self._booster_handler.turn_on()
            if not retval[0]:
                self._show_aux_message_box(retval[1], retval[2])
                return

        for addr, val in self._address2values.items():
            if val is None:
                continue
            plugin = pydm.data_plugins.plugin_for_address(addr)
            conn = plugin.connections[addr]
            conn.put_value(val)

        if self._pressvalue == 0:
            retval = self._booster_handler.turn_off()
            if not retval[0]:
                self._show_aux_message_box(retval[1], retval[2])
                return

    @Slot(bool)
    def connection_changed(self, conn):
        """Handle connections."""
        if not self.sender():   # do nothing when sender is None
            return
        address = self.sender().address
        self._address2conn[address] = conn
        allconn = True
        for conn in self._address2conn.values():
            allconn &= conn
        PyDMWidget.connection_changed(self, allconn)
        self._connected = allconn
        self.update()

    def _show_aux_message_box(self, text, data_list):
        if 'PS' in text:
            dlg = PSStatusDialog(data_list, text, self)
        else:
            dlg = QMessageBox(self)
            dlg.setIcon(QMessageBox.Critical)
            dlg.setWindowTitle('Message')
            dlg.setText(text)
            details = ''
            for item in data_list:
                details += item + '\n'
            dlg.setDetailedText(details)
        dlg.exec_()


class InjSysStandbyEnblDsbl(QWidget):
    """Widget to control injection system standby state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._booster_handler = BoRampStandbyHandler()

        self.pb_off = InjSysStandbyButton(
            parent=self, pressValue=0,
            icon=qta.icon('mdi.power-off'),
            booster_handler=self._booster_handler)
        self.pb_off.setToolTip('Click to Turn Off')
        self.pb_off.setObjectName('pb_off')
        self.pb_off.setStyleSheet("""
            #pb_off{
                min-width:25px; max-width:25px;
                min-height:25px; max-height:25px;
                icon-size:20px;}
            """)
        self.pb_on = InjSysStandbyButton(
            parent=self, pressValue=1,
            icon=qta.icon('mdi.power-on'),
            booster_handler=self._booster_handler)
        self.pb_on.setToolTip('Click to Turn On')
        self.pb_on.setObjectName('pb_on')
        self.pb_on.setStyleSheet("""
            #pb_on{
                min-width:25px; max-width:25px;
                min-height:25px; max-height:25px;
                icon-size:20px;}
            """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        lay.addStretch()
        lay.addWidget(self.pb_off)
        lay.addWidget(self.pb_on)
        lay.addStretch()


class InjSysStandbyStatusLed(PyDMLedMultiChannel):
    """Led to check whether several PVs are in stanby state."""

    def __init__(self, parent=None):
        channels2values = {k.replace('Sel', 'Sts'): v[1]
                           for k, v in CHANNELS_2_VALUES_LED.items()}
        super().__init__(parent, channels2values)
        self.stateColors = [PyDMLed.DarkGreen, PyDMLed.LightGreen,
                            PyDMLed.Yellow, PyDMLed.Gray]

    def _update_statuses(self):
        if not self._connected:
            state = 3
        else:
            status_off = 0
            for status in self._address2status.values():
                if status == 'UNDEF' or not status:
                    status_off += 1
            if status_off == len(self._address2status.values()):
                state = 0
            elif status_off > 0:
                state = 2
            else:
                state = 1
        self.setState(state)

    def mouseDoubleClickEvent(self, ev):
        pvs = set()
        for k, v in self._address2status.items():
            if (not v) or (v == 'UNDEF'):
                pvs.add(k)
        if pvs:
            msg = MultiChannelStatusDialog(
                parent=self, pvs=pvs,
                text="The following PVs have value\n"
                     "equivalent to 'off' status!",
                fun_show_diff=self._show_diff)
            msg.exec_()
        QLed.mouseDoubleClickEvent(self, ev)
