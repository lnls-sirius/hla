from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFormLayout, QLabel, QSpacerItem, \
    QSizePolicy as QSzPlcy, QGridLayout, QHBoxLayout
from pydm.widgets import PyDMLabel
from siriushla.widgets import SiriusDialog, SiriusLedAlert, \
    PyDMLedMultiChannel
from .util import SEC_2_CHANNELS


class CavityStatusDetails(SiriusDialog):
    """Cavity Status Datails."""

    def __init__(self, parent=None, prefix='', section=''):
        super().__init__(parent)
        self.prefix = prefix
        self.section = section.upper()
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section + 'App')
        self.setWindowTitle(self.section + ' Cavity Detailed Status')
        self._setupUi()

    def _setupUi(self):
        lay_temp1 = QFormLayout()
        lay_temp1.setHorizontalSpacing(9)
        lay_temp1.setVerticalSpacing(9)
        lay_temp1.setLabelAlignment(Qt.AlignRight)
        lay_temp1.setFormAlignment(Qt.AlignTop)
        lb_temp1 = QLabel('Cell and Coupler\nTemperatures\nPT100', self)
        lb_temp1.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_temp1.addRow(lb_temp1)
        lims = [25.0, 35.0]
        tooltip = 'Interlock limits: \nMin: ' + str(lims[0]) + \
            '°C, Max: '+str(lims[1])+'°C'
        for idx, cell in enumerate(self.chs['Cav Sts']['Temp']['Cells']):
            lb = PyDMLabel(self, cell[0])
            lb.showUnits = True
            lb.setStyleSheet('min-width:3.5em; max-width:3.5em;')
            led = PyDMLedMultiChannel(
                self,
                {cell[0]: {'comp': 'wt', 'value': lims},
                 cell[0].replace('T-Mon', 'TUp-Mon'): 0,
                 cell[0].replace('T-Mon', 'TDown-Mon'): 0})
            led.setToolTip(tooltip)
            hb = QHBoxLayout()
            hb.setAlignment(Qt.AlignLeft)
            hb.addWidget(lb)
            hb.addWidget(led)
            lay_temp1.addRow('Cell '+str(idx + 1)+': ', hb)
        ch_coup = self.chs['Cav Sts']['Temp']['Coupler'][0]
        lims_coup = [25.0, 50.0]
        lb_coup = PyDMLabel(self, ch_coup)
        lb_coup.setStyleSheet('min-width:3.5em; max-width:3.5em;')
        lb_coup.showUnits = True
        led_coup = PyDMLedMultiChannel(
            self,
            {ch_coup: {'comp': 'wt', 'value': lims_coup},
             ch_coup.replace('T-Mon', 'TUp-Mon'): 0,
             ch_coup.replace('T-Mon', 'TDown-Mon'): 0})
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
            led.channel = cell[0].replace('T-Mon', 'Tms-Mon')
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
            led.channel = disc
            lay_dtemp.addRow('Disc '+str(idx)+': ', led)

        self.led_HDFlwRt1 = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['FlwRt'][0])
        self.led_HDFlwRt2 = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['FlwRt'][1])
        self.led_HDFlwRt3 = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['FlwRt'][2])
        lay_flwrt = QFormLayout()
        lay_flwrt.setHorizontalSpacing(9)
        lay_flwrt.setVerticalSpacing(9)
        lay_flwrt.setLabelAlignment(Qt.AlignRight)
        lay_flwrt.setFormAlignment(Qt.AlignTop)
        lb_flwrf = QLabel('Flow Switches', self)
        lb_flwrf.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_flwrt.addRow(lb_flwrf)
        lay_flwrt.addRow('Flow Switch 1: ', self.led_HDFlwRt1)
        lay_flwrt.addRow('Flow Switch 2: ', self.led_HDFlwRt2)
        lay_flwrt.addRow('Flow Switch 3: ', self.led_HDFlwRt3)

        self.led_CoupPressure = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['Vac']['Coupler ok'])
        self.led_Pressure = SiriusLedAlert(self)
        self.led_Pressure.setToolTip('Interlock limits:\nMax: 5e-7mBar')
        self.led_Pressure.channel = \
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
        lay_vac.addRow('Pressure Sensor: ', self.led_CoupPressure)
        lay_vac.addRow('Vacuum: ', self.led_Pressure)

        lb = QLabel('Cavity - Detailed Status', self)
        lb.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay = QGridLayout(self)
        lay.setHorizontalSpacing(30)
        lay.setVerticalSpacing(20)
        lay.addWidget(lb, 0, 0, 1, 4)
        lay.addLayout(lay_temp1, 1, 0, 2, 1)
        lay.addLayout(lay_temp2, 1, 1, 2, 1)
        lay.addLayout(lay_dtemp, 1, 2, 2, 1)
        lay.addLayout(lay_flwrt, 1, 3)
        lay.addLayout(lay_vac, 2, 3)

        self.setStyleSheet("""
            PyDMLabel{
                qproperty-alignment: AlignLeft;
            }
            QLed{
                max-width: 1.29em;
            }
            .QLabel{
                max-height:4em;
                qproperty-alignment: AlignRight;
            }""")


