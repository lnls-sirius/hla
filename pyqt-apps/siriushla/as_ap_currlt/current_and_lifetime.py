#!/usr/bin/env python-sirius
"""HLA Current and Lifetime Modules."""

import os as _os
from datetime import datetime as _datetime, timedelta as _timedelta
from functools import partial as _part
import time as _time
import numpy as _np
from qtpy.uic import loadUi
from qtpy.QtCore import Slot, Qt
from qtpy.QtWidgets import QHBoxLayout
import qtawesome as qta
from pyqtgraph import ViewBox
from pydm import utilities
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from pydm.widgets.timeplot import PyDMTimePlot, TimePlotCurveItem
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.clientarch import ClientArchiver
from siriushla.util import connect_window
from siriushla.widgets import SiriusMainWindow, SiriusConnectionSignal
from siriushla.as_di_dccts import DCCTMain


class CurrLTWindow(SiriusMainWindow):
    """Class to include some intelligence in the .ui file."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """Initialize some widgets."""
        super(CurrLTWindow, self).__init__(parent)

        UI_FILE = (_os.path.abspath(_os.path.dirname(__file__)) +
                   '/ui_si_ap_currlt.ui')
        tmp_file = _substitute_in_file(UI_FILE, {'PREFIX': prefix})
        self.prefix = prefix
        self.centralwidget = loadUi(tmp_file)
        self.setObjectName('SIApp')
        self.centralwidget.setObjectName('SIApp')
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle('SI Current Info: Current and Lifetime')
        self._setupUi()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        # channels
        self.lifetime_dcct_pv = SiriusConnectionSignal(
            self.prefix+'SI-Glob:AP-CurrInfo:Lifetime-Mon')
        self.lifetime_dcct_pv.new_value_signal[float].connect(
            self.formatLifetime)
        self.lifetime_bpm_pv = SiriusConnectionSignal(
            self.prefix+'SI-Glob:AP-CurrInfo:LifetimeBPM-Mon')
        self.lifetime_bpm_pv.new_value_signal[float].connect(
            self.formatLifetime)
        self.dcct_buff_y_pv = SiriusConnectionSignal(
            self.prefix+'SI-Glob:AP-CurrInfo:BufferValue-Mon')
        self.dcct_buff_x_pv = SiriusConnectionSignal(
            self.prefix+'SI-Glob:AP-CurrInfo:BufferTimestamp-Mon')
        self.bpm_buff_y_pv = SiriusConnectionSignal(
            self.prefix+'SI-Glob:AP-CurrInfo:BufferValueBPM-Mon')
        self.bpm_buff_x_pv = SiriusConnectionSignal(
            self.prefix+'SI-Glob:AP-CurrInfo:BufferTimestampBPM-Mon')

        # set params in widgets in .ui
        self.centralwidget.label_lifetime.channel = \
            self.prefix+'SI-Glob:AP-CurrInfo:Lifetime-Mon'
        self.centralwidget.label_lifetime.setText("0:00:00")
        self.centralwidget.label_lifetime.setStyleSheet('font-size: 40px;')
        self.centralwidget.label_current.setStyleSheet('font-size: 40px;')

        self.centralwidget.DCCT13C4_detail.setObjectName('DCCT13C4_dtl')
        self.centralwidget.DCCT13C4_detail.setStyleSheet(
            "#DCCT13C4_dtl{min-width:25px; max-width:25px; icon-size:20px;}")
        self.centralwidget.DCCT13C4_detail.setIcon(qta.icon('fa5s.ellipsis-h'))
        connect_window(
            self.centralwidget.DCCT13C4_detail, DCCTMain, self,
            prefix=self.prefix, device='SI-13C4:DI-DCCT')
        self.centralwidget.DCCT14C4_detail.setObjectName('DCCT13C4_dtl')
        self.centralwidget.DCCT14C4_detail.setStyleSheet(
            "#DCCT13C4_dtl{min-width:25px; max-width:25px; icon-size:20px;}")
        self.centralwidget.DCCT14C4_detail.setIcon(qta.icon('fa5s.ellipsis-h'))
        connect_window(
            self.centralwidget.DCCT14C4_detail, DCCTMain, self,
            prefix=self.prefix, device='SI-14C4:DI-DCCT')

        self.centralwidget.label_buffersize_tot.channel = \
            self.prefix+'SI-Glob:AP-CurrInfo:BuffSizeTot-Mon'
        self.centralwidget.label_buffersize.channel = \
            self.prefix+'SI-Glob:AP-CurrInfo:BuffSize-Mon'

        self.centralwidget.comboBox_lifetime.currentTextChanged.connect(
            self.handle_lifetime_pv)
        self.centralwidget.spinBox_TimeSpan.valueChanged.connect(
            self.setGraphTimeSpan)

        # create graph
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
        self.graph.bufferSize = 20000
        self.setGraphTimeSpan(2000)

        self.graph.addYChannel(
            y_channel=self.prefix+'SI-Glob:AP-CurrInfo:Current-Mon',
            axis='left', name='Current', color='blue', lineWidth=1)
        self._curve_current = self.graph.curveAtIndex(0)
        self._fillCurveWithArchData(
            self._curve_current,
            self.prefix+'SI-Glob:AP-CurrInfo:Current-Mon')

        self.graph.addYChannel(
            y_channel=self.prefix+'SI-01M1:DI-BPM:Sum-Mon',
            axis='left', name='Current', color='blue', lineWidth=1)
        self._curve_bpmsum = self.graph.curveAtIndex(1)
        self._fillCurveWithArchData(
            self._curve_bpmsum, self.prefix+'SI-01M1:DI-BPM:Sum-Mon')

        self.graph.addYChannel(
            y_channel='FAKE:Lifetime', axis='right', name='Lifetime',
            color='red', lineWidth=1)
        self._curve_lifetimedcct = self.graph.curveAtIndex(2)
        self._fillCurveWithArchData(
            self._curve_lifetimedcct,
            self.prefix+'SI-Glob:AP-CurrInfo:Lifetime-Mon',
            factor=3600)

        self.graph.addYChannel(
            y_channel='FAKE:LifetimeBPM', axis='right', name='Lifetime',
            color='red', lineWidth=1)
        self._curve_lifetimebpm = self.graph.curveAtIndex(3)
        self._fillCurveWithArchData(
            self._curve_lifetimebpm,
            self.prefix+'SI-Glob:AP-CurrInfo:LifetimeBPM-Mon',
            factor=3600)

        self.lifetime_dcct_pv.new_value_signal[float].connect(
            self._updategraph)
        self.lifetime_bpm_pv.new_value_signal[float].connect(
            self._updategraph)

        self._flag_need_dcctx = True
        self._flag_need_dccty = True
        self._flag_need_bpmx = True
        self._flag_need_bpmy = True
        self.dcct_wavx = _np.array([])
        self.dcct_wavy = _np.array([])
        self.bpm_wavx = _np.array([])
        self.bpm_wavy = _np.array([])
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

        self.centralwidget.graphs_wid.setLayout(QHBoxLayout())
        self.centralwidget.graphs_wid.layout().setContentsMargins(0, 0, 0, 0)
        self.centralwidget.graphs_wid.layout().addWidget(self.graph)

    def formatLifetime(self, value):
        """Format lifetime label."""
        if self.centralwidget.label_lifetime.channel != self.sender().address:
            return
        lt = 0 if _np.isnan(value) else value
        H = int(lt // 3600)
        m = int((lt % 3600) // 60)
        s = int((lt % 3600) % 60)
        lt_str = '{:d}:{:02d}:{:02d}'.format(H, m, s)
        self.centralwidget.label_lifetime.setText(lt_str)

    @Slot(int)
    def setGraphTimeSpan(self, value):
        """Set graph time span."""
        self.graph.setTimeSpan(float(value))

    @Slot(str)
    def handle_lifetime_pv(self, text):
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
            self.centralwidget.label_lifetime.channel = \
                self.prefix+'SI-Glob:AP-CurrInfo:LifetimeBPM-Mon'
            self.centralwidget.label_buffersize_tot.channel = \
                self.prefix+'SI-Glob:AP-CurrInfo:BuffSizeTotBPM-Mon'
            self.centralwidget.label_buffersize.channel = \
                self.prefix+'SI-Glob:AP-CurrInfo:BuffSizeBPM-Mon'
        else:
            self.graph.plotItem.getAxis('left').setLabel(
                'Current [mA]', color='blue')
            self.centralwidget.label_lifetime.channel = \
                self.prefix+'SI-Glob:AP-CurrInfo:Lifetime-Mon'
            self.centralwidget.label_buffersize_tot.channel = \
                self.prefix+'SI-Glob:AP-CurrInfo:BuffSizeTot-Mon'
            self.centralwidget.label_buffersize.channel = \
                self.prefix+'SI-Glob:AP-CurrInfo:BuffSize-Mon'

    @Slot(float)
    def _updategraph(self, value):
        if 'BPM' in self.sender().address:
            self._curve_lifetimebpm.receiveNewValue(value/3600)
        else:
            self._curve_lifetimedcct.receiveNewValue(value/3600)

    @Slot(_np.ndarray)
    def _update_waveforms(self, value):
        address = self.sender().address
        if 'BPM' in address:
            if 'Timestamp' in address:
                self.bpm_wavx = value + _time.time()
                self._flag_need_bpmx = False
            elif 'Value' in address:
                self.bpm_wavy = value
                self._flag_need_bpmy = False
            if not self._flag_need_bpmy and not self._flag_need_bpmx:
                self._fillCurveBuffer(
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
                self._fillCurveBuffer(
                    self._curve_dcct_buff, self.dcct_wavx, self.dcct_wavy)
                self._flag_need_dcctx = True
                self._flag_need_dccty = True

    def _get_value_from_arch(self, pvname):
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

    def _fillCurveWithArchData(self, curve, pvname, factor=None):
        data = self._get_value_from_arch(pvname)
        if not data:
            return
        datax, datay = data
        self._fillCurveBuffer(curve, datax, datay)

    def _fillCurveBuffer(self, curve, datax, datay, factor=None):
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


class MyGraph(PyDMTimePlot):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.vb2 = ViewBox()
        self.plotItem.scene().addItem(self.vb2)
        self.vb2.setXLink(self.plotItem)
        self.plotItem.getAxis('right').linkToView(self.vb2)
        self.plotItem.showAxis('right')
        self._updateViews()
        self.plotItem.vb.sigResized.connect(self._updateViews)

    def addCurve(self, plot_item, axis='left', curve_color=None):
        if curve_color is None:
            curve_color = utilities.colors.default_colors[
                len(self._curves) % len(utilities.colors.default_colors)]
            plot_item.color_string = curve_color
        self._curves.append(plot_item)
        if axis == 'left':
            self.plotItem.addItem(plot_item)
        elif axis == 'right':
            self.vb2.addItem(plot_item)
        else:
            raise ValueError('Choose a valid axis!')
        self.redraw_timer.start()
        # Connect channels
        for chan in plot_item.channels():
            if chan:
                chan.connect()

    def addYChannel(self, y_channel=None, name=None, color=None,
                    lineStyle=None, lineWidth=None, symbol=None,
                    symbolSize=None, axis='left'):
        """Reimplement addYChannel."""
        plot_opts = dict()
        plot_opts['symbol'] = symbol
        if symbolSize is not None:
            plot_opts['symbolSize'] = symbolSize
        if lineStyle is not None:
            plot_opts['lineStyle'] = lineStyle
        if lineWidth is not None:
            plot_opts['lineWidth'] = lineWidth

        # Add curve
        new_curve = TimePlotCurveItem(
            y_channel,
            plot_by_timestamps=self._plot_by_timestamps,
            name=name, color=color,
            **plot_opts)
        new_curve.setUpdatesAsynchronously(self.updatesAsynchronously)
        new_curve.setBufferSize(self._bufferSize)

        self.update_timer.timeout.connect(new_curve.asyncUpdate)
        self.addCurve(new_curve, axis, curve_color=color)

        new_curve.data_changed.connect(self.set_needs_redraw)
        self.redraw_timer.start()

    def _updateViews(self):
        self.vb2.setGeometry(self.plotItem.vb.sceneBoundingRect())
        self.vb2.linkedViewChanged(self.plotItem.vb, self.vb2.XAxis)
