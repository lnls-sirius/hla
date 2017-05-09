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
        self.job_done.emit(self._pass_list, self._pane_list)

    def _start_test(self, magps_list):

        for item in magps_list:
            # Use vaca PVs for now
            pv_name_rb = pvnaming.get_mon_pv_name(item.replace('MA', 'PS'))
            pv_rb = PV(pv_name_rb)
            print(pv_name_rb)
            pv_rb.add_callback(self._read_back_changed)

        for item in magps_list:
            # Use vaca PVs for now
            pv_name_sp = pvnaming.get_sp_pv_name(item.replace('MA','PS'))
            test_value_dict = magdata.get_magps_setpoint_limits(item)
            pv_sp = PV(pv_name_sp)
            pv_sp.put(test_value_dict['TSTV'])

    def finished(self):
        self.job_done.emit(self._pass_list, self._pane_list)


    def _read_back_changed(self, pvname, value, **kws):

        print("************Inside Callback************")
        index_to_cut_str = pvname.find(':')
        index_to_cut_str = pvname.find(':', index_to_cut_str + 1)
        magps = pvname[0:index_to_cut_str]

        test_value_dict = magdata.get_magps_setpoint_limits(magps)
        test_setpoint = test_value_dict['TSTV']
        low_limit = test_setpoint - (test_value_dict['TSTR'] / 2)
        high_limit = test_setpoint + (test_value_dict['TSTR'] / 2)

        result = (magps, test_setpoint, value)

        print(result)

        if value < low_limit or value > high_limit:
            self._pane_list.append(result)
        else:
            self._pass_list.append(result)
