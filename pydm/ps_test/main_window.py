from pydm import Display
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from epics import PV
from os import path
from pstest import PowerSupplyTest
from siriuspy.magnet import magdata as _magdata

class ControlMainWindow(Display):
    # Accelerator sections
    _STORAGE_RING = 'SI'
    _BOOSTER = 'BO'
    _LINAC = 'LI'
    _TRANSPORT_LINE_SI = 'TS'
    _TRANSPORT_LINE_BO = 'TB'

    # Power supply groups
    _FAMILY = 'Fam'
    _TRIM = 'Trim'

    # Power supply types
    _QUADRUPOLE = '-Q'
    _SEXTUPOLE = '-S'
    _DIPOLE = '-B'

    # Actions for Test test_thread
    _TEST = 'TEST'
    _ON_OFF = 'ON_OFF'
    _RESET = 'RESET'

    def __init__(self, parent=None, args=None):
        super(ControlMainWindow, self).__init__(parent)

        # Checkbox
        self.ui.cb_select_all_si.stateChanged.connect(lambda: self._select_all(self.ui.cb_select_all_si))
        self.ui.cb_select_all_bo.stateChanged.connect(lambda: self._select_all(self.ui.cb_select_all_bo))
        self.ui.cb_select_all_linac.stateChanged.connect(lambda: self._select_all(self.ui.cb_select_all_linac))
        self.ui.cb_select_all_ts.stateChanged.connect(lambda: self._select_all(self.ui.cb_select_all_ts))
        self.ui.cb_select_all_tb.stateChanged.connect(lambda: self._select_all(self.ui.cb_select_all_tb))

        # Button
        self.ui.pb_on_off.clicked.connect(self._treat_on_off_button)
        self.ui.pb_test_sequence.clicked.connect(self._test_sequence)
        self.ui.pb_reset.clicked.connect(self._reset)
        self.ui.pb_export.clicked.connect(self._export_pane_report)

        # Power supplies list (All power supplies)
        self._power_supply_list = _magdata.get_ps_names()


    def ui_filename(self):
        return 'main_window.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    ''' Executed when the button Reset is pressed.
    '''
    @pyqtSlot()
    def _reset(self):
        bt = self.ui.pb_reset
        reset_list = list(self._get_test_list())

        if len(reset_list) < 1:
            self.messsage_box = QMessageBox.information(self,
                                'Alerta', 'Selecione pelo menos uma fonte')
            bt.setChecked(False)

        if bt.isChecked() == True:
            bt.setEnabled(False)
            self.ui.lb_status.setText("<p style='color:red;'>Resetando fontes, aguarde...</p>")

            self.test_thread = PowerSupplyTest(reset_list, self._RESET)
            self.test_thread.reset_complete.connect(self._finish_reset)
            self.test_thread.start()

    ''' Executed when the button Start Sequence is pressed.
    '''
    @pyqtSlot()
    def _test_sequence(self):

        bt = self.ui.pb_test_sequence
        test_list = list(self._get_test_list())

        if len(test_list) < 1:
            self.messsage_box = QMessageBox.information(self,
                                'Alerta', 'Selecione pelo menos uma fonte')
            bt.setChecked(False)

        if bt.isChecked() == True:
            bt.setEnabled(False)

            self.ui.lb_status.setText("<p style='color:red;'>Teste Iniciado. \
                                        Por favor, aguarde...</p>")
            self.ui.te_test_sequence.clear()
            self.ui.te_pane_report.clear()
            self.ui.te_test_sequence.append('Por favor, aguarde...')
            self.ui.te_pane_report.append('Por favor, aguarde...')

            self.test_thread = PowerSupplyTest(test_list, self._TEST)
            self.test_thread.test_complete.connect(self._finish_test)
            self.test_thread.start()

    ''' Executed when button On Off is pressed
    '''
    @pyqtSlot()
    def _treat_on_off_button(self):
        OFF = 0
        ON = 1
        on_off_list = list(self._get_test_list())
        bt = self.ui.pb_on_off

        if len(on_off_list) < 1:
            self.messsage_box = QMessageBox.information(self,
                                'Alerta', 'Selecione pelo menos uma fonte')
            if bt.isChecked() == True:
                bt.setChecked(False)
            else:
                bt.setChecked(True)
        else:
            if bt.isChecked() == True:
                bt.setText('DESLIGAR')
                self.ui.lb_status.setText("<p style='color:red;'>Ligando Fontes. \
                                            Por favor, aguarde...</p>")
                self.test_thread = PowerSupplyTest(on_off_list, self._ON_OFF, ON)
                self.test_thread.pwr_state_changed.connect(self._pwr_toggled_magps)
                self.test_thread.start()

            else:
                bt.setText('LIGAR')
                self.ui.lb_status.setText("<p style='color:red;'>Desligando Fontes. \
                                            Por favor, aguarde...</p>")
                self.test_thread = PowerSupplyTest(on_off_list, self._ON_OFF, OFF)
                self.test_thread.pwr_state_changed.connect(self._pwr_toggled_magps)
                self.test_thread.start()

    ''' Executed when reset process is finished.
    '''
    @pyqtSlot()
    def _finish_reset(self):
        bt = self.ui.pb_reset
        self.ui.lb_status.setText("<p style='color:blue;'>Fontes Resetadas!</p>")
        bt.setEnabled(True)
        bt.setChecked(False)

    ''' Executed when test process is finished
    '''
    @pyqtSlot(list, list)
    def _finish_test(self, pass_list, pane_list):

        bt = self.ui.pb_test_sequence
        self.ui.te_test_sequence.clear()
        self.ui.te_pane_report.clear()

        self._print_headers()

        for item in pass_list:
            self._add_to_test_sequence(item)
            QApplication.processEvents()

        for item in pane_list:
            self._add_to_pane_report(item)
            QApplication.processEvents()

        bt.setEnabled(True)
        bt.setChecked(False)
        self.ui.lb_status.setText("<p style='color:blue;'>Teste Completo!</p>")


    ''' Executed when On or Off rotine is finished
    '''
    @pyqtSlot(int)
    def _pwr_toggled_magps(self, pwr_state):
        if pwr_state == 1:
            self.ui.lb_status.setText("<p style='color:blue;'>Fontes Ligadas!</p>")
        else:
            self.ui.lb_status.setText("<p style='color:blue;'>Fontes Desligas!</p>")

    ''' Print header for OK textedit and for Pane textedit
    '''
    def _print_headers(self):
        self.ui.te_test_sequence.clear()
        self.ui.te_pane_report.clear()

        ok_header ="<table><tr><td align='center' width=140><b>Fonte</b>\
                    </td><td width=90 align='center'><b>Setpoint(A)<b></td> \
                    <td align='center' width=90><b>Readback(A)</b></td></tr></table>"

        pane_header ="<table><tr><td align='center' width=140><b>Fonte</b>\
                    </td><td width=90 align='center'><b>Setpoint(A)<b></td> \
                    <td align='center' width=90><b>Readback(A)</b></td></tr></table>"

        self.ui.te_test_sequence.append(ok_header)
        self.ui.te_pane_report.append(pane_header)

    ''' Append a new result line to OK textedit
    '''
    def _add_to_test_sequence(self, item):

        pass_report ="<table><tr><td align='left' width=140>" + item[0] + \
                    "</td><td width=90 align='center'>" + str(item[1]) + "</td> \
                    <td align='center' width=90>" + str(item[2]) + "</td></tr></table>"

        self.ui.te_test_sequence.append(pass_report)

    ''' Append a new result line to Pane textedit
    '''
    def _add_to_pane_report(self, item):

        pane_report ="<table><tr><td align='left' width=140>" + item[0] + \
                    " </td><td width=90 align='center'>" + str(item[1]) + "</td> \
                    <td align='center' width=90>" + str(item[2]) + "</td></tr></table>"

        self.ui.te_pane_report.append(pane_report)


    ''' Export a list with all power supplies in pane list.
    '''
    @pyqtSlot()
    def _export_pane_report(self):
        text = self.ui.te_pane_report.toPlainText()
        name = QFileDialog.getSaveFileName(self, 'pane_report.txt')
        file_object = open(name, 'w')
        file_object.write(text)
        file_object.close()

    ''' Update checkbox when a group is selected
    '''
    @pyqtSlot()
    def _select_all(self, cb):

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


    ''' Get a list of power supplies to be tested based on selected items.
    '''
    def _get_test_list(self):
        test_set = set()
        if self.ui.cb_quadrupole_si.isChecked() == True:
            test_set = test_set | self._search_ps(self._STORAGE_RING, self._FAMILY, self._QUADRUPOLE)
        if self.ui.cb_sextupole_si.isChecked() == True:
            test_set = test_set | self._search_ps(self._STORAGE_RING, self._FAMILY, self._SEXTUPOLE)
        if self.ui.cb_dipole_si.isChecked() == True:
            test_set = test_set | self._search_ps(self._STORAGE_RING, self._FAMILY, self._DIPOLE)
        if self.ui.cb_quadrupole_bo.isChecked() == True:
            test_set = test_set | self._search_ps(self._BOOSTER, self._FAMILY, self._QUADRUPOLE)
        if self.ui.cb_sextupole_bo.isChecked() == True:
            test_set = test_set | self._search_ps(self._BOOSTER, self._FAMILY, self._SEXTUPOLE)
        if self.ui.cb_dipole_bo.isChecked() == True:
            test_set = test_set | self._search_ps(self._BOOSTER, self._FAMILY, self._DIPOLE)
        if self.ui.cb_quadrupole_linac.isChecked() == True:
            test_set = test_set | self._search_ps(self._LINAC, self._FAMILY, self._QUADRUPOLE)
        if self.ui.cb_sextupole_linac.isChecked() == True:
            test_set = test_set | self._search_ps(self._LINAC, self._FAMILY, self._SEXTUPOLE)
        if self.ui.cb_dipole_linac.isChecked() == True:
            test_set = test_set | self._search_ps(self._LINAC, self._FAMILY, self._DIPOLE)
        if self.ui.cb_quadrupole_ts.isChecked() == True:
            test_set = test_set | self._search_ps(self._TRANSPORT_LINE_SI, self._FAMILY, self._QUADRUPOLE)
        if self.ui.cb_sextupole_ts.isChecked() == True:
            test_set = test_set | self._search_ps(self._TRANSPORT_LINE_SI, self._FAMILY, self._SEXTUPOLE)
        if self.ui.cb_dipole_ts.isChecked() == True:
            test_set = test_set | self._search_ps(self._TRANSPORT_LINE_SI, self._FAMILY, self._DIPOLE)
        if self.ui.cb_quadrupole_tb.isChecked() == True:
            test_set = test_set | self._search_ps(self._TRANSPORT_LINE_BO, self._FAMILY, self._QUADRUPOLE)
        if self.ui.cb_sextupole_tb.isChecked() == True:
            test_set = test_set | self._search_ps(self._TRANSPORT_LINE_BO, self._FAMILY, self._SEXTUPOLE)
        if self.ui.cb_dipole_tb.isChecked() == True:
            test_set = test_set | self._search_ps(self._TRANSPORT_LINE_BO, self._FAMILY, self._DIPOLE)
        return test_set

    ''' Select items in power supply list based on name composition.
    '''
    def _search_ps(self, accel_section, ps_group, ps_type):
        ps_set = set()
        if ps_group == self._FAMILY:
            for item in self._power_supply_list:
                if accel_section in item and ps_group in item and ps_type in item:
                    ps_set.add(item)
        else:
            for item in self._power_supply_list:
                if accel_section in item and self._FAMILY not in item and ps_type in item:
                    ps_set.add(item)

        return ps_set



intelclass = ControlMainWindow
