"""DCCT graphics module."""

import numpy as np
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, \
    QHBoxLayout, QGroupBox, QSpinBox, QComboBox, QSpacerItem, \
    QSizePolicy as QSzPly
from siriuspy.namesys import SiriusPVName
from siriuspy.csdevice.dccts import Const as _DCCTc
from pydm.widgets import PyDMWaveformPlot
from siriushla.widgets import SiriusConnectionSignal as SignalChannel


class DCCTMonitor(QWidget):
    """Widget to ramp status monitoring."""

    _buffSizeUpdate = Signal(str)

    def __init__(self, parent=None, prefix='', device='',
                 layout_with_settings=False):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = SiriusPVName(prefix)
        self.device = SiriusPVName(device)
        self.use_raw = False
        self.layout_with_settings = layout_with_settings
        if self.device.sec == 'BO':
            self.use_raw = True
        self.dcct_prefix = prefix + device + ':'

        self.acqmode_channel = SignalChannel(self.dcct_prefix+'MeasMode-Sel')
        self.acqmode_channel.new_value_signal[int].connect(self.setNrSamples)
        self.normalnrsamp_channel = SignalChannel(
            self.dcct_prefix + 'SampleCnt-RB')
        self.normalnrsamp_channel.new_value_signal[int].connect(
            self.setNrSamples)
        self.fastnrsamp_channel = SignalChannel(
            self.dcct_prefix + 'FastSampleCnt-RB')
        self.fastnrsamp_channel.new_value_signal[int].connect(
            self.setNrSamples)
        self._acq_mode = None
        self._acq_normalnrsamp = None
        self._acq_fastnrsamp = None

        self._downsampling = 1
        self._smooth_method = 'Average'
        self._smooth_nracq = 1
        self._smooth_buffer = list()

        self._setupUi()

    def _setupUi(self):
        text = 'Current Raw Readings' if self.use_raw else 'Current History'
        label = QLabel('<h3>'+text+'</h3>', self, alignment=Qt.AlignCenter)

        self.graph = PyDMWaveformPlot(self)
        self.graph.autoRangeX = True
        self.graph.autoRangeY = True
        self.graph.backgroundColor = QColor(255, 255, 255)
        self.graph.axisColor = QColor(0, 0, 0)
        self.graph.showLegend = False
        self.graph.showXGrid = True
        self.graph.showYGrid = True
        self.graph.setLabels(left='Current [mA]', bottom='Index')
        if self.use_raw:
            channel = 'FAKE:Readings'
            self.rawreadings_channel = SignalChannel(
                self.dcct_prefix + 'RawReadings-Mon')
            self.rawreadings_channel.new_value_signal[np.ndarray].connect(
                self._updateBuffer)
        else:
            channel = self.dcct_prefix + 'CurrHstr-Mon'
        self.graph.addChannel(
            y_channel=channel, name=text, color='blue',
            lineWidth=2, lineStyle=Qt.SolidLine)
        leftAxis = self.graph.getAxis('left')
        leftAxis.setStyle(autoExpandTextSpace=False, tickTextWidth=25)
        self.curve = self.graph.curveAtIndex(0)

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 9)
        lay.addWidget(label, 0, 0)
        if self.layout_with_settings:
            lay.addWidget(self.graph, 1, 0, 2, 1)
        else:
            lay.addWidget(self.graph, 1, 0)
        self.setLayout(lay)

        # Smoothing
        if self.use_raw:
            l_smoothmethod = QLabel('Method: ', self)
            self.cb_smoothmethod = QComboBox(self)
            self.cb_smoothmethod.addItems(['Average', 'Median'])
            self.cb_smoothmethod.currentTextChanged.connect(
                self.setSmoothMethod)

            l_smoothnracq = QLabel('Nr.Acqs.: ', self)
            self.sb_smoothnracq = QSpinBox(self)
            self.sb_smoothnracq.setValue(1)
            self.sb_smoothnracq.valueChanged.connect(
                self.setSmoothNrAcq)

            l_smoothbuff = QLabel('Buffer Size: ', self)
            l_smoothbuff.setSizePolicy(QSzPly.Minimum, QSzPly.Preferred)
            self.label_buffsize = QLabel('', self)
            self.label_buffsize.setStyleSheet(
                'min-width:3em; max-width:3em;')
            self._buffSizeUpdate.connect(self.label_buffsize.setText)
            self.pb_resetbuff = QPushButton('Reset', self)
            self.pb_resetbuff.clicked.connect(self.resetBuffer)
            hlay_buff = QHBoxLayout()
            hlay_buff.addWidget(self.label_buffsize)
            hlay_buff.addWidget(self.pb_resetbuff)

            l_down = QLabel('Downsampling: ', self)
            self.sb_down = QSpinBox(self)
            self.sb_down.setValue(1)
            self.sb_down.valueChanged.connect(self.setDownsampling)

            gbox_smooth = QGroupBox('Smoothing of Readings')
            glay_smooth = QGridLayout(gbox_smooth)
            if self.layout_with_settings:
                glay_smooth.addWidget(l_smoothmethod, 0, 0)
                glay_smooth.addWidget(self.cb_smoothmethod, 0, 1)
                glay_smooth.addWidget(l_smoothnracq, 1, 0)
                glay_smooth.addWidget(self.sb_smoothnracq, 1, 1)
                glay_smooth.addWidget(l_smoothbuff, 2, 0)
                glay_smooth.addLayout(hlay_buff, 2, 1)
                glay_smooth.addWidget(l_down, 3, 0)
                glay_smooth.addWidget(self.sb_down, 3, 1)
                glay_smooth.setAlignment(Qt.AlignCenter)
                lay.addWidget(gbox_smooth, 2, 1)
            else:
                glay_smooth.addWidget(l_smoothmethod, 0, 0)
                glay_smooth.addWidget(self.cb_smoothmethod, 0, 1)
                glay_smooth.addWidget(l_smoothnracq, 1, 0)
                glay_smooth.addWidget(self.sb_smoothnracq, 1, 1)
                glay_smooth.addWidget(QLabel(''), 0, 2)
                glay_smooth.addWidget(l_smoothbuff, 0, 3)
                glay_smooth.addLayout(hlay_buff, 0, 4, 1, 2)
                glay_smooth.addWidget(l_down, 1, 3)
                glay_smooth.addWidget(self.sb_down, 1, 4, 1, 2)
                glay_smooth.setColumnStretch(0, 10)
                glay_smooth.setColumnStretch(1, 10)
                glay_smooth.setColumnStretch(2, 2)
                glay_smooth.setColumnStretch(3, 10)
                glay_smooth.setColumnStretch(4, 5)
                glay_smooth.setColumnStretch(5, 5)
                lay.addWidget(gbox_smooth, 2, 0)
                lay.setRowStretch(2, 3)
            gbox_smooth.setStyleSheet("""
                .QLabel{
                    qproperty-alignment: 'AlignVCenter | AlignRight';}
                QPushButton{
                    min-width:3em; max-width:3em;}""")

        self.setStyleSheet("""
            .QLabel{
                max-height:1.5em;}
            PyDMWaveformPlot{
                min-width:30em; min-height:20em;}
        """)

    def _updateBuffer(self, raw):
        if raw is None:
            return
        samp = self._acq_fastnrsamp \
            if self._acq_mode == _DCCTc.MeasModeSel.Fast \
            else self._acq_normalnrsamp
        if not samp:
            return
        samp -= samp % self._downsampling
        if samp < 1:
            return
        data = raw[:samp]

        self._smooth_buffer.append(data)
        if len(self._smooth_buffer) > self._smooth_nracq:
            self._smooth_buffer.pop(0)

        self._updateCurve()

    def _updateCurve(self):
        buff = np.array(self._smooth_buffer, dtype=float)
        self._buffSizeUpdate.emit(str(self.bufferSize))

        if not len(buff):
            return
        if len(buff) > 1:
            if self._smooth_method == 'Average':
                fdata = np.mean(buff, axis=0)
            elif self._smooth_method == 'Median':
                fdata = np.median(buff, axis=0)
        else:
            fdata = buff[0]

        down = self._downsampling
        if down > 1:
            fdata = np.mean(fdata.reshape(-1, down), axis=1)

        self.curve.receiveYWaveform(fdata)
        self.curve.redrawCurve()

    def setDownsampling(self, new_value):
        """Update number of samples to use in downsampling."""
        self._downsampling = new_value
        self.resetBuffer()

    def setSmoothMethod(self, new_method):
        """Update method to perform raw readings smoothing."""
        self._smooth_method = new_method
        self._updateCurve()

    def setSmoothNrAcq(self, new_value):
        """Update number of samples to use in smoothing."""
        self._smooth_nracq = new_value
        exc = len(self._smooth_buffer) - self._smooth_nracq
        if exc > 0:
            for i in range(exc):
                self._smooth_buffer.pop(0)

    @property
    def bufferSize(self):
        """Smoothing buffer length."""
        return len(self._smooth_buffer)

    def resetBuffer(self):
        """Reset smoothing buffer."""
        self._smooth_buffer = list()
        self._updateCurve()

    def setNrSamples(self, new_value):
        address = self.sender().address
        if 'Mode' in address:
            self._acq_mode = new_value
        elif 'Fast' in address:
            self._acq_fastnrsamp = new_value
        else:
            self._acq_normalnrsamp = new_value
        self.resetBuffer()


