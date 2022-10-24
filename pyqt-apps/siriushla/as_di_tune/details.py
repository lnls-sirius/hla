
from qtpy.QtGui import QPalette
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QFormLayout, QHBoxLayout, QVBoxLayout, \
    QGridLayout, QGroupBox, QWidget, QSpacerItem, QSizePolicy as QSzPlcy
import qtawesome as qta
from pydm.widgets import PyDMEnumComboBox, PyDMPushButton, PyDMLineEdit

from siriuspy.namesys import SiriusPVName
from siriushla.widgets import PyDMLedMultiChannel, SiriusMainWindow, \
    PyDMStateButton, SiriusLedState, SiriusConnectionSignal, PyDMLed, \
    SiriusStringComboBox, SiriusLabel, SiriusSpinbox
from siriushla.as_ti_control import HLTriggerSimple


class TuneDetails(SiriusMainWindow):
    """Tune Details."""

    def __init__(self, parent=None, prefix='', section='', orientation='H',
                 background=None):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.section = section.upper()
        self.orientation = orientation
        self.device = SiriusPVName('AC-Glob:DI-Tune-O')
        self.device = self.device.substitute(
            sec=self.section, idx=self.orientation, prefix=self.prefix)
        if self.section == 'BO':
            self.trigger = SiriusPVName('BO-Glob:TI-TuneProc')
        self.background = background
        self.setWindowTitle(self.device + ' Detailed Settings')
        self.setObjectName(self.section + 'App')
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)

        # title
        self.title_label = QLabel(
            '<h3>Tune '+self.orientation+' Detailed Settings<h3>', self)
        self.title_label.setObjectName('title')
        pal = self.title_label.palette()
        pal.setColor(QPalette.Background, self.background)
        self.title_label.setAutoFillBackground(True)
        self.title_label.setPalette(pal)

        # measurement
        self.meas_gbox = QGroupBox('Measurement', self)
        self.meas_gbox.setLayout(self._measLayout())

        # config
        self.config_gbox = QGroupBox('Configuration', self)
        self.config_gbox.setLayout(self._configLayout())

        if self.section == 'BO':
            # trigger
            self.trg_gbox = QGroupBox('Trigger', self)
            self.trg_gbox.setLayout(QHBoxLayout())
            self.trg_gbox.layout().addWidget(HLTriggerSimple(
                self.trg_gbox,
                device='BO-Glob:TI-TuneProc', prefix=self.prefix,
                duration=True, nrpulses=True))
            # spectrogram view
            self.spec_gbox = QGroupBox('Spectrogram View', self)
            self.spec_gbox.setLayout(self._specViewLayout())
            # roi
            self.roi_gbox = QGroupBox('ROI', self)
            self.roi_gbox.setLayout(self._roiLayout())

            vbox = QVBoxLayout()
            vbox.addWidget(self.trg_gbox)
            vbox.addWidget(self.spec_gbox)
            vbox.addWidget(self.roi_gbox)
            vbox.addWidget(self.config_gbox)

            lay = QGridLayout(cw)
            lay.addWidget(self.title_label, 0, 0, 1, 2)
            lay.addWidget(self.meas_gbox, 1, 0)
            lay.addLayout(vbox, 1, 1)
        else:
            lay = QVBoxLayout(cw)
            lay.addWidget(self.title_label)
            lay.addWidget(self.meas_gbox)
            lay.addWidget(self.config_gbox)

        self.setStyleSheet("""
            QLed{
                min-width:1.29em; max-width:1.29em;
            }
            #title {
                min-height:1.29em; max-height:1.29em;
                qproperty-alignment: "AlignVCenter | AlignHCenter";
            }
            SiriusLabel, SiriusSpinbox, PyDMEnumComboBox,
            PyDMStateButton{
                min-width:6em; max-width:6em;
            }""")

    def _measLayout(self):
        # Acquisition
        lbl_acq = QLabel('Acquisition', self)
        self.bt_acq = PyDMStateButton(
            self, self.device.substitute(propty='SpecAnaGetSpec-Sel'))
        self.bt_acq.shape = 1
        self.led_acq = SiriusLedState(
            self, self.device.substitute(propty='SpecAnaGetSpec-Sts'))
        hbox_acq = QHBoxLayout()
        hbox_acq.addWidget(self.bt_acq)
        hbox_acq.addWidget(self.led_acq)

        # Excitation
        lbl_drive = QLabel('Excitation', self)
        self.bt_drive = PyDMStateButton(
            self, self.device.substitute(propty='Enbl-Sel'))
        self.bt_drive.shape = 1
        value = 0b111 if self.section == 'BO' else 1
        self.led_drive = PyDMLedMultiChannel(
            parent=self, channels2values={
                self.device.substitute(propty='Enbl-Sts'): value})
        self.led_drive.setOffColor(PyDMLed.DarkGreen)
        hbox_drive = QHBoxLayout()
        hbox_drive.addWidget(self.bt_drive)
        hbox_drive.addWidget(self.led_drive)

        # Excitation Status Detailed
        gbox_enblsts = QGridLayout()
        lbl_enblsts = QLabel('Excitation\nEnable Status\nDetailed', self,
                             alignment=Qt.AlignVCenter | Qt.AlignRight)
        if self.section == 'BO':
            # # Carrier Generator
            self.led_carrier = SiriusLedState(
                self, self.device.substitute(propty='EnblCarrierGen-Sts'))
            gbox_enblsts.addWidget(self.led_carrier, 0, 0)
            gbox_enblsts.addWidget(QLabel('Carrier Generator'), 0, 1)
            # # Noise Generator
            self.led_noise = SiriusLedState(
                self, self.device.substitute(propty='EnblNoiseGen-Sts'))
            gbox_enblsts.addWidget(self.led_noise, 1, 0)
            gbox_enblsts.addWidget(QLabel('Noise Generator'), 1, 1)
        else:
            # # Noise Generator
            self.led_trkgen = SiriusLedState(
                self, self.device.substitute(propty='SpecAnaTrkGen-Sts'))
            gbox_enblsts.addWidget(self.led_trkgen, 1, 0)
            gbox_enblsts.addWidget(QLabel('Tracking Generator'), 1, 1)
        # # Amplifier
        self.led_amp = SiriusLedState(
            self, self.device.substitute(propty='EnblAmp-Sts'))
        gbox_enblsts.addWidget(self.led_amp, 2, 0)
        gbox_enblsts.addWidget(QLabel('Amplifier'), 2, 1)

        if self.section == 'BO':
            # Frame Count
            lbl_acqcnt = QLabel('Frame Count', self)
            dev = self.device.substitute(dev='TuneProc')
            self.lb_acqcnt = SiriusLabel(
                self, dev.substitute(propty='FrameCount-Mon'))
            self.lb_acqcnt.setAlignment(Qt.AlignCenter)
            self.led_acqcnt = PyDMLedMultiChannel(parent=self)
            self.trigNrPulseChannel = SiriusConnectionSignal(
                self.trigger.substitute(
                    prefix=self.prefix, propty='NrPulses-RB'))
            self.trigNrPulseChannel.new_value_signal[int].connect(
                self._updateNrAcq)
            hbox_acqcnt = QHBoxLayout()
            hbox_acqcnt.addWidget(self.lb_acqcnt)
            hbox_acqcnt.addWidget(self.led_acqcnt)

        # Nr. Samples p/ spec
        lbl_nrsmp = QLabel('Nr. Samples p/ Spec.', self)
        self.lb_nrsmp = SiriusLabel(
            parent=self, init_channel=self.device.substitute(
                dev='TuneProc', propty_name='SwePts',
                propty_suffix='RB'))

        if self.section == 'SI':
            # Acquisition Time
            lbl_acqtime = QLabel('Acq. Time', self)
            self.cb_acqtime = PyDMEnumComboBox(
                parent=self, init_channel=self.device.substitute(
                    dev='TuneProc', propty_name='Trace',
                    propty_suffix='Mon', field='SCAN'))

            # Sweep time
            lbl_swetime = QLabel('Sweep Time [ms]', self)
            self.lb_swetime = SiriusLabel(
                parent=self,
                init_channel=self.device.substitute(
                    dev='TuneProc', propty_name='SweTime',
                    propty_suffix='Mon'))

        # Span
        lbl_span = QLabel('Span [kHz]', self)
        self.le_span = PyDMLineEdit(
            self, self.device.substitute(propty='Span-SP'))
        self.le_span.precisionFromPV = True
        self.lb_span = SiriusLabel(
            self, self.device.substitute(propty='Span-RB'))
        hbox_span = QHBoxLayout()
        hbox_span.addWidget(self.le_span)
        hbox_span.addWidget(self.lb_span)

        # RBW
        lbl_rbw = QLabel('RBW', self)
        if self.section == 'BO':
            self.cb_rbw = PyDMEnumComboBox(
                self, self.device.substitute(propty='SpecAnaRBW-Sel'))
        else:
            items = ['1 Hz', '2 Hz', '3 Hz', '5 Hz',
                     '10 Hz', '20 Hz', '30 Hz', '50 Hz',
                     '100 Hz', '200 Hz', '300 Hz', '500 Hz',
                     '1 kHz', '2 kHz', '3 kHz', '5 kHz', '6.25 kHz',
                     '10 kHz', '20 kHz', '30 kHz', '50 kHz',
                     '100 kHz', '200 kHz', '300 kHz', '500 kHz',
                     '1 MHz', '2 MHz', '3 MHz', '5 MHz', '10 MHz']
            self.cb_rbw = SiriusStringComboBox(
                self, self.device.substitute(propty='SpecAnaRBW-Sel'),
                items=items)
        self.lb_rbw = SiriusLabel(
            self, self.device.substitute(propty='SpecAnaRBW-Sts'))
        hbox_rbw = QHBoxLayout()
        hbox_rbw.addWidget(self.cb_rbw)
        hbox_rbw.addWidget(self.lb_rbw)

        # Harmonic
        lbl_h = QLabel('Harmonic (n)', self)
        self.sb_h = SiriusSpinbox(
            self, self.device.substitute(propty='RevN-SP'))
        self.sb_h.precisionFromPV = True
        self.lb_h = SiriusLabel(
            self, self.device.substitute(propty='RevN-RB'))
        hbox_h = QHBoxLayout()
        hbox_h.addWidget(self.sb_h)
        hbox_h.addWidget(self.lb_h)

        # Harmonic Frequency
        lbl_Fh = QLabel('Harm. Freq. [kHz]', self)
        self.lb_Fh = SiriusLabel(parent=self)
        self.lb_Fh.setToolTip('Frf/(h*n)')
        self.lb_Fh.channel = self.device.substitute(propty='FreqRevN-Mon')

        # Frequency Offset
        lbl_foff = QLabel('Frequency Offset [kHz]', self)
        self.sb_foff = SiriusSpinbox(
            self, self.device.substitute(propty='FreqOff-SP'))
        self.sb_foff.precisionFromPV = True
        self.lb_foff = SiriusLabel(
            self, self.device.substitute(propty='FreqOff-RB'))
        hbox_foff = QHBoxLayout()
        hbox_foff.addWidget(self.sb_foff)
        hbox_foff.addWidget(self.lb_foff)

        # Center Frequency
        lbl_Fc = QLabel('Center Frequency [MHz]', self)
        self.le_Fc = PyDMLineEdit(
            self, self.device.substitute(propty='CenterFreq-SP'))
        self.le_Fc.precisionFromPV = True
        self.lb_Fc = SiriusLabel(
            self, self.device.substitute(propty='CenterFreq-RB'))
        hbox_Fc = QHBoxLayout()
        hbox_Fc.addWidget(self.le_Fc)
        hbox_Fc.addWidget(self.lb_Fc)

        # Lock Center Freq.
        lbl_autoFc = QLabel('Lock Center Frequency ', self)
        self.bt_autoFc = PyDMStateButton(
            self, self.device.substitute(propty='CenterFreqAuto-Sel'))
        self.bt_autoFc.shape = 1
        self.led_autoFc = SiriusLedState(
            self, self.device.substitute(propty='CenterFreqAuto-Sts'))
        hbox_autoFc = QHBoxLayout()
        hbox_autoFc.addWidget(self.bt_autoFc)
        hbox_autoFc.addWidget(self.led_autoFc)

        # Amplifier Gain
        lbl_drivegain = QLabel('Amplifier Gain [dB]', self)
        self.sb_drivegain = SiriusSpinbox(
            self, self.device.substitute(propty='AmpGain-SP'))
        self.sb_drivegain.precisionFromPV = True
        self.lb_drivegain = SiriusLabel(
            self, self.device.substitute(propty='AmpGain-RB'))
        hbox_drivegain = QHBoxLayout()
        hbox_drivegain.addWidget(self.sb_drivegain)
        hbox_drivegain.addWidget(self.lb_drivegain)

        if self.section == 'BO':
            # Auto Configure Excitation
            lbl_driveauto = QLabel('Auto Config. Excit.', self)
            self.bt_driveauto = PyDMStateButton(
                self, self.device.substitute(propty='DriveAuto-Sel'))
            self.bt_driveauto.shape = 1
            self.led_driveauto = SiriusLedState(
                self, self.device.substitute(propty='DriveAuto-Sts'))
            hbox_driveauto = QHBoxLayout()
            hbox_driveauto.addWidget(self.bt_driveauto)
            hbox_driveauto.addWidget(self.led_driveauto)

            # Noise Amplitude
            lbl_noiseamp = QLabel('Noise Amplitude [V]', self)
            self.sb_noiseamp = SiriusSpinbox(
                self, self.device.substitute(propty='NoiseAmpl-SP'))
            self.sb_noiseamp.precisionFromPV = True
            self.lb_noiseamp = SiriusLabel(
                self, self.device.substitute(propty='NoiseAmpl-RB'))
            hbox_noiseamp = QHBoxLayout()
            hbox_noiseamp.addWidget(self.sb_noiseamp)
            hbox_noiseamp.addWidget(self.lb_noiseamp)
        else:
            # Noise Amplitude
            lbl_trkgenlvl = QLabel('Trk. Gen. Power [dBm]', self)
            self.sb_trkgenlvl = PyDMLineEdit(
                self, self.device.substitute(propty='SpecAnaTrkGenLvl-SP'))
            self.lb_trkgenlvl = SiriusLabel(
                self, self.device.substitute(propty='SpecAnaTrkGenLvl-RB'))
            hbox_trkgenlvl = QHBoxLayout()
            hbox_trkgenlvl.addWidget(self.sb_trkgenlvl)
            hbox_trkgenlvl.addWidget(self.lb_trkgenlvl)

            # Spectrum Acquisition
            lbl_getspec = QLabel('Spectrum Acq.', self)
            self.cb_getspec = PyDMStateButton(
                parent=self, init_channel=self.device.substitute(
                    dev='TuneProc', propty_name='GetSpectrum',
                    propty_suffix='Sel'))
            self.cb_getspec.shape = 1
            self.lb_getspec = PyDMLed(
                parent=self, init_channel=self.device.substitute(
                    dev='TuneProc', propty_name='GetSpectrum',
                    propty_suffix='Sts'))
            hbox_getspec = QHBoxLayout()
            hbox_getspec.addWidget(self.cb_getspec)
            hbox_getspec.addWidget(self.lb_getspec)

        lay = QFormLayout()
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow(lbl_acq, hbox_acq)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lbl_drive, hbox_drive)
        lay.addRow(lbl_enblsts, gbox_enblsts)
        if self.section == 'BO':
            lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
            lay.addRow(lbl_acqcnt, hbox_acqcnt)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lbl_nrsmp, self.lb_nrsmp)
        if self.section == 'SI':
            lay.addRow(lbl_acqtime, self.cb_acqtime)
            lay.addRow(lbl_swetime, self.lb_swetime)
        lay.addRow(lbl_span, hbox_span)
        lay.addRow(lbl_rbw, hbox_rbw)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lbl_h, hbox_h)
        lay.addRow(lbl_Fh, self.lb_Fh)
        lay.addRow(lbl_foff, hbox_foff)
        lay.addRow(lbl_Fc, hbox_Fc)
        lay.addRow(lbl_autoFc, hbox_autoFc)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lbl_drivegain, hbox_drivegain)
        if self.section == 'BO':
            lay.addRow(lbl_driveauto, hbox_driveauto)
            lay.addRow(lbl_noiseamp, hbox_noiseamp)
        else:
            lay.addRow(lbl_trkgenlvl, hbox_trkgenlvl)
            lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
            lay.addRow(lbl_getspec, hbox_getspec)
        return lay

    def _configLayout(self):
        self.bt_rst = PyDMPushButton(
            parent=self, init_channel=self.device.substitute(propty='Rst-Cmd'),
            pressValue=1, icon=qta.icon('fa5s.sync'))
        self.bt_rst.setObjectName('bt_rst')
        self.bt_rst.setStyleSheet(
            '#bt_rst{min-width:25px; max-width:25px; icon-size:20px;}')
        lay = QFormLayout()
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow('Restore Default', self.bt_rst)
        return lay

    def _specViewLayout(self):
        dev = self.device.substitute(dev='TuneProc')

        # Mode
        lbl_mode = QLabel('Mode', self)
        self.cb_mode = PyDMEnumComboBox(
            self, dev.substitute(propty='SpecMode-Sel'))
        self.lb_mode = SiriusLabel(
            self, dev.substitute(propty='SpecMode-Sts'))
        hbox_mode = QHBoxLayout()
        hbox_mode.addWidget(self.cb_mode)
        hbox_mode.addWidget(self.lb_mode)

        # Time window
        lbl_timewdw = QLabel('Time Window [ms]', self)
        self.le_timewdw = PyDMLineEdit(
            self, dev.substitute(propty='SpecTime-SP'))
        self.le_timewdw.precisionFromPV = True
        self.lb_timewdw = SiriusLabel(
            self, dev.substitute(propty='SpecTime-RB'))
        hbox_timewdw = QHBoxLayout()
        hbox_timewdw.addWidget(self.le_timewdw)
        hbox_timewdw.addWidget(self.lb_timewdw)

        lay = QFormLayout()
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow(lbl_mode, hbox_mode)
        lay.addRow(lbl_timewdw, hbox_timewdw)
        return lay

    def _roiLayout(self):
        # StartX
        lbl_roistartx = QLabel('Start X [MHz]', self)
        self.le_roistartx = PyDMLineEdit(
            self, self.device.substitute(propty='ROIOffsetX-SP'))
        self.le_roistartx.precisionFromPV = True
        self.lb_roistartx = SiriusLabel(
            self, self.device.substitute(propty='ROIOffsetX-RB'))
        hbox_roistartx = QHBoxLayout()
        hbox_roistartx.addWidget(self.le_roistartx)
        hbox_roistartx.addWidget(self.lb_roistartx)

        # Width
        lbl_roiwidth = QLabel('Width [MHz]', self)
        self.le_roiwidth = PyDMLineEdit(
            self, self.device.substitute(propty='ROIWidth-SP'))
        self.le_roiwidth.precisionFromPV = True
        self.lb_roiwidth = SiriusLabel(
            self, self.device.substitute(propty='ROIWidth-RB'))
        hbox_roiwidth = QHBoxLayout()
        hbox_roiwidth.addWidget(self.le_roiwidth)
        hbox_roiwidth.addWidget(self.lb_roiwidth)

        # StartY
        lbl_roistarty = QLabel('Start Y [ms]', self)
        self.le_roistarty = PyDMLineEdit(
            self, self.device.substitute(propty='ROIOffsetY-SP'))
        self.le_roistarty.precisionFromPV = True
        self.lb_roistarty = SiriusLabel(
            self, self.device.substitute(propty='ROIOffsetY-RB'))
        hbox_roistarty = QHBoxLayout()
        hbox_roistarty.addWidget(self.le_roistarty)
        hbox_roistarty.addWidget(self.lb_roistarty)

        # Height
        lbl_roiheight = QLabel('Height [ms]', self)
        self.le_roiheight = PyDMLineEdit(
            self, self.device.substitute(propty='ROIHeight-SP'))
        self.le_roiheight.precisionFromPV = True
        self.lb_roiheight = SiriusLabel(
            self, self.device.substitute(propty='ROIHeight-RB'))
        hbox_roiheight = QHBoxLayout()
        hbox_roiheight.addWidget(self.le_roiheight)
        hbox_roiheight.addWidget(self.lb_roiheight)

        # Auto adjust
        lbl_roiauto = QLabel('Auto Positioning', self)
        self.bt_roiauto = PyDMStateButton(
            self, self.device.substitute(propty='ROIAuto-Sel'))
        self.bt_roiauto.shape = 1
        self.led_roiauto = SiriusLedState(
            self, self.device.substitute(propty='ROIAuto-Sts'))
        hbox_roiauto = QHBoxLayout()
        hbox_roiauto.addWidget(self.bt_roiauto)
        hbox_roiauto.addWidget(self.led_roiauto)

        lay = QFormLayout()
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow(lbl_roistartx, hbox_roistartx)
        lay.addRow(lbl_roiwidth, hbox_roiwidth)
        lay.addRow(lbl_roistarty, hbox_roistarty)
        lay.addRow(lbl_roiheight, hbox_roiheight)
        lay.addRow(lbl_roiauto, hbox_roiauto)
        return lay

    def _updateNrAcq(self, new_value):
        dev = self.device.substitute(dev='TuneProc')
        self.led_acqcnt.set_channels2values(
            {dev.substitute(propty='FrameCount-Mon'): new_value})


