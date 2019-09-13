
from qtpy.QtGui import QPalette
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QFormLayout, QHBoxLayout, QVBoxLayout, \
    QGridLayout, QGroupBox, QWidget, QPushButton
import qtawesome as qta
from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMPushButton, PyDMLineEdit

from siriuspy.namesys import SiriusPVName
import siriushla.util as util
from siriushla.widgets import PyDMLedMultiChannel, SiriusMainWindow, \
    PyDMStateButton, SiriusLedState, SiriusLedAlert, SiriusConnectionSignal
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ti_control import HLTriggerDetailed


class BOTuneDetails(SiriusMainWindow):
    """BO Tune Details."""

    def __init__(self, parent=None, prefix='', orientation='H',
                 background=None):
        """Init."""
        super().__init__(parent)
        self.device = SiriusPVName(prefix + 'BO-Glob:DI-Tune-' + orientation)
        self.trigger = SiriusPVName('BO-Glob:TI-TuneProc')
        self.prefix = prefix
        self.orientation = orientation
        self.background = background
        self.setWindowTitle(self.device + ' Detailed Settings')
        self.setObjectName('BOApp')
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        # title
        self.title_label = QLabel(
            '<h3>Tune '+self.orientation+' Detailed Settings<h3>', self)
        self.title_label.setObjectName('title')
        pal = self.title_label.palette()
        pal.setColor(QPalette.Background, self.background)
        self.title_label.setAutoFillBackground(True)
        self.title_label.setPalette(pal)

        # acquisition
        self.acq_gbox = QGroupBox('Acquisition', self)
        self.acq_gbox.setLayout(self._acqLayout())
        # excitation
        self.exc_gbox = QGroupBox('Excitation', self)
        self.exc_gbox.setLayout(self._excitLayout())
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.acq_gbox)
        vbox1.addWidget(self.exc_gbox)

        # trigger
        self.trg_gbox = BOTuneTrigger(self, self.prefix)
        # config
        self.config_gbox = QGroupBox('Configuration', self)
        self.config_gbox.setLayout(self._configLayout())
        # spectrogram view
        self.spec_gbox = QGroupBox('Spectrogram View', self)
        self.spec_gbox.setLayout(self._specViewLayout())
        # roi
        self.roi_gbox = QGroupBox('ROI', self)
        self.roi_gbox.setLayout(self._roiLayout())
        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.trg_gbox)
        vbox2.addWidget(self.config_gbox)
        vbox2.addWidget(self.spec_gbox)
        vbox2.addWidget(self.roi_gbox)

        cw = QWidget(self)
        lay = QGridLayout(cw)
        lay.addWidget(self.title_label, 0, 0, 1, 2)
        lay.addLayout(vbox1, 1, 0)
        lay.addLayout(vbox2, 1, 1)
        self.setCentralWidget(cw)

        self.setStyleSheet("""
            QLed{
                min-width:1.29em; max-width:1.29em;
            }
            #title {
                min-height:1.29em; max-height:1.29em;
                qproperty-alignment: "AlignVCenter | AlignHCenter";
            }
            PyDMLabel, PyDMSpinbox, PyDMEnumComboBox,
            PyDMStateButton{
                min-width:6em; max-width:6em;
            }""")

    def _acqLayout(self):
        # Enable
        lbl_acq = QLabel('Enable', self)
        self.bt_acq = PyDMStateButton(
            parent=self, init_channel=self.device + ':SpecAnaGetSpec-Sel')
        self.led_acq = SiriusLedState(
            parent=self, init_channel=self.device + ':SpecAnaGetSpec-Sts')
        hbox_acq = QHBoxLayout()
        hbox_acq.addWidget(self.bt_acq)
        hbox_acq.addWidget(self.led_acq)

        # Frame Count
        lbl_acqcnt = QLabel('Frame Count', self)
        dev = self.device.substitute(dev='TuneProc')
        self.lb_acqcnt = PyDMLabel(
            parent=self, init_channel=dev + ':FrameCount-Mon')
        self.lb_acqcnt.setAlignment(Qt.AlignCenter)
        self.led_acqcnt = PyDMLedMultiChannel(parent=self)
        self.trigNrPulseChannel = SiriusConnectionSignal(
            self.prefix+self.trigger+':NrPulses-RB')
        self.trigNrPulseChannel.new_value_signal[int].connect(
            self._updateNrAcq)
        hbox_acqcnt = QHBoxLayout()
        hbox_acqcnt.addWidget(self.lb_acqcnt)
        hbox_acqcnt.addWidget(self.led_acqcnt)

        # Harmonic
        lbl_h = QLabel('Harmonic (n)', self)
        self.sb_h = PyDMSpinbox(
            parent=self, init_channel=self.device + ':RevN-SP')
        self.sb_h.showStepExponent = False
        self.sb_h.precisionFromPV = True
        self.lb_h = PyDMLabel(
            parent=self, init_channel=self.device + ':RevN-RB')
        hbox_h = QHBoxLayout()
        hbox_h.addWidget(self.sb_h)
        hbox_h.addWidget(self.lb_h)

        # Frequency Offset
        lbl_foff = QLabel('Frequency Offset [kHz]', self)
        self.sb_foff = PyDMSpinbox(
            parent=self, init_channel=self.device + ':FreqOff-SP')
        self.sb_foff.showStepExponent = False
        self.sb_foff.precisionFromPV = True
        self.lb_foff = PyDMLabel(
            parent=self, init_channel=self.device + ':FreqOff-RB')
        hbox_foff = QHBoxLayout()
        hbox_foff.addWidget(self.sb_foff)
        hbox_foff.addWidget(self.lb_foff)

        # Center Frequency
        lbl_Fc = QLabel('Center Frequency [MHz]', self)
        self.le_Fc = PyDMLineEdit(
            parent=self, init_channel=self.device + ':CenterFreq-SP')
        self.le_Fc.precisionFromPV = True
        self.lb_Fc = PyDMLabel(
            parent=self, init_channel=self.device + ':CenterFreq-RB')
        hbox_Fc = QHBoxLayout()
        hbox_Fc.addWidget(self.le_Fc)
        hbox_Fc.addWidget(self.lb_Fc)

        # Auto Center
        lbl_autoFc = QLabel('Auto Center', self)
        self.bt_autoFc = PyDMStateButton(
            parent=self, init_channel=self.device + ':CenterFreqAuto-Sel')
        self.led_autoFc = SiriusLedState(
            parent=self, init_channel=self.device + ':CenterFreqAuto-Sts')
        hbox_autoFc = QHBoxLayout()
        hbox_autoFc.addWidget(self.bt_autoFc)
        hbox_autoFc.addWidget(self.led_autoFc)

        # Harmonic Frequency
        lbl_Fh = QLabel('Harmonic Frequency [MHz]', self)
        self.lb_Fh = PyDMLabel(
            parent=self, init_channel=self.device + ':FreqRevN-Mon')
        self.lb_Fh.setToolTip('Frf/(h*n)')

        lay = QFormLayout()
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow(lbl_acq, hbox_acq)
        lay.addRow(lbl_acqcnt, hbox_acqcnt)
        lay.addRow(lbl_h, hbox_h)
        lay.addRow(lbl_foff, hbox_foff)
        lay.addRow(lbl_Fc, hbox_Fc)
        lay.addRow(lbl_autoFc, hbox_autoFc)
        lay.addRow(lbl_Fh, self.lb_Fh)
        return lay

    def _excitLayout(self):
        # Enable
        lbl_drive = QLabel('Enable', self)
        self.bt_drive = PyDMStateButton(
            parent=self, init_channel=self.device + ':Enbl-Sel')
        self.led_drive = PyDMLedMultiChannel(
            parent=self, channels2values={self.device + ':Enbl-Sts': 0b111})
        hbox_drive = QHBoxLayout()
        hbox_drive.addWidget(self.bt_drive)
        hbox_drive.addWidget(self.led_drive)

        # Status
        lbl_enblsts = QLabel('Enable Status\nDetailed')
        # # Carrier Generator
        self.led_carrier = SiriusLedState(
            parent=self, init_channel=self.device + ':EnblCarrierGen-Sts')
        # # Noise Generator
        self.led_noise = SiriusLedState(
            parent=self, init_channel=self.device + ':EnblNoiseGen-Sts')
        # # Amplifier
        self.led_amp = SiriusLedState(
            parent=self, init_channel=self.device + ':EnblAmp-Sts')
        gbox_enblsts = QGridLayout()
        gbox_enblsts.addWidget(self.led_carrier, 0, 0)
        gbox_enblsts.addWidget(QLabel('Carrier Generator'), 0, 1)
        gbox_enblsts.addWidget(self.led_noise, 1, 0)
        gbox_enblsts.addWidget(QLabel('Noise Generator'), 1, 1)
        gbox_enblsts.addWidget(self.led_amp, 2, 0)
        gbox_enblsts.addWidget(QLabel('Amplifier'), 2, 1)

        # Span
        lbl_span = QLabel('Span [kHz]', self)
        self.le_span = PyDMLineEdit(
            parent=self, init_channel=self.device + ':Span-SP')
        self.le_span.precisionFromPV = True
        self.lb_span = PyDMLabel(
            parent=self, init_channel=self.device + ':Span-RB')
        hbox_span = QHBoxLayout()
        hbox_span.addWidget(self.le_span)
        hbox_span.addWidget(self.lb_span)

        # RBW
        lbl_rbw = QLabel('RBW', self)
        self.cb_rbw = PyDMEnumComboBox(
            parent=self, init_channel=self.device + ':SpecAnaRBW-Sel')
        self.lb_rbw = PyDMLabel(
            parent=self, init_channel=self.device + ':SpecAnaRBW-Sts')
        hbox_rbw = QHBoxLayout()
        hbox_rbw.addWidget(self.cb_rbw)
        hbox_rbw.addWidget(self.lb_rbw)

        # Auto Configure
        lbl_driveauto = QLabel('Auto Configure', self)
        self.bt_driveauto = PyDMStateButton(
            parent=self, init_channel=self.device + ':DriveAuto-Sel')
        self.led_driveauto = SiriusLedState(
            parent=self, init_channel=self.device + ':DriveAuto-Sts')
        hbox_driveauto = QHBoxLayout()
        hbox_driveauto.addWidget(self.bt_driveauto)
        hbox_driveauto.addWidget(self.led_driveauto)

        # Amplifier Gain
        lbl_drivegain = QLabel('Amplifier Gain [dB]', self)
        self.sb_drivegain = PyDMSpinbox(
            parent=self, init_channel=self.device + ':AmpGain-SP')
        self.sb_drivegain.showStepExponent = False
        self.sb_drivegain.precisionFromPV = True
        self.lb_drivegain = PyDMLabel(
            parent=self, init_channel=self.device + ':AmpGain-RB')
        hbox_drivegain = QHBoxLayout()
        hbox_drivegain.addWidget(self.sb_drivegain)
        hbox_drivegain.addWidget(self.lb_drivegain)

        # Noise Amplitude
        lbl_noiseamp = QLabel('Noise Amplitude [V]', self)
        self.sb_noiseamp = PyDMSpinbox(
            parent=self, init_channel=self.device + ':NoiseAmpl-SP')
        self.sb_noiseamp.showStepExponent = False
        self.sb_noiseamp.precisionFromPV = True
        self.lb_noiseamp = PyDMLabel(
            parent=self, init_channel=self.device + ':NoiseAmpl-RB')
        hbox_noiseamp = QHBoxLayout()
        hbox_noiseamp.addWidget(self.sb_noiseamp)
        hbox_noiseamp.addWidget(self.lb_noiseamp)

        lay = QFormLayout()
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow(lbl_drive, hbox_drive)
        lay.addRow(lbl_enblsts, gbox_enblsts)
        lay.addRow(lbl_span, hbox_span)
        lay.addRow(lbl_rbw, hbox_rbw)
        lay.addRow(lbl_driveauto, hbox_driveauto)
        lay.addRow(lbl_drivegain, hbox_drivegain)
        lay.addRow(lbl_noiseamp, hbox_noiseamp)
        return lay

    def _configLayout(self):
        self.bt_rst = PyDMPushButton(
            parent=self, init_channel=self.device + ':Rst-Cmd',
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
            parent=self, init_channel=dev + ':SpecMode-Sel')
        self.lb_mode = PyDMLabel(
            parent=self, init_channel=dev + ':SpecMode-Sts')
        hbox_mode = QHBoxLayout()
        hbox_mode.addWidget(self.cb_mode)
        hbox_mode.addWidget(self.lb_mode)

        # Time window
        lbl_timewdw = QLabel('Time Window [ms]', self)
        self.le_timewdw = PyDMLineEdit(
            parent=self, init_channel=dev + ':SpecTime-SP')
        self.le_timewdw.precisionFromPV = True
        self.lb_timewdw = PyDMLabel(
            parent=self, init_channel=dev + ':SpecTime-RB')
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
            parent=self, init_channel=self.device + ':ROIOffsetX-SP')
        self.le_roistartx.precisionFromPV = True
        self.lb_roistartx = PyDMLabel(
            parent=self, init_channel=self.device + ':ROIOffsetX-RB')
        hbox_roistartx = QHBoxLayout()
        hbox_roistartx.addWidget(self.le_roistartx)
        hbox_roistartx.addWidget(self.lb_roistartx)

        # Width
        lbl_roiwidth = QLabel('Width [MHz]', self)
        self.le_roiwidth = PyDMLineEdit(
            parent=self, init_channel=self.device + ':ROIWidth-SP')
        self.le_roiwidth.precisionFromPV = True
        self.lb_roiwidth = PyDMLabel(
            parent=self, init_channel=self.device + ':ROIWidth-RB')
        hbox_roiwidth = QHBoxLayout()
        hbox_roiwidth.addWidget(self.le_roiwidth)
        hbox_roiwidth.addWidget(self.lb_roiwidth)

        # StartY
        lbl_roistarty = QLabel('Start Y [ms]', self)
        self.le_roistarty = PyDMLineEdit(
            parent=self, init_channel=self.device + ':ROIOffsetY-SP')
        self.le_roistarty.precisionFromPV = True
        self.lb_roistarty = PyDMLabel(
            parent=self, init_channel=self.device + ':ROIOffsetY-RB')
        hbox_roistarty = QHBoxLayout()
        hbox_roistarty.addWidget(self.le_roistarty)
        hbox_roistarty.addWidget(self.lb_roistarty)

        # Height
        lbl_roiheight = QLabel('Height [ms]', self)
        self.le_roiheight = PyDMLineEdit(
            parent=self, init_channel=self.device + ':ROIHeight-SP')
        self.le_roiheight.precisionFromPV = True
        self.lb_roiheight = PyDMLabel(
            parent=self, init_channel=self.device + ':ROIHeight-RB')
        hbox_roiheight = QHBoxLayout()
        hbox_roiheight.addWidget(self.le_roiheight)
        hbox_roiheight.addWidget(self.lb_roiheight)

        # Auto adjust
        lbl_roiauto = QLabel('Auto Positioning', self)
        self.bt_roiauto = PyDMStateButton(
            parent=self, init_channel=self.device + ':ROIAuto-Sel')
        self.led_roiauto = SiriusLedState(
            parent=self, init_channel=self.device + ':ROIAuto-Sts')
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
            {dev + ':FrameCount-Mon': new_value})


