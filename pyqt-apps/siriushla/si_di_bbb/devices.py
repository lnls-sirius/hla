"""BbB Devices Module."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QTabWidget, \
    QGroupBox, QHBoxLayout, QSpacerItem, QSizePolicy as QSzPlcy, \
    QVBoxLayout, QSpacerItem

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMLineEdit

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriushla.widgets import PyDMStateButton, PyDMLed, SiriusFrame
from .custom_widgets import WfmGraph, MyScaleIndicator


class BbBMainDevicesWidget(QWidget):
    """BbB Main Devices Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self._ld_maindev = QLabel(
            '<h3>Main Devices Settings</h3>', self, alignment=Qt.AlignCenter)

        # # Delay Lines
        self._ld_adcclock = QLabel('ADC Clock', self)
        self._sb_adcclock = PyDMSpinbox(self, self.dev_pref+':ECLDEL0')
        self._sb_adcclock.showStepExponent = False
        self._fr_adcclock = SiriusFrame(self, self.dev_pref+':ECLDEL0_SUBWR')
        self._fr_adcclock.add_widget(self._sb_adcclock)

        self._ld_fidclock = QLabel('Fiducial Clock', self)
        self._sb_fidclock = PyDMSpinbox(self, self.dev_pref+':ECLDEL1')
        self._sb_fidclock.showStepExponent = False
        self._fr_fidclock = SiriusFrame(self, self.dev_pref+':ECLDEL1_SUBWR')
        self._fr_fidclock.add_widget(self._sb_fidclock)

        self._ld_fiducial = QLabel('Fiducial', self)
        self._sb_fiducial = PyDMSpinbox(self, self.dev_pref+':ECLDEL2')
        self._sb_fiducial.showStepExponent = False
        self._fr_fiducial = SiriusFrame(self, self.dev_pref+':ECLDEL2_SUBWR')
        self._fr_fiducial.add_widget(self._sb_fiducial)

        self._ld_dacclock = QLabel('DAC Clock', self)
        self._sb_dacclock = PyDMSpinbox(self, self.dev_pref+':ECLDEL3')
        self._sb_dacclock.showStepExponent = False
        self._fr_dacclock = SiriusFrame(self, self.dev_pref+':ECLDEL3_SUBWR')
        self._fr_dacclock.add_widget(self._sb_dacclock)

        gbox_delaylines = QGroupBox('Delay lines', self)
        lay_delaylines = QGridLayout(gbox_delaylines)
        lay_delaylines.addWidget(self._ld_adcclock, 0, 0)
        lay_delaylines.addWidget(self._fr_adcclock, 0, 1)
        lay_delaylines.addWidget(self._ld_fidclock, 1, 0)
        lay_delaylines.addWidget(self._fr_fidclock, 1, 1)
        lay_delaylines.addWidget(self._ld_fiducial, 2, 0)
        lay_delaylines.addWidget(self._fr_fiducial, 2, 1)
        lay_delaylines.addWidget(self._ld_dacclock, 3, 0)
        lay_delaylines.addWidget(self._fr_dacclock, 3, 1)

        # # Thresholds and offsets
        self._ld_lvl = QLabel('<h4>Level</h4>', self, alignment=Qt.AlignCenter)
        self._ld_enbl = QLabel('<h4>Enbl</h4>', self, alignment=Qt.AlignCenter)
        self._ld_v = QLabel('<h4>V</h4>', self, alignment=Qt.AlignCenter)
        self._ld_edge = QLabel('<h4>Edge</h4>', self, alignment=Qt.AlignCenter)

        self._ld_fid = QLabel('Fiducial', self)
        self._cb_fidlvl = PyDMEnumComboBox(self, self.dev_pref+':LEVEL_FID')
        self._cb_fidlvlenbl = PyDMEnumComboBox(
            self, self.dev_pref+':LEVEL_FID_ENABLE')
        self._cb_fidlvlenbl.setStyleSheet('max-width:3em;')
        self._sb_fidv = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH9')
        self._sb_fidv.showStepExponent = False
        self._sb_fidv.showUnits = True
        self._fr_fidv = SiriusFrame(self, self.dev_pref+':AD5644CH9_SUBWR')
        self._fr_fidv.add_widget(self._sb_fidv)

        self._ld_trg1 = QLabel('Trigger 1', self)
        self._cb_trg1lvl = PyDMEnumComboBox(self, self.dev_pref+':LEVEL_TRIG1')
        self._cb_trg1lvlenbl = PyDMEnumComboBox(
            self, self.dev_pref+':LEVEL_TRIG1_ENABLE')
        self._cb_trg1lvlenbl.setStyleSheet('max-width:3em;')
        self._sb_trg1lvlv = PyDMSpinbox(self, self.dev_pref+':LEVEL_VTRIG1')
        self._sb_trg1lvlv.showStepExponent = False
        self._sb_trg1lvlv.showUnits = True
        self._fr_trg1lvlv = SiriusFrame(
            self, self.dev_pref+':AD5644CH10_SUBWR')
        self._fr_trg1lvlv.add_widget(self._sb_trg1lvlv)
        self._cb_trg1edge = PyDMEnumComboBox(self, self.dev_pref+':TRIG1INV')
        self._cb_trg1edge.setStyleSheet('max-width:3.2em;')

        self._ld_trg2 = QLabel('Trigger 2', self)
        self._cb_trg2lvl = PyDMEnumComboBox(self, self.dev_pref+':LEVEL_TRIG2')
        self._cb_trg2lvlenbl = PyDMEnumComboBox(
            self, self.dev_pref+':LEVEL_TRIG2_ENABLE')
        self._cb_trg2lvlenbl.setStyleSheet('max-width:3em;')
        self._sb_trg2lvlv = PyDMSpinbox(self, self.dev_pref+':LEVEL_VTRIG2')
        self._sb_trg2lvlv.showStepExponent = False
        self._sb_trg2lvlv.showUnits = True
        self._fr_trg2lvlv = SiriusFrame(self, self.dev_pref+':AD5644CH8_SUBWR')
        self._fr_trg2lvlv.add_widget(self._sb_trg2lvlv)
        self._cb_trg2edge = PyDMEnumComboBox(self, self.dev_pref+':TRIG2INV')
        self._cb_trg2edge.setStyleSheet('max-width:3.2em;')

        self._ld_dacoff = QLabel('DAC Offset', self)
        self._sb_dacoff = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH11')
        self._sb_dacoff.showStepExponent = False
        self._sb_dacoff.showUnits = True
        self._fr_dacoff = SiriusFrame(self, self.dev_pref+':AD5644CH11_SUBWR')
        self._fr_dacoff.add_widget(self._sb_dacoff)

        gbox_thoff = QGroupBox('Thresholds and Offsets', self)
        lay_thoff = QGridLayout(gbox_thoff)
        lay_thoff.addWidget(self._ld_lvl, 0, 1)
        lay_thoff.addWidget(self._ld_enbl, 0, 2)
        lay_thoff.addWidget(self._ld_v, 0, 3)
        lay_thoff.addWidget(self._ld_edge, 0, 4)
        lay_thoff.addWidget(self._ld_fid, 1, 0)
        lay_thoff.addWidget(self._cb_fidlvl, 1, 1)
        lay_thoff.addWidget(self._cb_fidlvlenbl, 1, 2)
        lay_thoff.addWidget(self._fr_fidv, 1, 3)
        lay_thoff.addWidget(self._ld_trg1, 2, 0)
        lay_thoff.addWidget(self._cb_trg1lvl, 2, 1)
        lay_thoff.addWidget(self._cb_trg1lvlenbl, 2, 2)
        lay_thoff.addWidget(self._fr_trg1lvlv, 2, 3)
        lay_thoff.addWidget(self._cb_trg1edge, 2, 4)
        lay_thoff.addWidget(self._ld_trg2, 3, 0)
        lay_thoff.addWidget(self._cb_trg2lvl, 3, 1)
        lay_thoff.addWidget(self._cb_trg2lvlenbl, 3, 2)
        lay_thoff.addWidget(self._fr_trg2lvlv, 3, 3)
        lay_thoff.addWidget(self._cb_trg2edge, 3, 4)
        lay_thoff.addWidget(self._ld_dacoff, 4, 0)
        lay_thoff.addWidget(self._fr_dacoff, 4, 3)
        lay_thoff.setColumnStretch(0, 3)
        lay_thoff.setColumnStretch(1, 2)
        lay_thoff.setColumnStretch(2, 1)
        lay_thoff.setColumnStretch(3, 5)
        lay_thoff.setColumnStretch(4, 1)

        # # FIR
        self._ld_sfir = QLabel('Shaper FIR ([C0 2^17 C2])', self)

        self._ld_firc0 = QLabel('C0', self)
        self._sb_firc0 = PyDMSpinbox(self, self.dev_pref+':SHAPE_C0')
        self._sb_firc0.showStepExponent = False
        self._fr_firc0 = SiriusFrame(self, self.dev_pref+':SHAPE_C0_SUBWR')
        self._fr_firc0.add_widget(self._sb_firc0)

        self._ld_firc2 = QLabel('C2', self)
        self._sb_firc2 = PyDMSpinbox(self, self.dev_pref+':SHAPE_C2')
        self._sb_firc2.showStepExponent = False
        self._fr_firc2 = SiriusFrame(self, self.dev_pref+':SHAPE_C2_SUBWR')
        self._fr_firc2.add_widget(self._sb_firc2)

        lay_fir = QHBoxLayout()
        lay_fir.addStretch()
        lay_fir.addWidget(self._ld_sfir)
        lay_fir.addStretch()
        lay_fir.addWidget(self._ld_firc0)
        lay_fir.addWidget(self._fr_firc0)
        lay_fir.addStretch()
        lay_fir.addWidget(self._ld_firc2)
        lay_fir.addWidget(self._fr_firc2)
        lay_fir.addStretch()

        lay = QGridLayout(self)
        lay.addWidget(self._ld_maindev, 0, 1, 1, 2)
        lay.addWidget(gbox_delaylines, 1, 1)
        lay.addWidget(gbox_thoff, 1, 2)
        lay.addLayout(lay_fir, 2, 1, 1, 2)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(3, 3)
        lay.setRowStretch(3, 3)

        self.setStyleSheet("""
            SiriusFrame{
                max-height: 1.8em;
            }
        """)


