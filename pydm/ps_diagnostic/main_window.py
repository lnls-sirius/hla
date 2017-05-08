from pydm import Display
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from epics import PV
from os import path
#from pstest import PowerSupplyTest
import pstest
from siriuspy.magnet import magdata
import threading

class DiagnosticsMainWindow(Display):

    def __init__(self, parent=None, args=None):

        super(DiagnosticsMainWindow, self).__init__(parent)

        self.ui.sb_time_interval.setValue(1)
        self.ui.sb_time_interval.valueChanged.connect(self._update_time_interval)

        self._time_between_readings = self.ui.sb_time_interval.value()
        self._magps_list = magdata.get_ps_names()

        self._start_sequence()


    def ui_filename(self):

        return 'main_window.ui'

    def ui_filepath(self):

        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    @pyqtSlot()
    def _update_time_interval(self):

        self._time_between_readings = self.ui.sb_time_interval.value()

    def _start_sequence(self):

        threading.Timer(self._time_between_readings, self._start_sequence).start()
        hist, status, pane = pstest.start_test(self._magps_list)
        self._print_list(hist, self.ui.te_historic)
        self._print_list(status, self.ui.te_current_status)
        self._print_list(pane, self.ui.te_pane_report)

    def _print_list(self, items, text_edit):

        text_edit.clear()
        for item in item:
            text_edit.append(item)


intelclass = DiagnosticsMainWindow
