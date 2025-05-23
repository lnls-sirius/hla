"""BPM Settings."""

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QPushButton, QGroupBox, QWidget, QScrollArea
from qtpy.QtCore import Qt

from siriuspy.diagbeam.bpm.csdev import Const as _csbpm

from siriushla import util
from siriushla.widgets import PyDMStateButton, SiriusLedState, \
    SiriusLedAlert, SiriusWaveformLineEdit, SiriusLabel
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
        if not self.is_pbpm:
            grpbx = CustomGroupBox('Status', self)
            gdl = QGridLayout(grpbx)
            props = (
                ('RFFEasyn.CNCT', 'RFFE Connected'),
                ('ADCAD9510PllStatus-Mon', 'FMC PLL Clock Locked'),
                ('MMCMLocked-Mon', 'MMCM Clock Locked'),
                ('ClksLocked-Mon', 'All Clocks Locked'),
            )
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
        pbt = QPushButton(self.bpm.dev)
        Window = create_window_from_widget(
            BPMAdvancedSettings, title=self.bpm+' Advanced Settings')
        util.connect_window(
            pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
        vbl2.addWidget(pbt)
        if not self.is_pbpm:
            pbt = QPushButton('RFFE')
            Window = create_window_from_widget(
                RFFEAdvancedSettings, title=self.bpm+':RFFE Advanced Settings')
            util.connect_window(
                pbt, Window, parent=grpbx, prefix=self.prefix, bpm=self.bpm)
            vbl2.addWidget(pbt)
        pbt = QPushButton('Hardware')
        Window = create_window_from_widget(
            PBPMHardwareSettings if self.is_pbpm else BPMHardwareSettings,
            title=self.bpm+': Hardware Settings')
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
        if not self.is_pbpm:
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
        title = ('' if self.is_pbpm else 'RFFE and ') + 'Switching Settings'
        formlist = (('SwMode-Sel', 'Switching Mode'), )
        if not self.is_pbpm:
            formlist += (('RFFEAtt-SP', 'RFFE Attenuation'), )
        grpbx = self._create_formlayout_groupbox(title, formlist)
        vbl.addWidget(grpbx)
        vbl.addSpacing(20)
        vbl.addStretch()


class BPMAdvancedSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    @staticmethod
    def get_acqrate_props(rate):
        items = list()
        if rate == 'Monit':
            items.append(('MONITUpdtTime-SP', 'Update Time', False))
        if rate != 'FOFB':
            items.append((
                f'{rate}PhaseSyncDly-SP', 'Delay',
                {'isdata': False, 'widgets': ['lineedit', 'label']}
            ))
        items.extend([
            (f'{rate}PhaseSyncEn-Sel', 'Sync Enable',
             {'isdata': False, 'widgets': ['statebutton', 'ledstate']}),
            ((f'{rate}PhaseDesyncCnt-Mon', f'{rate}PhaseDesyncCntRst-Cmd'),
             'Desync. Count',
             {
              'isdata': False,
              'widgets': ['label', ('pushbutton', 'Reset Count', None, 1, 0)]
             }),
            (f'{rate}DataMaskEn-Sel', 'Data Mask Enable',
             {'isdata': False, 'widgets': ['statebutton', 'ledstate']}),
        ])
        if rate == 'FOFB':
            items.extend([
                (f'{rate}DataMaskSamples-SP', 'Data Mask Samples',
                 {'isdata': False, 'widgets': ['lineedit', 'label']}),
            ])
        else:
            items.extend([
                (f'{rate}DataMaskSamplesBeg-SP', 'Data Mask Samples Begin',
                 {'isdata': False, 'widgets': ['lineedit', 'label']}),
                (f'{rate}DataMaskSamplesEnd-SP', 'Data Mask Samples End',
                 {'isdata': False, 'widgets': ['lineedit', 'label']}),
            ])
        return items

    def setupui(self):
        gdl = QGridLayout(self)
        lab = QLabel('<h2>' + self.bpm + ' Advanced Settings</h2>')
        lab.setAlignment(Qt.AlignCenter)
        gdl.addWidget(lab, 0, 0, 1, 4)

        conflist = (
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
        )
        if self.is_pbpm:
            conflist += (
                ('', '', ()),
                ('', '<h4>Antenna Offsets</h4>', ()),
                ('SwDirOffsetA-SP', 'Direct Offset A'),
                ('SwDirOffsetB-SP', 'Direct Offset B'),
                ('SwDirOffsetC-SP', 'Direct Offset C'),
                ('SwDirOffsetD-SP', 'Direct Offset D'),
                ('SwInvOffsetA-SP', 'Inverse Offset A'),
                ('SwInvOffsetB-SP', 'Inverse Offset B'),
                ('SwInvOffsetC-SP', 'Inverse Offset C'),
                ('SwInvOffsetD-SP', 'Inverse Offset D'),
            )

        grpbx = self._create_formlayout_groupbox('Switching', conflist)

        if self.is_pbpm:
            gdl.addWidget(grpbx, 1, 0, 4, 2)
            rate2pos = {
                'Monit': (1, 2, 1, 2),
                'FAcq': (2, 2, 1, 2),
                'FOFB': (3, 2, 1, 2),
                'TbT': (4, 2, 1, 2),
            }
        else:
            gdl.addWidget(grpbx, 1, 0, 2, 2)
            rate2pos = {
                'Monit': (3, 0, 1, 2),
                'FAcq': (1, 2, 1, 2),
                'FOFB': (2, 2, 1, 2),
                'TbT': (3, 2, 1, 2),
            }

        for rate, pos in rate2pos.items():
            items = self.get_acqrate_props(rate)
            grpbx = self._create_formlayout_groupbox(rate, items)
            gdl.addWidget(grpbx, *pos)

            hrow = QHBoxLayout()
            hrow.setContentsMargins(0, 0, 0, 0)

            grpbx = TriggersLauncherWidget(
                self, prefix=self.prefix, bpm=self.bpm, acqcores=['GEN', 'PM'])
            hrow.addWidget(grpbx)

            if not self.is_pbpm:
                grpbx = CustomGroupBox('ACQ Polynomials', self)
                hbl = QHBoxLayout(grpbx)
                hbl.setSpacing(10)
                hbl.addStretch()
                pbt = QPushButton('Settings')
                Window = create_window_from_widget(
                    PolySettings, title=self.bpm+': ACQ Polynomials'
                )
                util.connect_window(
                    pbt, Window, parent=self, prefix=self.prefix, bpm=self.bpm
                )
                hbl.addWidget(pbt)
                hbl.addStretch()
                hrow.addWidget(grpbx)

            gdl.addLayout(hrow, 5, 0, 1, 4)

            gdl.setColumnStretch(0, 1)
            gdl.setColumnStretch(1, 1)
            gdl.setColumnStretch(2, 1)
            gdl.setColumnStretch(3, 1)


class TriggersLauncherWidget(BaseWidget):

    def __init__(
            self, parent=None, prefix='', bpm='', acqcores=['ACQ', 'PM']):
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
        if 'GEN' in self.acqcores:
            pbt = QPushButton('General Logical Triggers')
            wind = create_window_from_widget(
                LogicalTriggers, title=self.bpm+': General Logical Triggers')
            util.connect_window(
                pbt, wind, parent=self, prefix=self.prefix, device=self.bpm,
                names=_csbpm.LogTrigIntern._fields, trig_tp='_GEN')
            hbl.addWidget(pbt)
            hbl.addStretch()
        if 'PM' in self.acqcores:
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
        enblctl = 'XY' if coeff in ['X', 'Y'] else coeff.capitalize()

        ldc_enbl = QLabel('Enable: ', self)
        but_enbl = PyDMStateButton(
            self, self.get_pvname(f'{enblctl}PosCal-Sel'))
        led_enbl = SiriusLedState(
            self, self.get_pvname(f'{enblctl}PosCal-Sts'))

        ldc_gen = QLabel('GEN: ', self)
        but_gen = SiriusWaveformLineEdit(
            self, self.get_pvname(f'GEN_Poly{coeff}ArrayCoeff-SP'))
        lbl_gen = SiriusLabel(
            self, self.get_pvname(f'GEN_Poly{coeff}ArrayCoeff-RB'))

        ldc_generr = QLabel('Check Error: ', self)
        led_generr = SiriusLedAlert(
            self, self.get_pvname(f'GEN_Poly{enblctl}ASubCalc.SEVR'))

        ldc_pm = QLabel('PM: ', self)
        but_pm = SiriusWaveformLineEdit(
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


class BPMHardwareSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        lay = QGridLayout(self)

        lab = QLabel(
            '<h2>'+self.bpm+' FMC250 Settings</h2>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(lab, 0, 0, 1, 2)

        vlay0 = QVBoxLayout()
        vlay0.setContentsMargins(0, 0, 0, 0)
        vlay0.addWidget(self._setupADCCommonWidget())
        vlay0.addWidget(self._setupActiveClockWidget())
        vlay0.addWidget(self._setupAD9510PLLWidget())

        # vlay1 = QVBoxLayout()
        # vlay1.setContentsMargins(0, 0, 0, 0)
        # vlay1.addWidget(self._setupADCsWidget())

        lay.addLayout(vlay0, 1, 0)
        # lay.addLayout(vlay1, 1, 1)

    def _setupADCCommonWidget(self):
        return self._create_formlayout_groupbox('ADC Common', (
            ('MMCMLocked-Mon', 'MMCM Status',
             [('ledstate', SiriusLedState.Red, SiriusLedState.LightGreen)]),
            ('ADCTrigDir-Sel', 'Trigger Direction'),
            ('ADCTrigTerm-Sel', 'Trigger Termination'),
            ('ADCTestDataEn-Sel', 'Enable test data',
             ['statebutton', 'ledstate']),
        ))

    def _setupAD9510PLLWidget(self):
        return self._create_formlayout_groupbox('AD9510 PLL', (
            ('ADCAD9510PllStatus-Mon', 'PLL Status',
             [('ledstate', SiriusLedState.Red, SiriusLedState.LightGreen)]),
            # ('ADCAD9510Defaults-Sel', 'Reset',
            #  [('pushbutton', 'Reset', None, 1, 0)]),
            ('ADCAD9510ADiv-SP', 'A divider', ['lineedit', 'label']),
            ('ADCAD9510BDiv-SP', 'B divider', ['lineedit', 'label']),
            ('ADCAD9510RDiv-SP', 'R divider', ['lineedit', 'label']),
        ))

    def _setupActiveClockWidget(self):
        return self._create_formlayout_groupbox('Active Clock', (
            ('ADCSi57xOe-Sel', 'Osc. output enable',
             ['statebutton', 'ledstate']),
            ('ADCSi57xFreq-SP', 'Osc. Frequency [Hz]', ['lineedit', 'label']),
            ('ADCClkSel-Sel', 'Reference Clock'),
        ))

    def _setupADCsWidget(self):
        proplist = (
            ('ActiveClkRstAdcs-Sel', 'Reset',
             [('pushbutton', 'Reset', None, 1, 0)]),
        )
        for chan in range(4):
            proplist += (
                ('', '', ()),
                ('', f'<h4>Channel {chan}</h4>', ()),
                (f'ADC{chan}Temp-Mon', 'Temp. code'),
                (f'ADC{chan}TestMode-SP', 'Test mode', ['lineedit', ]),
                (f'ADC{chan}RstModes-Sel', 'Reset Mode', ['combo']),
                (f'ADC{chan}CalStatus-Mon', 'Calibration Done', ['ledstate']),
            )
        return self._create_formlayout_groupbox('ADCs', proplist)


class PBPMHardwareSettings(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setupui()

    def setupui(self):
        lay = QGridLayout(self)

        lab = QLabel(
            '<h2>'+self.bpm+' Hardware Settings</h2>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(lab, 0, 0, 1, 2)

        lay.addWidget(self._setupFMCPICOWidget(), 1, 0)

    def _setupFMCPICOWidget(self):
        return self._create_formlayout_groupbox(
            'FMCPICO',
            ((f'FMCPICORngR{i}-Sel', f'RNG R{i}') for i in range(4))
        )
