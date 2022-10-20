"""BbB Devices Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QGroupBox, QHBoxLayout
import qtawesome as qta
from pydm.widgets import PyDMEnumComboBox

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName

from ..widgets import SiriusFrame, SiriusLabel, SiriusPushButton, SiriusSpinbox

from .custom_widgets import MyScaleIndicator
from .util import set_bbb_color


class BbBAdvancedSettingsWidget(QWidget):
    """BbB Advanced Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self.prefix = prefix
        self.device = device
        self._setupUi()

    def _setupUi(self):
        dac_wid = BbBSlowDACsWidget(self, self.prefix, self.device)
        adc_wid = BbBADCWidget(self, self.prefix, self.device)
        devs_wid = BbBGeneralSettingsWidget(self, self.prefix, self.device)
        intlk = BbBInterlock(self, self.prefix, self.device)

        lay = QGridLayout(self)
        lay.addWidget(devs_wid, 1, 1)
        lay.addWidget(intlk, 1, 3)
        lay.addWidget(adc_wid, 3, 1)
        lay.addWidget(dac_wid, 3, 3)
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
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self._setupUi()

    def _setupUi(self):
        ld_maindev = QLabel(
            '<h3>General Settings</h3>', self, alignment=Qt.AlignCenter)

        # # Delay Lines
        ld_adcclock = QLabel('ADC Clock', self)
        sb_adcclock = SiriusSpinbox(self, self.dev_pref+':ECLDEL0')
        sb_adcclock.showStepExponent = False
        fr_adcclock = SiriusFrame(self, self.dev_pref+':ECLDEL0_SUBWR')
        fr_adcclock.add_widget(sb_adcclock)

        ld_fidclock = QLabel('Fiducial Clock', self)
        sb_fidclock = SiriusSpinbox(self, self.dev_pref+':ECLDEL1')
        sb_fidclock.showStepExponent = False
        fr_fidclock = SiriusFrame(self, self.dev_pref+':ECLDEL1_SUBWR')
        fr_fidclock.add_widget(sb_fidclock)

        ld_fiducial = QLabel('Fiducial', self)
        sb_fiducial = SiriusSpinbox(self, self.dev_pref+':ECLDEL2')
        sb_fiducial.showStepExponent = False
        fr_fiducial = SiriusFrame(self, self.dev_pref+':ECLDEL2_SUBWR')
        fr_fiducial.add_widget(sb_fiducial)

        ld_dacclock = QLabel('DAC Clock', self)
        sb_dacclock = SiriusSpinbox(self, self.dev_pref+':ECLDEL3')
        sb_dacclock.showStepExponent = False
        fr_dacclock = SiriusFrame(self, self.dev_pref+':ECLDEL3_SUBWR')
        fr_dacclock.add_widget(sb_dacclock)

        gbox_delaylines = QGroupBox('Delay lines', self)
        lay_delaylines = QGridLayout(gbox_delaylines)
        lay_delaylines.addWidget(ld_adcclock, 0, 0)
        lay_delaylines.addWidget(fr_adcclock, 0, 1)
        lay_delaylines.addWidget(ld_fidclock, 1, 0)
        lay_delaylines.addWidget(fr_fidclock, 1, 1)
        lay_delaylines.addWidget(ld_fiducial, 2, 0)
        lay_delaylines.addWidget(fr_fiducial, 2, 1)
        lay_delaylines.addWidget(ld_dacclock, 3, 0)
        lay_delaylines.addWidget(fr_dacclock, 3, 1)

        # # Thresholds and offsets
        ld_lvl = QLabel('<h4>Level</h4>', self, alignment=Qt.AlignCenter)
        ld_enbl = QLabel('<h4>Enbl</h4>', self, alignment=Qt.AlignCenter)
        ld_v = QLabel('<h4>V</h4>', self, alignment=Qt.AlignCenter)
        ld_edge = QLabel('<h4>Edge</h4>', self, alignment=Qt.AlignCenter)

        ld_fid = QLabel('Fiducial', self)
        cb_fidlvl = PyDMEnumComboBox(self, self.dev_pref+':LEVEL_FID')
        cb_fidlvlenbl = PyDMEnumComboBox(
            self, self.dev_pref+':LEVEL_FID_ENABLE')
        cb_fidlvlenbl.setStyleSheet('max-width:3em;')
        sb_fidv = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH9')
        sb_fidv.showStepExponent = False
        sb_fidv.showUnits = True
        fr_fidv = SiriusFrame(self, self.dev_pref+':AD5644CH9_SUBWR')
        fr_fidv.add_widget(sb_fidv)

        ld_trg1 = QLabel('Trigger 1', self)
        cb_trg1lvl = PyDMEnumComboBox(self, self.dev_pref+':LEVEL_TRIG1')
        cb_trg1lvlenbl = PyDMEnumComboBox(
            self, self.dev_pref+':LEVEL_TRIG1_ENABLE')
        cb_trg1lvlenbl.setStyleSheet('max-width:3em;')
        sb_trg1lvlv = SiriusSpinbox(self, self.dev_pref+':LEVEL_VTRIG1')
        sb_trg1lvlv.showStepExponent = False
        sb_trg1lvlv.showUnits = True
        fr_trg1lvlv = SiriusFrame(
            self, self.dev_pref+':AD5644CH10_SUBWR')
        fr_trg1lvlv.add_widget(sb_trg1lvlv)
        cb_trg1edge = PyDMEnumComboBox(self, self.dev_pref+':TRIG1INV')
        cb_trg1edge.setStyleSheet('max-width:3.2em;')

        ld_trg2 = QLabel('Trigger 2', self)
        cb_trg2lvl = PyDMEnumComboBox(self, self.dev_pref+':LEVEL_TRIG2')
        cb_trg2lvlenbl = PyDMEnumComboBox(
            self, self.dev_pref+':LEVEL_TRIG2_ENABLE')
        cb_trg2lvlenbl.setStyleSheet('max-width:3em;')
        sb_trg2lvlv = SiriusSpinbox(self, self.dev_pref+':LEVEL_VTRIG2')
        sb_trg2lvlv.showStepExponent = False
        sb_trg2lvlv.showUnits = True
        fr_trg2lvlv = SiriusFrame(self, self.dev_pref+':AD5644CH8_SUBWR')
        fr_trg2lvlv.add_widget(sb_trg2lvlv)
        cb_trg2edge = PyDMEnumComboBox(self, self.dev_pref+':TRIG2INV')
        cb_trg2edge.setStyleSheet('max-width:3.2em;')

        ld_dacoff = QLabel('DAC Offset', self)
        sb_dacoff = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH11')
        sb_dacoff.showStepExponent = False
        sb_dacoff.showUnits = True
        fr_dacoff = SiriusFrame(self, self.dev_pref+':AD5644CH11_SUBWR')
        fr_dacoff.add_widget(sb_dacoff)

        gbox_thoff = QGroupBox('Thresholds and Offsets', self)
        lay_thoff = QGridLayout(gbox_thoff)
        lay_thoff.addWidget(ld_lvl, 0, 1)
        lay_thoff.addWidget(ld_enbl, 0, 2)
        lay_thoff.addWidget(ld_v, 0, 3)
        lay_thoff.addWidget(ld_edge, 0, 4)
        lay_thoff.addWidget(ld_fid, 1, 0)
        lay_thoff.addWidget(cb_fidlvl, 1, 1)
        lay_thoff.addWidget(cb_fidlvlenbl, 1, 2)
        lay_thoff.addWidget(fr_fidv, 1, 3)
        lay_thoff.addWidget(ld_trg1, 2, 0)
        lay_thoff.addWidget(cb_trg1lvl, 2, 1)
        lay_thoff.addWidget(cb_trg1lvlenbl, 2, 2)
        lay_thoff.addWidget(fr_trg1lvlv, 2, 3)
        lay_thoff.addWidget(cb_trg1edge, 2, 4)
        lay_thoff.addWidget(ld_trg2, 3, 0)
        lay_thoff.addWidget(cb_trg2lvl, 3, 1)
        lay_thoff.addWidget(cb_trg2lvlenbl, 3, 2)
        lay_thoff.addWidget(fr_trg2lvlv, 3, 3)
        lay_thoff.addWidget(cb_trg2edge, 3, 4)
        lay_thoff.addWidget(ld_dacoff, 4, 0)
        lay_thoff.addWidget(fr_dacoff, 4, 3)
        lay_thoff.setColumnStretch(0, 3)
        lay_thoff.setColumnStretch(1, 2)
        lay_thoff.setColumnStretch(2, 1)
        lay_thoff.setColumnStretch(3, 5)
        lay_thoff.setColumnStretch(4, 1)

        # # FIR
        ld_sfir = QLabel('Shaper FIR ([C0 2^17 C2])', self)

        ld_firc0 = QLabel('C0', self)
        sb_firc0 = SiriusSpinbox(self, self.dev_pref+':SHAPE_C0')
        sb_firc0.showStepExponent = False
        fr_firc0 = SiriusFrame(self, self.dev_pref+':SHAPE_C0_SUBWR')
        fr_firc0.add_widget(sb_firc0)

        ld_firc2 = QLabel('C2', self)
        sb_firc2 = SiriusSpinbox(self, self.dev_pref+':SHAPE_C2')
        sb_firc2.showStepExponent = False
        fr_firc2 = SiriusFrame(self, self.dev_pref+':SHAPE_C2_SUBWR')
        fr_firc2.add_widget(sb_firc2)

        lay_fir = QHBoxLayout()
        lay_fir.addStretch()
        lay_fir.addWidget(ld_sfir)
        lay_fir.addStretch()
        lay_fir.addWidget(ld_firc0)
        lay_fir.addWidget(fr_firc0)
        lay_fir.addStretch()
        lay_fir.addWidget(ld_firc2)
        lay_fir.addWidget(fr_firc2)
        lay_fir.addStretch()

        lay = QGridLayout(self)
        lay.addWidget(ld_maindev, 0, 1, 1, 2)
        lay.addWidget(gbox_delaylines, 1, 1)
        lay.addWidget(gbox_thoff, 1, 2)
        lay.addLayout(lay_fir, 2, 1, 1, 2)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(3, 3)
        lay.setRowStretch(3, 3)

        self.setStyleSheet("""SiriusFrame{max-height: 1.8em;}""")


