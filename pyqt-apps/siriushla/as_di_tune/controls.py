from qtpy.QtGui import QPalette
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, QMenu, \
    QFormLayout, QHBoxLayout, QSpacerItem, QSizePolicy as QSzPlcy
import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMLineEdit, \
    PyDMEnumComboBox, PyDMPushButton

from siriuspy.namesys import SiriusPVName
import siriushla.util as util
from siriushla.widgets import PyDMLedMultiChannel, PyDMLed, SiriusComboBox, \
    PyDMStateButton, SiriusLedState, SiriusConnectionSignal
from .details import TuneDetails, SITuneMarkerDetails
from .util import marker_color


class TuneControls(QWidget):
    """Tune Controls."""

    def __init__(self, parent=None, prefix='', section='', orientation='H',
                 background=None):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.section = section.upper()
        self.orientation = orientation
        self.device = SiriusPVName(
            prefix+self.section+'-Glob:DI-Tune-'+orientation)
        if self.section == 'BO':
            self.trigger = SiriusPVName('BO-Glob:TI-TuneProc')
        self.background = background
        self._setupUi()

    def _setupUi(self):
        # # Measurement
        if self.section == 'SI':
            # Tune
            label_tunefreq = QLabel('Tune Frequency [Hz]')
            self.lb_tunefreq = PyDMLabel(
                parent=self, init_channel=self.device+':TuneFreq-Mon')
            self.lb_tunefreq.setStyleSheet('min-width:8em;max-width:8em;')
            label_tunefrac = QLabel('Tune Fraction')
            self.lb_tunefrac = PyDMLabel(
                parent=self, init_channel=self.device+':TuneFrac-Mon')

        # Acquisition
        lbl_acq = QLabel('Acquisition', self)
        self.bt_acq = PyDMStateButton(
            parent=self, init_channel=self.device + ':SpecAnaGetSpec-Sel')
        self.bt_acq.shape = 1
        self.led_acq = SiriusLedState(
            parent=self, init_channel=self.device + ':SpecAnaGetSpec-Sts')
        hbox_acq = QHBoxLayout()
        hbox_acq.addWidget(self.bt_acq)
        hbox_acq.addWidget(self.led_acq)

        # Drive Enable
        lbl_drive = QLabel('Excitation', self)
        self.bt_drive = PyDMStateButton(
            parent=self, init_channel=self.device + ':Enbl-Sel')
        self.bt_drive.shape = 1
        value = 0b111 if self.section == 'BO' else 1
        self.led_drive = PyDMLedMultiChannel(
            parent=self, channels2values={self.device + ':Enbl-Sts': value})
        self.led_drive.setOffColor(PyDMLed.DarkGreen)
        hbox_drive = QHBoxLayout()
        hbox_drive.addWidget(self.bt_drive)
        hbox_drive.addWidget(self.led_drive)

        if self.section == 'BO':
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

        # Nr. Samples p/ spec
        # Nr. Samples p/ spec
        lbl_nrsmp = QLabel('Nr. Samples p/ Spec.', self)
        self.lb_nrsmp = PyDMLabel(
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

            # Sweep timeEnbl-
            lbl_swetime = QLabel('Sweep Time [ms]', self)
            self.lb_swetime = PyDMLabel(
                parent=self,
                init_channel=self.device.substitute(
                    dev='TuneProc', propty_name='SweTime',
                    propty_suffix='Mon'))

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
        if self.section == 'BO':
            self.cb_rbw = PyDMEnumComboBox(
                parent=self, init_channel=self.device + ':SpecAnaRBW-Sel')
        else:
            items = ['1 Hz', '2 Hz', '3 Hz', '5 Hz',
                     '10 Hz', '20 Hz', '30 Hz', '50 Hz',
                     '100 Hz', '200 Hz', '300 Hz', '500 Hz',
                     '1 kHz', '2 kHz', '3 kHz', '5 kHz', '6.25 kHz',
                     '10 kHz', '20 kHz', '30 kHz', '50 kHz',
                     '100 kHz', '200 kHz', '300 kHz', '500 kHz',
                     '1 MHz', '2 MHz', '3 MHz', '5 MHz', '10 MHz']
            self.cb_rbw = SiriusComboBox(
                parent=self, init_channel=self.device + ':SpecAnaRBW-Sel',
                items=items)
        self.lb_rbw = PyDMLabel(
            parent=self, init_channel=self.device + ':SpecAnaRBW-Sts')
        hbox_rbw = QHBoxLayout()
        hbox_rbw.addWidget(self.cb_rbw)
        hbox_rbw.addWidget(self.lb_rbw)

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

        # Harmonic Frequency
        lbl_Fh = QLabel('Harm. Freq. [kHz]', self)
        self.lb_Fh = PyDMLabel(parent=self)
        self.lb_Fh.setToolTip('Frf/(h*n)')
        self.lb_Fh.channel = self.device + ':FreqRevN-Mon'

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

        # Lock Center Freq.
        lbl_autoFc = QLabel('Lock Center Freq. ', self)
        self.bt_autoFc = PyDMStateButton(
            parent=self, init_channel=self.device + ':CenterFreqAuto-Sel')
        self.bt_autoFc.shape = 1
        self.led_autoFc = SiriusLedState(
            parent=self, init_channel=self.device + ':CenterFreqAuto-Sts')
        hbox_autoFc = QHBoxLayout()
        hbox_autoFc.addWidget(self.bt_autoFc)
        hbox_autoFc.addWidget(self.led_autoFc)

        if self.section == 'BO':
            # # ROI
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
            self.bt_roiauto.shape = 1
            self.led_roiauto = SiriusLedState(
                parent=self, init_channel=self.device + ':ROIAuto-Sts')
            hbox_roiauto = QHBoxLayout()
            hbox_roiauto.addWidget(self.bt_roiauto)
            hbox_roiauto.addWidget(self.led_roiauto)
        else:
            # # Markers
            self.pb_markers = QPushButton(
                qta.icon('mdi.view-headline'), '', self)
            self.pb_markers.setObjectName('mark_menu')
            menu_markers = QMenu(self)
            self.pb_markers.setMenu(menu_markers)
            self.pb_deltamarkers = QPushButton(
                qta.icon('mdi.view-headline'), '', self)
            self.pb_deltamarkers.setObjectName('mark_menu')
            menu_deltamarkers = QMenu(self)
            self.pb_deltamarkers.setMenu(menu_deltamarkers)

            for i in range(1, 5):
                act_m = menu_markers.addAction(
                    qta.icon('mdi.circle-medium',
                             color=marker_color['Mark'][str(i)]),
                    'Marker '+str(i))
                util.connect_window(
                    act_m, SITuneMarkerDetails, self,
                    prefix=self.prefix, orientation=self.orientation,
                    index=i, background=self.background)
                act_dm = menu_deltamarkers.addAction(
                    qta.icon('mdi.circle-medium',
                             color=marker_color['DMark'][str(i)]),
                    'Delta Marker '+str(i))
                util.connect_window(
                    act_dm, SITuneMarkerDetails, self,
                    prefix=self.prefix, orientation=self.orientation,
                    index=i, isdelta=True, background=self.background)

            label_marker = QLabel('Markers', self)
            label_marker.setObjectName('label_marker')
            self.bt_dsblmark = PyDMPushButton(
                parent=self, icon=qta.icon('mdi.window-close'),  pressValue=1,
                init_channel=self.device.substitute(
                    dev='TuneProc', propty_name='MarkAOff',
                    propty_suffix='Cmd'))
            self.bt_dsblmark.setObjectName('mark_dsbl')
            hbox_marker = QHBoxLayout()
            hbox_marker.setAlignment(Qt.AlignCenter)
            hbox_marker.addWidget(self.pb_markers)
            hbox_marker.addWidget(label_marker)
            hbox_marker.addWidget(self.bt_dsblmark)

            label_dmarker = QLabel('Delta Markers', self)
            label_dmarker.setObjectName('label_marker')
            self.bt_dsbldmark = PyDMPushButton(
                parent=self, icon=qta.icon('mdi.window-close'),  pressValue=1,
                init_channel=self.device.substitute(
                    dev='TuneProc', propty_name='DMarkAOff',
                    propty_suffix='Cmd'))
            self.bt_dsbldmark.setObjectName('mark_dsbl')
            hbox_deltamarker = QHBoxLayout()
            hbox_deltamarker.setAlignment(Qt.AlignCenter)
            hbox_deltamarker.addWidget(self.pb_deltamarkers)
            hbox_deltamarker.addWidget(label_dmarker)
            hbox_deltamarker.addWidget(self.bt_dsbldmark)

        # Details
        self.pb_details = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
        self.pb_details.setObjectName('detail')
        util.connect_window(self.pb_details, TuneDetails, parent=self,
                            prefix=self.prefix, section=self.section,
                            orientation=self.orientation,
                            background=self.background)
        hbox_details = QHBoxLayout()
        hbox_details.addStretch()
        hbox_details.addWidget(self.pb_details)

        # layout
        lay = QFormLayout(self)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignCenter)
        if self.section == 'SI':
            lay.addRow(QLabel('<h4>Measure</h4>'))
            lay.addRow(label_tunefreq, self.lb_tunefreq)
            lay.addRow(label_tunefrac, self.lb_tunefrac)
            lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(QLabel('<h4>Measurement Settings</h4>'))
        lay.addRow(lbl_acq, hbox_acq)
        lay.addRow(lbl_drive, hbox_drive)
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
        if self.section == 'BO':
            lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
            lay.addRow(QLabel('<h4>ROI</h4>'))
            lay.addRow(lbl_roistartx, hbox_roistartx)
            lay.addRow(lbl_roiwidth, hbox_roiwidth)
            lay.addRow(lbl_roistarty, hbox_roistarty)
            lay.addRow(lbl_roiheight, hbox_roiheight)
            lay.addRow(lbl_roiauto, hbox_roiauto)
        else:
            lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
            lay.addRow(QLabel('<h4>Markers</h4>'))
            lay.addRow(hbox_marker)
            lay.addRow(hbox_deltamarker)
        lay.addRow(hbox_details)

        self.setStyleSheet("""
            QLed{
                min-width:1.29em; max-width:1.29em;
            }
            #label_marker{
                min-width:7em; max-width:7em;
            }
            #mark_dsbl, #detail{
                min-width:25px; max-width:25px; icon-size:20px;
            }
            #mark_menu, #detail{
                min-width:35px; max-width:35px; icon-size:20px;
            }
            PyDMLabel, PyDMSpinbox, PyDMStateButton,
            PyDMLineEdit, PyDMEnumComboBox{
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
