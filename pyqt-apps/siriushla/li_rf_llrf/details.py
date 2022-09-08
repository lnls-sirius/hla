"""LILLRF Device Detail Windows."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QFrame, QGridLayout, QGroupBox, QWidget

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from ..widgets import SiriusMainWindow, PyDMStateButton, SiriusLedState, \
    SiriusSpinbox, SiriusLabel
from .widgets import DeltaIQPhaseCorrButton


class DeviceParamSettingWindow(SiriusMainWindow):
    """Device Parameter Setting Window."""

    def __init__(self, parent=None, device=None, main_dev='', prefix=_VACA_PREFIX):
        """Init."""
        super().__init__(parent)

        self.prefix = prefix + ('-' if prefix else '')
        self.main_dev = main_dev
        self.dev = device
        self.devpref = self.prefix + self.main_dev + self.dev.pvname

        self.setObjectName('LIApp')
        self.setWindowTitle(self.dev.label + ' Parameter Setting')

        self._setupUi()

    def _setupUi(self):
        self.title = QLabel(
            '<h3>'+self.dev.label+' Parameter Setting</h3>', self)

        wid_delay = self._setupDelaySettingWidget()
        wid_pi = self._setupPISettingWidget()
        wid_iqcorr = self._setupIQCorrectionWidget()
        wid_att = self._setupAttenuationWidget()
        wid_attcomp = self._setupAttCompensationWidget()

        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0, 1, 4)
        lay.addWidget(wid_delay, 1, 0)
        lay.addWidget(wid_pi, 2, 0)
        lay.addWidget(wid_iqcorr, 1, 1)
        lay.addWidget(wid_att, 1, 2)
        lay.addWidget(wid_attcomp, 1, 3)

        wid.setStyleSheet("""
            SiriusSpinbox{
                min-width: 4em;
            };
            SiriusLabel{
                min-width: 4em;
            };
        """)

    def _setupDelaySettingWidget(self):
        props = [
            ('Trigger', 'TRIGGER_DELAY'),
            ('Refer_'+self.dev.nickname, 'CH7_DELAY'),
            ('VM_'+self.dev.nickname, 'CH8_DELAY'),
            ('SSA_'+self.dev.nickname, 'CH2_DELAY'),
        ]
        if self.dev.nickname == 'SHB':
            props.append(('Pick-Up', 'CH1_DELAY'))
        elif self.dev.nickname == 'K1':
            props.extend([
                (self.dev.nickname+' Fwd', 'CH1_DELAY'),
                (self.dev.nickname+' Reflec', 'CH9_DELAY'),
                ('Buncher Input', 'CH3_DELAY'),
                ('A1 Input', 'CH4_DELAY'),
                ('A2 Input', 'CH5_DELAY'),
                ('Buncher Output', 'CH6_DELAY')])
        elif self.dev.nickname == 'K2':
            props.extend([
                (self.dev.nickname+' Fwd', 'CH1_DELAY'),
                (self.dev.nickname+' Reflec', 'CH9_DELAY'),
                ('A3 Input', 'CH3_DELAY'),
                ('A4 Input', 'CH4_DELAY'),
                ('A3 Output', 'CH5_DELAY'),
                ('A4 Output', 'CH6_DELAY')])

        wid = QGroupBox('Delay Setting')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        row = 0
        lb_sett = QLabel('<h4>Settings</h4>', self, alignment=Qt.AlignCenter)
        lb_actl = QLabel('<h4>Actual</h4>', self, alignment=Qt.AlignCenter)
        lay.addWidget(lb_sett, row, 1)
        lay.addWidget(lb_actl, row, 2)

        row += 1
        lim_label = '0~4095' if self.dev.nickname == 'SHB' else '0~1023'
        lb_lim1 = QLabel(lim_label, self, alignment=Qt.AlignCenter)
        lb_unit = QLabel('clk', self, alignment=Qt.AlignCenter)
        lay.addWidget(lb_lim1, row, 1)
        lay.addWidget(lb_unit, row, 2)

        for name, prop in props:
            row += 1
            laba = QLabel(name, self)
            sppv = self.devpref + ':SET_' + prop
            rbpv = self.devpref + ':GET_' + prop
            spa = SiriusSpinbox(self, init_channel=sppv)
            spa.showStepExponent = False
            rba = SiriusLabel(self, init_channel=rbpv)
            lay.addWidget(laba, row, 0)
            lay.addWidget(spa, row, 1)
            lay.addWidget(rba, row, 2)

            if name == 'Trigger' and self.dev.nickname == 'SHB':
                row += 1
                lb_lim2 = QLabel('0~1023', self, alignment=Qt.AlignCenter)
                lay.addWidget(lb_lim2, row, 1)

        return wid

    def _setupPISettingWidget(self):
        wid = QGroupBox('PI Setting')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        row = 0
        lb_sett = QLabel('<h4>Settings</h4>', self, alignment=Qt.AlignCenter)
        lb_actl = QLabel('<h4>Actual</h4>', self, alignment=Qt.AlignCenter)
        lay.addWidget(lb_sett, row, 1)
        lay.addWidget(lb_actl, row, 2)

        row += 1
        lb_lim = QLabel('0~1023', self, alignment=Qt.AlignCenter)
        lay.addWidget(lb_lim, row, 1)

        for prop in ['KP', 'KI']:
            row += 1
            laba = QLabel(prop, self)
            sppv = self.devpref + ':SET_' + prop
            rbpv = self.devpref + ':GET_' + prop
            spa = SiriusSpinbox(self, init_channel=sppv)
            spa.showStepExponent = False
            rba = SiriusLabel(self, init_channel=rbpv)
            lay.addWidget(laba, row, 0)
            lay.addWidget(spa, row, 1)
            lay.addWidget(rba, row, 2)

        row += 1
        lab1 = QLabel('Integral', self)
        sppv = self.devpref + ':SET_INTEGRAL_ENABLE'
        rbpv = self.devpref + ':GET_INTEGRAL_ENABLE'
        sp1 = PyDMStateButton(self, init_channel=sppv)
        rb1 = SiriusLedState(self, init_channel=rbpv)
        lay.addWidget(lab1, row, 0)
        lay.addWidget(sp1, row, 1)
        lay.addWidget(rb1, row, 2)

        return wid

    def _setupIQCorrectionWidget(self):
        props = list()
        props.extend([
            ('Refer_'+self.dev.nickname, 'CH7_PHASE_CORR'),
            ('VM_'+self.dev.nickname, 'CH8_PHASE_CORR'),
            ('SSA_'+self.dev.nickname, 'CH2_PHASE_CORR')])
        if self.dev.nickname == 'SHB':
            props.append(('Pick-Up', 'CH1_PHASE_CORR'))
        elif self.dev.nickname == 'K1':
            props.extend([
                (self.dev.nickname+' Fwd', 'CH1_PHASE_CORR'),
                ('Buncher Input', 'CH3_PHASE_CORR'),
                ('A1 Input', 'CH4_PHASE_CORR'),
                ('A2 Input', 'CH5_PHASE_CORR'),
                ('Buncher Output', 'CH6_PHASE_CORR')])
        elif self.dev.nickname == 'K2':
            props.extend([
                (self.dev.nickname+' Fwd', 'CH1_PHASE_CORR'),
                ('A3 Input', 'CH3_PHASE_CORR'),
                ('A4 Input', 'CH4_PHASE_CORR'),
                ('A3 Output', 'CH5_PHASE_CORR'),
                ('A4 Output', 'CH6_PHASE_CORR')])
        props.extend([
            ('VM Cal Phase', 'FBLOOP_PHASE_CORR'),
            ('VM Cal Amp', 'FBLOOP_AMP_CORR')])

        wid = QGroupBox('IQ Correction')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        row = 0
        lb_sett = QLabel('<h4>Settings</h4>', self, alignment=Qt.AlignCenter)
        lb_actl = QLabel('<h4>Actual</h4>', self, alignment=Qt.AlignCenter)
        lay.addWidget(lb_sett, row, 2)
        lay.addWidget(lb_actl, row, 4)

        row += 1
        lb_lim = QLabel('-180.0°~+180.0°', self, alignment=Qt.AlignCenter)
        lay.addWidget(lb_lim, row, 2, 1, 3)

        for name, prop in props:
            row += 1
            laba = QLabel(name, self)
            lay.addWidget(laba, row, 0)

            sppv = self.devpref + ':SET_' + prop
            rbpv = self.devpref + ':GET_' + prop
            spa = SiriusSpinbox(self, init_channel=sppv)
            spa.showStepExponent = False
            spa.precisionFromPV = False
            spa.precision = 2
            lay.addWidget(spa, row, 2)
            if prop == 'CH1_PHASE_CORR':
                dniqc = DeltaIQPhaseCorrButton(
                    self, self.dev.pvname, main_dev=self.main_dev,
                    delta=-90, show_label=False, prefix=self.prefix)
                dpiqc = DeltaIQPhaseCorrButton(
                    self, self.dev.pvname, main_dev=self.main_dev,
                    delta=90, show_label=False, prefix=self.prefix)
                lay.addWidget(dniqc, row, 1)
                lay.addWidget(dpiqc, row, 3)

            rba = SiriusLabel(self, init_channel=rbpv)
            rba.precisionFromPV = False
            rba.precision = 2
            lay.addWidget(rba, row, 4)

            if name == 'VM Cal Phase':
                row += 1
                line = QFrame(self)
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                lay.addWidget(line, row, 0, 1, 5)

        lay.setColumnStretch(0, 5)
        lay.setColumnStretch(1, 1)
        lay.setColumnStretch(2, 4)
        lay.setColumnStretch(3, 1)
        lay.setColumnStretch(4, 4)

        self.setStyleSheet(
            "DeltaIQPhaseCorrButton{max-width: 1.2em;}")

        return wid

    def _setupAttenuationWidget(self):
        props = [
            ('VM', 'VM_ADT', 0.25),
            ('Refer_'+self.dev.nickname, 'CH7_ADT', 0.5),
            ('VM_'+self.dev.nickname, 'CH8_ADT', 0.5),
            ('SSA_'+self.dev.nickname, 'CH2_ADT', 0.5),
        ]
        if self.dev.nickname == 'SHB':
            props.append(('Pick-Up', 'CH1_ADT', 0.5))
        elif self.dev.nickname == 'K1':
            props.extend([
                (self.dev.nickname+' Fwd', 'CH1_ADT', 0.5),
                ('Buncher Input', 'CH3_ADT', 0.5),
                ('A1 Input', 'CH4_ADT', 0.5),
                ('A2 Input', 'CH5_ADT', 0.5),
                ('Buncher Output', 'CH6_ADT', 0.5)])
        elif self.dev.nickname == 'K2':
            props.extend([
                (self.dev.nickname+' Fwd', 'CH1_ADT', 0.5),
                ('A3 Input', 'CH3_ADT', 0.5),
                ('A4 Input', 'CH4_ADT', 0.5),
                ('A3 Output', 'CH5_ADT', 0.5),
                ('A4 Output', 'CH6_ADT', 0.5)])

        wid = QGroupBox('Attenuation')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        row = 0
        lb_lim = QLabel('0~63', self, alignment=Qt.AlignCenter)
        lb_unit = QLabel('dB', self, alignment=Qt.AlignCenter)
        lay.addWidget(lb_lim, row, 1)
        lay.addWidget(lb_unit, row, 2)

        for name, prop, factor in props:
            row += 1
            laba = QLabel(name, self)
            sppv = self.devpref + ':SET_' + prop
            spa = SiriusSpinbox(self, init_channel=sppv)
            spa.showStepExponent = False
            dsc = QLabel('*'+str(factor))
            lay.addWidget(laba, row, 0)
            lay.addWidget(spa, row, 1)
            lay.addWidget(dsc, row, 2)

        return wid

    def _setupAttCompensationWidget(self):
        props = [
            ('Refer_'+self.dev.nickname, 'CH7_ATT'),
            ('VM_'+self.dev.nickname, 'CH8_ATT'),
            ('SSA_'+self.dev.nickname, 'CH2_ATT'),
        ]
        if self.dev.nickname == 'SHB':
            props.append(('Pick-Up', 'CH1_ATT'))
        elif self.dev.nickname == 'K1':
            props.extend([
                (self.dev.nickname+' Fwd', 'CH1_ATT'),
                (self.dev.nickname+' Reflec', 'CH9_ATT'),
                ('Buncher Input', 'CH3_ATT'),
                ('A1 Input', 'CH4_ATT'),
                ('A2 Input', 'CH5_ATT'),
                ('Buncher Output', 'CH6_ATT')])
        elif self.dev.nickname == 'K2':
            props.extend([
                (self.dev.nickname+' Fwd', 'CH1_ATT'),
                (self.dev.nickname+' Reflec', 'CH9_ATT'),
                ('A3 Input', 'CH3_ATT'),
                ('A4 Input', 'CH4_ATT'),
                ('A3 Output', 'CH5_ATT'),
                ('A4 Output', 'CH6_ATT')])

        wid = QGroupBox('Att. Compensation')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        row = 0
        lb_lim = QLabel('(0.00~200.00)', self, alignment=Qt.AlignCenter)
        lay.addWidget(lb_lim, row, 1)

        for name, prop in props:
            row += 1
            laba = QLabel(name, self)
            sppv = self.devpref + ':SET_' + prop
            spa = SiriusSpinbox(self, init_channel=sppv)
            spa.showStepExponent = False
            spa.precisionFromPV = False
            spa.precision = 2
            lay.addWidget(laba, row, 0)
            lay.addWidget(spa, row, 1)

        return wid
