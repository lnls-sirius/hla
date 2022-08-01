from qtpy.QtGui import QPalette
from qtpy.QtCore import Qt, QEvent
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, \
    QFormLayout, QHBoxLayout, QSpacerItem, QSizePolicy as QSzPlcy, \
    QTabWidget, QVBoxLayout, QApplication
import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMLineEdit, \
    PyDMEnumComboBox, PyDMPushButton

from siriuspy.namesys import SiriusPVName
import siriushla.util as util
from siriushla.widgets import PyDMLedMultiChannel, PyDMLed, PyDMStateButton, \
    SiriusStringComboBox, SiriusLedState, SiriusConnectionSignal
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
        self.device = SiriusPVName('AC-Glob:DI-Tune-O')
        self.device = self.device.substitute(
            sec=self.section, idx=self.orientation, prefix=self.prefix)
        if self.section == 'BO':
            self.trigger = SiriusPVName('BO-Glob:TI-TuneProc')
        self.background = background
        self._setupUi()

    def _setupUi(self):
        # # Measurement
        if self.section == 'SI':
            # Tune
            label_tunefreq = QLabel('Tune Frequency')
            self.lb_tunefreq = PyDMLabel(self)
            self.lb_tunefreq._unit = 'kHz'
            self.lb_tunefreq.showUnits = True
            self.lb_tunefreq.precisionFromPV = False
            self.lb_tunefreq.precision = 3
            self.tunefreq_currval = 0.0
            self.freqrevn_currval = 0.0
            self.tunefreq_ch = SiriusConnectionSignal(
                self.device.substitute(propty='TuneFreq-Mon'))
            self.tunefreq_ch.new_value_signal[float].connect(
                self._calc_tunefreq)
            self.freqrevn_ch = SiriusConnectionSignal(
                self.device.substitute(propty='FreqRevN-Mon'))
            self.freqrevn_ch.new_value_signal[float].connect(
                self._calc_tunefreq)
            self.lb_tunefreq.setStyleSheet('min-width:8em;max-width:8em;')
            label_tunefrac = QLabel('Tune Fraction')
            self.lb_tunefrac = PyDMLabel(
                self, self.device.substitute(propty='TuneFrac-Mon'))
            self.lb_tunefrac.precisionFromPV = False
            self.lb_tunefrac.precision = 4

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

        # Drive Enable
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

        if self.section == 'BO':
            # Frame Count
            lbl_acqcnt = QLabel('Frame Count', self)
            dev = self.device.substitute(dev='TuneProc')
            self.lb_acqcnt = PyDMLabel(
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
            self, self.device.substitute(propty='Span-SP'))
        self.le_span.precisionFromPV = True
        self.lb_span = PyDMLabel(
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
        self.lb_rbw = PyDMLabel(
            self, self.device.substitute(propty='SpecAnaRBW-Sts'))
        hbox_rbw = QHBoxLayout()
        hbox_rbw.addWidget(self.cb_rbw)
        hbox_rbw.addWidget(self.lb_rbw)

        # Harmonic
        lbl_h = QLabel('Harmonic (n)', self)
        self.sb_h = PyDMSpinbox(
            self, self.device.substitute(propty='RevN-SP'))
        self.sb_h.showStepExponent = False
        self.sb_h.precisionFromPV = True
        self.lb_h = PyDMLabel(
            self, self.device.substitute(propty='RevN-RB'))
        hbox_h = QHBoxLayout()
        hbox_h.addWidget(self.sb_h)
        hbox_h.addWidget(self.lb_h)

        # Harmonic Frequency
        lbl_Fh = QLabel('Harm. Freq. [kHz]', self)
        self.lb_Fh = PyDMLabel(parent=self)
        self.lb_Fh.setToolTip('Frf/(h*n)')
        self.lb_Fh.channel = self.device.substitute(propty='FreqRevN-Mon')

        # Frequency Offset
        lbl_foff = QLabel('Freq. Offset [kHz]', self)
        self.sb_foff = PyDMSpinbox(
            self, self.device.substitute(propty='FreqOff-SP'))
        self.sb_foff.showStepExponent = False
        self.sb_foff.precisionFromPV = True
        self.lb_foff = PyDMLabel(
            self, self.device.substitute(propty='FreqOff-RB'))
        hbox_foff = QHBoxLayout()
        hbox_foff.addWidget(self.sb_foff)
        hbox_foff.addWidget(self.lb_foff)

        # Center Frequency
        lbl_Fc = QLabel('Center Freq. [MHz]', self)
        self.le_Fc = PyDMLineEdit(
            self, self.device.substitute(propty='CenterFreq-SP'))
        self.le_Fc.precisionFromPV = True
        self.lb_Fc = PyDMLabel(
            self, self.device.substitute(propty='CenterFreq-RB'))
        hbox_Fc = QHBoxLayout()
        hbox_Fc.addWidget(self.le_Fc)
        hbox_Fc.addWidget(self.lb_Fc)

        # Lock Center Freq.
        lbl_autoFc = QLabel('Lock Center Freq. ', self)
        self.bt_autoFc = PyDMStateButton(
            self, self.device.substitute(propty='CenterFreqAuto-Sel'))
        self.bt_autoFc.shape = 1
        self.led_autoFc = SiriusLedState(
            self, self.device.substitute(propty='CenterFreqAuto-Sts'))
        hbox_autoFc = QHBoxLayout()
        hbox_autoFc.addWidget(self.bt_autoFc)
        hbox_autoFc.addWidget(self.led_autoFc)

        if self.section == 'BO':
            # # ROI
            # StartX
            lbl_roistartx = QLabel('Start X [MHz]', self)
            self.le_roistartx = PyDMLineEdit(
                self, self.device.substitute(propty='ROIOffsetX-SP'))
            self.le_roistartx.precisionFromPV = True
            self.lb_roistartx = PyDMLabel(
                self, self.device.substitute(propty='ROIOffsetX-RB'))
            hbox_roistartx = QHBoxLayout()
            hbox_roistartx.addWidget(self.le_roistartx)
            hbox_roistartx.addWidget(self.lb_roistartx)

            # Width
            lbl_roiwidth = QLabel('Width [MHz]', self)
            self.le_roiwidth = PyDMLineEdit(
                self, self.device.substitute(propty='ROIWidth-SP'))
            self.le_roiwidth.precisionFromPV = True
            self.lb_roiwidth = PyDMLabel(
                self, self.device.substitute(propty='ROIWidth-RB'))
            hbox_roiwidth = QHBoxLayout()
            hbox_roiwidth.addWidget(self.le_roiwidth)
            hbox_roiwidth.addWidget(self.lb_roiwidth)

            # StartY
            lbl_roistarty = QLabel('Start Y [ms]', self)
            self.le_roistarty = PyDMLineEdit(
                self, self.device.substitute(propty='ROIOffsetY-SP'))
            self.le_roistarty.precisionFromPV = True
            self.lb_roistarty = PyDMLabel(
                self, self.device.substitute(propty='ROIOffsetY-RB'))
            hbox_roistarty = QHBoxLayout()
            hbox_roistarty.addWidget(self.le_roistarty)
            hbox_roistarty.addWidget(self.lb_roistarty)

            # Height
            lbl_roiheight = QLabel('Height [ms]', self)
            self.le_roiheight = PyDMLineEdit(
                self, self.device.substitute(propty='ROIHeight-SP'))
            self.le_roiheight.precisionFromPV = True
            self.lb_roiheight = PyDMLabel(
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
        else:
            tab_markers = QTabWidget(self)
            tab_markers.setStyleSheet("""
                QTabWidget::pane {
                    border-left: 2px solid gray;
                    border-bottom: 2px solid gray;
                    border-right: 2px solid gray;
                }
                QTabBar::tab:first {
                    background-color: transparent;
                }
                QTabBar::tab:last {
                    background-color: transparent;
                }""")
            # # Markers
            for mtyp in ['', 'D']:
                wid_markers = QWidget()
                grid_markers = QGridLayout(wid_markers)
                bt_dsblmark = PyDMPushButton(
                    parent=self, icon=qta.icon('mdi.window-close'),
                    pressValue=1)
                bt_dsblmark.setToolTip(
                    'Disable All '+('Delta ' if mtyp else '')+'Markers')
                bt_dsblmark.channel = self.device.substitute(
                    dev='TuneProc', propty_name=mtyp+'MarkAOff',
                    propty_suffix='Cmd')
                bt_dsblmark.setObjectName('mark_dsbl')
                grid_markers.addWidget(bt_dsblmark, 0, 0)
                grid_markers.addWidget(
                    QLabel('Enable', self, alignment=Qt.AlignHCenter),
                    0, 1, 1, 2)
                grid_markers.addWidget(
                    QLabel('Auto Max', self, alignment=Qt.AlignHCenter),
                    0, 3, 1, 2)

                for i in range(1, 5):
                    bt_enbl = PyDMStateButton(
                        self, self.device.substitute(
                            dev='TuneProc', propty_name='Enbl'+mtyp+'Mark' +
                                str(i), propty_suffix='Sel'))
                    bt_enbl.setStyleSheet('min-width:2.5em; max-width:2.5em;')
                    led_enbl = SiriusLedState(
                        self, self.device.substitute(
                            dev='TuneProc', propty_name='Enbl'+mtyp+'Mark' +
                                str(i), propty_suffix='Sts'))
                    bt_max = PyDMStateButton(
                        self, self.device.substitute(
                            dev='TuneProc', propty_name='Enbl'+mtyp+'MaxAuto' +
                                str(i), propty_suffix='Sel'))
                    bt_max.setStyleSheet('min-width:2.5em;max-width:2.5em;')
                    led_max = SiriusLedState(
                        self, self.device.substitute(
                            dev='TuneProc', propty_name='Enbl'+mtyp+'MaxAuto' +
                                str(i), propty_suffix='Sts'))
                    color = marker_color[mtyp+'Mark'][self.orientation][str(i)]
                    pb_m = QPushButton(
                        qta.icon('mdi.record-circle-outline', color=color),
                        str(i), self)
                    pb_m.setObjectName('mark_dtl')
                    util.connect_window(
                        pb_m, SITuneMarkerDetails, self,
                        prefix=self.prefix, orientation=self.orientation,
                        index=i, background=self.background,
                        isdelta=bool(mtyp))
                    grid_markers.addWidget(pb_m, i, 0)
                    grid_markers.addWidget(
                        bt_enbl, i, 1, alignment=Qt.AlignRight)
                    grid_markers.addWidget(
                        led_enbl, i, 2, alignment=Qt.AlignLeft)
                    grid_markers.addWidget(
                        bt_max, i, 3, alignment=Qt.AlignRight)
                    grid_markers.addWidget(
                        led_max, i, 4, alignment=Qt.AlignLeft)
                tab_markers.addTab(
                    wid_markers, ('Delta' if mtyp else '')+'Markers')

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
        lay.addRow(hbox_details)
        if self.section == 'SI':
            lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
            lay.addRow(tab_markers)

        self.setStyleSheet("""
            QLed{
                min-width:1.29em; max-width:1.29em;
            }
            #mark_dsbl{
                min-width:25px; max-width:25px; icon-size:20px;
            }
            #detail, #mark_dtl{
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
            {dev.substitute(propty='FrameCount-Mon'): new_value})

    def _calc_tunefreq(self, val):
        address = self.sender().address
        if 'TuneFreq' in address:
            self.tunefreq_currval = val
        elif 'FreqRevN' in address:
            self.freqrevn_currval = val
        delta = self.tunefreq_currval - self.freqrevn_currval*1e3
        delta /= 1e3
        self.lb_tunefreq.value_changed(delta)


class SITuneMonitor(QWidget):

    def __init__(self, parent=None, prefix='', description='long',
                 use_color_labels=True):
        super().__init__(parent)
        self.prefix = prefix
        self.app = QApplication.instance()
        self.description = description
        self.use_color_labels = use_color_labels
        if self.description == 'long':
            self.hdesc = '<h4> Horizontal </h4>'
            self.vdesc = '<h4> Vertical </h4>'
        else:
            self.hdesc = '<h3> Tune-H </h3>'
            self.vdesc = '<h3> Tune-V </h3>'
        self._setupUi()

    def _setupUi(self):
        lay_tune = QGridLayout(self)

        self.ld_tunefrach = QLabel(self.hdesc, self, alignment=Qt.AlignHCenter)
        self.lb_tunefrach = PyDMLabel(self, SiriusPVName(
            'SI-Glob:DI-Tune-H:TuneFrac-Mon').substitute(prefix=self.prefix))
        self.lb_tunefrach.precisionFromPV = False
        self.lb_tunefrach.precision = 4
        self.lb_tunefrach.setAlignment(Qt.AlignHCenter)
        self.lb_tunefrach.setStyleSheet('QLabel{font-size: 30pt;}')
        wid_tuneh = QWidget()
        wid_tuneh.setObjectName('wid_tuneh')
        if self.use_color_labels:
            wid_tuneh.setStyleSheet('background-color:#B3E5FF;')
        vbox_tuneh = QVBoxLayout(wid_tuneh)
        vbox_tuneh.addWidget(self.ld_tunefrach)
        vbox_tuneh.addWidget(self.lb_tunefrach)
        lay_tune.addWidget(wid_tuneh, 0, 0)

        self.ld_tunefracv = QLabel(self.vdesc, self, alignment=Qt.AlignHCenter)
        self.lb_tunefracv = PyDMLabel(self, SiriusPVName(
            'SI-Glob:DI-Tune-V:TuneFrac-Mon').substitute(prefix=self.prefix))
        self.lb_tunefracv.precisionFromPV = False
        self.lb_tunefracv.precision = 4
        self.lb_tunefracv.setAlignment(Qt.AlignHCenter)
        self.lb_tunefracv.setStyleSheet('QLabel{font-size: 30pt;}')
        wid_tunev = QWidget()
        wid_tunev.setObjectName('wid_tunev')
        if self.use_color_labels:
            wid_tunev.setStyleSheet('background-color:#FFB3B3;')
        vbox_tunev = QVBoxLayout(wid_tunev)
        vbox_tunev.setAlignment(Qt.AlignHCenter)
        vbox_tunev.addWidget(self.ld_tunefracv)
        vbox_tunev.addWidget(self.lb_tunefracv)
        lay_tune.addWidget(wid_tunev, 0, 1)

    def changeEvent(self, event):
        if event.type() == QEvent.FontChange and self.description == 'long':
            fontsize = self.app.font().pointSize() + 20
            self.lb_tunefrach.setStyleSheet(
                'QLabel{font-size: '+str(fontsize)+'pt;}')
            self.lb_tunefracv.setStyleSheet(
                'QLabel{font-size: '+str(fontsize)+'pt;}')

            self.ensurePolished()
