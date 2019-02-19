#!/usr/bin/env python-sirius
"""HLA TB and TS ICT monitoring Window."""

import sys
import numpy as np
from qtpy.uic import loadUi
from qtpy.QtCore import Slot, Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QFormLayout, QGridLayout, QHBoxLayout, QVBoxLayout,\
                           QSizePolicy as QSzPlcy, QLabel, QPushButton,\
                           QSpacerItem, QGroupBox, QWidget, QSpinBox
from pydm.widgets import PyDMLabel, PyDMEnumComboBox, PyDMSpinbox, \
                         PyDMPushButton, PyDMWaveformPlot
from pydm.widgets.waveformplot import WaveformCurveItem
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, SiriusDialog, \
                              SiriusConnectionSignal, SiriusLedAlert, \
                              PyDMStateButton, PyDMLedMultiChannel
from siriushla.widgets.windows import create_window_from_widget
from siriushla import util
from siriushla.as_ti_control.hl_trigger import HLTriggerDetailed

POINTS_TO_PLOT = 500


class ICTMonitoring(SiriusMainWindow):
    """Class to create ICTs History Monitor Window."""

    def __init__(self, tl, parent=None, prefix=None):
        """Create graphs."""
        super(ICTMonitoring, self).__init__(parent)
        # Set transport line
        if tl.upper() == 'TB':
            ICT1 = 'TB-02:DI-ICT'
            ICT2 = 'TB-04:DI-ICT'
        elif tl.upper() == 'TS':
            ICT1 = 'TS-01:DI-ICT'
            ICT2 = 'TS-04:DI-ICT'

        tmp_file = _substitute_in_file(
            '/home/sirius/repos/hla/pyqt-apps/siriushla'
            '/tl_ap_control/ui_tl_ap_ictmon.ui',
            {'TL': tl.upper(), 'ICT1': ICT1, 'ICT2': ICT2, 'PREFIX': prefix})
        self.setWindowTitle(tl.upper()+' ICTs Monitor')
        self.centralwidget = loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)

        # Add curves accordingly
        self.centralwidget.PyDMTimePlot_Charge.addYChannel(
            y_channel=prefix+ICT1+':Charge-Mon',
            name='Charge '+ICT1, color='red', lineWidth=2)
        self.centralwidget.PyDMTimePlot_Charge.addYChannel(
            y_channel=prefix+ICT2+':Charge-Mon',
            name='Charge '+ICT2, color='blue', lineWidth=2)
        self.centralwidget.PyDMWaveformPlot_ChargeHstr.addChannel(
            y_channel=prefix+ICT1+':ChargeHstr-Mon',
            name='Charge History '+ICT1, color='red', lineWidth=2)
        self.centralwidget.PyDMWaveformPlot_ChargeHstr.addChannel(
            y_channel=prefix+ICT2+':ChargeHstr-Mon',
            name='Charge History '+ICT2, color='blue', lineWidth=2)

        # Connect signals to controls curves visibility
        self.centralwidget.checkBox.stateChanged.connect(
            self._setICT1CurveVisibility)
        self.centralwidget.checkBox_2.stateChanged.connect(
            self._setICT2CurveVisibility)

        # Add menu
        menu = self.menuBar().addMenu('Settings')
        act_ICT1settings = menu.addAction(ICT1)
        util.connect_window(act_ICT1settings, _ICTSettings,
                            parent=self, prefix=prefix, device=ICT1)
        act_ICT2settings = menu.addAction(ICT2)
        util.connect_window(act_ICT2settings, _ICTSettings,
                            parent=self, prefix=prefix, device=ICT2)

        self.centralwidget.setStyleSheet("""
            #tabWidget{
                min-width:40em;
                min-height:28em;}
            #label_window{
                font-size:1.1em;
                font-weight:bold;
                background-color: qlineargradient(spread:pad,
                    x1:1, y1:0.0227273, x2:0, y2:0,
                    stop:0 rgba(173, 190, 207, 255),
                    stop:1 rgba(213, 213, 213, 255));
                min-height:1.29em; max-height:1.29em;
            }""")

    @Slot(int)
    def _setICT1CurveVisibility(self, value):
        """Set curves visibility."""
        self.centralwidget.PyDMTimePlot_Charge._curves[0].setVisible(value)
        self.centralwidget.PyDMWaveformPlot_ChargeHstr._curves[0].setVisible(
            value)

    @Slot(int)
    def _setICT2CurveVisibility(self, value):
        """Set curves visibility."""
        self.centralwidget.PyDMTimePlot_Charge._curves[1].setVisible(value)
        self.centralwidget.PyDMWaveformPlot_ChargeHstr._curves[1].setVisible(
            value)


