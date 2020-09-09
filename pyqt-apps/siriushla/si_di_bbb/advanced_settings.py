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


class BbBAdvancedSettingsWidget(QWidget):
    """BbB Advanced Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self.prefix = prefix
        self.device = device
        self._setupUi()

    def _setupUi(self):
        self._dac_wid = BbBSlowDACsWidget(self, self.prefix, self.device)
        self._adc_wid = BbBADCWidget(self, self.prefix, self.device)
        self._devs_wid = BbBGeneralSettingsWidget(
            self, self.prefix, self.device)

        lay = QGridLayout(self)
        lay.addWidget(self._devs_wid, 1, 1, 1, 3)
        lay.addWidget(self._adc_wid, 3, 1)
        lay.addWidget(self._dac_wid, 3, 3)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(2, 3)
        lay.setColumnStretch(4, 3)
        lay.setRowStretch(0, 3)
        lay.setRowStretch(2, 3)
        lay.setRowStretch(4, 3)


class BbBGeneralSettingsWidget(QWidget):
    """BbB General Settings Widget."""

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
            '<h3>General Settings</h3>', self, alignment=Qt.AlignCenter)

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


if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    w = BbBInfoWidget(
        prefix=_vaca_prefix, device='SI-Glob:DI-BbBProc-H')
    w.show()
    sys.exit(app.exec_())
