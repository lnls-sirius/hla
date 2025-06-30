"""Cavity Status Datails."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFormLayout, QGridLayout, QHBoxLayout, QLabel, QFrame

from ...widgets import PyDMLedMultiChannel, SiriusDialog, SiriusLabel, \
    SiriusLedAlert
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


class CavityStatusDetails(SiriusDialog):
    """Cavity Status Datails."""

    def __init__(self, parent=None, prefix='', section=''):
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section.upper()
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section + 'App')
        if self.section == 'SI':
            self.setWindowTitle(self.section + ' Cryo Module Detailed Status')
            self._setupUi_SI()
        else:
            self.setWindowTitle(self.section + ' Cavity Detailed Status')
            self._setupUi_BO()

    def _setupUi_BO(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay_temp1 = QFormLayout()
        lay_temp1.setHorizontalSpacing(9)
        lay_temp1.setVerticalSpacing(9)
        lay_temp1.setLabelAlignment(Qt.AlignRight)
        lay_temp1.setFormAlignment(Qt.AlignTop)
        lb_temp1 = QLabel('Cell and Coupler\nTemperatures\nPT100', self)
        lb_temp1.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_temp1.addRow(lb_temp1)
        lims = self.chs['Cav Sts']['Temp']['Cells Limits']
        tooltip = 'Interlock limits: \nMin: ' + str(lims[0]) + \
            '°C, Max: '+str(lims[1])+'°C'
        for idx, cell in enumerate(self.chs['Cav Sts']['Temp']['Cells']):
            lbl = SiriusLabel(self, self.prefix+cell[0])
            lbl.showUnits = True
            lbl.setStyleSheet('min-width:3.5em; max-width:3.5em;')
            led = PyDMLedMultiChannel(
                self,
                {self.prefix+cell[0]: {'comp': 'wt', 'value': lims},
                self.prefix+cell[0].replace('T-Mon', 'TUp-Mon'): 0,
                self.prefix+cell[0].replace('T-Mon', 'TDown-Mon'): 0})
            led.setToolTip(tooltip)
            hbox = QHBoxLayout()
            hbox.setAlignment(Qt.AlignLeft)
            hbox.addWidget(lbl)
            hbox.addWidget(led)
            lay_temp1.addRow('Cell '+str(idx + 1)+': ', hbox)
        ch_coup = self.chs['Cav Sts']['Temp']['Coupler'][0]
        lims_coup = self.chs['Cav Sts']['Temp']['Coupler Limits']
        lb_coup = SiriusLabel(self, self.prefix+ch_coup)
        lb_coup.setStyleSheet('min-width:3.5em; max-width:3.5em;')
        lb_coup.showUnits = True
        led_coup = PyDMLedMultiChannel(
            self,
            {self.prefix+ch_coup: {'comp': 'wt', 'value': lims_coup},
            self.prefix+ch_coup.replace('T-Mon', 'TUp-Mon'): 0,
            self.prefix+ch_coup.replace('T-Mon', 'TDown-Mon'): 0})
        led_coup.setToolTip(
            'Interlock limits: \n'
            'Min: '+str(lims_coup[0])+'°C, Max: '+str(lims_coup[1])+'°C')
        hb_coup = QHBoxLayout()
        hb_coup.setAlignment(Qt.AlignLeft)
        hb_coup.addWidget(lb_coup)
        hb_coup.addWidget(led_coup)
        lay_temp1.addRow('Coupler: ', hb_coup)
        lay_temp2 = QFormLayout()
        lay_temp2.setHorizontalSpacing(9)
        lay_temp2.setVerticalSpacing(9)
        lay_temp2.setLabelAlignment(Qt.AlignRight)
        lay_temp2.setFormAlignment(Qt.AlignTop | Qt.AlignHCenter)
        lb_temp2 = QLabel('Cell\nTemperatures\nThermostats', self)
        lb_temp2.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_temp2.addRow(lb_temp2)
        for idx, cell in enumerate(self.chs['Cav Sts']['Temp']['Cells']):
            led = SiriusLedAlert(self)
            led.setToolTip('Interlock limits:\nMax: 60°C')
            led.channel = self.prefix+cell[0].replace('T-Mon', 'Tms-Mon')
            lay_temp2.addRow('Cell '+str(idx + 1)+': ', led)
        lay_dtemp = QFormLayout()
        lay_dtemp.setHorizontalSpacing(9)
        lay_dtemp.setVerticalSpacing(9)
        lay_dtemp.setLabelAlignment(Qt.AlignRight)
        lay_dtemp.setFormAlignment(Qt.AlignTop | Qt.AlignHCenter)
        lb_dtemp = QLabel('Disc\nTemperatures\nThermostats', self)
        lb_dtemp.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_dtemp.addRow(lb_dtemp)
        for idx, disc in enumerate(self.chs['Cav Sts']['Temp']['Discs']):
            led = SiriusLedAlert(self)
            led.setToolTip('Interlock limits:\nMax: 60°C')
            led.channel = self.prefix+disc
            lay_dtemp.addRow('Disc '+str(idx)+': ', led)
        lay_flwrt = QFormLayout()
        lay_flwrt.setHorizontalSpacing(9)
        lay_flwrt.setVerticalSpacing(9)
        lay_flwrt.setLabelAlignment(Qt.AlignRight)
        lay_flwrt.setFormAlignment(Qt.AlignTop)
        lb_flwrf = QLabel('Flow Switches', self)
        lb_flwrf.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_flwrt.addRow(lb_flwrf)
        for flwsw, pvn in self.chs['Cav Sts']['FlwRt'].items():
            led = SiriusLedAlert(self, self.prefix+pvn)
            lay_flwrt.addRow(flwsw+': ', led)
        self.led_couppressure = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['Vac']['Coupler ok'])
        self.led_pressure = SiriusLedAlert(self)
        self.led_pressure.setToolTip('Interlock limits:\nMax: 5e-7mBar')
        self.led_pressure.channel = \
            self.prefix+self.chs['Cav Sts']['Vac']['Cells ok']
        lay_vac = QFormLayout()
        lay_vac.setHorizontalSpacing(9)
        lay_vac.setVerticalSpacing(9)
        lay_vac.setLabelAlignment(Qt.AlignRight)
        lay_vac.setFormAlignment(Qt.AlignTop)
        lb_vac = QLabel('Vacuum', self)
        lb_vac.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_flwrt.addRow(lb_vac)
        lay_vac.addRow('Pressure Sensor: ', self.led_couppressure)
        lay_vac.addRow('Vacuum: ', self.led_pressure)
        lbl = QLabel('Cavity - Detailed Status', self)
        lbl.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay = QGridLayout(self)
        lay.setHorizontalSpacing(30)
        lay.setVerticalSpacing(20)
        lay.addWidget(lbl, 0, 0, 1, 4)
        lay.addLayout(lay_temp1, 1, 0, 2, 1)
        lay.addLayout(lay_temp2, 1, 1, 2, 1)
        lay.addLayout(lay_dtemp, 1, 2, 2, 1)
        lay.addLayout(lay_flwrt, 1, 3)
        lay.addLayout(lay_vac, 2, 3)

    def _setupUi_SI(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QGridLayout(self)
        lay.setSpacing(1)
        lay.setHorizontalSpacing(25)
        lay.setVerticalSpacing(20)

        lbl = QLabel('Cryo Module - Detailed Status', self)
        lbl.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay.addWidget(lbl, 0, 1, 1, 3)

        lbl_cm1 = QLabel('<h4>Cryo Module 1</h4>', self)
        lay.addWidget(lbl_cm1, 1, 1)
            
        lbl_cm2 = QLabel('<h4>Cryo Module 2</h4>', self)
        lay.addWidget(lbl_cm2, 1, 3)

        lbl_rfs1 = QLabel('RF Stop 1', self)
        slbl_rfs1cm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['RF Stop 1']['label'])
        led_rfs1cm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['RF Stop 1']['led'])
            
        slbl_rfs1cm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['RF Stop 1']['label'])
        led_rfs1cm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['RF Stop 1']['led'])

        lay.addWidget(lbl_rfs1, 2, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_rfs1cm1, 2, 1)
        lay.addWidget(led_rfs1cm1, 2, 2)
        lay.addWidget(slbl_rfs1cm2, 2, 3)
        lay.addWidget(led_rfs1cm2, 2, 4)

        lbl_rfs2 = QLabel('RF Stop 2', self)
        slbl_rfs2cm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['RF Stop 2']['label'])
        led_rfs2cm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['RF Stop 2']['led'])

        slbl_rfs2cm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['RF Stop 2']['label'])
        led_rfs2cm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['RF Stop 2']['led'])
            
        lay.addWidget(lbl_rfs2, 3, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_rfs2cm1, 3, 1)
        lay.addWidget(led_rfs2cm1, 3, 2)
        lay.addWidget(slbl_rfs2cm2, 3, 3)
        lay.addWidget(led_rfs2cm2, 3, 4)
            
        lbl_rfs3 = QLabel('RF Stop 3', self)
        slbl_rfs3cm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['RF Stop 3']['label'])
        led_rfs3cm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['RF Stop 3']['led'])

        slbl_rfs3cm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['RF Stop 3']['label'])
        led_rfs3cm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['RF Stop 3']['led'])
            
        lay.addWidget(lbl_rfs3, 4, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_rfs3cm1, 4, 1)
        lay.addWidget(led_rfs3cm1, 4, 2)
        lay.addWidget(slbl_rfs3cm2, 4, 3)
        lay.addWidget(led_rfs3cm2, 4, 4)

        lbl_hs = QLabel('Heater Stop', self)
        slbl_hscm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['Heater Stop']['label'])
        led_hscm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['Heater Stop']['led'])

        slbl_hscm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['Heater Stop']['label'])
        led_hscm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['Heater Stop']['led'])

        lay.addWidget(lbl_hs, 5, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_hscm1, 5, 1)
        lay.addWidget(led_hscm1, 5, 2)
        lay.addWidget(slbl_hscm2, 5, 3)
        lay.addWidget(led_hscm2, 5, 4)

        lbl_css = QLabel('Cryo Supply Stop', self)
        slbl_csscm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['Cryo Supply Stop']['label'])
        led_csscm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['Cryo Supply Stop']['led'])

        slbl_csscm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['Cryo Supply Stop']['label'])
        led_csscm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['Cryo Supply Stop']['led'])

        lay.addWidget(lbl_css, 6, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_csscm1, 6, 1)
        lay.addWidget(led_csscm1, 6, 2)
        lay.addWidget(slbl_csscm2, 6, 3)
        lay.addWidget(led_csscm2, 6, 4)

        lbl_crs = QLabel('Cryo Return Stop', self)
        slbl_crscm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['Cryo Return Stop']['label'])
        led_crscm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['Cryo Return Stop']['led'])

        slbl_crscm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['Cryo Return Stop']['label'])
        led_crscm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['Cryo Return Stop']['led'])

        lay.addWidget(lbl_crs, 7, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_crscm1, 7, 1)
        lay.addWidget(led_crscm1, 7, 2)
        lay.addWidget(slbl_crscm2, 7, 3)
        lay.addWidget(led_crscm2, 7, 4)

        lay.addWidget(self.horizontal_separator(), 8, 0, 1, 7)
        lbl_VB = QLabel('<h4>Valve Box</h4>', self)
        lay.addWidget(lbl_VB, 9, 0, alignment=Qt.AlignRight)

        lbl_rfs4_VB = QLabel('RF Stop 4', self)
        slbl_rfs4cm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['Valve Box']['RF Stop 4']['label'])
        led_rfs4cm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['Valve Box']['RF Stop 4']['led'])

        slbl_rfs4cm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['Valve Box']['RF Stop 4']['label'])
        led_rfs4cm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['Valve Box']['RF Stop 4']['led'])

        lay.addWidget(lbl_rfs4_VB, 10, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_rfs4cm1, 10, 1)
        lay.addWidget(led_rfs4cm1, 10, 2)
        lay.addWidget(slbl_rfs4cm2, 10, 3)
        lay.addWidget(led_rfs4cm2, 10, 4)

        lbl_hs_VB = QLabel('Heater Stop', self)
        slbl_hsvbcm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['Valve Box']['Heater Stop']['label'])
        led_hsvbcm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['Valve Box']['Heater Stop']['led'])

        slbl_hsvbcm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['Valve Box']['Heater Stop']['label'])
        led_hsvbcm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['Valve Box']['Heater Stop']['led'])

        lay.addWidget(lbl_hs_VB, 11, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_hsvbcm1, 11, 1)
        lay.addWidget(led_hsvbcm1, 11, 2)
        lay.addWidget(slbl_hsvbcm2, 11, 3)
        lay.addWidget(led_hsvbcm2, 11, 4)

        lbl_css_VB = QLabel('Cryo Supply Stop', self)
        slbl_cssvbcm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['Valve Box']['Cryo Supply Stop']['label'])
        led_cssvbcm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['Valve Box']['Cryo Supply Stop']['led'])

        slbl_cssvbcm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['Valve Box']['Cryo Supply Stop']['label'])
        led_cssvbcm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['Valve Box']['Cryo Supply Stop']['led'])

        lay.addWidget(lbl_css_VB, 12, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_cssvbcm1, 12, 1)
        lay.addWidget(led_cssvbcm1, 12, 2)
        lay.addWidget(slbl_cssvbcm2, 12, 3)
        lay.addWidget(led_cssvbcm2, 12, 4)

        lbl_crs_VB = QLabel('Cryo Return Stop', self)
        slbl_crsvbcm1 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 1']['Valve Box']['Cryo Return Stop']['label'])
        led_crsvbcm1 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 1']['Valve Box']['Cryo Return Stop']['led'])

        slbl_crsvbcm2 = SiriusLabel(self, self.chs['Cryo Module']['Cryo Module 2']['Valve Box']['Cryo Return Stop']['label'])
        led_crsvbcm2 = SiriusLedAlert(self, self.chs['Cryo Module']['Cryo Module 2']['Valve Box']['Cryo Return Stop']['led'])

        lay.addWidget(lbl_crs_VB, 13, 0, alignment=Qt.AlignRight)
        lay.addWidget(slbl_crsvbcm1, 13, 1)
        lay.addWidget(led_crsvbcm1, 13, 2)
        lay.addWidget(slbl_crsvbcm2, 13, 3)
        lay.addWidget(led_crsvbcm2, 13, 4)

        lay.addWidget(self.horizontal_separator(), 14, 0, 1, 7)
        lbl_ES = QLabel('<h4>External Stop</h4>', self)
        slbl_ES = SiriusLabel(self, self.chs['Cryo Module']['External Stop']['label'])
        led_ES = SiriusLedAlert(self, self.chs['Cryo Module']['External Stop']['led'])

        lay.addWidget(lbl_ES, 15, 1, alignment=Qt.AlignRight)
        lay.addWidget(slbl_ES, 15, 2)
        lay.addWidget(led_ES, 15, 3)

        lay.addWidget(self.horizontal_separator(), 16, 0, 1, 7)

        self.setStyleSheet("""
            SiriusLabel{
                qproperty-alignment: AlignLeft;
            }
            QLed{
                max-width: 1.29em;
            }
            .QLabel{
                max-height:4em;
                qproperty-alignment: AlignRight;
            }""")

    def horizontal_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line
    