class _ICTSettings(SiriusDialog):
    """Auxiliar window to diagnosis settings."""

    def __init__(self, parent, prefix, device):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = device
        self.ict_prefix = prefix+device
        self.ict_trig_prefix = self.ict_prefix.replace(':DI-', ':TI-')
        self.setWindowTitle(self.ict_prefix+' Settings')
        self._setupUi()

    def _setupUi(self):
        l_ictacq = QLabel('<h3>'+self.ict_prefix+' Settings</h3>', self,
                          alignment=Qt.AlignCenter)

        self.gbox_reliablemeas = self._setupReliableMeasWidget()
        self.gbox_generalsettings = self._setupICTGeneralSettingsWidget()

        self.bt_cal = QPushButton('ICT Calibration', self)
        dialog = create_window_from_widget(
            _ICTCalibration, name=self.ict_prefix+' Calibration')
        util.connect_window(self.bt_cal, dialog, parent=self,
                            ict_prefix=self.ict_prefix)
        self.bt_cal.setAutoDefault(False)
        self.bt_cal.setDefault(False)
        hlay_cal = QHBoxLayout()
        hlay_cal.addItem(QSpacerItem(4, 2, QSzPlcy.Expanding, QSzPlcy.Fixed))
        hlay_cal.addWidget(self.bt_cal)

        self.gbox_generalsettings.setStyleSheet("""
            PyDMSpinbox{
                min-width:7.10em;\nmax-width:7.10em;
                min-height:1.29em;\nmax-height:1.29em;
                qproperty-alignment: AlignCenter;\n}
            PyDMEnumComboBox{
                min-width:7.10em;\nmax-width:7.10em;
                min-height:1.29em;\nmax-height:1.29em;\n}
            PyDMLedMultiChannel{
                min-width:7.10em;\nmax-width:7.10em;
                min-height:1.29em;\nmax-height:1.29em;\n}""")

        lay = QVBoxLayout()
        lay.addStretch()
        lay.addWidget(l_ictacq)
        lay.addStretch()
        lay.addWidget(self.gbox_reliablemeas)
        lay.addStretch()
        lay.addWidget(self.gbox_generalsettings)
        lay.addStretch()
        lay.addLayout(hlay_cal)
        lay.addStretch()
        lay.setSpacing(20)
        self.setLayout(lay)

    def _setupReliableMeasWidget(self):
        reliablemeas_channel = SiriusConnectionSignal(
            self.ict_prefix+':ReliableMeasLabels-Mon')
        reliablemeas_channel.new_value_signal.connect(
            self._updateReliableMeasLabels)

        gbox_reliablemeas = _GroupBoxWithChannel(
            'ICT Measure Reliability Status', self, [reliablemeas_channel])
        gbox_reliablemeas.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Fixed)

        self.label_reliablemeas0 = QLabel('', self)
        self.led_ReliableMeas0 = SiriusLedAlert(
            parent=self, init_channel=self.ict_prefix+':ReliableMeas-Mon',
            bit=0)
        self.label_reliablemeas1 = QLabel('', self)
        self.led_ReliableMeas1 = SiriusLedAlert(
            parent=self, init_channel=self.ict_prefix+':ReliableMeas-Mon',
            bit=1)
        self.label_reliablemeas2 = QLabel('', self)
        self.led_ReliableMeas2 = SiriusLedAlert(
            parent=self, init_channel=self.ict_prefix+':ReliableMeas-Mon',
            bit=2)
        lay_reliablemeas = QGridLayout()
        lay_reliablemeas.addWidget(self.led_ReliableMeas0, 0, 0)
        lay_reliablemeas.addWidget(self.label_reliablemeas0, 0, 1)
        lay_reliablemeas.addWidget(self.led_ReliableMeas1, 1, 0)
        lay_reliablemeas.addWidget(self.label_reliablemeas1, 1, 1)
        lay_reliablemeas.addWidget(self.led_ReliableMeas2, 2, 0)
        lay_reliablemeas.addWidget(self.label_reliablemeas2, 2, 1)
        gbox_reliablemeas.setLayout(lay_reliablemeas)
        return gbox_reliablemeas

    def _setupICTGeneralSettingsWidget(self):
        gbox_generalsettings = QGroupBox(
            'ICT Measurement Settings', self)

        l_sampletrg = QLabel('Measurement Trigger Source: ', self)
        self.pydmenumcombobox_SampleTrg = PyDMEnumComboBox(
            parent=self, init_channel=self.ict_prefix+':SampleTrg-Sel')
        self.pydmlabel_SampleTrg = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':SampleTrg-Sts')
        hlay_sampletrg = QHBoxLayout()
        hlay_sampletrg.addWidget(self.pydmenumcombobox_SampleTrg)
        hlay_sampletrg.addWidget(self.pydmlabel_SampleTrg)

        l_TIstatus = QLabel('Timing Trigger Status: ', self)
        self.ledmulti_TIStatus = PyDMLedMultiChannel(
            parent=self,
            channels2values={self.ict_trig_prefix+':State-Sts': 1,
                             self.ict_trig_prefix+':Status-Mon': 0})
        self.pb_trgdetails = QPushButton('Open details', self)
        self.pb_trgdetails.setAutoDefault(False)
        self.pb_trgdetails.setDefault(False)
        util.connect_window(
            self.pb_trgdetails, HLTriggerDetailed, parent=self,
            prefix=self.ict_trig_prefix+':')
        hlay_TIstatus = QHBoxLayout()
        hlay_TIstatus.addWidget(self.ledmulti_TIStatus)
        hlay_TIstatus.addWidget(self.pb_trgdetails)

        l_TIdelay = QLabel('Timing Trigger Delay: ', self)
        self.pydmspinbox_TIDelay = PyDMSpinbox(
            parent=self, init_channel=self.ict_trig_prefix+':Delay-SP')
        self.pydmspinbox_TIDelay.showStepExponent = False
        self.pydmlabel_TIDelay = PyDMLabel(
            parent=self, init_channel=self.ict_trig_prefix+':Delay-RB')
        hlay_TIdelay = QHBoxLayout()
        hlay_TIdelay.addWidget(self.pydmspinbox_TIDelay)
        hlay_TIdelay.addWidget(self.pydmlabel_TIDelay)

        l_thold = QLabel('Charge Threshold [mA]: ', self)
        self.pydmspinbox_Threshold = PyDMSpinbox(
            parent=self, init_channel=self.ict_prefix+':Threshold-SP')
        self.pydmspinbox_Threshold.showStepExponent = False
        self.pydmlabel_Threshold = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':Threshold-RB')
        hlay_thold = QHBoxLayout()
        hlay_thold.addWidget(self.pydmspinbox_Threshold)
        hlay_thold.addWidget(self.pydmlabel_Threshold)

        flay_generalsettings = QFormLayout()
        flay_generalsettings.setFormAlignment(Qt.AlignCenter)
        flay_generalsettings.addRow(l_sampletrg, hlay_sampletrg)
        flay_generalsettings.addRow(l_TIstatus, hlay_TIstatus)
        flay_generalsettings.addRow(l_TIdelay, hlay_TIdelay)
        flay_generalsettings.addItem(
            QSpacerItem(1, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))
        flay_generalsettings.addRow(l_thold, hlay_thold)
        flay_generalsettings.setFormAlignment(Qt.AlignCenter)
        flay_generalsettings.setLabelAlignment(Qt.AlignRight)
        gbox_generalsettings.setLayout(flay_generalsettings)
        return gbox_generalsettings

    def _updateReliableMeasLabels(self, labels):
        if labels:
            self.label_reliablemeas0.setText(labels[0])
            self.label_reliablemeas1.setText(labels[1])
            self.label_reliablemeas2.setText(labels[2])


