from pydm import Display
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from epics import PV
from os import path
from power_supply_test import PowerSupplyTest
from pv_naming import PVNaming
from file_parser import FileParser

class DiagnosticsMainWindow(Display):

    def __init__(self, parent=None, args=None):
        super(DiagnosticsMainWindow, self).__init__(parent)
        # Buttons
        self.ui.pb_start.clicked.connect(self.startSequence)
        self.ui.pb_stop.clicked.connect(self.stopSequence)

    def ui_filename(self):
        return 'main_window.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def _ps_list_filename(self):
        return 'ps_names.txt'

    def _ps_list_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self._ps_list_filename())

    @pyqtSlot()
    def startSequence(self):
        bt = self.ui.pb_start
        test_list = self._get_ps_list(self._ps_list_filepath)
        if bt.isChecked() == True:
            bt.setEnabled(False)
            self.ui.te_test_sequence.clear()
            self.ui.te_pane_report.clear()
            self.ui.te_test_sequence.setText('Start Test...\n')
            self.ui.te_pane_report.setText('Pane List:')
            for item in test_list:
                print(item)
                result, current = PowerSupplyTest.start_test(item)
                if result == True:
                    self.ui.te_test_sequence.append(item[0] + ' | ' + str(round(current, 3)) + ' A')
                else:
                    self.ui.te_pane_report.append(item[0] + ' | ' + str(round(current, 3)) + ' A')
                QApplication.processEvents() # Avoid freeze in interface
            bt.setEnabled(True)
            bt.setChecked(False)
        else:
            # TODO: stopSequence()
            pass

    @pyqtSlot()
    def stopSequence(self):
        bt = self.ui.pb_start
        test_list = self._get_ps_list(self._ps_list_filepath)
        if bt.isChecked() == True:
            bt.setEnabled(False)
            self.ui.te_test_sequence.clear()
            self.ui.te_pane_report.clear()
            self.ui.te_test_sequence.setText('Start Test...\n')
            self.ui.te_pane_report.setText('Pane List:')
            for item in test_list:
                print(item)
                result, current = PowerSupplyTest.start_test(item)
                if result == True:
                    self.ui.te_test_sequence.append(item[0] + ' | ' + str(round(current, 3)) + ' A')
                else:
                    self.ui.te_pane_report.append(item[0] + ' | ' + str(round(current, 3)) + ' A')
                QApplication.processEvents() # Avoid freeze in interface
            bt.setEnabled(True)
            bt.setChecked(False)
        else:
            # TODO: stopSequence()
            pass

    # List of all power supplies
    def _get_ps_list(self, file_name):
            # get power supplies list
            parsed_file = FileParser(file_name)
            power_suply_list = parsed_file.getParamsTable()
            return power_suply_list

intelclass = DiagnosticsMainWindow
