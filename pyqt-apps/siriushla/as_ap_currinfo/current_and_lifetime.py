"""Current and Lifetime Window."""

import time as _time
import numpy as _np

from qtpy.QtCore import Slot, Qt
from qtpy.QtWidgets import QLabel, QGroupBox, QWidget, QSpacerItem,\
    QSizePolicy as QSzPlcy, QComboBox, QPushButton, QCheckBox,\
    QGridLayout, QHBoxLayout, QVBoxLayout
import qtawesome as qta
from pydm.widgets import PyDMEnumComboBox, PyDMLabel, PyDMLineEdit,\
    PyDMPushButton, PyDMSpinbox

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.clientarch.time import Time
from siriushla.util import connect_window
from siriushla.widgets import SiriusLabel, SiriusLedAlert, SiriusLedState,\
    SiriusSpinbox, PyDMStateButton, SiriusMainWindow, SiriusConnectionSignal,\
    SiriusTimePlot, QSpinBoxPlus
from siriushla.as_di_dccts import DCCTMain, EffMonitor


class CurrLTWindow(SiriusMainWindow):
    """Current and Lifetime Window."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """Initialize some widgets."""
        super(CurrLTWindow, self).__init__(parent)
        self.prefix = prefix
        self.device = _PVName('SI-Glob:AP-CurrInfo')
        self.devname = self.device.substitute(prefix=self.prefix)
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

        self.settings = QWidget()
        vlay_sett = QVBoxLayout(self.settings)
        vlay_sett.setContentsMargins(0, 0, 0, 0)
        vlay_sett.addWidget(self._setupCurrentSettingsWidget())
        vlay_sett.addWidget(self._setupLifetimeSettigsWidget())
        vlay_sett.addWidget(self._setupGraphSettingsWidget())

        self.pb_showsett = QPushButton('<', self)
        self.pb_showsett.setObjectName('showsett')
        self.pb_showsett.setToolTip('Hide settings')
        self.pb_showsett.setStyleSheet(
            '#showsett{min-width:0.7em;max-width:0.7em;}')
        self.pb_showsett.released.connect(self._handle_settings_vis)

        self.pb_showeff = QPushButton('v', self)
        self.pb_showeff.setObjectName('showeff')
        self.pb_showeff.setToolTip('Show efficiency graph')
        self.pb_showeff.setStyleSheet(
            '#showeff{min-width:0.7em;max-width:0.7em;}')
        self.pb_showeff.released.connect(self._handle_efficiency_vis)

        hbox_visi = QHBoxLayout()
        hbox_visi.addStretch()
        hbox_visi.addWidget(self.pb_showsett)
        hbox_visi.addWidget(self.pb_showeff)

        self.eff_graph = EffMonitor(self, self.prefix, self.device.sec)
        self.eff_graph.setVisible(False)

        cw = QWidget()
        self.setCentralWidget(cw)
        lay = QGridLayout(cw)
        lay.addWidget(self.label_title, 0, 0, 1, 2)
        lay.addLayout(self._setupGraphPanelLayout(), 1, 0)
        lay.addWidget(self.settings, 1, 1)
        lay.addLayout(hbox_visi, 2, 0, 1, 2, alignment=Qt.AlignRight)
        lay.addWidget(self.eff_graph, 3, 0, 1, 2)
        lay.setColumnStretch(0, 6)
        lay.setColumnStretch(1, 1)

    def _setupGraphPanelLayout(self):
        # Main Panel
        # # Labels
        self._ld_current = QLabel('Current', self, alignment=Qt.AlignCenter)
        self._ld_current.setStyleSheet("font-weight:bold; max-height1.5em;")
        self._lb_current = PyDMLabel(
            self, self.devname.substitute(propty='Current-Mon'))
        self._lb_current.setStyleSheet("font-size:40px;")
        self._lb_current.precision = 0
        self._lb_current.showUnits = True

        self._ld_lifetime = QLabel('Lifetime', self)
        self._ld_lifetime.setStyleSheet("font-weight:bold; max-height1.5em;")
        self._ld_lifetime.setAlignment(Qt.AlignCenter)
        self._lb_lifetime = QLabel('0:00:00', self)
        self._lb_lifetime.channel = self.devname.substitute(
            propty='Lifetime-Mon')
        self._lb_lifetime.setStyleSheet("font-size:40px;")
        self.lifetime_dcct_pv = SiriusConnectionSignal(
            self.devname.substitute(propty='Lifetime-Mon'))
        self.lifetime_dcct_pv.new_value_signal[float].connect(
            self._format_lifetime_label)
        self.lifetime_bpm_pv = SiriusConnectionSignal(
            self.devname.substitute(propty='LifetimeBPM-Mon'))
        self.lifetime_bpm_pv.new_value_signal[float].connect(
            self._format_lifetime_label)

        # # Graph
        self.graph = SiriusTimePlot(self, background='w')
        self.graph.plotItem.getAxis('left').setLabel(
            'Current [mA]', color='blue')
        self.graph.plotItem.getAxis('right').setLabel(
            'Lifetime [h]', color='red')
        self.graph.showLegend = False
        self.graph.showXGrid = True
        self.graph.showYGrid = True
        self.graph.autoRangeY = True
        self.graph.setObjectName('graph')
        self.graph.setStyleSheet('#graph{min-width:40em;min-height:32em;}')
        self.graph.bufferSize = 60*60*10
        self._set_graph_timespan(30*60)

        t_end = Time.now()
        t_init = t_end - 30*60
        t_end_iso = t_end.get_iso8601()
        t_init_iso = t_init.get_iso8601()

        pvname = self.devname.substitute(propty='Current-Mon')
        self.graph.addYChannel(
            y_channel=pvname, axis='left', name='Current',
            color='blue', lineWidth=1)
        self._curve_current = self.graph.curveAtIndex(0)
        self.graph.fill_curve_with_archdata(
            self._curve_current, pvname,
            t_init=t_init_iso, t_end=t_end_iso)

        pvname = _PVName(
            'SI-01M1:DI-BPM:Sum-Mon').substitute(prefix=self.prefix)
        self.graph.addYChannel(
            y_channel=pvname,
            axis='left', name='Current', color='blue', lineWidth=1)
        self._curve_bpmsum = self.graph.curveAtIndex(1)
        self.graph.fill_curve_with_archdata(
            self._curve_bpmsum,  pvname,
            t_init=t_init_iso, t_end=t_end_iso)

        self.graph.addYChannel(
            y_channel='FAKE:Lifetime', axis='right', name='Lifetime',
            color='red', lineWidth=1)
        self._curve_lifetimedcct = self.graph.curveAtIndex(2)
        self.graph.fill_curve_with_archdata(
            self._curve_lifetimedcct,
            self.devname.substitute(propty='Lifetime-Mon'),
            t_init=t_init_iso, t_end=t_end_iso, factor=3600)

        self.graph.addYChannel(
            y_channel='FAKE:LifetimeBPM', axis='right', name='Lifetime',
            color='red', lineWidth=1)
        self._curve_lifetimebpm = self.graph.curveAtIndex(3)
        self.graph.fill_curve_with_archdata(
            self._curve_lifetimebpm,
            self.devname.substitute(propty='LifetimeBPM-Mon'),
            t_init=t_init_iso, t_end=t_end_iso, factor=3600)

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
            self.devname.substitute(propty='BufferValue-Mon'))
        self.dcct_buff_x_pv = SiriusConnectionSignal(
            self.devname.substitute(propty='BufferTimestamp-Mon'))
        self.bpm_buff_y_pv = SiriusConnectionSignal(
            self.devname.substitute(propty='BufferValueBPM-Mon'))
        self.bpm_buff_x_pv = SiriusConnectionSignal(
            self.devname.substitute(propty='BufferTimestampBPM-Mon'))
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
            self, self.devname.substitute(propty='StoredEBeam-Mon'))

        self._ld_dcctfault = QLabel('DCCT Fault Check:', self)
        self._ld_dcctfault.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._bt_dcctfault = PyDMStateButton(
            self, self.devname.substitute(propty='DCCTFltCheck-Sel'))
        self._bt_dcctfault.shape = PyDMStateButton.Rounded
        self._led_dcctfault = SiriusLedState(
            self, self.devname.substitute(propty='DCCTFltCheck-Sts'))

        self._ld_seldcct = QLabel('Select DCCT:', self)
        self._ld_seldcct.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._cb_seldcct = PyDMEnumComboBox(
            self, self.devname.substitute(propty='DCCT-Sel'))
        self._lb_seldcct = PyDMLabel(
            self, self.devname.substitute(propty='DCCT-Sts'))
        self._lb_seldcct.setAlignment(Qt.AlignCenter)
        self._lb_seldcct.precision = 0

        self._led_dcct13c4 = SiriusLedAlert(self, _PVName(
            'SI-13C4:DI-DCCT:ReliableMeas-Mon').substitute(prefix=self.prefix))
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

        self._led_dcct14c4 = SiriusLedAlert(self, _PVName(
            'SI-14C4:DI-DCCT:ReliableMeas-Mon').substitute(prefix=self.prefix))
        self._lb_dcct14c4 = QLabel('DCCT 14C4', self)
        self._lb_dcct14c4.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._pb_14c4_detail = QPushButton(self)
        self._pb_14c4_detail.setObjectName('DCCT14C4_dtl')
        self._pb_14c4_detail.setStyleSheet(
            "#DCCT14C4_dtl{min-width:25px; max-width:25px; icon-size:20px;}")
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
            self, self.devname.substitute(propty='LtFitMode-Sel'))
        self._lb_calcmode = SiriusLabel(
            self, self.devname.substitute(propty='LtFitMode-Sts'))
        self._lb_calcmode.setAlignment(Qt.AlignCenter)

        self._ld_curroffset = QLabel(
            'Current\nOffset [mA]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._sb_curroffset = SiriusSpinbox(
            self, self.devname.substitute(propty='CurrOffset-SP'))
        self._sb_curroffset.showStepExponent = False
        self._lb_curroffset = PyDMLabel(
            self, self.devname.substitute(propty='CurrOffset-RB'))
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
        self._ld_maxintvl.setToolTip(
            "Timestamp settings use 2 parameters to define the\n"
            "timestamp interval.\n\n"
            "If 'Max. Sampling Interval' == -1:\n"
            "    use 'Last Time' and 'First Time' parameters.\n"
            "Else:\n"
            "    use 'Max. Sampling Interval' and last timestamp set.\n\n"
            "Default: use 'Max. Sampling Interval' and 'Last Time'.")
        hlay_maxintvl = QHBoxLayout()
        hlay_maxintvl.addWidget(self._pb_plussett)
        hlay_maxintvl.addWidget(self._ld_maxintvl)
        self._sb_maxintvl = PyDMSpinbox(
            self, self.devname.substitute(propty='MaxSplIntvl-SP'))
        self._sb_maxintvl.precisionFromPV = True
        self._sb_maxintvl.showStepExponent = False
        self._lb_maxintvl = PyDMLabel(
            self, self.devname.substitute(propty='MaxSplIntvl-RB'))
        self._lb_maxintvl.setAlignment(Qt.AlignCenter)
        self._lb_maxintvl.precisionFromPV = True

        self._ld_firstsmpl = QLabel(
            'First Time [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._ld_firstsmpl.setVisible(False)
        self._le_firstsmpl = PyDMLineEdit(
            self, self.devname.substitute(propty='FrstSplTime-SP'))
        self._le_firstsmpl.setVisible(False)
        self._lb_firstsmpl_dcct = PyDMLabel(
            self, self.devname.substitute(propty='FrstSplTime-RB'))
        self._lb_firstsmpl_dcct.setVisible(False)
        self._lb_firstsmpl_bpm = PyDMLabel(
            self, self.devname.substitute(propty='FrstSplTimeBPM-RB'))
        self._lb_firstsmpl_bpm.setVisible(False)
        self._pb_firstnow = QPushButton(
            qta.icon('mdi.clock-end'), '', self)
        self._pb_firstnow.setObjectName('firstnow')
        self._pb_firstnow.setStyleSheet(
            '#firstnow{min-width:25px; max-width:25px; icon-size:20px;}')
        self._pb_firstnow.setToolTip('Click to set current timestamp')
        self._pb_firstnow.released.connect(self._update_first_time)
        self._pb_firstnow.setVisible(False)
        hbox_sp_first = QHBoxLayout()
        hbox_sp_first.addWidget(self._le_firstsmpl)
        hbox_sp_first.addWidget(self._pb_firstnow)

        self._ld_lastsmpl = QLabel(
            'Last Time [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._ld_lastsmpl.setToolTip(
            "If 'Last Time' == -1, use current timestamp.")
        self._ld_lastsmpl.setVisible(False)
        self._le_lastsmpl = PyDMLineEdit(
            self, self.devname.substitute(propty='LastSplTime-SP'))
        self._le_lastsmpl.setVisible(False)
        self._lb_lastsmpl_dcct = PyDMLabel(
            self, self.devname.substitute(propty='LastSplTime-RB'))
        self._lb_lastsmpl_dcct.setVisible(False)
        self._lb_lastsmpl_bpm = PyDMLabel(
            self, self.devname.substitute(propty='LastSplTimeBPM-RB'))
        self._lb_lastsmpl_bpm.setVisible(False)
        self._pb_lastnow = QPushButton(
            qta.icon('mdi.clock-end'), '', self)
        self._pb_lastnow.setObjectName('lastnow')
        self._pb_lastnow.setStyleSheet(
            '#lastnow{min-width:25px; max-width:25px; icon-size:20px;}')
        self._pb_lastnow.setToolTip('Click to set current timestamp')
        self._pb_lastnow.released.connect(self._update_last_time)
        self._pb_lastnow.setVisible(False)
        hbox_sp_last = QHBoxLayout()
        hbox_sp_last.addWidget(self._le_lastsmpl)
        hbox_sp_last.addWidget(self._pb_lastnow)

        self._ld_smplintvl = QLabel(
            'Samples\nInterval [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._lb_smplintvl_dcct = PyDMLabel(
            self, self.devname.substitute(propty='SplIntvl-Mon'))
        self._lb_smplintvl_bpm = PyDMLabel(
            self, self.devname.substitute(propty='SplIntvlBPM-Mon'))
        self._lb_smplintvl_bpm.setVisible(False)

        self._ld_intvlbtwspl = QLabel(
            'Interval Between\nSamples [s]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._sb_intvlbtwspl = PyDMSpinbox(
            self, self.devname.substitute(propty='MinIntvlBtwSpl-SP'))
        self._sb_intvlbtwspl.precisionFromPV = True
        self._sb_intvlbtwspl.showStepExponent = False
        self._lb_intvlbtwspl = PyDMLabel(
            self, self.devname.substitute(propty='MinIntvlBtwSpl-RB'))
        self._lb_intvlbtwspl.setAlignment(Qt.AlignCenter)
        self._lb_intvlbtwspl.precisionFromPV = True

        self._ld_bufautoreset = QLabel(
            'Auto Reset:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._cb_bufautoreset = PyDMEnumComboBox(
            self, self.devname.substitute(propty='BuffAutoRst-Sel'))
        self._lb_bufautoreset = PyDMLabel(
            self, self.devname.substitute(propty='BuffAutoRst-Sts'))

        self._ld_bufdcurr = QLabel(
            'Auto Reset Delta\nCurrent [mA]:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._sb_bufdcurr = PyDMSpinbox(
            self, self.devname.substitute(propty='BuffAutoRstDCurr-SP'))
        self._sb_bufdcurr.showStepExponent = False
        self._lb_bufdcurr = PyDMLabel(
            self, self.devname.substitute(propty='BuffAutoRstDCurr-RB'))

        self._ld_bufsize = QLabel(
            'Size:', self,
            alignment=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._lb_bufsize_dcct = PyDMLabel(
            self, self.devname.substitute(propty='BuffSize-Mon'))
        self._lb_bufsize_dcct.setAlignment(Qt.AlignCenter)
        self._lb_bufsize_bpm = PyDMLabel(
            self, self.devname.substitute(propty='BuffSizeBPM-Mon'))
        self._lb_bufsize_bpm.setAlignment(Qt.AlignCenter)
        self._lb_bufsize_bpm.setVisible(False)
        self._pb_bufreset = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.delete-empty'), pressValue=1,
            init_channel=self.devname.substitute(propty='BuffRst-Cmd'))
        self._pb_bufreset.setObjectName('reset')
        self._pb_bufreset.setStyleSheet(
            "#reset{min-width:25px; max-width:25px; icon-size:20px;}")
        self._ld_sep = QLabel('/', self)
        self._lb_bufsizetot_dcct = PyDMLabel(
            self, self.devname.substitute(propty='BuffSizeTot-Mon'))
        self._lb_bufsizetot_dcct.setStyleSheet(
            "min-width:5em; max-width:5em;")
        self._lb_bufsizetot_dcct.setAlignment(Qt.AlignCenter)
        self._lb_bufsizetot_dcct.precision = 0
        self._lb_bufsizetot_bpm = PyDMLabel(
            self, self.devname.substitute(propty='BuffSizeTotBPM-Mon'))
        self._lb_bufsizetot_bpm.setStyleSheet(
            "min-width:5em; max-width:5em;")
        self._lb_bufsizetot_bpm.setAlignment(Qt.AlignCenter)
        self._lb_bufsizetot_bpm.precision = 0
        self._lb_bufsizetot_bpm.setVisible(False)
        glay_bufsize = QGridLayout()
        glay_bufsize.addWidget(self._lb_bufsize_dcct, 0, 0)
        glay_bufsize.addWidget(self._lb_bufsize_bpm, 0, 0)
        glay_bufsize.addWidget(self._pb_bufreset, 0, 1)
        glay_bufsize.addWidget(self._ld_sep, 0, 2)
        glay_bufsize.addWidget(self._lb_bufsizetot_dcct, 0, 3)
        glay_bufsize.addWidget(self._lb_bufsizetot_bpm, 0, 3)
        glay_bufsize.setColumnStretch(0, 5)
        glay_bufsize.setColumnStretch(1, 2)
        glay_bufsize.setColumnStretch(2, 1)
        glay_bufsize.setColumnStretch(3, 5)

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
        lay.addWidget(self._lb_firstsmpl_dcct, 6, 1, 1, 2)
        lay.addWidget(self._lb_firstsmpl_bpm, 6, 1, 1, 2)
        lay.addWidget(self._ld_lastsmpl, 7, 0)
        lay.addLayout(hbox_sp_last, 7, 1, 1, 2)
        lay.addWidget(self._lb_lastsmpl_dcct, 8, 1, 1, 2)
        lay.addWidget(self._lb_lastsmpl_bpm, 8, 1, 1, 2)
        lay.addWidget(self._ld_smplintvl, 9, 0)
        lay.addWidget(self._lb_smplintvl_dcct, 9, 1)
        lay.addWidget(self._lb_smplintvl_bpm, 9, 1)
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
        lay.addLayout(glay_bufsize, 15, 1, 1, 2)
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
        self._sb_timespan = QSpinBoxPlus()
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
        self._lb_bufsizetot_dcct.setVisible(cond)
        self._lb_bufsize_dcct.setVisible(cond)
        self._lb_smplintvl_dcct.setVisible(cond)

        self._curve_bpmsum.setVisible(not cond)
        self._curve_lifetimebpm.setVisible(not cond)
        self._curve_bpm_buff.setVisible(not cond)
        self._lb_bufsizetot_bpm.setVisible(not cond)
        self._lb_bufsize_bpm.setVisible(not cond)
        self._lb_smplintvl_bpm.setVisible(not cond)

        visi = self._pb_plussett.text() == '-'
        self._lb_firstsmpl_dcct.setVisible(cond and visi)
        self._lb_lastsmpl_dcct.setVisible(cond and visi)
        self._lb_firstsmpl_bpm.setVisible(not cond and visi)
        self._lb_lastsmpl_bpm.setVisible(not cond and visi)

        if not cond:
            self.graph.plotItem.getAxis('left').setLabel(
                '01M1 BPM Sum', color='blue')
            self._lb_lifetime.channel = \
                self.devname.substitute(propty='LifetimeBPM-Mon')
        else:
            self.graph.plotItem.getAxis('left').setLabel(
                'Current [mA]', color='blue')
            self._lb_lifetime.channel = \
                self.devname.substitute(propty='Lifetime-Mon')

    def _handle_intvl_sett_visibility(self):
        """Handle sampling interval settings."""
        text = self.sender().text()
        visi = text == '+'
        self._ld_firstsmpl.setVisible(visi)
        self._le_firstsmpl.setVisible(visi)
        self._pb_firstnow.setVisible(visi)
        self._ld_lastsmpl.setVisible(visi)
        self._le_lastsmpl.setVisible(visi)
        self._pb_lastnow.setVisible(visi)

        showingdcct = self._cb_ltfrom.currentText() == 'DCCT'
        self._lb_firstsmpl_dcct.setVisible(showingdcct and visi)
        self._lb_lastsmpl_dcct.setVisible(showingdcct and visi)
        self._lb_firstsmpl_bpm.setVisible(not showingdcct and visi)
        self._lb_lastsmpl_bpm.setVisible(not showingdcct and visi)

        self.sender().setText('+' if text == '-' else '-')

    @Slot(int)
    def _handle_samples_visibility(self, state):
        """Handle samples visibility."""
        showingdcct = self._cb_ltfrom.currentText() == 'DCCT'
        self._curve_dcct_buff.setVisible(showingdcct and state)
        self._curve_bpm_buff.setVisible(not showingdcct and state)

    def _handle_settings_vis(self):
        vis = self.settings.isVisible()
        text = '>' if vis else '<'
        ttip = 'Show' if vis else 'Hide'
        self.pb_showsett.setText(text)
        self.pb_showsett.setToolTip(ttip+' settings')
        self.settings.setVisible(not vis)
        self.sender().parent().adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()

    def _handle_efficiency_vis(self):
        vis = self.eff_graph.isVisible()
        text = 'v' if vis else '^'
        ttip = 'Show' if vis else 'Hide'
        self.pb_showeff.setText(text)
        self.pb_showeff.setToolTip(ttip+' efficiency graph')
        self.eff_graph.setVisible(not vis)
        self.sender().parent().adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()

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
                self.graph.fill_curve_buffer(
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
                self.graph.fill_curve_buffer(
                    self._curve_dcct_buff, self.dcct_wavx, self.dcct_wavy)
                self._flag_need_dcctx = True
                self._flag_need_dccty = True