class _ICTCalibration(QWidget):

    def __init__(self, parent, ict_prefix):
        """Initialize object."""
        super().__init__(parent)
        self.ict_prefix = ict_prefix
        self.setObjectName('ICTCalibration')
        self._setupUi()

    def _setupUi(self):
        label_cal = QLabel('<h3>'+self.ict_prefix+' Calibration</h3>', self,
                           alignment=Qt.AlignCenter)
        lay_meassettings = self._setupMeasSettingsLayout()
        [self.graph_rawread, lay_graphsettings] = self._setupGraph()

        glay = QGridLayout()
        glay.addWidget(label_cal, 0, 0, 1, 2)
        glay.addWidget(QLabel('<h4>Measurement Settings</h4>', self,
                              alignment=Qt.AlignCenter), 1, 0)
        glay.addLayout(lay_meassettings, 2, 0, alignment=Qt.AlignCenter)
        glay.addLayout(lay_graphsettings, 3, 0)
        glay.addWidget(QLabel('<h4>RawReadings Monitor</h4>', self,
                              alignment=Qt.AlignCenter), 1, 1)
        glay.addWidget(self.graph_rawread, 2, 1, 2, 1)
        self.setLayout(glay)
        self.setStyleSheet("""
            #ICTCalibration{
                min-width:65em;
                min-height:34em;}
            PyDMSpinbox{
                min-width:7.10em;\nmax-width:7.10em;
                min-height:1.29em;\nmax-height:1.29em;
                qproperty-alignment: AlignCenter;\n}
            PyDMStateButton{
                min-width:7.10em;\nmax-width:7.10em;
                min-height:1.29em;\nmax-height:1.29em;\n}
            PyDMEnumComboBox{
                min-width:7.10em;\nmax-width:7.10em;
                min-height:1.29em;\nmax-height:1.29em;\n}
            PyDMLabel{
                min-width:7.10em;\nmax-width:7.10em;
                min-height:1.29em;\nmax-height:1.29em;
                qproperty-alignment: AlignCenter;\n}
            QPushButton{
                min-width:14.2em;\nmax-width:14.2em;\n}""")
        glay.setRowStretch(0, 4)
        glay.setRowStretch(1, 2)
        glay.setRowStretch(2, 24)
        glay.setRowStretch(3, 4)

    def _setupMeasSettingsLayout(self):
        l_thold = QLabel('Charge Threshold [nC]: ', self)
        self.pydmspinbox_Threshold = PyDMSpinbox(
            parent=self, init_channel=self.ict_prefix+':Threshold-SP')
        self.pydmspinbox_Threshold.showStepExponent = False
        self.pydmlabel_Threshold = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':Threshold-RB')
        hlay_thold = QHBoxLayout()
        hlay_thold.addWidget(self.pydmspinbox_Threshold)
        hlay_thold.addWidget(self.pydmlabel_Threshold)

        l_hfreject = QLabel('High Frequency Rejection: ', self)
        self.pydmstatebutton_HFReject = PyDMStateButton(
            parent=self, init_channel=self.ict_prefix+':HFReject-Sel')
        self.pydmstatebutton_HFReject.shape = 1
        self.pydmlabel_HFReject = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':HFReject-Sts')
        hlay_hfreject = QHBoxLayout()
        hlay_hfreject.addWidget(self.pydmstatebutton_HFReject)
        hlay_hfreject.addWidget(self.pydmlabel_HFReject)

        l_2ndreaddy = QLabel('2nd Read Delay [s]: ', self)
        self.pydmspinbox_2ndReadDly = PyDMSpinbox(
            parent=self, init_channel=self.ict_prefix+':2ndReadDly-SP')
        self.pydmspinbox_2ndReadDly.showStepExponent = False
        self.pydmlabel_2ndReadDly = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':2ndReadDly-RB')
        hlay_2ndreaddy = QHBoxLayout()
        hlay_2ndreaddy.addWidget(self.pydmspinbox_2ndReadDly)
        hlay_2ndreaddy.addWidget(self.pydmlabel_2ndReadDly)

        l_samplecnt = QLabel('Sample Count: ', self)
        self.pydmspinbox_SampleCnt = PyDMSpinbox(
            parent=self, init_channel=self.ict_prefix+':SampleCnt-SP')
        self.pydmspinbox_SampleCnt.showStepExponent = False
        self.pydmlabel_SampleCnt = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':SampleCnt-RB')
        hlay_samplecnt = QHBoxLayout()
        hlay_samplecnt.addWidget(self.pydmspinbox_SampleCnt)
        hlay_samplecnt.addWidget(self.pydmlabel_SampleCnt)

        l_aperture = QLabel('Aperture [us]: ', self)
        self.pydmspinbox_Aperture = PyDMSpinbox(
            parent=self, init_channel=self.ict_prefix+':Aperture-SP')
        self.pydmspinbox_Aperture.showStepExponent = False
        self.pydmlabel_Aperture = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':Aperture-RB')
        hlay_aperture = QHBoxLayout()
        hlay_aperture.addWidget(self.pydmspinbox_Aperture)
        hlay_aperture.addWidget(self.pydmlabel_Aperture)

        l_samplerate = QLabel('Sample Rate [rdgs/s]: ', self)
        self.pydmspinbox_SampleRate = PyDMSpinbox(
            parent=self, init_channel=self.ict_prefix+':SampleRate-SP')
        self.pydmspinbox_SampleRate.showStepExponent = False
        self.pydmlabel_SampleRate = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':SampleRate-RB')
        hlay_samplerate = QHBoxLayout()
        hlay_samplerate.addWidget(self.pydmspinbox_SampleRate)
        hlay_samplerate.addWidget(self.pydmlabel_SampleRate)

        l_imped = QLabel('Impedance: ', self)
        self.pydmstatebutton_Imped = PyDMEnumComboBox(
            parent=self, init_channel=self.ict_prefix+':Imped-Sel')
        self.pydmstatebutton_Imped.shape = 1
        self.pydmlabel_Imped = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':Imped-Sts')
        hlay_imped = QHBoxLayout()
        hlay_imped.addWidget(self.pydmstatebutton_Imped)
        hlay_imped.addWidget(self.pydmlabel_Imped)

        l_bcmrange = QLabel('BCM Range [V]: ', self)
        self.pydmspinbox_BCMRange = PyDMSpinbox(
            parent=self, init_channel=self.ict_prefix+':BCMRange-SP')
        self.pydmspinbox_BCMRange.showStepExponent = False

        l_range = QLabel('Range: ', self)
        self.pydmenumcombobox_Range = PyDMEnumComboBox(
            parent=self, init_channel=self.ict_prefix+':Range-Sel')
        self.pydmlabel_Range = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':Range-Sts')
        hlay_range = QHBoxLayout()
        hlay_range.addWidget(self.pydmenumcombobox_Range)
        hlay_range.addWidget(self.pydmlabel_Range)

        l_calenbl = QLabel('Calibration Enable: ', self)
        self.pydmstatebutton_CalEnbl = PyDMStateButton(
            parent=self, init_channel=self.ict_prefix+':CalEnbl-Sel')
        self.pydmstatebutton_CalEnbl.shape = 1
        self.pydmlabel_CalEnbl = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':CalEnbl-Sts')
        hlay_calenbl = QHBoxLayout()
        hlay_calenbl.addWidget(self.pydmstatebutton_CalEnbl)
        hlay_calenbl.addWidget(self.pydmlabel_CalEnbl)

        l_calcharge = QLabel('Calibration Charge: ', self)
        self.pydmenumcombobox_CalCharge = PyDMEnumComboBox(
            parent=self, init_channel=self.ict_prefix+':CalCharge-Sel')
        self.pydmlabel_CalCharge = PyDMLabel(
            parent=self, init_channel=self.ict_prefix+':CalCharge-Sts')
        hlay_calcharge = QHBoxLayout()
        hlay_calcharge.addWidget(self.pydmenumcombobox_CalCharge)
        hlay_calcharge.addWidget(self.pydmlabel_CalCharge)

        l_download = QLabel('Download to hardware? ', self)
        self.pydmpushbutton_Download = PyDMPushButton(
            parent=self, init_channel=self.ict_prefix+':Download-Cmd',
            label='Download', pressValue=1)

        flay = QFormLayout()
        flay.addRow(l_thold, hlay_thold)
        flay.addRow(l_hfreject, hlay_hfreject)
        flay.addItem(QSpacerItem(1, 20, QSzPlcy.Ignored, QSzPlcy.Preferred))
        flay.addRow(l_2ndreaddy, hlay_2ndreaddy)
        flay.addItem(QSpacerItem(1, 20, QSzPlcy.Ignored, QSzPlcy.Preferred))
        flay.addRow(l_samplecnt, hlay_samplecnt)
        flay.addRow(l_aperture, hlay_aperture)
        flay.addRow(l_samplerate, hlay_samplerate)
        flay.addRow(l_imped, hlay_imped)
        flay.addItem(QSpacerItem(1, 20, QSzPlcy.Ignored, QSzPlcy.Preferred))
        flay.addRow(l_bcmrange, self.pydmspinbox_BCMRange)
        flay.addRow(l_range, hlay_range)
        flay.addItem(QSpacerItem(1, 20, QSzPlcy.Ignored, QSzPlcy.Preferred))
        flay.addRow(l_calenbl, hlay_calenbl)
        flay.addRow(l_calcharge, hlay_calcharge)
        flay.addItem(QSpacerItem(1, 20, QSzPlcy.Ignored, QSzPlcy.Preferred))
        flay.addRow(l_download, self.pydmpushbutton_Download)
        flay.addItem(QSpacerItem(1, 20, QSzPlcy.Ignored, QSzPlcy.Preferred))
        flay.setLabelAlignment(Qt.AlignRight)
        return flay

    def _setupGraph(self):
        graph_rawread = _MyWaveformPlot(self)
        graph_rawread.setObjectName('graph_rawread')
        graph_rawread.autoRangeX = True
        graph_rawread.autoRangeY = True
        graph_rawread.backgroundColor = QColor(255, 255, 255)
        graph_rawread.showLegend = True
        graph_rawread.showXGrid = True
        graph_rawread.showYGrid = True
        graph_rawread.setStyleSheet("""
            #graph_rawread{min-width:36em;\nmin-height:28em;}""")
        graph_rawread.setLabels(left='Raw Readings', bottom='Index')
        graph_rawread.addChannel(
            y_channel=self.ict_prefix+':RawPulse-Mon', name='RawPulse',
            color='blue', lineWidth=2, lineStyle=Qt.SolidLine)
        graph_rawread.addChannel(
            y_channel=self.ict_prefix+':RawNoise-Mon', name='RawNoise',
            color='red', lineWidth=2, lineStyle=Qt.SolidLine)
        leftAxis = graph_rawread.getAxis('left')
        leftAxis.setStyle(autoExpandTextSpace=False, tickTextWidth=25)
        self.curvePulse = graph_rawread.curveAtIndex(0)
        self.curveNoise = graph_rawread.curveAtIndex(1)

        label_graphsettings = QLabel('<h4>Graph Settings</h4>', self,
                                     alignment=Qt.AlignHCenter)
        l_plot = QLabel('Plot first', self, alignment=Qt.AlignRight)
        l_points = QLabel(' points ', self)
        self.sb_nrpoints = QSpinBox(self)
        self.sb_nrpoints.setMinimum(0)
        self.sb_nrpoints.setMaximum(1000)
        self.sb_nrpoints.setValue(POINTS_TO_PLOT)
        self.sb_nrpoints.setStyleSheet("""
            min-width:7.10em;\nmax-width:7.10em;\n
            min-height:1.29em;\nmax-height:1.29em;\n""")
        self.sb_nrpoints.editingFinished.connect(self._set_nrpoints)
        glay_graphpoints = QGridLayout()
        glay_graphpoints.addWidget(label_graphsettings, 0, 0, 1, 3)
        glay_graphpoints.addWidget(l_plot, 1, 0)
        glay_graphpoints.addWidget(self.sb_nrpoints, 1, 1)
        glay_graphpoints.addWidget(l_points, 1, 2)
        return [graph_rawread, glay_graphpoints]

    def _set_nrpoints(self):
        global POINTS_TO_PLOT
        POINTS_TO_PLOT = self.sb_nrpoints.value()


