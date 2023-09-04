"""BPM Settings."""

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QPushButton, QGroupBox, QWidget, QScrollArea
from qtpy.QtCore import Qt

from siriuspy.diagbeam.bpm.csdev import Const as _csbpm

from siriushla import util
from siriushla.widgets import PyDMStateButton, SiriusLedState, \
    SiriusLedAlert, SiriusLineEdit, SiriusLabel
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms.base import BaseWidget, CustomGroupBox
from siriushla.common.afc_acq_core import PhysicalTriggers, LogicalTriggers


class ParamsSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('<h2>' + self.bpm + ' Settings</h2>')
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.addSpacing(10)

        hbl = QHBoxLayout()
        hbl.setSpacing(15)
        hbl.addStretch()
        grpbx = CustomGroupBox('Status', self)
        gdl = QGridLayout(grpbx)
        props = (
            ('RFFEasyn.CNCT', 'RFFE Connected'),
            ('ADCAD9510PllStatus-Mon', 'ADC Clock Synched'))
        for i, prop in enumerate(props):
            led = SiriusLedState(grpbx, init_channel=self.get_pvname(prop[0]))
            led.setOffColor(led.Red)
            lab = QLabel(prop[1], grpbx)
            gdl.addWidget(led, i, 0)
            gdl.addWidget(lab, i, 1)
        hbl.addWidget(grpbx)
        hbl.addStretch()

        grpbx = CustomGroupBox('Advanced Settings', self)
        vbl2 = QVBoxLayout(grpbx)
        vbl2.setSpacing(10)
        pbt = QPushButton('BPM')
        Window = create_window_from_widget(
            BPMAdvancedSettings, title=self.bpm+' Advanced Settings')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        vbl2.addWidget(pbt)
        pbt = QPushButton('RFFE')
        Window = create_window_from_widget(
            RFFEAdvancedSettings, title=self.bpm+':RFFE Advanced Settings')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        vbl2.addWidget(pbt)
        pbt = QPushButton('Hardware')
        Window = create_window_from_widget(
            HardwareSettings, title=self.bpm+': Hardware Settings')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        vbl2.addWidget(pbt)
        hbl.addWidget(grpbx)
        hbl.addStretch()
        vbl.addItem(hbl)
        vbl.addSpacing(20)
        vbl.addStretch()

        grpbx = self._create_formlayout_groupbox('Offset Parameters', (
            ('PosQOffset-SP', 'Offset PosQ', ['lineedit', 'label']),
            ('PosXOffset-SP', 'Offset PosX', ['lineedit', 'label']),
            ('PosYOffset-SP', 'Offset PosY', ['lineedit', 'label'])))
        vbl.addWidget(grpbx)
        vbl.addSpacing(20)
        vbl.addStretch()
        grpbx = self._create_formlayout_groupbox('Gain Parameters', (
            ('PosKq-SP', 'Gain PosQ', ['lineedit', 'label']),
            ('PosKsum-SP', 'Gain Sum', ['lineedit', 'label']),
            ('PosKx-SP', 'Gain PosX', ['lineedit', 'label']),
            ('PosKy-SP', 'Gain PosY', ['lineedit', 'label'])))
        vbl.addWidget(grpbx)
        vbl.addSpacing(20)
        vbl.addStretch()
        grpbx = self._create_formlayout_groupbox('Informations', (
            ('INFOHarmonicNumber-RB', 'Harmonic Number'),
            ('INFOMONITRate-RB', 'Monitor Rate'),
            ('INFOFAcqRate-RB', 'FAcq Rate'),
            ('INFOFOFBRate-RB', 'FOFB Rate'),
            ('INFOTbTRate-RB', 'TbT Rate')),
        )
        vbl.addWidget(grpbx)
        vbl.addSpacing(20)
        vbl.addStretch()
        grpbx = self._create_formlayout_groupbox(
            'RFFE and Switching Settings', (
                ('RFFEAtt-SP', 'RFFE Attenuation'),
                ('SwMode-Sel', 'Switching Mode')))
        vbl.addWidget(grpbx)
        vbl.addSpacing(20)
        vbl.addStretch()


class BPMAdvancedSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        gdl = QGridLayout(self)
        lab = QLabel('<h2>' + self.bpm + ' Advanced Settings</h2>')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 0, 0, 1, 4)

        grpbx = self._create_formlayout_groupbox('Switching', (
            ('SwMode-Sel', 'Mode'),
            ('SwPhaseSyncEn-Sel', 'Sync Enable', ['statebutton', 'ledstate']),
            ('SwDeswapDly-SP', 'Delay', ['lineedit', 'label']),
            ('SwDivClk-SP', 'Division Clock', ['lineedit', 'label']),
            ('', '', ()),
            ('', '<h4>Antenna Gains</h4>', ()),
            ('SwDirGainA-SP', 'Direct Gain A', 12),
            ('SwDirGainB-SP', 'Direct Gain B', 12),
            ('SwDirGainC-SP', 'Direct Gain C', 12),
            ('SwDirGainD-SP', 'Direct Gain D', 12),
            ('SwInvGainA-SP', 'Inverse Gain A', 12),
            ('SwInvGainB-SP', 'Inverse Gain B', 12),
            ('SwInvGainC-SP', 'Inverse Gain C', 12),
            ('SwInvGainD-SP', 'Inverse Gain D', 12),
        ))
        gdl.addWidget(grpbx, 1, 0, 2, 2)

        rate2pos = {
            'Monit': (3, 0, 1, 2),
            'FAcq': (1, 2, 1, 2),
            'FOFB': (2, 2, 1, 2),
            'TbT': (3, 2, 1, 2),
        }

        for rate, pos in rate2pos.items():
            items = list()
            if rate == 'Monit':
                items.extend([
                    ('MonitEnable-Sel', 'Enable', ['statebutton', 'ledstate']),
                    ('MONITUpdtTime-SP', 'Update Time'),
                ])
            items.extend([
                (f'{rate}PhaseSyncDly-SP', 'Delay', ['lineedit', 'label']),
                (f'{rate}PhaseSyncEn-Sel', 'Sync Enable',
                 ['statebutton', 'ledstate']),
                ((f'{rate}PhaseDesyncCnt-Mon', f'{rate}PhaseDesyncCntRst-Cmd'),
                 'Desync. Count',
                 ['label', ('pushbutton', 'Reset Count', None, 1, 0)]),
                (f'{rate}DataMaskEn-Sel', 'Data Mask Enable',
                 ['statebutton', 'ledstate']),
            ])
            if rate == 'FOFB':
                items.extend([
                    (f'{rate}DataMaskSamples-SP', 'Data Mask Samples',
                     ['lineedit', 'label']),
                ])
            else:
                items.extend([
                    (f'{rate}DataMaskSamplesBeg-SP', 'Data Mask Samples Begin',
                     ['lineedit', 'label']),
                    (f'{rate}DataMaskSamplesEnd-SP', 'Data Mask Samples End',
                     ['lineedit', 'label']),
                ])
            grpbx = self._create_formlayout_groupbox(rate, items)
            gdl.addWidget(grpbx, *pos)

            grpbx = TriggersLauncherWidget(
                self, prefix=self.prefix, bpm=self.bpm)
            gdl.addWidget(grpbx, 4, 0, 1, 3)

            grpbx = CustomGroupBox('ACQ Polynomials', self)
            hbl = QHBoxLayout(grpbx)
            hbl.setSpacing(10)
            hbl.addStretch()
            pbt = QPushButton('Settings')
            Window = create_window_from_widget(
                PolySettings, title=self.bpm+': ACQ Polynomials')
            util.connect_window(
                pbt, Window, parent=self, prefix=self.prefix, bpm=self.bpm)
            hbl.addWidget(pbt)
            hbl.addStretch()
            gdl.addWidget(grpbx, 4, 3, 1, 1)

            gdl.setColumnStretch(0, 1)
            gdl.setColumnStretch(1, 1)
            gdl.setColumnStretch(2, 1)
            gdl.setColumnStretch(3, 1)


class TriggersLauncherWidget(BaseWidget):

    def __init__(
            self, parent=None, prefix='', bpm='', acqcores=['ACQ', 'ACQ_PM']):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.acqcores = acqcores
        self.setupui()

    def setupui(self):
        grpbx = CustomGroupBox('Triggers Configuration', self)
        hbl = QHBoxLayout(grpbx)
        hbl.setSpacing(10)
        hbl.addStretch()
        pbt = QPushButton('Physical Triggers')
        wind = create_window_from_widget(
            PhysicalTriggers, title=self.bpm+': Physical Triggers')
        util.connect_window(
            pbt, wind, parent=self, prefix=self.prefix, device=self.bpm)
        hbl.addWidget(pbt)
        hbl.addStretch()
        if 'ACQ' in self.acqcores:
            pbt = QPushButton('ACQ Logical Triggers')
            wind = create_window_from_widget(
                LogicalTriggers, title=self.bpm+': ACQ Logical Triggers')
            util.connect_window(
                pbt, wind, parent=self, prefix=self.prefix, device=self.bpm,
                names=_csbpm.LogTrigIntern._fields, trig_tp='')
            hbl.addWidget(pbt)
            hbl.addStretch()
        if 'ACQ_PM' in self.acqcores:
            pbt = QPushButton('Post-Mortem Logical Triggers')
            wind = create_window_from_widget(
                LogicalTriggers,
                title=self.bpm+': Post-Mortem Logical Triggers')
            util.connect_window(
                pbt, wind, parent=self, prefix=self.prefix, device=self.bpm,
                trig_tp='_PM')
            hbl.addWidget(pbt)
            hbl.addStretch()

        gdl = QGridLayout(self)
        gdl.setContentsMargins(0, 9, 0, 0)
        gdl.addWidget(grpbx)


class PolySettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        wid = QWidget(self)
        wid.setObjectName('wid')
        wid.setStyleSheet('#wid{background-color: transparent;}')
        gdl = QGridLayout(wid)

        lab = QLabel('<h2>' + self.bpm + ' ACQ Polynomials</h2>')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 0, 0)

        for idx, coeff in enumerate(['X', 'Y', 'Q', 'SUM']):
            grpbx = self._create_coeff_group(coeff)
            gdl.addWidget(grpbx, idx+1, 0)

        sc_area = QScrollArea()
        sc_area.setStyleSheet('QScrollArea{min-width: 30em;}')
        sc_area.setWidgetResizable(True)
        sc_area.setWidget(wid)

        lay = QHBoxLayout(self)
        lay.addWidget(sc_area)

    def _create_coeff_group(self, coeff):
        enblctl = 'XY' if coeff in ['X', 'Y'] else coeff

        ldc_enbl = QLabel('Enable: ', self)
        but_enbl = PyDMStateButton(
            self, self.get_pvname(f'{enblctl}PosCal-Sel'))
        led_enbl = SiriusLedState(
            self, self.get_pvname(f'{enblctl}PosCal-Sts'))

        ldc_gen = QLabel('GEN: ', self)
        but_gen = SiriusLineEdit(
            self, self.get_pvname(f'GEN_Poly{coeff}ArrayCoeff-SP'))
        lbl_gen = SiriusLabel(
            self, self.get_pvname(f'GEN_Poly{coeff}ArrayCoeff-RB'))

        ldc_generr = QLabel('Check Error: ', self)
        led_generr = SiriusLedAlert(
            self, self.get_pvname(f'GEN_Poly{enblctl}ASubCalc.SEVR'))

        ldc_pm = QLabel('PM: ', self)
        but_pm = SiriusLineEdit(
            self, self.get_pvname(f'PM_Poly{coeff}ArrayCoeff-SP'))
        lbl_pm = SiriusLabel(
            self, self.get_pvname(f'PM_Poly{coeff}ArrayCoeff-RB'))

        ldc_pmerr = QLabel('Check Error: ', self)
        led_pmerr = SiriusLedAlert(
            self, self.get_pvname(f'PM_Poly{enblctl}ASubCalc.SEVR'))

        grpbx = QGroupBox(coeff + ' Coeff.', self)
        lay = QGridLayout(grpbx)
        lay.addWidget(ldc_enbl, 0, 0)
        lay.addWidget(but_enbl, 0, 1)
        lay.addWidget(led_enbl, 0, 2)
        lay.addWidget(ldc_gen, 1, 0)
        lay.addWidget(ldc_generr, 1, 6)
        lay.addWidget(led_generr, 1, 7)
        lay.addWidget(but_gen, 2, 0, 1, 8)
        lay.addWidget(lbl_gen, 3, 0, 1, 8)
        lay.addWidget(ldc_pm, 4, 0)
        lay.addWidget(ldc_pmerr, 4, 6)
        lay.addWidget(led_pmerr, 4, 7)
        lay.addWidget(but_pm, 5, 0, 1, 8)
        lay.addWidget(lbl_pm, 6, 0, 1, 8)
        return grpbx


class RFFEAdvancedSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        gdl = QGridLayout(self)
        lab = QLabel('<h2>' + self.bpm + ':RFFE Advanced Settings</h2>')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 0, 0, 1, 2)

        grpbx = self._create_formlayout_groupbox('General', (
            ('RFFEAtt-SP', 'Attenuation'),
            ('RFFETempCtl-SP', 'Temp. Control', ['statebutton', 'ledstate']),
        ))
        gdl.addWidget(grpbx, 1, 0, 1, 2)

        for i, pair in enumerate(['AC', 'BD']):
            grpbx = self._create_formlayout_groupbox(pair, (
                (f'RFFETemp{pair}-Mon', 'Temperature'),
                (f'RFFEPidSp{pair}-SP', 'PID Setpoint',
                 ['lineedit', 'label']),
                (f'RFFEHeater{pair}-SP', 'Heater'),
                (f'RFFEPid{pair}Kp-SP', 'PID Kp'),
                (f'RFFEPid{pair}Ti-SP', 'PID Ti'),
                (f'RFFEPid{pair}Td-SP', 'PID Td'),
            ))
            gdl.addWidget(grpbx, 2, i)


class HardwareSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        lay = QGridLayout(self)

        lab = QLabel(
            '<h2>'+self.bpm+' Hardware Settings</h2>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(lab, 0, 0, 1, 2)

        lay.addWidget(self._setupADCWidget(), 1, 0)
        lay.addWidget(self._setupAD9510Widget(), 2, 0, 5, 1)
        lay.addWidget(self._setupActiveClockWidget(), 1, 1)
        lay.addWidget(self._setupFMC250MWidget(), 2, 1)
        for chan in range(4):
            lay.addWidget(self._setupADCChannelMWidget(chan), chan+3, 1)

    def _setupADCWidget(self):
        return self._create_formlayout_groupbox('ADC', (
            ('ADCTrigDir-Sel', 'Trigger Direction'),
            ('ADCTrigTerm-Sel', 'Trigger Termination'),
            ('ADCClkSel-Sel', 'Reference Clock'),
            ('ADCTestDataEn-Sel', 'Enable test data',
             ['statebutton', 'ledstate']),
        ))

    def _setupAD9510Widget(self):
        return self._create_formlayout_groupbox('ADC AD9510', (
            ('ADCAD9510PllStatus-Mon', 'PLL Status',
             [('ledstate', SiriusLedState.Red, SiriusLedState.LightGreen)]),
            ('ADCAD9510Defaults-Sel', 'Reset',
             [('pushbutton', 'Reset', None, 1, 0)]),
            ('ADCAD9510PllFunc-SP', 'PLL Function', ['lineedit', 'label']),
            ('ADCAD9510ClkSel-Sel', 'Reference Clock'),
            ('ADCAD9510PllPDown-Sel', 'PLL Power Down'),
            ('ADCAD9510CpCurrent-Sel', 'CP Current'),
            ('ADCAD9510ADiv-SP', 'A divider', ['lineedit', 'label']),
            ('ADCAD9510BDiv-SP', 'B divider', ['lineedit', 'label']),
            ('ADCAD9510Prescaler-SP', 'Prescaler', ['lineedit', 'label']),
            ('ADCAD9510RDiv-SP', 'R divider', ['lineedit', 'label']),
            ('ADCAD9510MuxStatus-SP', 'Mux status', ['lineedit', 'label']),
            ('ADCAD9510Outputs-SP', 'Outputs', ['lineedit', 'label']),
        ))

    def _setupActiveClockWidget(self):
        return self._create_formlayout_groupbox('Active Clock', (
            ('INFOClkFreq-SP', 'Clock Frequency [Hz]', ['lineedit', 'label']),
            ('ADCSi57xOe-Sel', 'Osc. output enable',
             ['statebutton', 'ledstate']),
            ('INFOClkProp-Sel', 'Link Frequency',
             ['statebutton', 'ledstate']),
            ('ADCSi57xFreq-SP', 'Osc. Frequency [Hz]', ['lineedit', 'label']),
            ('ADCSi57xFStartup-SP', 'Osc. Frequency [Hz]\nStartup ',
             ['lineedit', 'label']),
        ))

    def _setupFMC250MWidget(self):
        return self._create_formlayout_groupbox('FMC250', (
            ('ActiveClkRstAdcs-Sel', 'Reset',
             [('pushbutton', 'Reset', None, 1, 0)]),
            (([f'ADC{i}CalStatus-Mon' for i in range(4)]), 'Calibration Done',
             ['ledstate', 'ledstate', 'ledstate', 'ledstate']),
        ))

    def _setupADCChannelMWidget(self, chan):
        return self._create_formlayout_groupbox(f'ADC Channel {chan}', (
            (f'ADC{chan}Temp-Mon', 'Temp. code'),
            (f'ADC{chan}TestMode-SP', 'Test mode', ['lineedit', ]),
            (f'ADC{chan}RstModes-Sel', 'Reset Mode', ['combo']),
        ))
