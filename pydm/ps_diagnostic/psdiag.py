from epics import PV
import time
import pvnaming
from siriuspy.magnet import magdata
from PyQt5.QtCore import QThread, pyqtSignal


class Test(QThread):

    job_done = pyqtSignal(list, list)

    def __init__(self, magps_list):
        QThread.__init__(self)
        self._magps_list = magps_list
        self.stopped = False
        self._pass_list = []
        self._pane_list = []

    def run(self):
        while not self.stopped:
            self._start_test(self._magps_list)

    def stop(self):
        self.stopped = True
        #self.job_done.emit(self._pass_list, self._pane_list)

    def _start_test(self, magps_list):

        for item in magps_list:
            # Use vaca PVs for now
            pv_name_mon = pvnaming.get_mon_pv_name(item.replace('MA','PS'))
            test_value_dict = magdata.get_magps_setpoint_limits(item)
            pv_mon = PV(pv_name_mon)
            value_mon = pv_mon.value
            test_setpoint = test_value_dict['TSTV']
            low_limit = test_setpoint - (test_value_dict['TSTR'] / 2)
            high_limit = test_setpoint + (test_value_dict['TSTR'] / 2)
            result = [item, test_setpoint, value_mon]
            print(result)
            if value_mon != None:
                if value_mon < low_limit or value_mon > high_limit:
                    self._pane_list.append(result)
                else:
                    self._pass_list.append(result)
        self.job_done.emit(self._pass_list, self._pane_list)