class BbBSlowDACsWidget(QWidget):
    """BbB Slow DACs Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self._setupUi()

    def _setupUi(self):
        ld_dacs = QLabel(
            '<h3>AD5644 DACs</h3>', self, alignment=Qt.AlignCenter)

        ld_dacch0 = QLabel('0', self, alignment=Qt.AlignCenter)
        ld_dacch0.setStyleSheet('font-weight: bold; max-width: 3em;')
        sb_dacch0 = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH0')
        sb_dacch0.showStepExponent = False
        sb_dacch0.showUnits = True
        fr_dacch0 = SiriusFrame(self, self.dev_pref+':AD5644CH0_SUBWR')
        fr_dacch0.add_widget(sb_dacch0)

        ld_dacch1 = QLabel('1', self, alignment=Qt.AlignCenter)
        ld_dacch1.setStyleSheet('font-weight: bold; max-width: 3em;')
        sb_dacch1 = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH1')
        sb_dacch1.showStepExponent = False
        sb_dacch1.showUnits = True
        fr_dacch1 = SiriusFrame(self, self.dev_pref+':AD5644CH1_SUBWR')
        fr_dacch1.add_widget(sb_dacch1)

        ld_dacch2 = QLabel('2', self, alignment=Qt.AlignCenter)
        ld_dacch2.setStyleSheet('font-weight: bold; max-width: 3em;')
        sb_dacch2 = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH2')
        sb_dacch2.showStepExponent = False
        sb_dacch2.showUnits = True
        fr_dacch2 = SiriusFrame(self, self.dev_pref+':AD5644CH2_SUBWR')
        fr_dacch2.add_widget(sb_dacch2)

        ld_dacch3 = QLabel('3', self, alignment=Qt.AlignCenter)
        ld_dacch3.setStyleSheet('font-weight: bold; max-width: 3em;')
        sb_dacch3 = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH3')
        sb_dacch3.showStepExponent = False
        sb_dacch3.showUnits = True
        fr_dacch3 = SiriusFrame(self, self.dev_pref+':AD5644CH3_SUBWR')
        fr_dacch3.add_widget(sb_dacch3)

        ld_dacref0 = QLabel('Ref\n0-3', self, alignment=Qt.AlignCenter)
        ld_dacref0.setStyleSheet('font-weight: bold; max-width: 3em;')
        cb_dacref0 = PyDMEnumComboBox(self, self.dev_pref+':AD5644REF0_BO')

        ld_dacch4 = QLabel('4', self, alignment=Qt.AlignCenter)
        ld_dacch4.setStyleSheet('font-weight: bold; max-width: 3em;')
        sb_dacch4 = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH4')
        sb_dacch4.showStepExponent = False
        sb_dacch4.showUnits = True
        fr_dacch4 = SiriusFrame(self, self.dev_pref+':AD5644CH4_SUBWR')
        fr_dacch4.add_widget(sb_dacch4)

        ld_dacch5 = QLabel('5', self, alignment=Qt.AlignCenter)
        ld_dacch5.setStyleSheet('font-weight: bold; max-width: 3em;')
        sb_dacch5 = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH5')
        sb_dacch5.showStepExponent = False
        sb_dacch5.showUnits = True
        fr_dacch5 = SiriusFrame(self, self.dev_pref+':AD5644CH5_SUBWR')
        fr_dacch5.add_widget(sb_dacch5)

        ld_dacch6 = QLabel('6', self, alignment=Qt.AlignCenter)
        ld_dacch6.setStyleSheet('font-weight: bold; max-width: 3em;')
        sb_dacch6 = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH6')
        sb_dacch6.showStepExponent = False
        sb_dacch6.showUnits = True
        fr_dacch6 = SiriusFrame(self, self.dev_pref+':AD5644CH6_SUBWR')
        fr_dacch6.add_widget(sb_dacch6)

        ld_dacch7 = QLabel('7', self, alignment=Qt.AlignCenter)
        ld_dacch7.setStyleSheet('font-weight: bold; max-width: 3em;')
        sb_dacch7 = SiriusSpinbox(self, self.dev_pref+':AD5644_V_CH7')
        sb_dacch7.showStepExponent = False
        sb_dacch7.showUnits = True
        fr_dacch7 = SiriusFrame(self, self.dev_pref+':AD5644CH7_SUBWR')
        fr_dacch7.add_widget(sb_dacch7)

        ld_dacref1 = QLabel('Ref\n4-7', self, alignment=Qt.AlignCenter)
        ld_dacref1.setStyleSheet('font-weight: bold; max-width: 3em;')
        cb_dacref1 = PyDMEnumComboBox(self, self.dev_pref+':AD5644REF1_BO')

        cb_dacmode = PyDMEnumComboBox(self, self.dev_pref+':AD5644TEST_BO')

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.setHorizontalSpacing(15)
        lay.setVerticalSpacing(15)
        lay.addWidget(ld_dacs, 0, 1, 1, 5)
        lay.addWidget(ld_dacch0, 1, 1)
        lay.addWidget(fr_dacch0, 1, 2)
        lay.addWidget(ld_dacch1, 2, 1)
        lay.addWidget(fr_dacch1, 2, 2)
        lay.addWidget(ld_dacch2, 3, 1)
        lay.addWidget(fr_dacch2, 3, 2)
        lay.addWidget(ld_dacch3, 4, 1)
        lay.addWidget(fr_dacch3, 4, 2)
        lay.addWidget(ld_dacref0, 5, 1)
        lay.addWidget(cb_dacref0, 5, 2)
        lay.addWidget(ld_dacch4, 1, 4)
        lay.addWidget(fr_dacch4, 1, 5)
        lay.addWidget(ld_dacch5, 2, 4)
        lay.addWidget(fr_dacch5, 2, 5)
        lay.addWidget(ld_dacch6, 3, 4)
        lay.addWidget(fr_dacch6, 3, 5)
        lay.addWidget(ld_dacch7, 4, 4)
        lay.addWidget(fr_dacch7, 4, 5)
        lay.addWidget(ld_dacref1, 5, 4)
        lay.addWidget(cb_dacref1, 5, 5)
        lay.addWidget(cb_dacmode, 6, 1, 1, 5)


class BbBADCWidget(QWidget):
    """BbB 8-Channel ADC Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self._setupUi()

    def _setupUi(self):
        ld_adc = QLabel(
            '<h3>8-Channel ADC</h3>', self, alignment=Qt.AlignCenter)

        ld_adcch0 = QLabel(
            '<h4>Channel 0</h4>', self, alignment=Qt.AlignCenter)
        si_adcch0 = MyScaleIndicator(self, self.dev_pref+':MAX1202_CH0')
        si_adcch0.showUnits = True
        si_adcch0.setObjectName('ch0')
        si_adcch0.setStyleSheet('#ch0{min-height:6em; min-width:8em;}')

        ld_adcch1 = QLabel(
            '<h4>Channel 1</h4>', self, alignment=Qt.AlignCenter)
        si_adcch1 = MyScaleIndicator(self, self.dev_pref+':MAX1202_CH1')
        si_adcch1.showUnits = True
        si_adcch1.setObjectName('ch1')
        si_adcch1.setStyleSheet('#ch1{min-height:6em; min-width:8em;}')

        ld_adcch2 = QLabel(
            '<h4>Channel 2</h4>', self, alignment=Qt.AlignCenter)
        si_adcch2 = MyScaleIndicator(self, self.dev_pref+':MAX1202_CH2')
        si_adcch2.showUnits = True
        si_adcch2.setObjectName('ch2')
        si_adcch2.setStyleSheet('#ch2{min-height:6em; min-width:8em;}')

        ld_adcch3 = QLabel(
            '<h4>Channel 3</h4>', self, alignment=Qt.AlignCenter)
        si_adcch3 = MyScaleIndicator(self, self.dev_pref+':MAX1202_CH3')
        si_adcch3.showUnits = True
        si_adcch3.setObjectName('ch3')
        si_adcch3.setStyleSheet('#ch3{min-height:6em; min-width:8em;}')

        ld_adcch4 = QLabel(
            '<h4>Channel 4</h4>', self, alignment=Qt.AlignCenter)
        si_adcch4 = MyScaleIndicator(self, self.dev_pref+':MAX1202_CH4')
        si_adcch4.showUnits = True
        si_adcch4.setObjectName('ch4')
        si_adcch4.setStyleSheet('#ch4{min-height:6em; min-width:8em;}')

        ld_adcch5 = QLabel(
            '<h4>Channel 5</h4>', self, alignment=Qt.AlignCenter)
        si_adcch5 = MyScaleIndicator(self, self.dev_pref+':MAX1202_CH5')
        si_adcch5.showUnits = True
        si_adcch5.setObjectName('ch5')
        si_adcch5.setStyleSheet('#ch5{min-height:6em; min-width:8em;}')

        ld_adcch6 = QLabel(
            '<h4>Channel 6</h4>', self, alignment=Qt.AlignCenter)
        si_adcch6 = MyScaleIndicator(self, self.dev_pref+':MAX1202_CH6')
        si_adcch6.showUnits = True
        si_adcch6.setObjectName('ch6')
        si_adcch6.setStyleSheet('#ch6{min-height:6em; min-width:8em;}')

        ld_adcch7 = QLabel(
            '<h4>Channel 7</h4>', self, alignment=Qt.AlignCenter)
        si_adcch7 = MyScaleIndicator(self, self.dev_pref+':MAX1202_CH7')
        si_adcch7.showUnits = True
        si_adcch7.setObjectName('ch7')
        si_adcch7.setStyleSheet('#ch7{min-height:6em; min-width:8em;}')

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.setHorizontalSpacing(15)
        lay.setVerticalSpacing(15)
        lay.addWidget(ld_adc, 0, 0, 1, 4)
        lay.addWidget(ld_adcch0, 1, 0)
        lay.addWidget(ld_adcch2, 1, 1)
        lay.addWidget(ld_adcch4, 1, 2)
        lay.addWidget(ld_adcch6, 1, 3)
        lay.addWidget(si_adcch0, 2, 0)
        lay.addWidget(si_adcch2, 2, 1)
        lay.addWidget(si_adcch4, 2, 2)
        lay.addWidget(si_adcch6, 2, 3)
        lay.addWidget(ld_adcch1, 3, 0)
        lay.addWidget(ld_adcch3, 3, 1)
        lay.addWidget(ld_adcch5, 3, 2)
        lay.addWidget(ld_adcch7, 3, 3)
        lay.addWidget(si_adcch1, 4, 0)
        lay.addWidget(si_adcch3, 4, 1)
        lay.addWidget(si_adcch5, 4, 2)
        lay.addWidget(si_adcch7, 4, 3)


