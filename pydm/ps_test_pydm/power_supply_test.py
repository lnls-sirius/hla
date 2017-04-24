from epics import PV
from threading import Thread
import time
from pv_naming import PVNaming

class PowerSupplyTest(object):
    __pass = False     # PS pass in test?
    __elapsed_time = 0
    __time_limit = 5
    __flag_read_back_change = False
    __ps_current = 0   # Current to return
    __pv_object_sp = None
    __pv_object_rb = None

    @staticmethod
    def start_test(item):
        #if PowerSupplyTest.__validate_item(item) == False:
            #return None, None

        pv_name_sp = PVNaming.get_sp_pv_name(item[0])
        pv_name_rb = PVNaming.get_rb_pv_name(item[0])
        setpoint = item[1]
        low_limit = item[2]
        high_limit = item[3]

        PowerSupplyTest.__pv_object_sp = PV(pv_name_sp)
        PowerSupplyTest.__pv_object_rb = PV(pv_name_rb)

        # Add callback for read back pv
        PowerSupplyTest.__pv_object_rb.add_callback(lambda: PowerSupplyTest.__read_back_changed(low_limit, high_limit))
        PowerSupplyTest.__pv_object_sp.put(setpoint)

        #start timer
        start_time = time.time()
        while PowerSupplyTest.__elapsed_time < PowerSupplyTest.__time_limit:
            PowerSupplyTest.__elapsed_time = time.time() - start_time
            if PowerSupplyTest.__flag_read_back_change == True:
                PowerSupplyTest.__elapsed_time = 0
                break
        if PowerSupplyTest.__flag_read_back_change == False:
            PowerSupplyTest.__timer_interrupt(PowerSupplyTest.__pv_object_rb)

        return PowerSupplyTest.__pass, PowerSupplyTest.__ps_current

    @classmethod
    def __timer_interrupt(self, pv):
        self.__elapsed_time = 0
        # pv.remove_callback()
        self.__ps_current = pv.value

    @classmethod
    def __read_back_changed(self, pvname, value, low, high, **kwargs):
        # Remove callback?
        self.__flag_read_back_change = True
        self.__ps_current = value
        if value < low or value > high:
            self.__pass = False
        else:
            self.__pass = True

    # validate item format and data types
    @classmethod
    def __validate_item(self, item):
        if len(item) < 4: return False
        if type(item[0]) is not str: return False
        if type(item[1]) is not float: return False
        if type(item[2]) is not float: return False
        if type(item[3]) is not float: return False
        return True