class BORampEffMonitor(QWidget):
    """Booster Ramp Efficiency Graph."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = 'BO-35D:DI-DCCT'
        self.dcct_prefix = prefix + self.device + ':'
        self._wavEff = list()
        self._inj_idx = 0
        self._eje_idx = -1
        self._init_indices = False
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h3>Booster Ramp Efficiency</h3>', self,
                       alignment=Qt.AlignCenter)

        self.rawreadings_channel = SignalChannel(
            self.dcct_prefix+'RawReadings-Mon')
        self.rawreadings_channel.new_value_signal[np.ndarray].connect(
            self._updateRampEffGraph)

        self.graph = PyDMWaveformPlot(self)
        self.graph.autoRangeX = True
        self.graph.autoRangeY = True
        self.graph.backgroundColor = QColor(255, 255, 255)
        self.graph.axisColor = QColor(0, 0, 0)
        self.graph.showLegend = False
        self.graph.showXGrid = True
        self.graph.showYGrid = True
        self.graph.setLabels(
            left='Ramp Efficiency [%]', bottom='Pulse')
        self.graph.addChannel(
            y_channel='FAKE:RampEff-Mon', name='Efficiency',
            color='blue', lineWidth=2, lineStyle=Qt.SolidLine,
            symbol='o', symbolSize=2)
        leftAxis = self.graph.getAxis('left')
        leftAxis.setStyle(autoExpandTextSpace=False, tickTextWidth=25)
        self.curve = self.graph.curveAtIndex(0)

        self.pb_clearGraph = QPushButton('Clear graph', self)
        self.pb_clearGraph.clicked.connect(self._clearGraph)

        l_indices = QLabel('Curve indices', self, alignment=Qt.AlignCenter)
        l_indices.setStyleSheet('font-weight: bold;')
        l_injidx = QLabel('Injection: ', self)
        self.sb_injidx = QSpinBox(self)
        self.sb_injidx.setValue(self._inj_idx)
        self.sb_injidx.setObjectName('injection_index')
        self.sb_injidx.valueChanged.connect(self._updateIndices)

        l_ejeidx = QLabel('Ejection: ', self)
        self.sb_ejeidx = QSpinBox(self)
        self.sb_ejeidx.setValue(self._eje_idx)
        self.sb_ejeidx.setObjectName('ejection_index')
        self.sb_ejeidx.valueChanged.connect(self._updateIndices)

        # Set index limits
        self.fastsamplecnt_channel = SignalChannel(
            self.dcct_prefix+'FastSampleCnt-RB')
        self.fastsamplecnt_channel.new_value_signal[int].connect(
            self._updateIndecesLimits)
        self.sb_injidx.setMinimum(0)
        self.sb_ejeidx.setMinimum(0)

        l_injcurr = QLabel('Injected:', self)
        self.label_injcurr = QLabel(self)
        l_ejecurr = QLabel('Ejected:', self)
        self.label_ejecurr = QLabel(self)
        l_rampeff = QLabel('<h4>Efficiency:</h4>', self)
        self.label_rampeff = QLabel(self)

        glay = QGridLayout()
        glay.addWidget(label, 0, 0, 1, 8)
        glay.addWidget(self.graph, 1, 0, 1, 8)
        glay.addItem(QSpacerItem(1, 1, QSzPly.Expanding, QSzPly.Ignored), 2, 0)
        glay.addWidget(l_indices, 2, 1, 1, 2)
        glay.addWidget(l_injidx, 3, 1)
        glay.addWidget(self.sb_injidx, 3, 2)
        glay.addWidget(l_ejeidx, 4, 1)
        glay.addWidget(self.sb_ejeidx, 4, 2)
        glay.addItem(QSpacerItem(1, 1, QSzPly.Expanding, QSzPly.Ignored), 2, 3)
        glay.addWidget(l_rampeff, 2, 4)
        glay.addWidget(self.label_rampeff, 2, 5)
        glay.addWidget(l_injcurr, 3, 4)
        glay.addWidget(self.label_injcurr, 3, 5)
        glay.addWidget(l_ejecurr, 4, 4)
        glay.addWidget(self.label_ejecurr, 4, 5)
        glay.addItem(QSpacerItem(1, 1, QSzPly.Expanding, QSzPly.Ignored), 2, 6)
        glay.addWidget(self.pb_clearGraph, 2, 7, alignment=Qt.AlignRight)
        self.setLayout(glay)
        self.setStyleSheet("""
            .QLabel{
                qproperty-alignment:'AlignCenter';}
            PyDMWaveformPlot{
                min-width:30em; min-height:20em;}
        """)

    def _updateRampEffGraph(self, data):
        if data is not None:
            inj_curr = data[self._inj_idx]
            eje_curr = data[self._eje_idx]
            eff = 100*eje_curr/inj_curr
            self._wavEff.append(eff)
            if len(self._wavEff) > 1000:
                self._wavEff.pop(0)
            self.label_injcurr.setText(str('{: .4f} mA'.format(inj_curr)))
            self.label_ejecurr.setText(str('{: .4f} mA'.format(eje_curr)))
            self.label_rampeff.setText(str('{: .3f} %'.format(eff)))
            self.curve.receiveYWaveform(np.array(self._wavEff))
            self.curve.redrawCurve()

    def _clearGraph(self):
        self._wavEff.clear()
        self.curve.receiveYWaveform(np.array(self._wavEff))
        self.graph.redrawPlot()

    def _updateIndices(self, index):
        """Update indices to calculate ramp efficiency."""
        sender_name = self.sender().objectName()
        if 'injection' in sender_name:
            self._inj_idx = index
        else:
            self._eje_idx = index

    def _updateIndecesLimits(self, new_max_lim):
        """Update upper indeces limit."""
        if not self._init_indices:
            self._inj_idx = 0
            self.sb_injidx.setMaximum(new_max_lim-1)
            self.sb_injidx.setValue(0)
            self._eje_idx = new_max_lim-1
            self.sb_ejeidx.setMaximum(new_max_lim-1)
            self.sb_ejeidx.setValue(new_max_lim-1)
            self._init_indices = True
        self.sb_injidx.setMaximum(new_max_lim-1)
        self.sb_ejeidx.setMaximum(new_max_lim-1)


if __name__ == '__main__':
    """Run test."""
    import sys as _sys
    import argparse as _argparse
    from siriuspy.envars import vaca_prefix as _vaca_prefix
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import create_window_from_widget as \
        _create_window_from_widget

    parser = _argparse.ArgumentParser(description="DCCT graphics.")
    parser.add_argument(
        '-o', "--option", type=str, default='monitor',
        help="Use 'monitor' to show current monitoring and "
             "'rampeff' to show Booster ramp efficiency graph.")
    args = parser.parse_args()

    app = SiriusApplication()
    if args.option == 'rampeff':
        BORampEffWindow = _create_window_from_widget(
            BORampEffMonitor, 'Booster Ramp Efficiency',
            is_main=True)
        window = BORampEffWindow(None, prefix=_vaca_prefix)
    else:
        device = 'BO-35D:DI-DCCT'
        Monitor = _create_window_from_widget(
            DCCTMonitor, 'Booster Ramp Efficiency', is_main=True)
        window = Monitor(None, prefix=_vaca_prefix, device=device)
    window.show()
    _sys.exit(app.exec_())
