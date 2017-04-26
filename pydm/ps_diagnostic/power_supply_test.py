from epics import PV
from threading import Thread
import time
from pv_naming import PVNaming

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
    def start_test(item):
        #if PowerSupplyTest._validate_item(item) == False:
            #return None, None

        pv_name_sp = PVNaming.get_sp_pv_name(item[0])
        pv_name_rb = PVNaming.get_rb_pv_name(item[0])
        setpoint = item[1]
        PowerSupplyTest._low_limit = item[2]
        PowerSupplyTest._high_limit = item[3]

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

    # validate item format and data types
    @classmethod
    def _validate_item(self, item):
        if len(item) < 4: return False
        if type(item[0]) is not str: return False
        if type(item[1]) is not float: return False
        if type(item[2]) is not float: return False
        if type(item[3]) is not float: return False
        return True
