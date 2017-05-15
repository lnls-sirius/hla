from epics import PV
import time
import pvnaming
from siriuspy.magnet import magdata
from PyQt5.QtCore import pyqtSlot, QTimer, QThread, pyqtSignal

class PowerSupplyTest(QThread):

    test_complete = pyqtSignal(list, list)
    reset_complete = pyqtSignal()
    pwr_state_changed = pyqtSignal(bool)

    def __init__(self, magps_list, action = 'TEST', pwr_state = 'ON'):
        QThread.__init__(self)
        self._magps_list = magps_list
        self._action = action
        self._pwr_state = pwr_state
        self._pass_list = []
        self._pane_list = []

    def run(self):

        if self._action == 'TEST':
            self._teste_magps()
        elif self._action == 'ON_OFF':
            self._set_magps_power_state(self._pwr_state)
        elif self._action == 'RESET':
            self._reset_magps()


    def _teste_magps(self):

        self._set_test_values()
        time.sleep(3)
        self._get_test_result()

    def _set_test_values(self):

        for item in self._magps_list:

            # pv_name_sp = pvnaming.get_sp_pv_name(item)
            pv_name_sp = pvnaming.get_sp_pv_name(item.replace('MA', 'PS')) # Use VACA pvs for now
            test_values_dict = magdata.get_magps_setpoint_limits(item)
            pv_sp = PV(pv_name_sp)
            test_value = test_values_dict['TSTV']
            pv_sp.put(test_value)

    def _get_test_result(self):

        for item in self._magps_list:
            # pv_name_sp = pvnaming.get_sp_pv_name(item)
            pv_name_mon = pvnaming.get_mon_pv_name(item.replace('MA','PS')) # Use VACA pvs for now
            test_values_dict = magdata.get_magps_setpoint_limits(item)
            pv_mon = PV(pv_name_mon)
            value_mon = pv_mon.value
            test_value = test_values_dict['TSTV']
            low_limit = test_value - (test_values_dict['TSTR'] / 2)
            high_limit = test_value + (test_values_dict['TSTR'] / 2)
            result = [item, test_value, value_mon]

            print(result)

            if value_mon == None:
                self._pane_list.append(result)
            elif value_mon < low_limit or value_mon > high_limit:
                self._pane_list.append(result)
            else:
                self._pass_list.append(result)

        self.test_complete.emit(self._pass_list, self._pane_list)

    def _reset_magps(self):

        RESET_VALUE = 0

        for item in self._magps_list:
            # pv_name_reset = pvnaming.get_reset_pv_name(item)
            pv_name_reset = pvnaming.get_reset_pv_name(item.replace('MA', 'PS')) # Use VACA pvs for now
            pv_reset = PV(pv_name_reset)
            pv_reset.put(RESET_VALUE)

        self.reset_complete.emit()

    def _set_magps_power_state(self, state):

        if state == 0:
            on_off_state = state
        else:
            on_off_state = 1

        for item in self._magps_list:
            # pv_name = pvnaming.get_pwr_state_sel_pv(item)
            pv_name_on_off = pvnaming.get_pwr_state_sel_pv_name(item.replace('MA', 'PS')) # Use VACA pvs for now
            pv_on_off = PV(pv_name_on_off)
            pv_on_off.put(on_off_state)

        if on_off_state == 0:
            self.pwr_state_changed.emit(False)
        else:
            self.pwr_state_changed.emit(True)