class BOTuneTrigger(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super().__init__('Trigger', parent)
        self.trigger = SiriusPVName(prefix + 'BO-Glob:TI-TuneProc')
        self.prefix = prefix
        self._setupUi()

    def _setupUi(self):
        lbl_sts = QLabel('Status', self)
        self.led_sts = SiriusLedAlert(
            parent=self, init_channel=self.prefix+self.trigger+':Status-Mon')
        self.bt_trig_dtl = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
        self.bt_trig_dtl.setObjectName('trg_dtl')
        self.bt_trig_dtl.setStyleSheet(
            "#trg_dtl{min-width:25px; max-width:25px; icon-size:20px;}")
        trg_w = create_window_from_widget(
            HLTriggerDetailed, is_main=True,
            title=self.prefix+self.trigger+' Detailed Settings')
        util.connect_window(
            self.bt_trig_dtl, trg_w, parent=self, prefix=self.trigger)
        hbox_resume = QHBoxLayout()
        hbox_resume.addWidget(self.led_sts)
        hbox_resume.addWidget(self.bt_trig_dtl)

        # NrPulses
        lbl_nrp = QLabel('NrPulses', self)
        self.sb_nrp = PyDMSpinbox(
            parent=self, init_channel=self.prefix+self.trigger+':NrPulses-SP')
        self.sb_nrp.showStepExponent = False
        self.lb_nrp = PyDMLabel(
            parent=self, init_channel=self.prefix+self.trigger+':NrPulses-RB')
        hbox_nrp = QHBoxLayout()
        hbox_nrp.addWidget(self.sb_nrp)
        hbox_nrp.addWidget(self.lb_nrp)

        # Duration
        lbl_dur = QLabel('Duration [us]', self)
        self.sb_dur = PyDMSpinbox(
            parent=self, init_channel=self.prefix+self.trigger+':Duration-SP')
        self.sb_dur.showStepExponent = False
        self.lb_dur = PyDMLabel(
            parent=self, init_channel=self.prefix+self.trigger+':Duration-RB')
        hbox_dur = QHBoxLayout()
        hbox_dur.addWidget(self.sb_dur)
        hbox_dur.addWidget(self.lb_dur)

        # Delay
        lbl_dly = QLabel('Delay [us]', self)
        self.sb_dly = PyDMSpinbox(
            parent=self, init_channel=self.prefix+self.trigger+':Delay-SP')
        self.sb_dly.showStepExponent = False
        self.lb_dly = PyDMLabel(
            parent=self, init_channel=self.prefix+self.trigger+':Delay-RB')
        hbox_dly = QHBoxLayout()
        hbox_dly.addWidget(self.sb_dly)
        hbox_dly.addWidget(self.lb_dly)

        lay = QFormLayout(self)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow(lbl_sts, hbox_resume)
        lay.addRow(lbl_nrp, hbox_nrp)
        lay.addRow(lbl_dur, hbox_dur)
        lay.addRow(lbl_dly, hbox_dly)

        self.setStyleSheet("""
            QLed{
                min-width:1.29em; max-width:1.29em;
            }
            PyDMLabel, PyDMSpinbox, PyDMEnumComboBox,
            PyDMStateButton{
                min-width:6em; max-width:6em;
            }""")
