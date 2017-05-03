from epics import PV
from pv_naming import PVNaming
from PyQt5.QtCore import QCoreApplication, QThread
import time

class TestThread(QThread):

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self._pass = False          # PS pass in test?
        self._elapsed_time = 0
        self._time_limit = 5
        self._flag_read_back_change = False
        self._ps_current = 0.0      # Current to return
        self._pv_object_sp = None
        self._pv_object_rb = None
        self._low_limit = 0.0       # I can pass this as argument in callback and use a local variable?
        self._high_limit = 0.0      # I can pass this as argument in callback and use a local variable?
        self._item = None

    # when the thread is destroyed
    def __del__(self):
        self._pv_object_rb.clear_callbacks()

    # use this to setup the atributtes required by the thread before starting it
    def start_test(self, item):
        self._item = item
        self.start()

    def run(self):

        if self._validate_item(item) == False:
            return False, 0.0

        pv_name_sp = PVNaming.get_sp_pv_name(self._item[0])
        pv_name_rb = PVNaming.get_rb_pv_name(self._item[0])
        setpoint = self._item[1]
        self._low_limit = self._item[2]
        self._high_limit = self._item[3]

        self._pv_object_sp = PV(pv_name_sp)
        self._pv_object_rb = PV(pv_name_rb)

        # Add callback for read back pv
        self._pv_object_rb.add_callback(_read_back_changed)
        self._pv_object_sp.put(setpoint)

        #start timer
        start_time = time.time()
        while self._elapsed_time < self._time_limit:
            self._elapsed_time = time.time() - start_time
            if self._flag_read_back_change == True:
                self._elapsed_time = 0
                break
            #QApplication.processEvents()
        if self._flag_read_back_change == False:
            self._timer_interrupt(self._pv_object_rb)

        return self._pass, self._ps_current

    def _timer_interrupt(self, pv):
        print("********Time Overflow********")
        self._elapsed_time = 0
        pv.clear_callbacks()
        self._ps_current = pv.value

    def _read_back_changed(self, pvname, value, **kws):
        # Remove callback?
        print("********Inside Callback********")
        self._flag_read_back_change = True
        self._ps_current = value
        if value < self._low_limit or value > self._high_limit:
            self._pass = False
        else:
            self._pass = True

    def _validate_item(self, item):
        if len(item) < 4: return False
        if type(item[0]) is not str: return False
        if type(item[1]) is not float: return False
        if type(item[2]) is not float: return False
        if type(item[3]) is not float: return False
        return True
