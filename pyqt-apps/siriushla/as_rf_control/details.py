from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFormLayout, QLabel, QSpacerItem, \
    QSizePolicy as QSzPlcy, QGridLayout, QHBoxLayout
from pydm.widgets import PyDMLabel
from siriushla.widgets import SiriusDialog, SiriusLedAlert
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
        lay_celltemp = QFormLayout()
        lay_celltemp.setHorizontalSpacing(9)
        lay_celltemp.setVerticalSpacing(9)
        lay_celltemp.setLabelAlignment(Qt.AlignRight)
        lay_celltemp.setFormAlignment(Qt.AlignTop)
        lb_temp1 = QLabel('Cell and Coupler\nTemperatures', self)
        lb_temp1.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_celltemp.addRow(lb_temp1)
        for idx, cell in enumerate(self.chs['Cav Sts']['Temp']['Cells']):
            lb = PyDMLabel(self, cell[0])
            lb.showUnits = True
            lb.setStyleSheet('min-width:3.5em; max-width:3.5em;')
            led = SiriusLedAlert(self, cell[0].replace('T-Mon', 'Tms-Mon'))
            hb = QHBoxLayout()
            hb.setAlignment(Qt.AlignLeft)
            hb.addWidget(lb)
            hb.addWidget(led)
            lay_celltemp.addRow('Cell '+str(idx + 1)+': ', hb)
        lb_coupler = PyDMLabel(
            self, self.chs['Cav Sts']['Temp']['Coupler'][0])
        lb_coupler.showUnits = True
        lay_celltemp.addRow('Coupler: ', lb_coupler)

        lay_otemp = QFormLayout()
        lay_otemp.setHorizontalSpacing(9)
        lay_otemp.setVerticalSpacing(9)
        lay_otemp.setLabelAlignment(Qt.AlignRight)
        lay_otemp.setFormAlignment(Qt.AlignTop | Qt.AlignHCenter)
        lb_temp2 = QLabel('Other\nTemperatures', self)
        lb_temp2.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_otemp.addRow(lb_temp2)
        for idx, disc in enumerate(self.chs['Cav Sts']['Temp']['Discs']):
            led = SiriusLedAlert(self, disc)
            lay_otemp.addRow('Disc '+str(idx)+': ', led)

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
        lb_flwrf = QLabel('Flow Switchs', self)
        lb_flwrf.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_flwrt.addRow(lb_flwrf)
        lay_flwrt.addRow('Flow Switch 1: ', self.led_HDFlwRt1)
        lay_flwrt.addRow('Flow Switch 2: ', self.led_HDFlwRt2)
        lay_flwrt.addRow('Flow Switch 3: ', self.led_HDFlwRt3)

        self.led_CoupPressure = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['Vac']['Coupler ok'])
        self.led_Pressure = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['Vac']['Cells ok'])
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
        lay.addWidget(lb, 0, 0, 1, 3)
        lay.addLayout(lay_celltemp, 1, 0, 2, 1)
        lay.addLayout(lay_otemp, 1, 1, 2, 1)
        lay.addLayout(lay_flwrt, 1, 2)
        lay.addLayout(lay_vac, 2, 2)

        self.setStyleSheet("""
            PyDMLabel{
                qproperty-alignment: AlignLeft;
            }
            QLed{
                max-width: 1.29em;
            }
            .QLabel{
                max-height:1.5em;
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
        self.led_LoadFlwRt = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Load FlwRt'])
        self.led_CircFlwRt = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Circ FlwRt'])
        self.led_CircIntlkOp = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Circ Intlk'])

        lay = QFormLayout(self)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(QLabel('<h4>Transm. Line - Detailed Status</h4>'))
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow('Circulator T In: ', self.lb_CircTin)
        lay.addRow('Circulator T Out: ', self.lb_CircTout)
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow('Load Flow: ', self.led_LoadFlwRt)
        lay.addRow('Circulator Flow: ', self.led_CircFlwRt)
        lay.addRow('Circulator Intlk: ', self.led_CircIntlkOp)


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
