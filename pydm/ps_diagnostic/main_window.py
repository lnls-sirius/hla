from pydm import Display
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QApplication
from epics import PV
from os import path
from psdiag import Test
from siriuspy.magnet import magdata as _magdata
import datetime

class DiagnosticsMainWindow(Display):

    def __init__(self, parent=None, args=None):

        super(DiagnosticsMainWindow, self).__init__(parent)

        self.ui.sb_time_interval.setValue(3)
        self.ui.sb_time_interval.valueChanged.connect(self._update_time_interval)

        self.print_headers()

        self._time_between_readings = self.ui.sb_time_interval.value()
        self._magps_list = _magdata.get_ps_names()

        self._timer = QTimer(self)
        self._timer.setInterval(1000 * self._time_between_readings)
        self._timer.timeout.connect(self._start_sequence)

        self.test_thread = Test(self._magps_list)
        self.test_thread.job_done.connect(self.update_interface)

    def ui_filename(self):

        return 'main_window.ui'

    def ui_filepath(self):

        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def showEvent(self, event):
        super(Display, self).showEvent(event)
        self._timer.start()

    @pyqtSlot()
    def _update_time_interval(self):

        self._time_between_readings = self.ui.sb_time_interval.value()

    @pyqtSlot()
    def _start_sequence(self):

        self._timer.setInterval(1000 * self._time_between_readings)
        self.test_thread.start()

    @pyqtSlot(list, list)
    def update_interface(self, magps_ok, magps_pane):

        # self.ui.te_current_status.clear()
        self.ui.te_pane_report.clear()
        for item in magps_ok:
            self.add_to_status_report(item)
            self.add_to_historic(item, "OK")
            QApplication.processEvents()
        for item in magps_pane:
            self.add_to_pane_report(item)
            self.add_to_historic(item, "Pane")
            QApplication.processEvents()

    def print_headers(self):
        self.ui.te_current_status.clear()
        self.ui.te_pane_report.clear()
        self.ui.te_historic.clear()

        ok_header ="<table><tr><td align='center' width=150><b>Fonte</b>\
                    </td><td width=100 align='center'><b>Setpoint(A)<b></td> \
                    <td align='center' width=100><b>Readback(A)</b></td></tr></table>"

        pane_header ="<table><tr><td align='center' width=150><b>Fonte</b>\
                    </td><td width=100 align='center'><b>Setpoint(A)<b></td> \
                    <td align='center' width=100><b>Readback(A)</b></td></tr></table>"

        historic_header ="<table><tr><td align='center' width=150><b>Fonte</b></td>\
                            <td width=100 align='center'><b>Setpoint(A)<b></td> \
                            <td align='center' width=100><b>Readback(A)</b></td>\
                            <td align='center' width=100><b>Hora</b></td>\
                            <td align='center' width=100><b>Status</b></td></tr></table>"

        self.ui.te_current_status.append(ok_header)
        self.ui.te_pane_report.append(pane_header)
        self.ui.te_historic.append(historic_header)

    def add_to_status_report(self, item):

        status_report ="<table><tr><td align='center' width=150>" + item[0] + \
                    "</td><td width=100 align='center'>" + str(item[1]) + "</td> \
                    <td align='center' width=100>" + str(item[2]) + "</td></tr></table>"

        self.ui.te_current_status.append(status_report)

    def add_to_pane_report(self, item):

        pane_report ="<table><tr><td align='center' width=150>" + item[0] + \
                    " </td><td width=100 align='center'>" + str(item[1]) + "</td> \
                    <td align='center' width=100>" + str(item[2]) + "</td></tr></table>"

        self.ui.te_pane_report.append(pane_report)

    def add_to_historic(self, item, status):

        time_now = str(datetime.datetime.now().time())
        index_round_sec = time_now.find('.')
        time_now = time_now[0:index_round_sec]

        historic ="<table><tr><td align='center' width=150>" + item[0] + "</td>\
                            <td width=100 align='center'>" + str(item[1]) + "</td> \
                            <td align='center' width=100>" + str(item[2]) + "</td>\
                            <td align='center' width=100>" + time_now + "</td>\
                            <td align='center' width=100><b>" + status + "</b></td></tr></table>"

        self.ui.te_historic.append(historic)


    def __del__(self):
        self.test_thread.stop()
        if not self.test_thread.finished():
            self.test_thread.wait()


intelclass = DiagnosticsMainWindow
