from qtpy.QtGui import QPalette
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, \
    QFormLayout, QHBoxLayout, QSpacerItem, QSizePolicy as QSzPlcy
import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMLineEdit, \
    PyDMEnumComboBox

from siriuspy.namesys import SiriusPVName
import siriushla.util as util
from siriushla.widgets import PyDMLedMultiChannel, \
    PyDMStateButton, SiriusLedState, SiriusConnectionSignal
from .details import BOTuneDetails


class BOTuneControls(QWidget):
    """BO Tune Controls."""

    def __init__(self, parent=None, prefix='', orientation='H',
                 background=None):
        """Init."""
        super().__init__(parent)
        self.device = SiriusPVName(prefix + 'BO-Glob:DI-Tune-' + orientation)
        self.trigger = SiriusPVName('BO-Glob:TI-TuneProc')
        self.prefix = prefix
        self.orientation = orientation
        self.background = background
        self._setupUi()

    def _setupUi(self):
        # Acquisition
        lbl_acq = QLabel('Acquisition', self)
        self.bt_acq = PyDMStateButton(
            parent=self, init_channel=self.device + ':SpecAnaGetSpec-Sel')
        self.led_acq = SiriusLedState(
            parent=self, init_channel=self.device + ':SpecAnaGetSpec-Sts')
        hbox_acq = QHBoxLayout()
        hbox_acq.addWidget(self.bt_acq)
        hbox_acq.addWidget(self.led_acq)

        # Drive Enable
        lbl_drive = QLabel('Excitation', self)
        self.bt_drive = PyDMStateButton(
            parent=self, init_channel=self.device + ':Enbl-Sel')
        self.led_drive = PyDMLedMultiChannel(
            parent=self, channels2values={self.device + ':Enbl-Sts': 0b111})
        hbox_drive = QHBoxLayout()
        hbox_drive.addWidget(self.bt_drive)
        hbox_drive.addWidget(self.led_drive)

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
        lbl_foff = QLabel('Freq. Offset [kHz]', self)
        self.sb_foff = PyDMSpinbox(
            parent=self, init_channel=self.device + ':FreqOff-SP')
        self.sb_foff.showStepExponent = False
        self.sb_foff.precisionFromPV = True
        self.lb_foff = PyDMLabel(
            parent=self, init_channel=self.device + ':FreqOff-RB')
        hbox_foff = QHBoxLayout()
        hbox_foff.addWidget(self.sb_foff)
        hbox_foff.addWidget(self.lb_foff)

        # Harmonic Frequency
        lbl_Fh = QLabel('Harm. Freq. [MHz]', self)
        self.lb_Fh = PyDMLabel(
            parent=self, init_channel=self.device + ':FreqRevN-Mon')
        self.lb_Fh.setToolTip('Frf/(h*n)')

        # Center Frequency
        lbl_Fc = QLabel('Center Freq. [MHz]', self)
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

        # Details
        self.pb_details = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
        self.pb_details.setObjectName('detail')
        self.pb_details.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        util.connect_window(self.pb_details, BOTuneDetails, parent=self,
                            prefix=self.prefix, orientation=self.orientation,
                            background=self.background)
        hbox_details = QHBoxLayout()
        hbox_details.addStretch()
        hbox_details.addWidget(self.pb_details)

        # layout
        lay = QFormLayout(self)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        lay.addRow(lbl_acq, hbox_acq)
        lay.addRow(lbl_drive, hbox_drive)
        lay.addRow(lbl_acqcnt, hbox_acqcnt)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lbl_h, hbox_h)
        lay.addRow(lbl_foff, hbox_foff)
        lay.addRow(lbl_Fh, self.lb_Fh)
        lay.addRow(lbl_Fc, hbox_Fc)
        lay.addRow(lbl_autoFc, hbox_autoFc)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lbl_span, hbox_span)
        lay.addRow(lbl_rbw, hbox_rbw)
        lay.addRow(hbox_details)

        self.setStyleSheet("""
            QLed{
                min-width:1.29em; max-width:1.29em;
            }
            PyDMLabel, PyDMSpinbox, PyDMStateButton,
            PyDMLineEdit{
                min-width:6em; max-width:6em;
            }""")
        pal = self.palette()
        pal.setColor(QPalette.Background, self.background)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def _updateNrAcq(self, new_value):
        dev = self.device.substitute(dev='TuneProc')
        self.led_acqcnt.set_channels2values(
            {dev + ':FrameCount-Mon': new_value})
