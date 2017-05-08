from epics import PV
import time
import pvnaming
from siriuspy.magnet import magdata

class PowerSupplyTest(object):
    _pass = False     # PS pass in test?
    _elapsed_time = 0
    _time_limit = 5
    _flag_read_back_change = False
    _ps_current = 0   # Current to return
    _pv_object_sp = None
    _pv_object_rb = None
    _low_limit = 0.0   # I can pass this as argument in callback and use a local variable?
    _high_limit = 0.0  # I can pass this as argument in callback and use a local variable?

    @staticmethod
    def start_test(magps_name):
        #if PowerSupplyTest._validate_item(item) == False:
            #return None, None

        pv_name_sp = pvnaming.get_sp_pv_name(magps_name)
        pv_name_rb = pvnaming.get_rb_pv_name(magps_name)

        # Dictionary with all test values for power supply
        test_values_dict = magdata.get_magps_setpoint_limits(magps_name)
        setpoint = test_values_dict['TSTV']
        test_range = test_values_dict['TSTR']

        PowerSupplyTest._low_limit = setpoint - (test_range / 2)
        PowerSupplyTest._high_limit = setpoint + (test_range / 2)

        PowerSupplyTest._pv_object_sp = PV(pv_name_sp)
        PowerSupplyTest._pv_object_rb = PV(pv_name_rb)

        # Add callback for read back pv
        PowerSupplyTest._pv_object_rb.add_callback(PowerSupplyTest._read_back_changed)
        PowerSupplyTest._pv_object_sp.put(setpoint)

        #start timer
        start_time = time.time()
        while PowerSupplyTest._elapsed_time < PowerSupplyTest._time_limit:
            PowerSupplyTest._elapsed_time = time.time() - start_time
            if PowerSupplyTest._flag_read_back_change == True:
                PowerSupplyTest._elapsed_time = 0
                break
        if PowerSupplyTest._flag_read_back_change == False:
            PowerSupplyTest._timer_interrupt(PowerSupplyTest._pv_object_rb)

        return PowerSupplyTest._pass, PowerSupplyTest._ps_current

    @classmethod
    def _timer_interrupt(self, pv):
        print("********Time Overflow********")
        self._elapsed_time = 0
        pv.clear_callbacks()
        if pv.value == None:
            self._ps_current = 0.0
        else:
            self._ps_current = pv.value

    @classmethod
    def _read_back_changed(self, pvname, value, **kws):
        # Remove callback?
        print("********Inside Callback********")
        self._flag_read_back_change = True
        self._ps_current = value
        if value < PowerSupplyTest._low_limit or value > PowerSupplyTest._high_limit:
            self._pass = False
        else:
            self._pass = True


_pass_list = []
_pane_list = []

def start_test(magps_list):
    global _pane_list
    _pane_list = []
    global _pass_list
    _pass_list = []
    
    for item in magps_list:
        pv_name_rb = pvnaming.get_rb_pv_name(item)
        pv_rb = PV(pv_name_rb)
        pv_rb.add_callback(_read_back_changed)

    for item in magps_list:
        pv_name_sp = pvnaming.get_sp_pv_name(item)
        test_value_dict = magdata.get_magps_setpoint_limits(item)
        pv_sp = PV(pv_name_sp)
        pv_sp.put(test_value_dict['TSTV'])


def _read_back_changed(pvname, value, **kws):

    print("************Inside Callback************")
    global _pane_list
    global _pass_list
    magps = pvname[0:-11]
    test_value_dict = magdata.get_magps_setpoint_limits(magps)
    test_setpoint = test_value_dict['TSTV']
    low_limit = test_setpoint - (test_value_dict['TSTR'] / 2)
    high_limit = test_setpoint + (test_value_dict['TSTR'] / 2)
    result = (magps, test_setpoint, value)
    print(result)
    if value < low_limit or value > high_limit:
        _pane_list.append(result)
    else:
        _pass_list.append(result)
