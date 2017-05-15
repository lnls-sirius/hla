''' Worker thread for power supply test.
    In this class we define three actions:

    1. TEST:    Set reference values for all selected power supplies,
                wait for 3 seconds and read Current:Mon PVs. If the
                read value for each power supply is equal or close
                to the reference (Tolerance defined in a file), the
                power supply is OK, if not, it is in pane.
    2. ON_OFF:  On or Off all selected power supplies.
    3. RESET:   Reset all selected power supplies. When this action is
                realized, all devices returns to default values.
'''

from epics import PV
import time
from siriuspy.magnet import magdata as _magdata
from pvnaming import PVNaming as _pvnaming
from PyQt5.QtCore import pyqtSlot, QTimer, QThread, pyqtSignal

class PowerSupplyTest(QThread):

    test_complete = pyqtSignal(list, list)      # Emit when TEST action is finished
    reset_complete = pyqtSignal()               # Emit when RESET action is finished
    pwr_state_changed = pyqtSignal(int)        # Emit when ON_OFF action is finished

    ''' The constructor receives three arguments.
        1. magps_list:  List of selected power supplies
        2. action:  Action to be executed. Can be TEST, ON_OFF
                    or RESET
        3. power_state: If selected action is ON_OFF, we need to
                        inform the desired state. 0 or 1
    '''
    def __init__(self, magps_list, action = 'TEST', pwr_state = 0):

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


    ''' Test sequence
    '''
    def _teste_magps(self):

        self._set_test_values()
        time.sleep(3)
        self._get_test_result()

    ''' Set reference values for all selected power supplies.
    '''
    def _set_test_values(self):

        for item in self._magps_list:

            # pv_name_sp = _pvnaming.get_sp_pv_name(item)
            pv_name_sp = _pvnaming.get_sp_pv_name(item.replace('MA', 'PS')) # Use VACA pvs for now
            test_values_dict = _magdata.get_magps_setpoint_limits(item)
            pv_sp = PV(pv_name_sp)
            test_value = test_values_dict['TSTV']
            pv_sp.put(test_value)

    ''' Read Current-Mon values for all selected power supplies
        and check if it is in the tolerance range. When finished,
        this method emit a signal with a list of Ok power supplies
        and a list with pane power supplies.
    '''
    def _get_test_result(self):

        for item in self._magps_list:
            # pv_name_sp = _pvnaming.get_sp_pv_name(item)
            pv_name_mon = _pvnaming.get_mon_pv_name(item.replace('MA','PS')) # Use VACA pvs for now
            test_values_dict = _magdata.get_magps_setpoint_limits(item)
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

    ''' Reset all selected power supplies.
        When finsihed emit a signal without data.
    '''
    def _reset_magps(self):

        RESET_VALUE = 0

        for item in self._magps_list:
            # pv_name_reset = _pvnaming.get_reset_pv_name(item)
            pv_name_reset = _pvnaming.get_reset_pv_name(item.replace('MA', 'PS')) # Use VACA pvs for now
            pv_reset = PV(pv_name_reset)
            pv_reset.put(RESET_VALUE)

        self.reset_complete.emit()

    ''' Set power state for all selected power supplies
        Argument:
            state: 0 for Off and 1 for On
        Signal:
            When finished emit 0 if ps are OFF or 1 if ps are On
    '''
    def _set_magps_power_state(self, state):

        if state == 0:
            on_off_state = state
        else:
            on_off_state = 1

        for item in self._magps_list:
            # pv_name = _pvnaming.get_pwr_state_sel_pv(item)
            pv_name_on_off = _pvnaming.get_pwr_state_sel_pv_name(item.replace('MA', 'PS')) # Use VACA pvs for now
            pv_on_off = PV(pv_name_on_off)
            pv_on_off.put(on_off_state)

        self.pwr_state_changed.emit(on_off_state)
