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
        self.stop_flag = False

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
        print("Entrou Start Sequence")
        bt = self.ui.pb_start
        test_list = self._get_ps_list(self._ps_list_filepath())
        #print(test_list)
        if bt.isChecked() == True:
            print('Botao Pressionado')
            self.stop_flag = False
            bt.setEnabled(False)
            self.ui.te_test_sequence.clear()
            self.ui.te_pane_report.clear()
            self.ui.te_test_sequence.setText('Start Test...\n')
            self.ui.te_pane_report.setText('Pane List:')
            counter = 0
            list_size = len(test_list)
            while self.stop_flag == False:
                QApplication.processEvents() # Avoid freeze in interface
                item = test_list[counter]
                result, current = PowerSupplyTest.start_test(item)
                print(item)
                result_text = "<table><tr><td align='left' width=150>" + item[0] + \
                '</td><td width=70>' + str(round(current, 3)) + '</td> \
                <td><b>A</b></td></tr></table>'
                if result == True:
                    # self.ui.te_test_sequence.append(item[0] + ' | ' + str(round(current, 3)) + ' A')
                    self.ui.te_test_sequence.append(result_text)
                else:
                    # self.ui.te_pane_report.append(item[0] + ' | ' + str(round(current, 3)) + ' A')
                    self.ui.te_pane_report.append(result_text)
                counter += 1
                if counter == list_size:
                    counter = 0
            bt.setEnabled(True)
            bt.setChecked(False)


    @pyqtSlot()
    def stopSequence(self):
        self.stop_flag = True
        self.ui.te_test_sequence.setText('End Test...\n')

    # List of all power supplies
    def _get_ps_list(self, file_name):
            # get power supplies list
            parsed_file = FileParser(file_name)
            power_suply_list = parsed_file.getParamsTable()
            return power_suply_list

intelclass = DiagnosticsMainWindow
