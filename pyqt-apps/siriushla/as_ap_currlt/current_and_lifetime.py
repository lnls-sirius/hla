"""Current and Lifetime Window."""

from datetime import datetime as _datetime, timedelta as _timedelta
import time as _time
import numpy as _np

from qtpy.QtCore import Slot, Qt
from qtpy.QtWidgets import QLabel, QGroupBox, QWidget, QSpacerItem,\
    QSizePolicy as QSzPlcy, QComboBox, QSpinBox, QPushButton, QCheckBox,\
    QGridLayout, QHBoxLayout, QVBoxLayout
import qtawesome as qta
from pydm.widgets import PyDMEnumComboBox, PyDMLabel, PyDMLineEdit,\
    PyDMPushButton, PyDMSpinbox

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.clientarch import ClientArchiver
from siriushla.util import connect_window
from siriushla.widgets import SiriusLabel, SiriusLedAlert, SiriusLedState,\
    SiriusSpinbox, PyDMStateButton, SiriusMainWindow, SiriusConnectionSignal
from siriushla.as_di_dccts import DCCTMain

from .custom_widgets import MyGraph


class CurrLTWindow(SiriusMainWindow):
    """Current and Lifetime Window."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """Initialize some widgets."""
        super(CurrLTWindow, self).__init__(parent)
        self.prefix = prefix
        self.device = 'SI-Glob:AP-CurrInfo'
        self.device_prefix = self.prefix + self.device
        self.setObjectName('SIApp')
        self.setWindowTitle('SI Current Info: Current and Lifetime')
        self._setupUi()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        self.label_title = QLabel('SI Current and Lifetime')
        self.label_title.setStyleSheet("""
            font-size:1.2em; font-weight:bold;
            background-color: qlineargradient(spread:pad, x1:1, y1:0.0227273,
                              x2:0, y2:0, stop:0 rgba(173, 190, 207, 255),
                              stop:1 rgba(213, 213, 213, 255));""")
        self.label_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        vlay = QVBoxLayout()
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.addWidget(self._setupCurrentSettingsWidget())
        vlay.addWidget(self._setupLifetimeSettigsWidget())
        vlay.addWidget(self._setupGraphSettingsWidget())

        cw = QWidget()
        self.setCentralWidget(cw)
        lay = QGridLayout(cw)
        lay.addWidget(self.label_title, 0, 0, 1, 2)
        lay.addLayout(self._setupGraphPanelLayout(), 1, 0)
        lay.addLayout(vlay, 1, 1)
        lay.setColumnStretch(0, 6)
        lay.setColumnStretch(1, 1)

    def _setupGraphPanelLayout(self):
        # Main Panel
        # # Labels
        self._ld_current = QLabel('Current', self, alignment=Qt.AlignCenter)
        self._ld_current.setStyleSheet("font-weight:bold; max-height1.5em;")
        self._lb_current = PyDMLabel(
            self, self.device_prefix+':Current-Mon')
        self._lb_current.setStyleSheet("font-size:40px;")
        self._lb_current.precision = 0
        self._lb_current.showUnits = True

        self._ld_lifetime = QLabel('Lifetime', self)
        self._ld_lifetime.setStyleSheet("font-weight:bold; max-height1.5em;")
        self._ld_lifetime.setAlignment(Qt.AlignCenter)
        self._lb_lifetime = QLabel('0:00:00', self)
        self._lb_lifetime.channel = self.device_prefix+':Lifetime-Mon'
        self._lb_lifetime.setStyleSheet("font-size:40px;")
        self.lifetime_dcct_pv = SiriusConnectionSignal(
            self.device_prefix+':Lifetime-Mon')
        self.lifetime_dcct_pv.new_value_signal[float].connect(
            self._format_lifetime_label)
        self.lifetime_bpm_pv = SiriusConnectionSignal(
            self.device_prefix+':LifetimeBPM-Mon')
        self.lifetime_bpm_pv.new_value_signal[float].connect(
            self._format_lifetime_label)

        # # Graph
        self.graph = MyGraph(self, background='w')
        self.graph.plotItem.getAxis('left').setLabel(
            'Current [mA]', color='blue')
        self.graph.plotItem.getAxis('right').setLabel(
            'Lifetime [h]', color='red')
        self.graph.showLegend = False
        self.graph.showXGrid = True
        self.graph.showYGrid = True
        self.graph.autoRangeY = True
        self.graph.setObjectName('graph')
        self.graph.setStyleSheet('#graph{min-width:40em;}')
        self.graph.bufferSize = 36000
        self._set_graph_timespan(2000)

        self.graph.addYChannel(
            y_channel=self.device_prefix+':Current-Mon',
            axis='left', name='Current', color='blue', lineWidth=1)
        self._curve_current = self.graph.curveAtIndex(0)
        self._fill_curve_with_archdata(
            self._curve_current,
            self.device_prefix+':Current-Mon')

        self.graph.addYChannel(
            y_channel=self.prefix+'SI-01M1:DI-BPM:Sum-Mon',
            axis='left', name='Current', color='blue', lineWidth=1)
        self._curve_bpmsum = self.graph.curveAtIndex(1)
        self._fill_curve_with_archdata(
            self._curve_bpmsum, self.prefix+'SI-01M1:DI-BPM:Sum-Mon')

        self.graph.addYChannel(
            y_channel='FAKE:Lifetime', axis='right', name='Lifetime',
            color='red', lineWidth=1)
        self._curve_lifetimedcct = self.graph.curveAtIndex(2)
        self._fill_curve_with_archdata(
            self._curve_lifetimedcct,
            self.device_prefix+':Lifetime-Mon',
            factor=3600)

        self.graph.addYChannel(
            y_channel='FAKE:LifetimeBPM', axis='right', name='Lifetime',
            color='red', lineWidth=1)
        self._curve_lifetimebpm = self.graph.curveAtIndex(3)
        self._fill_curve_with_archdata(
            self._curve_lifetimebpm,
            self.device_prefix+':LifetimeBPM-Mon',
            factor=3600)

        self.lifetime_dcct_pv.new_value_signal[float].connect(
            self._update_graph)
        self.lifetime_bpm_pv.new_value_signal[float].connect(
            self._update_graph)

        self._flag_need_dcctx = True
        self._flag_need_dccty = True
        self._flag_need_bpmx = True
        self._flag_need_bpmy = True
        self.dcct_wavx = _np.array([])
        self.dcct_wavy = _np.array([])
        self.bpm_wavx = _np.array([])
        self.bpm_wavy = _np.array([])
        self.dcct_buff_y_pv = SiriusConnectionSignal(
            self.device_prefix+':BufferValue-Mon')
        self.dcct_buff_x_pv = SiriusConnectionSignal(
            self.device_prefix+':BufferTimestamp-Mon')
        self.bpm_buff_y_pv = SiriusConnectionSignal(
            self.device_prefix+':BufferValueBPM-Mon')
        self.bpm_buff_x_pv = SiriusConnectionSignal(
            self.device_prefix+':BufferTimestampBPM-Mon')
        self.dcct_buff_y_pv.new_value_signal[_np.ndarray].connect(
            self._update_waveforms)
        self.dcct_buff_x_pv.new_value_signal[_np.ndarray].connect(
            self._update_waveforms)
        self.bpm_buff_y_pv.new_value_signal[_np.ndarray].connect(
            self._update_waveforms)
        self.bpm_buff_x_pv.new_value_signal[_np.ndarray].connect(
            self._update_waveforms)

        self.graph.addYChannel(
            y_channel='FAKE:DCCTBuffer', axis='left', name='DCCTBuffer',
            color='blue', lineStyle=Qt.NoPen, symbolSize=10, symbol='o')
        self._curve_dcct_buff = self.graph.curveAtIndex(4)
        self.graph.addYChannel(
            y_channel='FAKE:BPMBuffer', axis='left', name='BPMBuffer',
            color='blue', lineStyle=Qt.NoPen, symbolSize=10, symbol='o')
        self._curve_bpm_buff = self.graph.curveAtIndex(5)

        self._curve_bpmsum.setVisible(False)
        self._curve_lifetimebpm.setVisible(False)
        self._curve_bpm_buff.setVisible(False)

        lay = QGridLayout()
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum), 0, 0)
        lay.addWidget(self._ld_current, 0, 1)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum), 0, 2)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum), 0, 3)
        lay.addWidget(self._ld_lifetime, 0, 4)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum), 0, 5)
        lay.addWidget(self._lb_current, 1, 1)
        lay.addWidget(self._lb_lifetime, 1, 4)
        lay.addWidget(self.graph, 2, 0, 1, 6)
        return lay

    def _setupCurrentSettingsWidget(self):
        self._ld_storedebeam = QLabel('Stored EBeam?', self)
        self._ld_storedebeam.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._led_storedebeam = SiriusLedState(
            self, self.device_prefix+':StoredEBeam-Mon')

        self._ld_dcctfault = QLabel('DCCT Fault Check:', self)
        self._ld_dcctfault.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._bt_dcctfault = PyDMStateButton(
            self, self.device_prefix+':DCCTFltCheck-Sel')
        self._bt_dcctfault.shape = PyDMStateButton.Rounded
        self._led_dcctfault = SiriusLedState(
            self, self.device_prefix+':DCCTFltCheck-Sts')

        self._ld_seldcct = QLabel('Select DCCT:', self)
        self._ld_seldcct.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._cb_seldcct = PyDMEnumComboBox(
            self, self.device_prefix+':DCCT-Sel')
        self._lb_seldcct = PyDMLabel(
            self, self.device_prefix+':DCCT-Sts')
        self._lb_seldcct.setAlignment(Qt.AlignCenter)
        self._lb_seldcct.precision = 0

        self._led_dcct13c4 = SiriusLedAlert(
            self, self.prefix+'SI-13C4:DI-DCCT:ReliableMeas-Mon')
        self._lb_dcct13c4 = QLabel('DCCT 13C4', self)
        self._lb_dcct13c4.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._pb_13c4_detail = QPushButton(self)
        self._pb_13c4_detail.setObjectName('DCCT13C4_dtl')
        self._pb_13c4_detail.setStyleSheet(
            "#DCCT13C4_dtl{min-width:25px; max-width:25px; icon-size:20px;}")
        self._pb_13c4_detail.setIcon(qta.icon('fa5s.ellipsis-h'))
        connect_window(
            self._pb_13c4_detail, DCCTMain, self,
            prefix=self.prefix, device='SI-13C4:DI-DCCT')
        hlay_dcct13c4 = QHBoxLayout()
        hlay_dcct13c4.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum))
        hlay_dcct13c4.addWidget(self._led_dcct13c4)
        hlay_dcct13c4.addWidget(self._lb_dcct13c4)
        hlay_dcct13c4.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum))
        hlay_dcct13c4.addWidget(self._pb_13c4_detail)
        hlay_dcct13c4.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum))

        self._led_dcct14c4 = SiriusLedAlert(
            self, self.prefix+'SI-14C4:DI-DCCT:ReliableMeas-Mon')
        self._lb_dcct14c4 = QLabel('DCCT 14C4', self)
        self._lb_dcct14c4.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._pb_14c4_detail = QPushButton(self)
        self._pb_14c4_detail.setObjectName('DCCT13C4_dtl')
        self._pb_14c4_detail.setStyleSheet(
            "#DCCT13C4_dtl{min-width:25px; max-width:25px; icon-size:20px;}")
        self._pb_14c4_detail.setIcon(qta.icon('fa5s.ellipsis-h'))
        connect_window(
            self._pb_14c4_detail, DCCTMain, self,
            prefix=self.prefix, device='SI-14C4:DI-DCCT')
        hlay_dcct14c4 = QHBoxLayout()
        hlay_dcct14c4.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum))
        hlay_dcct14c4.addWidget(self._led_dcct14c4)
        hlay_dcct14c4.addWidget(self._lb_dcct14c4)
        hlay_dcct14c4.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum))
        hlay_dcct14c4.addWidget(self._pb_14c4_detail)
        hlay_dcct14c4.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum))

        gbox = QGroupBox('Current Settings and Status', self)
        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_storedebeam, 0, 0)
        lay.addWidget(self._led_storedebeam, 0, 1)
        lay.addWidget(self._ld_dcctfault, 1, 0)
        lay.addWidget(self._bt_dcctfault, 1, 1)
        lay.addWidget(self._led_dcctfault, 1, 2)
        lay.addWidget(self._ld_seldcct, 2, 0)
        lay.addWidget(self._cb_seldcct, 2, 1)
        lay.addWidget(self._lb_seldcct, 2, 2)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum), 3, 0)
        lay.addLayout(hlay_dcct13c4, 4, 0, 1, 3)
        lay.addLayout(hlay_dcct14c4, 5, 0, 1, 3)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 1)
        lay.setColumnStretch(2, 1)
        return gbox

    def _setupLifetimeSettigsWidget(self):
        self._ld_calcmode = QLabel(
            'Calc Mode:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._cb_calcmode = PyDMEnumComboBox(
            self, self.device_prefix+':LtFitMode-Sel')
        self._lb_calcmode = SiriusLabel(
            self, self.device_prefix+':LtFitMode-Sts')
        self._lb_calcmode.setAlignment(Qt.AlignCenter)

        self._ld_curroffset = QLabel(
            'Current\nOffset [mA]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._sb_curroffset = SiriusSpinbox(
            self, self.device_prefix+':CurrOffset-SP')
        self._sb_curroffset.showStepExponent = False
        self._lb_curroffset = PyDMLabel(
            self, self.device_prefix+':CurrOffset-RB')
        self._lb_curroffset.setAlignment(Qt.AlignCenter)

        self._ld_buffer = QLabel(
            '<h4>Buffer</h4>', self, alignment=Qt.AlignCenter)

        self._pb_plussett = QPushButton('+', self)
        self._pb_plussett.setStyleSheet('max-height:0.9em; max-width:0.9em;')
        self._pb_plussett.released.connect(
            self._handle_intvl_sett_visibility)
        self._ld_maxintvl = QLabel(
            'Max. Sampling\nInterval [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        hlay_maxintvl = QHBoxLayout()
        hlay_maxintvl.addWidget(self._pb_plussett)
        hlay_maxintvl.addWidget(self._ld_maxintvl)
        self._sb_maxintvl = PyDMSpinbox(
            self, self.device_prefix+':MaxSplIntvl-SP')
        self._sb_maxintvl.precisionFromPV = True
        self._sb_maxintvl.showStepExponent = False
        self._lb_maxintvl = PyDMLabel(
            self, self.device_prefix+':MaxSplIntvl-RB')
        self._lb_maxintvl.setAlignment(Qt.AlignCenter)
        self._lb_maxintvl.precisionFromPV = True

        self._ld_firstsmpl = QLabel(
            'First Time [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._ld_firstsmpl.setVisible(False)
        self._le_firstsmpl = PyDMLineEdit(
            self, self.device_prefix+':FrstSplTime-SP')
        self._le_firstsmpl.setVisible(False)
        self._lb_firstsmpl = PyDMLabel(
            self, self.device_prefix+':FrstSplTime-RB')
        self._lb_firstsmpl.setVisible(False)
        self._pb_firstnow = QPushButton(
            qta.icon('mdi.clock-end'), '', self)
        self._pb_firstnow.setObjectName('firstnow')
        self._pb_firstnow.setStyleSheet(
            '#firstnow{min-width:25px; max-width:25px; icon-size:20px;}')
        self._pb_firstnow.released.connect(self._update_first_time)
        self._pb_firstnow.setVisible(False)
        hbox_sp_first = QHBoxLayout()
        hbox_sp_first.addWidget(self._le_firstsmpl)
        hbox_sp_first.addWidget(self._pb_firstnow)

        self._ld_lastsmpl = QLabel(
            'Last Time [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._ld_lastsmpl.setVisible(False)
        self._le_lastsmpl = PyDMLineEdit(
            self, self.device_prefix+':LastSplTime-SP')
        self._le_lastsmpl.setVisible(False)
        self._lb_lastsmpl = PyDMLabel(
            self, self.device_prefix+':LastSplTime-RB')
        self._lb_lastsmpl.setVisible(False)
        self._pb_lastnow = QPushButton(
            qta.icon('mdi.clock-end'), '', self)
        self._pb_lastnow.setObjectName('lastnow')
        self._pb_lastnow.setStyleSheet(
            '#lastnow{min-width:25px; max-width:25px; icon-size:20px;}')
        self._pb_lastnow.released.connect(self._update_last_time)
        self._pb_lastnow.setVisible(False)
        hbox_sp_last = QHBoxLayout()
        hbox_sp_last.addWidget(self._le_lastsmpl)
        hbox_sp_last.addWidget(self._pb_lastnow)

        self._ld_smplintvl = QLabel(
            'Samples\nInterval [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._lb_smplintvl = PyDMLabel(
            self, self.device_prefix+':SplIntvl-Mon')

        self._ld_intvlbtwspl = QLabel(
            'Interval Between\nSamples [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._sb_intvlbtwspl = PyDMSpinbox(
            self, self.device_prefix+':MinIntvlBtwSpl-SP')
        self._sb_intvlbtwspl.precisionFromPV = True
        self._sb_intvlbtwspl.showStepExponent = False
        self._lb_intvlbtwspl = PyDMLabel(
            self, self.device_prefix+':MinIntvlBtwSpl-RB')
        self._lb_intvlbtwspl.setAlignment(Qt.AlignCenter)
        self._lb_intvlbtwspl.precisionFromPV = True

        self._ld_bufautoreset = QLabel(
            'Auto Reset:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._cb_bufautoreset = PyDMEnumComboBox(
            self, self.device_prefix+':BuffAutoRst-Sel')
        self._lb_bufautoreset = PyDMLabel(
            self, self.device_prefix+':BuffAutoRst-Sts')

        self._ld_bufdcurr = QLabel(
            'Auto Reset Delta\nCurrent [mA]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._sb_bufdcurr = PyDMSpinbox(
            self, self.device_prefix+':BuffAutoRstDCurr-SP')
        self._sb_bufdcurr.showStepExponent = False
        self._lb_bufdcurr = PyDMLabel(
            self, self.device_prefix+':BuffAutoRstDCurr-RB')

        self._ld_bufsize = QLabel(
            'Size:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._lb_bufsize = PyDMLabel(
            self, self.device_prefix+':BuffSize-Mon')
        self._lb_bufsize.setAlignment(Qt.AlignCenter)
        self._pb_bufreset = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.delete-empty'), pressValue=1,
            init_channel=self.device_prefix+':BuffRst-Cmd')
        self._pb_bufreset.setObjectName('reset')
        self._pb_bufreset.setStyleSheet(
            "#reset{min-width:25px; max-width:25px; icon-size:20px;}")
        self._ld_sep = QLabel('/', self)
        self._lb_bufsizetot = PyDMLabel(
            self, self.device_prefix+':BuffSizeTot-Mon')
        self._lb_bufsizetot.setStyleSheet(
            "min-width:5em; max-width:5em;")
        self._lb_bufsizetot.setAlignment(Qt.AlignCenter)
        self._lb_bufsizetot.precision = 0
        hlay_bufsize = QHBoxLayout()
        hlay_bufsize.addWidget(self._lb_bufsize)
        hlay_bufsize.addWidget(self._pb_bufreset)
        hlay_bufsize.addWidget(self._ld_sep)
        hlay_bufsize.addWidget(self._lb_bufsizetot)

        gbox = QGroupBox('Lifetime Settings', self)
        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_calcmode, 0, 0)
        lay.addWidget(self._cb_calcmode, 0, 1)
        lay.addWidget(self._lb_calcmode, 0, 2)
        lay.addWidget(self._ld_curroffset, 1, 0)
        lay.addWidget(self._sb_curroffset, 1, 1)
        lay.addWidget(self._lb_curroffset, 1, 2)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum), 2, 1)
        lay.addWidget(self._ld_buffer, 3, 0, 1, 3)
        lay.addLayout(hlay_maxintvl, 4, 0)
        lay.addWidget(self._sb_maxintvl, 4, 1)
        lay.addWidget(self._lb_maxintvl, 4, 2)
        lay.addWidget(self._ld_firstsmpl, 5, 0)
        lay.addLayout(hbox_sp_first, 5, 1, 1, 2)
        lay.addWidget(self._lb_firstsmpl, 6, 1, 1, 2)
        lay.addWidget(self._ld_lastsmpl, 7, 0)
        lay.addLayout(hbox_sp_last, 7, 1, 1, 2)
        lay.addWidget(self._lb_lastsmpl, 8, 1, 1, 2)
        lay.addWidget(self._ld_smplintvl, 9, 0)
        lay.addWidget(self._lb_smplintvl, 9, 1)
        lay.addWidget(self._ld_intvlbtwspl, 10, 0)
        lay.addWidget(self._sb_intvlbtwspl, 10, 1)
        lay.addWidget(self._lb_intvlbtwspl, 10, 2)
        lay.addItem(
            QSpacerItem(20, 5, QSzPlcy.Minimum, QSzPlcy.Fixed), 11, 1)
        lay.addWidget(self._ld_bufautoreset, 12, 0)
        lay.addWidget(self._cb_bufautoreset, 12, 1)
        lay.addWidget(self._lb_bufautoreset, 12, 2)
        lay.addWidget(self._ld_bufdcurr, 13, 0)
        lay.addWidget(self._sb_bufdcurr, 13, 1)
        lay.addWidget(self._lb_bufdcurr, 13, 2)
        lay.addItem(
            QSpacerItem(20, 5, QSzPlcy.Minimum, QSzPlcy.Fixed), 14, 1)
        lay.addWidget(self._ld_bufsize, 15, 0)
        lay.addLayout(hlay_bufsize, 15, 1, 1, 2)
        return gbox

    def _setupGraphSettingsWidget(self):
        self._ld_ltfrom = QLabel(
            'Show lifetime from:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._cb_ltfrom = QComboBox()
        self._cb_ltfrom.addItem('DCCT')
        self._cb_ltfrom.addItem('BPM')
        self._cb_ltfrom.currentTextChanged.connect(
            self._handle_lifetime_type_sel)

        self._lb_timespan = QLabel(
            'Time Span [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._sb_timespan = QSpinBox()
        self._sb_timespan.setMinimum(1)
        self._sb_timespan.setMaximum(1000000)
        self._sb_timespan.setValue(2000)
        self._sb_timespan.valueChanged.connect(self._set_graph_timespan)

        self._ld_showsmpl = QLabel(
            'Show samples: ', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._cb_showsmpl = QCheckBox(self)
        self._cb_showsmpl.setChecked(True)
        self._cb_showsmpl.stateChanged.connect(self._handle_samples_visibility)

        gbox = QGroupBox('Graphs Settings', self)
        lay = QGridLayout(gbox)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum), 0, 0)
        lay.addWidget(self._ld_ltfrom, 0, 1)
        lay.addWidget(self._cb_ltfrom, 0, 2)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Minimum), 0, 3)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Minimum, QSzPlcy.Expanding),
            1, 1, 1, 2)
        lay.addWidget(self._lb_timespan, 2, 1)
        lay.addWidget(self._sb_timespan, 2, 2)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Minimum, QSzPlcy.Expanding),
            3, 1, 1, 2)
        lay.addWidget(self._ld_showsmpl, 4, 1)
        lay.addWidget(self._cb_showsmpl, 4, 2)
        return gbox

    # ---------- auxiliar methods ----------

    def _format_lifetime_label(self, value):
        """Format lifetime label."""
        if self._lb_lifetime.channel != self.sender().address:
            return
        lt = 0 if _np.isnan(value) else value
        H = int(lt // 3600)
        m = int((lt % 3600) // 60)
        s = int((lt % 3600) % 60)
        lt_str = '{:d}:{:02d}:{:02d}'.format(H, m, s)
        self._lb_lifetime.setText(lt_str)

    @Slot(str)
    def _handle_lifetime_type_sel(self, text):
        """Handle lifetime type selection."""
        cond = bool(text == 'DCCT')
        self._curve_current.setVisible(cond)
        self._curve_lifetimedcct.setVisible(cond)
        self._curve_dcct_buff.setVisible(cond)
        self._curve_bpmsum.setVisible(not cond)
        self._curve_lifetimebpm.setVisible(not cond)
        self._curve_bpm_buff.setVisible(not cond)
        if not cond:
            self.graph.plotItem.getAxis('left').setLabel(
                '01M1 BPM Sum', color='blue')
            self._lb_lifetime.channel = \
                self.device_prefix+':LifetimeBPM-Mon'
            self._lb_bufsizetot.channel = \
                self.device_prefix+':BuffSizeTotBPM-Mon'
            self._lb_bufsize.channel = \
                self.device_prefix+':BuffSizeBPM-Mon'
            self._lb_firstsmpl.channel = \
                self.device_prefix+':FrstSplTimeBPM-RB'
            self._lb_lastsmpl.channel = \
                self.device_prefix+':LastSplTimeBPM-RB'
            self._lb_smplintvl.channel = \
                self.device_prefix+':SplIntvlBPM-Mon'
        else:
            self.graph.plotItem.getAxis('left').setLabel(
                'Current [mA]', color='blue')
            self._lb_lifetime.channel = \
                self.device_prefix+':Lifetime-Mon'
            self._lb_bufsizetot.channel = \
                self.device_prefix+':BuffSizeTot-Mon'
            self._lb_bufsize.channel = \
                self.device_prefix+':BuffSize-Mon'
            self._lb_firstsmpl.channel = \
                self.device_prefix+':FrstSplTime-RB'
            self._lb_lastsmpl.channel = \
                self.device_prefix+':LastSplTime-RB'
            self._lb_smplintvl.channel = \
                self.device_prefix+':SplIntvl-Mon'

    def _handle_intvl_sett_visibility(self):
        """Handle sampling interval settings."""
        text = self.sender().text()
        visi = text == '+'
        self._ld_firstsmpl.setVisible(visi)
        self._le_firstsmpl.setVisible(visi)
        self._lb_firstsmpl.setVisible(visi)
        self._pb_firstnow.setVisible(visi)
        self._ld_lastsmpl.setVisible(visi)
        self._le_lastsmpl.setVisible(visi)
        self._lb_lastsmpl.setVisible(visi)
        self._pb_lastnow.setVisible(visi)
        self.sender().setText('+' if text == '-' else '-')

    @Slot(int)
    def _handle_samples_visibility(self, state):
        """Handle samples visibility."""
        self._curve_dcct_buff.setVisible(state)
        self._curve_bpm_buff.setVisible(state)

    @Slot(int)
    def _set_graph_timespan(self, value):
        """Set graph time span."""
        self.graph.setTimeSpan(float(value))

    def _update_first_time(self):
        """Update first sample time to current timestamp."""
        now = _time.time()
        self._le_firstsmpl.send_value_signal[float].emit(now)

    def _update_last_time(self):
        """Update last sample time to current timestamp."""
        now = _time.time()
        self._le_lastsmpl.send_value_signal[float].emit(now)

    @Slot(float)
    def _update_graph(self, value):
        """Receive new lifetime values and update curves in hours."""
        if 'BPM' in self.sender().address:
            self._curve_lifetimebpm.receiveNewValue(value/3600)
        else:
            self._curve_lifetimedcct.receiveNewValue(value/3600)

    @Slot(_np.ndarray)
    def _update_waveforms(self, value):
        """Update samples waveforms."""
        address = self.sender().address
        if 'BPM' in address:
            if 'Timestamp' in address:
                self.bpm_wavx = value + _time.time()
                self._flag_need_bpmx = False
            elif 'Value' in address:
                self.bpm_wavy = value
                self._flag_need_bpmy = False
            if not self._flag_need_bpmy and not self._flag_need_bpmx:
                if len(self.bpm_wavx) != len(self.bpm_wavy):
                    return
                self._fill_curve_buffer(
                    self._curve_bpm_buff, self.bpm_wavx, self.bpm_wavy)
                self._flag_need_bpmx = True
                self._flag_need_bpmy = True
        else:
            if 'Timestamp' in address:
                self.dcct_wavx = value + _time.time()
                self._flag_need_dcctx = False
            elif 'Value' in address:
                self.dcct_wavy = value
                self._flag_need_dccty = False
            if not self._flag_need_dccty and not self._flag_need_dcctx:
                if len(self.dcct_wavx) != len(self.dcct_wavy):
                    return
                self._fill_curve_buffer(
                    self._curve_dcct_buff, self.dcct_wavx, self.dcct_wavy)
                self._flag_need_dcctx = True
                self._flag_need_dccty = True

    # ---------- handle archiver data ----------

    def _get_value_from_arch(self, pvname):
        """Get values from archiver."""
        carch = ClientArchiver()
        t1 = _datetime.now()
        t0 = t1 - _timedelta(seconds=2000)
        t0_str = t0.isoformat() + '-03:00'
        t1_str = t1.isoformat() + '-03:00'
        data = carch.getData(pvname, t0_str, t1_str)
        if not data:
            return
        timestamp, value, _, _ = data
        # ignore first sample
        if len(value) > 1:
            timestamp[0] = t0.timestamp()
            value[0] = value[1]
        return timestamp, value

    def _fill_curve_with_archdata(self, curve, pvname, factor=None):
        """Fill curve with archiver data."""
        data = self._get_value_from_arch(pvname)
        if not data:
            return
        datax, datay = data
        datax = _np.array(datax)
        datay = _np.array(datay)
        if 'Lifetime' in pvname:
            datay = datay/60/60
        self._fill_curve_buffer(curve, datax, datay)

    def _fill_curve_buffer(self, curve, datax, datay, factor=None):
        """Fill curve buffer."""
        nrpts = len(datax)
        if not nrpts:
            return
        buff = _np.zeros((2, self.graph.bufferSize), order='f', dtype=float)
        if nrpts > self.graph.bufferSize:
            smpls2discard = nrpts - self.graph.bufferSize
            datax = datax[smpls2discard:]
            datay = datay[smpls2discard:]
            nrpts = len(datax)
        firstsmpl2fill = self.graph.bufferSize - nrpts
        buff[0, firstsmpl2fill:] = datax
        buff[1, firstsmpl2fill:] = datay
        if factor:
            buff[1, :] /= factor
        curve.data_buffer = buff
        curve.points_accumulated = nrpts
        curve._min_y_value = min(datay)
        curve._max_y_value = max(datay)
        curve.latest_value = datay[-1]