class TransmLineStatusDetails(SiriusDialog):
    """Transmission Line Status Details."""

    def __init__(self, parent=None, prefix='', section=''):
        super().__init__(parent)
        self.prefix = prefix
        self.section = section.upper()
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section + 'App')
        self.setWindowTitle(self.section + ' Transm. Line Detailed Status')
        self._setupUi()

    def _setupUi(self):
        self.lb_CircTin = PyDMLabel(
            self, self.prefix+self.chs['TL Sts']['Circ TIn'])
        self.lb_CircTin.showUnits = True
        self.lb_CircTin.setStyleSheet('qproperty-alignment: AlignLeft;')
        self.lb_CircTout = PyDMLabel(
            self, self.prefix+self.chs['TL Sts']['Circ TOut'])
        self.lb_CircTout.showUnits = True
        self.lb_CircTout.setStyleSheet('qproperty-alignment: AlignLeft;')
        self.led_CircArc = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Circ Arc'])
        if self.section == 'SI':
            self.led_LoadArc = SiriusLedAlert(
                self, self.prefix+self.chs['TL Sts']['Load Arc'])
        self.led_CircFlwRt = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Circ FlwRt'])
        self.led_LoadFlwRt = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Load FlwRt'])
        self.led_CircIntlkOp = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Circ Intlk'])

        lay = QFormLayout(self)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(QLabel('<h4>Transm. Line - Detailed Status</h4>'))
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow('Circulator T In: ', self.lb_CircTin)
        lay.addRow('Circulator T Out: ', self.lb_CircTout)
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow('Circulator Arc Detector: ', self.led_CircArc)
        if self.section == 'SI':
            lay.addRow('Load Arc Detector: ', self.led_LoadArc)
        lay.addRow('Circulator Flow: ', self.led_CircFlwRt)
        lay.addRow('Load Flow: ', self.led_LoadFlwRt)
        lay.addRow('Circulator Intlk: ', self.led_CircIntlkOp)

        self.setStyleSheet("""
            PyDMLabel{
                qproperty-alignment: AlignLeft;
            }
            QLed{
                max-width: 1.29em;
            }
            .QLabel{
                max-height:2em;
                qproperty-alignment: AlignRight;
            }""")


class LLRFInterlockDetails(SiriusDialog):
    """LLRF Interlock Details."""

    def __init__(self, parent, prefix='', section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.section = section
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.setWindowTitle(self.section+' LLRF Interlock Details')
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setHorizontalSpacing(25)
        lay.setVerticalSpacing(15)

        lay.addWidget(
            QLabel('<h4>LLRF Interlock Details</h4>', self,
                   alignment=Qt.AlignCenter), 0, 0, 1, 2)
        for col, item in enumerate(self.chs['Intlk Details'].items()):
            name, dic = item
            lay_intlk = QGridLayout()
            lay_intlk.setHorizontalSpacing(9)
            lay_intlk.setVerticalSpacing(9)
            lay_intlk.addWidget(
                QLabel('<h4>'+name+'</h4>', self), 0, 0, 1, 2)
            pv = dic['PV']
            labels = dic['Labels']
            for idx, label in enumerate(labels):
                led = SiriusLedAlert(self, pv, bit=idx)
                lb = QLabel(label)
                lay_intlk.addWidget(led, idx+1, 0)
                lay_intlk.addWidget(lb, idx+1, 1)
            lay.addLayout(lay_intlk, 1, col)