class BbBSlowDACsWidget(QWidget):
    """BbB Slow DACs Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self._ld_dacs = QLabel(
            '<h3>AD5644 DACs</h3>', self, alignment=Qt.AlignCenter)

        self._ld_dacch0 = QLabel('0', self, alignment=Qt.AlignCenter)
        self._ld_dacch0.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._sb_dacch0 = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH0')
        self._sb_dacch0.showStepExponent = False
        self._sb_dacch0.showUnits = True
        self._fr_dacch0 = SiriusFrame(self, self.dev_pref+':AD5644CH0_SUBWR')
        self._fr_dacch0.add_widget(self._sb_dacch0)

        self._ld_dacch1 = QLabel('1', self, alignment=Qt.AlignCenter)
        self._ld_dacch1.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._sb_dacch1 = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH1')
        self._sb_dacch1.showStepExponent = False
        self._sb_dacch1.showUnits = True
        self._fr_dacch1 = SiriusFrame(self, self.dev_pref+':AD5644CH1_SUBWR')
        self._fr_dacch1.add_widget(self._sb_dacch1)

        self._ld_dacch2 = QLabel('2', self, alignment=Qt.AlignCenter)
        self._ld_dacch2.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._sb_dacch2 = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH2')
        self._sb_dacch2.showStepExponent = False
        self._sb_dacch2.showUnits = True
        self._fr_dacch2 = SiriusFrame(self, self.dev_pref+':AD5644CH2_SUBWR')
        self._fr_dacch2.add_widget(self._sb_dacch2)

        self._ld_dacch3 = QLabel('3', self, alignment=Qt.AlignCenter)
        self._ld_dacch3.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._sb_dacch3 = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH3')
        self._sb_dacch3.showStepExponent = False
        self._sb_dacch3.showUnits = True
        self._fr_dacch3 = SiriusFrame(self, self.dev_pref+':AD5644CH3_SUBWR')
        self._fr_dacch3.add_widget(self._sb_dacch3)

        self._ld_dacref0 = QLabel('Ref\n0-3', self, alignment=Qt.AlignCenter)
        self._ld_dacref0.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._cb_dacref0 = PyDMEnumComboBox(
            self, self.dev_pref+':AD5644REF0_BO')

        self._ld_dacch4 = QLabel('4', self, alignment=Qt.AlignCenter)
        self._ld_dacch4.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._sb_dacch4 = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH4')
        self._sb_dacch4.showStepExponent = False
        self._sb_dacch4.showUnits = True
        self._fr_dacch4 = SiriusFrame(self, self.dev_pref+':AD5644CH4_SUBWR')
        self._fr_dacch4.add_widget(self._sb_dacch4)

        self._ld_dacch5 = QLabel('5', self, alignment=Qt.AlignCenter)
        self._ld_dacch5.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._sb_dacch5 = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH5')
        self._sb_dacch5.showStepExponent = False
        self._sb_dacch5.showUnits = True
        self._fr_dacch5 = SiriusFrame(self, self.dev_pref+':AD5644CH5_SUBWR')
        self._fr_dacch5.add_widget(self._sb_dacch5)

        self._ld_dacch6 = QLabel('6', self, alignment=Qt.AlignCenter)
        self._ld_dacch6.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._sb_dacch6 = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH6')
        self._sb_dacch6.showStepExponent = False
        self._sb_dacch6.showUnits = True
        self._fr_dacch6 = SiriusFrame(self, self.dev_pref+':AD5644CH6_SUBWR')
        self._fr_dacch6.add_widget(self._sb_dacch6)

        self._ld_dacch7 = QLabel('7', self, alignment=Qt.AlignCenter)
        self._ld_dacch7.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._sb_dacch7 = PyDMSpinbox(self, self.dev_pref+':AD5644_V_CH7')
        self._sb_dacch7.showStepExponent = False
        self._sb_dacch7.showUnits = True
        self._fr_dacch7 = SiriusFrame(self, self.dev_pref+':AD5644CH7_SUBWR')
        self._fr_dacch7.add_widget(self._sb_dacch7)

        self._ld_dacref1 = QLabel('Ref\n4-7', self, alignment=Qt.AlignCenter)
        self._ld_dacref1.setStyleSheet('font-weight: bold; max-width: 3em;')
        self._cb_dacref1 = PyDMEnumComboBox(
            self, self.dev_pref+':AD5644REF1_BO')

        self._cb_dacmode = PyDMEnumComboBox(
            self, self.dev_pref+':AD5644TEST_BO')

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.setHorizontalSpacing(15)
        lay.setVerticalSpacing(15)
        lay.addWidget(self._ld_dacs, 0, 1, 1, 5)
        lay.addWidget(self._ld_dacch0, 1, 1)
        lay.addWidget(self._fr_dacch0, 1, 2)
        lay.addWidget(self._ld_dacch1, 2, 1)
        lay.addWidget(self._fr_dacch1, 2, 2)
        lay.addWidget(self._ld_dacch2, 3, 1)
        lay.addWidget(self._fr_dacch2, 3, 2)
        lay.addWidget(self._ld_dacch3, 4, 1)
        lay.addWidget(self._fr_dacch3, 4, 2)
        lay.addWidget(self._ld_dacref0, 5, 1)
        lay.addWidget(self._cb_dacref0, 5, 2)
        lay.addWidget(self._ld_dacch4, 1, 4)
        lay.addWidget(self._fr_dacch4, 1, 5)
        lay.addWidget(self._ld_dacch5, 2, 4)
        lay.addWidget(self._fr_dacch5, 2, 5)
        lay.addWidget(self._ld_dacch6, 3, 4)
        lay.addWidget(self._fr_dacch6, 3, 5)
        lay.addWidget(self._ld_dacch7, 4, 4)
        lay.addWidget(self._fr_dacch7, 4, 5)
        lay.addWidget(self._ld_dacref1, 5, 4)
        lay.addWidget(self._cb_dacref1, 5, 5)
        lay.addWidget(self._cb_dacmode, 6, 1, 1, 5)


class BbBADCWidget(QWidget):
    """BbB 8-Channel ADC Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self._ld_adc = QLabel(
            '<h3>8-Channel ADC</h3>', self, alignment=Qt.AlignCenter)

        self._ld_adcch0 = QLabel(
            '<h4>Channel 0</h4>', self, alignment=Qt.AlignCenter)
        self._si_adcch0 = MyScaleIndicator(
            self, self.dev_pref+':MAX1202_CH0')
        self._si_adcch0.showUnits = True
        self._si_adcch0.setObjectName('ch0')
        self._si_adcch0.setStyleSheet(
            '#ch0{min-height:6em; min-width:8em;}')

        self._ld_adcch1 = QLabel(
            '<h4>Channel 1</h4>', self, alignment=Qt.AlignCenter)
        self._si_adcch1 = MyScaleIndicator(
            self, self.dev_pref+':MAX1202_CH1')
        self._si_adcch1.showUnits = True
        self._si_adcch1.setObjectName('ch1')
        self._si_adcch1.setStyleSheet(
            '#ch1{min-height:6em; min-width:8em;}')

        self._ld_adcch2 = QLabel(
            '<h4>Channel 2</h4>', self, alignment=Qt.AlignCenter)
        self._si_adcch2 = MyScaleIndicator(
            self, self.dev_pref+':MAX1202_CH2')
        self._si_adcch2.showUnits = True
        self._si_adcch2.setObjectName('ch2')
        self._si_adcch2.setStyleSheet(
            '#ch2{min-height:6em; min-width:8em;}')

        self._ld_adcch3 = QLabel(
            '<h4>Channel 3</h4>', self, alignment=Qt.AlignCenter)
        self._si_adcch3 = MyScaleIndicator(
            self, self.dev_pref+':MAX1202_CH3')
        self._si_adcch3.showUnits = True
        self._si_adcch3.setObjectName('ch3')
        self._si_adcch3.setStyleSheet(
            '#ch3{min-height:6em; min-width:8em;}')

        self._ld_adcch4 = QLabel(
            '<h4>Channel 4</h4>', self, alignment=Qt.AlignCenter)
        self._si_adcch4 = MyScaleIndicator(
            self, self.dev_pref+':MAX1202_CH4')
        self._si_adcch4.showUnits = True
        self._si_adcch4.setObjectName('ch4')
        self._si_adcch4.setStyleSheet(
            '#ch4{min-height:6em; min-width:8em;}')

        self._ld_adcch5 = QLabel(
            '<h4>Channel 5</h4>', self, alignment=Qt.AlignCenter)
        self._si_adcch5 = MyScaleIndicator(
            self, self.dev_pref+':MAX1202_CH5')
        self._si_adcch5.showUnits = True
        self._si_adcch5.setObjectName('ch5')
        self._si_adcch5.setStyleSheet(
            '#ch5{min-height:6em; min-width:8em;}')

        self._ld_adcch6 = QLabel(
            '<h4>Channel 6</h4>', self, alignment=Qt.AlignCenter)
        self._si_adcch6 = MyScaleIndicator(
            self, self.dev_pref+':MAX1202_CH6')
        self._si_adcch6.showUnits = True
        self._si_adcch6.setObjectName('ch6')
        self._si_adcch6.setStyleSheet(
            '#ch6{min-height:6em; min-width:8em;}')

        self._ld_adcch7 = QLabel(
            '<h4>Channel 7</h4>', self, alignment=Qt.AlignCenter)
        self._si_adcch7 = MyScaleIndicator(
            self, self.dev_pref+':MAX1202_CH7')
        self._si_adcch7.showUnits = True
        self._si_adcch7.setObjectName('ch7')
        self._si_adcch7.setStyleSheet(
            '#ch7{min-height:6em; min-width:8em;}')

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.setHorizontalSpacing(15)
        lay.setVerticalSpacing(15)
        lay.addWidget(self._ld_adc, 0, 0, 1, 4)
        lay.addWidget(self._ld_adcch0, 1, 0)
        lay.addWidget(self._ld_adcch2, 1, 1)
        lay.addWidget(self._ld_adcch4, 1, 2)
        lay.addWidget(self._ld_adcch6, 1, 3)
        lay.addWidget(self._si_adcch0, 2, 0)
        lay.addWidget(self._si_adcch2, 2, 1)
        lay.addWidget(self._si_adcch4, 2, 2)
        lay.addWidget(self._si_adcch6, 2, 3)
        lay.addWidget(self._ld_adcch1, 3, 0)
        lay.addWidget(self._ld_adcch3, 3, 1)
        lay.addWidget(self._ld_adcch5, 3, 2)
        lay.addWidget(self._ld_adcch7, 3, 3)
        lay.addWidget(self._si_adcch1, 4, 0)
        lay.addWidget(self._si_adcch3, 4, 1)
        lay.addWidget(self._si_adcch5, 4, 2)
        lay.addWidget(self._si_adcch7, 4, 3)


