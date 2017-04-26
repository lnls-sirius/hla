from pydm import Display
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QFileDialog, QApplication
from epics import PV
from os import path
#from test_sequence import TestSequence
from power_supply_test import PowerSupplyTest
from pv_naming import PVNaming
from file_parser import FileParser

class ControlMainWindow(Display):
    # Accelerator sections
    __STORAGE_RING = 'SI'
    __BOOSTER = 'BO'
    __LINAC = 'LI'
    __TRANSPORT_LINE_SI = 'TS'
    __TRANSPORT_LINE_BO = 'TB'

    # Power supply groups
    __FAMILY = 'Fam'
    __TRIM = 'Trim'

    # Power supply types
    __QUADRUPOLE = '-Q'
    __SEXTUPOLE = '-S'
    __DIPOLE = '-B'

    def __init__(self, parent=None, args=None):
        super(ControlMainWindow, self).__init__(parent)

        # Checkbox
        self.ui.cb_select_all_si.stateChanged.connect(lambda: self.selectAll(self.ui.cb_select_all_si))
        self.ui.cb_select_all_bo.stateChanged.connect(lambda: self.selectAll(self.ui.cb_select_all_bo))
        self.ui.cb_select_all_linac.stateChanged.connect(lambda: self.selectAll(self.ui.cb_select_all_linac))
        self.ui.cb_select_all_ts.stateChanged.connect(lambda: self.selectAll(self.ui.cb_select_all_ts))
        self.ui.cb_select_all_tb.stateChanged.connect(lambda: self.selectAll(self.ui.cb_select_all_tb))

        # Button
        self.ui.pb_on_off.clicked.connect(self.treatOnOffButton)
        self.ui.pb_test_sequence.clicked.connect(self.testSequence)
        self.ui.pb_reset.clicked.connect(self.reset)
        self.ui.pb_export.clicked.connect(self.exportPaneReport)
        self.ui.pb_browse.clicked.connect(self.browseFile)

        # Power supplies list (All power supplies)
        self.__power_supply_list = self.__get_ps_list(self.__ps_list_filepath())

        # Set of power supplies to be tested
        #self.__test_set = set()

    def ui_filename(self):
        return 'main_window_2.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def __ps_list_filename(self):
        return 'ps_names.txt'

    def __ps_list_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.__ps_list_filename())

    @pyqtSlot()
    def reset(self):
        VALUE = 0
        reset_list = list(self.__get_test_list())
        self.ui.te_test_sequence.clear()
        self.ui.te_test_sequence.setText('Start Reset...\n')
        for item in reset_list:
            pv_name = PVNaming.get_reset_pv_name(item[0])
            pv_object = PV(pv_name)
            pv_object.value = VALUE
            self.ui.te_test_sequence.append(item[0] + '\n')
            QApplication.processEvents()
        self.ui.te_test_sequence.append('Finished...')

    @pyqtSlot()
    def testSequence(self):
        bt = self.ui.pb_test_sequence
        test_list = list(self.__get_test_list())
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
    def treatOnOffButton(self):
        OFF = 0
        ON = 1
        on_off_list = list(self.__get_test_list())
        bt = self.ui.pb_on_off
        if bt.isChecked() == True:
            bt.setText('OFF')
            self.ui.te_test_sequence.clear()
            self.ui.te_test_sequence.setText('Power On...\n')
            for item in on_off_list:
                pv_name = PVNaming.get_pwr_state_sel_pv_name(item[0])
                pv_object = PV(pv_name)
                pv_object.value = ON
                self.ui.te_test_sequence.append(item[0] + '\n')
                QApplication.processEvents()
        else:
            bt.setText('ON')
            self.ui.te_test_sequence.clear()
            self.ui.te_test_sequence.setText('Power Off...\n')
            for item in on_off_list:
                pv_name = PVNaming.get_pwr_state_sel_pv_name(item[0])
                pv_object = PV(pv_name)
                pv_object.value = OFF
                self.ui.te_test_sequence.append(item[0] + '\n')
                QApplication.processEvents()
        self.ui.te_test_sequence.append('Finished...' + '\n')

    @pyqtSlot()
    def browseFile(self):
        # TODO: Open File Chooser
        pass

    @pyqtSlot()
    def exportPaneReport(self):
        text = self.ui.te_pane_report.toPlainText()
        name = QFileDialog.getSaveFileName(self, 'pane_report.txt')
        file_object = open(name, 'w')
        file_object.write(text)
        file_object.close()

    @pyqtSlot()
    def selectAll(self, cb):

        if cb.text() == 'Storage Ring':
            if cb.isChecked() == True:
                self.ui.cb_quadrupole_si.setChecked(True)
                self.ui.cb_sextupole_si.setChecked(True)
                self.ui.cb_dipole_si.setChecked(True)
            else:
                self.ui.cb_quadrupole_si.setChecked(False)
                self.ui.cb_sextupole_si.setChecked(False)
                self.ui.cb_dipole_si.setChecked(False)

        if cb.text() == 'Booster':
            if cb.isChecked() == True:
                self.ui.cb_quadrupole_bo.setChecked(True)
                self.ui.cb_sextupole_bo.setChecked(True)
                self.ui.cb_dipole_bo.setChecked(True)
            else:
                self.ui.cb_quadrupole_bo.setChecked(False)
                self.ui.cb_sextupole_bo.setChecked(False)
                self.ui.cb_dipole_bo.setChecked(False)

        if cb.text() == 'LINAC':
            if cb.isChecked() == True:
                self.ui.cb_quadrupole_linac.setChecked(True)
                self.ui.cb_sextupole_linac.setChecked(True)
                self.ui.cb_dipole_linac.setChecked(True)
            else:
                self.ui.cb_quadrupole_linac.setChecked(False)
                self.ui.cb_sextupole_linac.setChecked(False)
                self.ui.cb_dipole_linac.setChecked(False)

        if cb.text() == 'TB':
            if cb.isChecked() == True:
                self.ui.cb_quadrupole_tb.setChecked(True)
                self.ui.cb_sextupole_tb.setChecked(True)
                self.ui.cb_dipole_tb.setChecked(True)
            else:
                self.ui.cb_quadrupole_tp.setChecked(False)
                self.ui.cb_sextupole_tp.setChecked(False)
                self.ui.cb_dipole_tp.setChecked(False)

        if cb.text() == 'TS':
            if cb.isChecked() == True:
                self.ui.cb_quadrupole_ts.setChecked(True)
                self.ui.cb_sextupole_ts.setChecked(True)
                self.ui.cb_dipole_ts.setChecked(True)
            else:
                self.ui.cb_quadrupole_ts.setChecked(False)
                self.ui.cb_sextupole_ts.setChecked(False)
                self.ui.cb_dipole_ts.setChecked(False)

    # List of all power supplies
    def __get_ps_list(self, file_name):
            # get power supplies list
            parsed_file = FileParser(file_name)
            power_suply_list = parsed_file.getParamsTable()
            return power_suply_list

    # Set of power supplies to be tested
    def __get_test_list(self):
        test_set = set()
        if self.ui.cb_quadrupole_si.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__STORAGE_RING, self.__FAMILY, self.__QUADRUPOLE)
        if self.ui.cb_sextupole_si.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__STORAGE_RING, self.__FAMILY, self.__SEXTUPOLE)
        if self.ui.cb_dipole_si.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__STORAGE_RING, self.__FAMILY, self.__DIPOLE)
        if self.ui.cb_quadrupole_bo.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__BOOSTER, self.__FAMILY, self.__QUADRUPOLE)
        if self.ui.cb_sextupole_bo.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__BOOSTER, self.__FAMILY, self.__SEXTUPOLE)
        if self.ui.cb_dipole_bo.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__BOOSTER, self.__FAMILY, self.__DIPOLE)
        if self.ui.cb_quadrupole_linac.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__LINAC, self.__FAMILY, self.__QUADRUPOLE)
        if self.ui.cb_sextupole_linac.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__LINAC, self.__FAMILY, self.__SEXTUPOLE)
        if self.ui.cb_dipole_linac.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__LINAC, self.__FAMILY, self.__DIPOLE)
        if self.ui.cb_quadrupole_ts.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__TRANSPORT_LINE_SI, self.__FAMILY, self.__QUADRUPOLE)
        if self.ui.cb_sextupole_ts.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__TRANSPORT_LINE_SI, self.__FAMILY, self.__SEXTUPOLE)
        if self.ui.cb_dipole_ts.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__TRANSPORT_LINE_SI, self.__FAMILY, self.__DIPOLE)
        if self.ui.cb_quadrupole_tb.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__TRANSPORT_LINE_BO, self.__FAMILY, self.__QUADRUPOLE)
        if self.ui.cb_sextupole_tb.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__TRANSPORT_LINE_BO, self.__FAMILY, self.__SEXTUPOLE)
        if self.ui.cb_dipole_tb.isChecked() == True:
            test_set = test_set | self.__search_ps(self.__TRANSPORT_LINE_BO, self.__FAMILY, self.__DIPOLE)
        return test_set

    # search selected power supplies
    def __search_ps(self, accel_section, ps_group, ps_type):
        ps_set = set()
        if ps_group == self.__FAMILY:
            for item in self.__power_supply_list:
                if accel_section in item[0] and ps_group in item[0] and ps_type in item[0]:
                    ps_set.add(tuple(item))
        else:
            for item in self.__power_supply_list:
                if accel_section in item[0] and self.__FAMILY not in item[0] and ps_type in item[0]:
                    ps_set.add(tuple(item))

        return ps_set


intelclass = ControlMainWindow