class BbBInterlock(QWidget):
    """BbB Interlock Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self._setupUi()

    def _setupUi(self):
        ld_intlk = QLabel(
            '<h3>Interlock Controls</h3>', self, alignment=Qt.AlignCenter)

        ld_sp = QLabel('Setpoint', self, alignment=Qt.AlignCenter)
        # ld_sp.setStyleSheet('font-weight: bold; max-width: 3em;')
        ld_cyc = QLabel('RF/4 Cycles', self, alignment=Qt.AlignCenter)
        # ld_cyc.setStyleSheet('font-weight: bold; max-width: 3em;')

        ld_sat = QLabel('Saturation Time', self)
        sb_sat = SiriusSpinbox(self, self.dev_pref+':ILOCK_TSAT')
        sb_sat.showStepExponent = False
        sb_sat.showUnits = True
        lb_sat = SiriusLabel(self, self.dev_pref+':ILOCK_TSAT_T2C')
        lb_sat.setAlignment(Qt.AlignCenter)

        ld_tim = QLabel('Timeout', self)
        sb_tim = SiriusSpinbox(self, self.dev_pref+':ILOCK_TOUT')
        sb_tim.showStepExponent = False
        sb_tim.showUnits = True
        lb_tim = SiriusLabel(self, self.dev_pref+':ILOCK_TOUT_T2C')
        lb_tim.setAlignment(Qt.AlignCenter)

        pvn = self.dev_pref+':ILOCK_TRIPPED'
        lb_sts = SiriusLabel(self, init_channel=pvn)
        lb_sts.enum_strings = ['Status Ok', 'Interlocked']
        lb_sts.displayFormat = lb_sts.DisplayFormat.String
        fr_sts = SiriusFrame(self, pvn, is_float=True)
        fr_sts.borderWidth = 2
        fr_sts.add_widget(lb_sts)
        pb_rst = SiriusPushButton(
            self, init_channel=self.dev_pref+':ILOCK_RESET', pressValue=1,
            releaseValue=0)
        pb_rst.setText('Reset')
        pb_rst.setToolTip('Reset Counts')
        pb_rst.setIcon(qta.icon('fa5s.sync'))
        wd_sts = QWidget(self)
        wd_sts.setLayout(QHBoxLayout())
        wd_sts.layout().addStretch()
        wd_sts.layout().addWidget(fr_sts)
        wd_sts.layout().addStretch()
        wd_sts.layout().addWidget(pb_rst)
        wd_sts.layout().addStretch()

        ld_sens = QLabel(
            '<h3>Sensitivity Controls</h3>', self, alignment=Qt.AlignCenter)

        ld_tun = QLabel('Fractional Tune', self)
        sb_tun = SiriusSpinbox(self, self.dev_pref+':ILOCK_TUNE')
        sb_tun.showStepExponent = False
        sb_tun.showUnits = True

        ld_tap = QLabel('Filter Taps', self)
        sb_tap = SiriusSpinbox(self, self.dev_pref+':ILOCK_TAPS')
        sb_tap.showStepExponent = False
        sb_tap.showUnits = True

        ld_cal = QLabel('Calibration', self)
        sb_cal = SiriusSpinbox(self, self.dev_pref+':ILOCK_FE_CAL')
        sb_cal.showStepExponent = False
        sb_cal.showUnits = True

        ld_ncur = QLabel('Nominal Current', self)
        sb_ncur = SiriusSpinbox(self, self.dev_pref+':ILOCK_CURRENT')
        sb_ncur.showStepExponent = False
        sb_ncur.showUnits = True

        ld_thr = QLabel('Threshold', self)
        sb_thr = SiriusSpinbox(self, self.dev_pref+':ILOCK_THRESH')
        sb_thr.showStepExponent = False
        sb_thr.showUnits = True

        pb_upt = SiriusPushButton(
            self, init_channel=self.dev_pref+':ILOCK_UPDATE', pressValue=1,
            releaseValue=0)
        pb_upt.setText('Update Filter')
        pb_upt.setToolTip('Update Filter Config')
        pb_upt.setIcon(qta.icon('mdi.sync'))
        pb_upt.setStyleSheet("icon-size:20px;")

        pb_ld = SiriusPushButton(
            self, init_channel=self.dev_pref+':BO_CPCOEFF', pressValue=1,
            releaseValue=0)
        pb_ld.setText('Apply Filter')
        pb_ld.setToolTip('Apply Filter Config to Feedback')
        pb_ld.setIcon(qta.icon('mdi.upload'))
        pb_ld.setStyleSheet("icon-size:20px;")

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        lay.addWidget(ld_intlk, 0, 0, 1, 5)
        lay.addWidget(ld_sp, 1, 1)
        lay.addWidget(ld_cyc, 1, 2)
        lay.addWidget(ld_sat, 2, 0)
        lay.addWidget(sb_sat, 2, 1)
        lay.addWidget(lb_sat, 2, 2)
        lay.addWidget(ld_tim, 3, 0)
        lay.addWidget(sb_tim, 3, 1)
        lay.addWidget(lb_tim, 3, 2)
        lay.addWidget(wd_sts, 4, 0, 1, 3)
        lays = QGridLayout()
        lays.addWidget(ld_sens, 0, 0, 1, 4)
        lays.addWidget(ld_tun, 1, 0)
        lays.addWidget(sb_tun, 1, 1)
        lays.addWidget(ld_tap, 2, 0)
        lays.addWidget(sb_tap, 2, 1)
        lays.addWidget(ld_cal, 3, 0)
        lays.addWidget(sb_cal, 3, 1)
        lays.addWidget(ld_ncur, 4, 0)
        lays.addWidget(sb_ncur, 4, 1)
        lays.addWidget(ld_thr, 1, 2)
        lays.addWidget(sb_thr, 1, 3)
        lays.addWidget(pb_upt, 3, 2, 1, 2)
        lays.addWidget(pb_ld, 4, 2, 1, 2)
        lay.addLayout(lays, 5, 0, 1, 3)