class _GroupBoxWithChannel(QGroupBox):

    def __init__(self, title='', parent=None, channels=None):
        self._channels = channels
        super().__init__(title, parent)

    def channels(self):
        """Return channels."""
        return self._channels


class _MyWaveformCurveItem(WaveformCurveItem):

    def redrawCurve(self):
        if self.y_waveform is None:
            return
        if self.x_waveform is None:
            self.setData(y=self.y_waveform[0:POINTS_TO_PLOT].astype(np.float))
            return
        if self.x_waveform.shape[0] > self.y_waveform.shape[0]:
            self.x_waveform = self.x_waveform[:self.y_waveform.shape[0]]
        elif self.x_waveform.shape[0] < self.y_waveform.shape[0]:
            self.y_waveform = self.y_waveform[:self.x_waveform.shape[0]]
        self.setData(x=self.x_waveform[0:POINTS_TO_PLOT].astype(np.float),
                     y=self.y_waveform[0:POINTS_TO_PLOT].astype(np.float))
        self.needs_new_x = True
        self.needs_new_y = True


class _MyWaveformPlot(PyDMWaveformPlot):

    def addChannel(self, y_channel=None, x_channel=None, name=None,
                   color=None, lineStyle=None, lineWidth=None,
                   symbol=None, symbolSize=None, redraw_mode=None):
        plot_opts = {}
        plot_opts['symbol'] = symbol
        if symbolSize is not None:
            plot_opts['symbolSize'] = symbolSize
        if lineStyle is not None:
            plot_opts['lineStyle'] = lineStyle
        if lineWidth is not None:
            plot_opts['lineWidth'] = lineWidth
        if redraw_mode is not None:
            plot_opts['redraw_mode'] = redraw_mode
        self._needs_redraw = False
        curve = _MyWaveformCurveItem(
            y_addr=y_channel, x_addr=x_channel, name=name,
            color=color, **plot_opts)
        self.channel_pairs[(y_channel, x_channel)] = curve
        self.addCurve(curve, curve_color=color)
        curve.data_changed.connect(self.set_needs_redraw)


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    w = ICTMonitoring(tl='TB', prefix=_vaca_prefix)
    w.show()
    sys.exit(app.exec_())