class SITuneMarkerDetails(SiriusMainWindow):
    """SI Tune Marker Details."""

    def __init__(self, parent=None, prefix='', orientation='', index=1,
                 isdelta=False, background=None):
        super().__init__(parent)
        self.prefix = prefix
        self.orientation = orientation
        self.idx = str(index)
        self.mtyp = 'D' if isdelta else ''
        self.dev = SiriusPVName('SI-Glob:DI-TuneProc-O')
        self.dev = self.dev.substitute(prefix=prefix, idx=self.orientation)
        self.background = background
        self.title = (
            self.dev.device_name +
            (' ' if self.mtyp == '' else ' Delta ') +
            'Marker '+self.idx+' Settings')
        self.setWindowTitle(self.title)
        self.setObjectName('SIApp')
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)
        lay = QFormLayout(cw)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)

        # title
        self.title_label = QLabel(
            '<h3>'+self.title+'<h3>', self, alignment=Qt.AlignCenter)
        self.title_label.setObjectName('title')
        pal = self.title_label.palette()
        pal.setColor(QPalette.Background, self.background)
        self.title_label.setAutoFillBackground(True)
        self.title_label.setPalette(pal)
        lay.addRow(self.title_label)

        label_enbl = QLabel('Enable: ', self)
        self.bt_enbl = PyDMStateButton(self, self.dev.substitute(
            propty='Enbl'+self.mtyp+'Mark'+self.idx+'-Sel'))
        self.bt_enbl.shape = 1
        self.led_enbl = SiriusLedState(self, self.dev.substitute(
            propty='Enbl'+self.mtyp+'Mark'+self.idx+'-Sts'))
        hbox_enbl = QHBoxLayout()
        hbox_enbl.addWidget(self.bt_enbl)
        hbox_enbl.addWidget(self.led_enbl)
        lay.addRow(label_enbl, hbox_enbl)

        label_enblautomax = QLabel('Auto Max Peak: ', self)
        ch_enblautomax = self.dev.substitute(
            propty='Enbl'+self.mtyp+'MaxAuto'+self.idx+'-Sel')
        self.enblAutoMaxChannel = SiriusConnectionSignal(ch_enblautomax)
        self.enblAutoMaxChannel.new_value_signal[int].connect(
            self._handle_values_visibility)
        self.bt_enblautomax = PyDMStateButton(self, ch_enblautomax)
        self.bt_enblautomax.shape = 1
        self.led_enblautomax = SiriusLedState(self, self.dev.substitute(
            propty='Enbl'+self.mtyp+'MaxAuto'+self.idx+'-Sts'))
        hbox_enblautomax = QHBoxLayout()
        hbox_enblautomax.addWidget(self.bt_enblautomax)
        hbox_enblautomax.addWidget(self.led_enblautomax)
        lay.addRow(label_enblautomax, hbox_enblautomax)

        label_x = QLabel(' X: ', self)
        self.sb_x = PyDMLineEdit(self, self.dev.substitute(
            propty=self.mtyp+'MarkX'+self.idx+'-SP'))
        self.lb_x = SiriusLabel(self, self.dev.substitute(
            propty=self.mtyp+'MarkX'+self.idx+'-RB'))
        hbox_x = QHBoxLayout()
        hbox_x.addWidget(self.sb_x)
        hbox_x.addWidget(self.lb_x)
        lay.addRow(label_x, hbox_x)

        label_y = QLabel(' Y: ', self)
        self.lb_y = SiriusLabel(self, self.dev.substitute(
            propty=self.mtyp+'MarkY'+self.idx+'-Mon'))
        hbox_y = QHBoxLayout()
        hbox_y.addWidget(self.lb_y)
        if self.mtyp == 'D':
            self.lb_dynamicY = SiriusLabel(self, self.dev.substitute(
                propty='DynamicDX'+self.idx+'-Mon'))
            self.lb_dynamicY.setVisible(False)
            hbox_y.addWidget(self.lb_dynamicY)
        lay.addRow(label_y, hbox_y)

        self.pb_max = PyDMPushButton(
            parent=self, label='Mark Max Peak', pressValue=1,
            init_channel=self.dev.substitute(
                propty=self.mtyp+'MarkMax'+self.idx+'-Cmd'))
        self.pb_maxnext = PyDMPushButton(
            parent=self, label='Mark Max Next', pressValue=1,
            init_channel=self.dev.substitute(
                propty=self.mtyp+'MarkMaxNext'+self.idx+'-Cmd'))
        self.pb_maxright = PyDMPushButton(
            parent=self, label='Mark Max Right', pressValue=1,
            init_channel=self.dev.substitute(
                propty=self.mtyp+'MarkMaxRight'+self.idx+'-Cmd'))
        self.pb_maxleft = PyDMPushButton(
            parent=self, label='Mark Max Left', pressValue=1,
            init_channel=self.dev.substitute(
                propty=self.mtyp+'MarkMaxLeft'+self.idx+'-Cmd'))
        vbox_cmd = QVBoxLayout()
        vbox_cmd.addWidget(self.pb_max)
        vbox_cmd.addWidget(self.pb_maxnext)
        vbox_cmd.addWidget(self.pb_maxright)
        vbox_cmd.addWidget(self.pb_maxleft)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(vbox_cmd)

        if self.mtyp == '' and self.idx == '1':
            lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))

            label_enblautomin = QLabel('Enable Auto Min: ', self)
            self.bt_enblautomin = PyDMStateButton(
                self, self.dev.substitute(propty='EnblMinAuto-Sel'))
            self.bt_enblautomin.shape = 1
            self.led_enblautomin = SiriusLedState(
                self, self.dev.substitute(propty='EnblMinAuto-Sts'))
            hbox_enblautomin = QHBoxLayout()
            hbox_enblautomin.addWidget(self.bt_enblautomin)
            hbox_enblautomin.addWidget(self.led_enblautomin)
            lay.addRow(label_enblautomin, hbox_enblautomin)

            label_enbllimit = QLabel('Enable Mark Limit: ', self)
            self.bt_enbllimit = PyDMStateButton(
                self, self.dev.substitute(propty='EnblMarkLimit-Sel'))
            self.bt_enbllimit.shape = 1
            self.led_enbllimit = SiriusLedState(
                self, self.dev.substitute(propty='EnblMarkLimit-Sts'))
            hbox_enbllimit = QHBoxLayout()
            hbox_enbllimit.addWidget(self.bt_enbllimit)
            hbox_enbllimit.addWidget(self.led_enbllimit)
            lay.addRow(label_enbllimit, hbox_enbllimit)

            label_limright = QLabel('Mark Limit Right: ', self)
            self.sb_limright = PyDMLineEdit(
                self, self.dev.substitute(propty='MarkLimitRight-SP'))
            self.lb_limright = SiriusLabel(
                self, self.dev.substitute(propty='MarkLimitRight-RB'))
            hbox_limright = QHBoxLayout()
            hbox_limright.addWidget(self.sb_limright)
            hbox_limright.addWidget(self.lb_limright)
            lay.addRow(label_limright, hbox_limright)

            label_limleft = QLabel('Mark Limit Left: ', self)
            self.sb_limleft = PyDMLineEdit(
                self, self.dev.substitute(propty='MarkLimitLeft-SP'))
            self.lb_limleft = SiriusLabel(
                self, self.dev.substitute(propty='MarkLimitLeft-RB'))
            hbox_limleft = QHBoxLayout()
            hbox_limleft.addWidget(self.sb_limleft)
            hbox_limleft.addWidget(self.lb_limleft)
            lay.addRow(label_limleft, hbox_limleft)

        self.setStyleSheet("""
            QLed{
                min-width:1.29em; max-width:1.29em;
            }
            #title {
                min-height:1.29em; max-height:1.29em;
                qproperty-alignment: "AlignVCenter | AlignHCenter";
            }
            SiriusLabel, SiriusSpinbox, PyDMEnumComboBox,
            PyDMStateButton{
                min-width:6em; max-width:6em;
            }""")

    def _handle_values_visibility(self, value):
        self.sb_x.setVisible(not value)
        if self.mtyp == 'D':
            self.lb_y.setVisible(not value)
            self.lb_dynamicY.setVisible(value)