class BbBPwrAmpsWidget(QWidget):
    """BbB Power Amplifiers Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        # wid_serial = self._setupSerialAmpWidget()
        # self.addTab(wid_serial, 'Serial/USB amplifier')

        # wid_mm = QWidget()
        # lay_mm = QGridLayout(wid_mm)
        # lay_mm.setContentsMargins(0, 0, 0, 0)
        # lay_mm.addWidget(self._setupMilmegaWidget(0), 0, 0)
        # lay_mm.addWidget(self._setupMilmegaWidget(1), 0, 1)
        # self.addTab(wid_mm, 'Milmegas')

        lay_mc = QGridLayout(self)
        lay_mc.setContentsMargins(0, 0, 0, 0)
        if self._device.endswith('-L'):
            lay_mc.addWidget(self._setupMiniCircWidget(0), 0, 0)
            lay_mc.addWidget(self._setupMiniCircWidget(1), 0, 1)
        # self.addTab(wid_mc, 'Mini-Circuits')

    def _setupSerialAmpWidget(self):
        self._ld_serial = QLabel(
            '<h3>Serial/USB amplifier</h3>', self,
            alignment=Qt.AlignCenter)

        self._ld_lctrl = QLabel('Line Control', self)
        self._bt_lctrl = PyDMStateButton(
            self, self.dev_pref+':SERIAL_CTRL_LINE')

        self._ld_rfctrl = QLabel('RF Control', self)
        self._bt_rfctrl = PyDMStateButton(
            self, self.dev_pref+':SERIAL_CTRL_RF')

        self._ld_pwrfreq = QLabel(
            'Power Meter Calibration Frequency',
            self, alignment=Qt.AlignCenter)
        self._le_pwrfreq = PyDMLineEdit(self, self.dev_pref+':SERIAL_CALFREQ')
        self._le_pwrfreq.showUnits = True

        gbox_ctrl = QGroupBox(self)
        lay_ctrl = QGridLayout(gbox_ctrl)
        lay_ctrl.addWidget(self._ld_lctrl, 0, 0, alignment=Qt.AlignRight)
        lay_ctrl.addWidget(self._bt_lctrl, 0, 1, alignment=Qt.AlignLeft)
        lay_ctrl.addWidget(self._ld_rfctrl, 0, 2, alignment=Qt.AlignRight)
        lay_ctrl.addWidget(self._bt_rfctrl, 0, 3, alignment=Qt.AlignLeft)
        lay_ctrl.addWidget(self._ld_pwrfreq, 1, 0, 1, 2,
                           alignment=Qt.AlignRight)
        lay_ctrl.addWidget(self._le_pwrfreq, 1, 2, 1, 2,
                           alignment=Qt.AlignLeft)
        lay_ctrl.setColumnStretch(0, 1)
        lay_ctrl.setColumnStretch(1, 1)
        lay_ctrl.setColumnStretch(2, 1)
        lay_ctrl.setColumnStretch(3, 1)

        self._ld_fwrpwr = QLabel(
            '<h4>Forward Power</h4>', self, alignment=Qt.AlignCenter)
        self._si_fwrpwr = MyScaleIndicator(self, self.dev_pref+':SERIAL_FWD')
        self._si_fwrpwr.indicatorColor = QColor('blue')
        self._si_fwrpwr.barIndicator = True
        self._si_fwrpwr.showUnits = True
        self._si_fwrpwr.setObjectName('fwrpwr')
        self._si_fwrpwr.setStyleSheet(
            '#fwrpwr{min-height:6em; min-width:8em;}')

        self._ld_revpwr = QLabel(
            '<h4>Reverse Power</h4>', self, alignment=Qt.AlignCenter)
        self._si_revpwr = MyScaleIndicator(self, self.dev_pref+':SERIAL_REV')
        self._si_revpwr.indicatorColor = QColor('red')
        self._si_revpwr.barIndicator = True
        self._si_revpwr.showUnits = True
        self._si_revpwr.setObjectName('revpwr')
        self._si_revpwr.setStyleSheet(
            '#revpwr{min-height:6em; min-width:8em;}')

        self._ld_id = QLabel('ID', self)
        self._lb_id = PyDMLabel(self, self.dev_pref+':SERIAL_ID')
        self._lb_id.displayFormat = PyDMLabel.DisplayFormat.String
        hbox_id = QHBoxLayout()
        hbox_id.setContentsMargins(0, 0, 0, 0)
        hbox_id.addWidget(self._ld_id)
        hbox_id.addWidget(self._lb_id)
        hbox_id.setStretch(0, 1)
        hbox_id.setStretch(1, 5)

        gbox_mon = QGroupBox(self)
        lay_mon = QGridLayout(gbox_mon)
        lay_mon.addWidget(self._ld_fwrpwr, 0, 0)
        lay_mon.addWidget(self._si_fwrpwr, 1, 0)
        lay_mon.addWidget(self._ld_revpwr, 0, 1)
        lay_mon.addWidget(self._si_revpwr, 1, 1)
        lay_mon.addLayout(hbox_id, 2, 0, 1, 2)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.addItem(
            QSpacerItem(10, 1, QSzPlcy.MinimumExpanding, QSzPlcy.Fixed), 0, 0)
        lay.addWidget(self._ld_serial, 0, 1)
        lay.addWidget(gbox_ctrl, 1, 1)
        lay.addWidget(gbox_mon, 2, 1)
        lay.addItem(
            QSpacerItem(10, 10, QSzPlcy.MinimumExpanding,
                        QSzPlcy.MinimumExpanding), 3, 2)
        return wid

    def _setupMilmegaWidget(self, unit):
        unit_label = str(unit)
        ld_mmdb15 = QLabel(
            '<h3>Milmega DB-15 '+unit_label+'</h3>',
            self, alignment=Qt.AlignCenter)
        ld_mmdesc = QLabel(
            'Milmega via DB-15 custom cable\nand '
            '8 channel ADC (unit '+unit_label+')',
            self, alignment=Qt.AlignCenter)

        ld_rfsts = QLabel('RF Status', self)
        led_rfsts = PyDMLed(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_RF')
        led_rfsts.onColor = PyDMLed.LightGreen
        led_rfsts.offColor = PyDMLed.Red
        lb_rfsts = PyDMLabel(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_RF')

        ld_fltlac = QLabel('Fault Latch', self)
        led_fltlac = PyDMLed(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_FAULT')
        led_fltlac.onColor = PyDMLed.LightGreen
        led_fltlac.offColor = PyDMLed.Red
        lb_fltlac = PyDMLabel(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_FAULT')

        ld_slope = QLabel('Slope', self)
        le_slope = PyDMLineEdit(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_SLOPE')
        le_slope.showUnits = True
        ld_offset = QLabel('Offset', self)
        le_offset = PyDMLineEdit(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_OFFSET')
        le_offset.showUnits = True

        gbox_ctrl = QGroupBox(self)
        lay_ctrl = QGridLayout(gbox_ctrl)
        lay_ctrl.addWidget(ld_rfsts, 0, 0)
        lay_ctrl.addWidget(led_rfsts, 0, 1)
        lay_ctrl.addWidget(lb_rfsts, 0, 2)
        lay_ctrl.addWidget(ld_fltlac, 1, 0)
        lay_ctrl.addWidget(led_fltlac, 1, 1)
        lay_ctrl.addWidget(lb_fltlac, 1, 2)
        lay_ctrl.addWidget(ld_slope, 2, 0)
        lay_ctrl.addWidget(le_slope, 2, 1, 1, 2)
        lay_ctrl.addWidget(ld_offset, 3, 0)
        lay_ctrl.addWidget(le_offset, 3, 1, 1, 2)

        ld_fwrpwr = QLabel(
            '<h4>Forward Power</h4>', self, alignment=Qt.AlignCenter)
        si_fwrpwr = MyScaleIndicator(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_FWD')
        si_fwrpwr.barIndicator = True
        si_fwrpwr.indicatorColor = QColor('blue')
        si_fwrpwr.showUnits = True
        si_fwrpwr.setObjectName('fwrpwr')
        si_fwrpwr.setStyleSheet(
            '#fwrpwr{min-height:6em; min-width:8em;}')

        ld_revpwr = QLabel(
            '<h4>Reverse Power</h4>', self, alignment=Qt.AlignCenter)
        si_revpwr = MyScaleIndicator(
            self, self.dev_pref+':MMGRAW_'+unit_label+'_REV')
        si_revpwr.barIndicator = True
        si_revpwr.indicatorColor = QColor('red')
        si_revpwr.showUnits = True
        si_revpwr.setObjectName('revpwr')
        si_revpwr.setStyleSheet(
            '#revpwr{min-height:6em; min-width:8em;}')

        gbox_mon = QGroupBox(self)
        lay_mon = QGridLayout(gbox_mon)
        lay_mon.addWidget(ld_fwrpwr, 0, 0)
        lay_mon.addWidget(si_fwrpwr, 1, 0)
        lay_mon.addWidget(ld_revpwr, 2, 0)
        lay_mon.addWidget(si_revpwr, 3, 0)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.addWidget(ld_mmdb15)
        lay.addWidget(ld_mmdesc)
        lay.addWidget(gbox_ctrl)
        lay.addWidget(gbox_mon)
        return wid

    def _setupMiniCircWidget(self, unit):
        unit_label = str(unit)
        ld_mczt102 = QLabel(
            '<h3>Mini-Circuits Zt-102 '+unit_label+'</h3>',
            self, alignment=Qt.AlignCenter)
        ld_mcdesc = QLabel(
            'Mini-Circuits ZT-102 DE-9\nmonitoring '
            'interface (unit '+unit_label+')', self,
            alignment=Qt.AlignCenter)

        ld_fault = QLabel('RF Status', self)
        led_fault = PyDMLed(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_FAULT')
        led_fault.onColor = PyDMLed.LightGreen
        led_fault.offColor = PyDMLed.Red
        lb_fault = PyDMLabel(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_FAULT')

        ld_temp = QLabel('Temperature', self)
        lb_temp = PyDMLabel(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_TEMP')
        lb_temp.showUnits = True

        ld_fwrloss = QLabel('Fwd Loss', self)
        le_fwrloss = PyDMLineEdit(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_FWDLOSS')
        le_fwrloss.showUnits = True
        ld_revloss = QLabel('Rev Loss', self)
        le_revloss = PyDMLineEdit(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_REVLOSS')
        le_revloss.showUnits = True

        gbox_ctrl = QGroupBox(self)
        lay_ctrl = QGridLayout(gbox_ctrl)
        lay_ctrl.addWidget(ld_fault, 0, 0)
        lay_ctrl.addWidget(led_fault, 0, 1)
        lay_ctrl.addWidget(lb_fault, 0, 2)
        lay_ctrl.addWidget(ld_temp, 1, 0)
        lay_ctrl.addWidget(lb_temp, 1, 1, 1, 2)
        lay_ctrl.addWidget(ld_fwrloss, 2, 0)
        lay_ctrl.addWidget(le_fwrloss, 2, 1, 1, 2)
        lay_ctrl.addWidget(ld_revloss, 3, 0)
        lay_ctrl.addWidget(le_revloss, 3, 1, 1, 2)

        ld_fwrpwr = QLabel(
            '<h4>Forward Power</h4>', self, alignment=Qt.AlignCenter)
        si_fwrpwr = MyScaleIndicator(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_FWD')
        si_fwrpwr.barIndicator = True
        si_fwrpwr.indicatorColor = QColor('blue')
        si_fwrpwr.showUnits = True
        si_fwrpwr.setObjectName('fwrpwr')
        si_fwrpwr.setStyleSheet(
            '#fwrpwr{min-height:6em; min-width:8em;}')

        ld_revpwr = QLabel(
            '<h4>Reverse Power</h4>', self, alignment=Qt.AlignCenter)
        si_revpwr = MyScaleIndicator(
            self, self.dev_pref+':MCLRAW_'+unit_label+'_REV')
        si_revpwr.barIndicator = True
        si_revpwr.indicatorColor = QColor('red')
        si_revpwr.showUnits = True
        si_revpwr.setObjectName('revpwr')
        si_revpwr.setStyleSheet(
            '#revpwr{min-height:6em; min-width:8em;}')

        gbox_mon = QGroupBox(self)
        lay_mon = QGridLayout(gbox_mon)
        lay_mon.addWidget(ld_fwrpwr, 0, 0)
        lay_mon.addWidget(si_fwrpwr, 1, 0)
        lay_mon.addWidget(ld_revpwr, 2, 0)
        lay_mon.addWidget(si_revpwr, 3, 0)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.addWidget(ld_mczt102)
        lay.addWidget(ld_mcdesc)
        lay.addWidget(gbox_ctrl)
        lay.addWidget(gbox_mon)
        return wid


class BbBMasksWidget(QWidget):
    """BbB Masks Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self._ld_exct_masks = QLabel(
            '<h3>Excitation Masks</h3>', self,
            alignment=Qt.AlignCenter)
        self._ld_spec_masks = QLabel(
            '<h3>Spectrum Averaging Masks</h3>', self,
            alignment=Qt.AlignCenter)

        self._graph_exct = WfmGraph(self)
        self._graph_exct.showLegend = True
        self._graph_exct.axisColor = QColor('black')
        self._graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':FB_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Feedback', color=QColor('blue'))
        self._graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':CF_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Alternate', color=QColor('green'))
        self._graph_exct.add_scatter_curve(
            ychannel=self.dev_pref+':DRIVE_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='Drive', color=QColor('red'))

        self._graph_spec = WfmGraph(self)
        self._graph_spec.showLegend = True
        self._graph_spec.axisColor = QColor('black')
        self._graph_spec.add_scatter_curve(
            ychannel=self.dev_pref+':SRAM_ACQ_MASK',
            xchannel=self.dev_pref+':SRAM_XSC',
            name='SRAM', color=QColor('red'))
        self._graph_spec.add_scatter_curve(
            ychannel=self.dev_pref+':BRAM_ACQ_MASK',
            xchannel=self.dev_pref+':BRAM_XSC',
            name='BRAM', color=QColor('blue'))

        lay = QGridLayout(self)
        lay.addWidget(self._ld_exct_masks, 0, 0)
        lay.addWidget(self._graph_exct, 1, 0)
        lay.addItem(QSpacerItem(20, 20), 2, 0)
        lay.addWidget(self._ld_spec_masks, 3, 0)
        lay.addWidget(self._graph_spec, 4, 0)


class BbBInfoWidget(QWidget):
    """BbB Info Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self._ld_sysinfo = QLabel(
            '<h3>System Information</h3>', self, alignment=Qt.AlignCenter)

        self._ld_rffreq = QLabel('Nominal RF Frequency', self)
        self._lb_rffreq = PyDMLabel(self, self.dev_pref+':RF_FREQ')
        self._lb_rffreq.showUnits = True

        self._ld_hn = QLabel('Harmonic Number', self)
        self._lb_hn = PyDMLabel(self, self.dev_pref+':HARM_NUM')

        self._ld_gtwrvw = QLabel('Gateway Revision', self)
        self._lb_gtwrvw = PyDMLabel(self, self.dev_pref+':REVISION')

        self._ld_gtwtyp = QLabel('Gateway Type', self)
        self._lb_gtwtyp = PyDMLabel(self, self.dev_pref+':GW_TYPE')
        self._lb_gtwtyp.displayFormat = PyDMLabel.DisplayFormat.Hex

        self._ld_ipaddr = QLabel('IP Address', self)
        self._lb_ipaddr = PyDMLabel(self, self.dev_pref+':IP_ADDR')

        lay = QGridLayout(self)
        lay.setVerticalSpacing(15)
        lay.addWidget(self._ld_sysinfo, 0, 0, 1, 2)
        lay.addWidget(self._ld_rffreq, 1, 0)
        lay.addWidget(self._lb_rffreq, 1, 1)
        lay.addWidget(self._ld_hn, 2, 0)
        lay.addWidget(self._lb_hn, 2, 1)
        lay.addWidget(self._ld_gtwrvw, 3, 0)
        lay.addWidget(self._lb_gtwrvw, 3, 1)
        lay.addWidget(self._ld_gtwtyp, 4, 0)
        lay.addWidget(self._lb_gtwtyp, 4, 1)
        lay.addWidget(self._ld_ipaddr, 5, 0)
        lay.addWidget(self._lb_ipaddr, 5, 1)

        self.setStyleSheet(
            "PyDMLabel{qproperty-alignment: AlignCenter;}")


if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    w = BbBInfoWidget(
        prefix=_vaca_prefix, device='SI-Glob:DI-BbBProc-H')
    w.show()
    sys.exit(app.exec_())
