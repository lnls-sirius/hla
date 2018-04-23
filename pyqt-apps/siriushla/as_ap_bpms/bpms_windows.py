from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QRadioButton,
                             QGridLayout, QTabWidget, QStackedWidget, QLabel,
                             QGroupBox, QFormLayout, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from pydm.widgets import (PyDMWaveformPlot, PyDMTimePlot, PyDMSpinbox,
                          PyDMLabel, PyDMCheckbox)
from pydm.widgets import PyDMPushButton as PyDMPB
from pydm.widgets import PyDMEnumComboBox as PyDMECB
from pydm.widgets.channel import PyDMChannel
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, SiriusDialog, SiriusLedAlert
from siriushla import util


class _WidgetsCreator:

    def __init__(self, prefix='', bpm_list=tuple(), data_prefix=''):
        self.prefix = prefix
        self.bpm_list = bpm_list
        self.data_prefix = data_prefix

    def create_wid(self, cls, propty, parent=None, write=True,
                   use_data_prefix=True):
        wid = cls(parent or self)
        wid._channels = []
        for bpm in self.bpm_list:
            addr = self.prefix + bpm
            addr += self.data_prefix if use_data_prefix else ''
            addr += propty
            chan = PyDMChannel(
                    address=addr,
                    connection_slot=wid.connectionStateChanged,
                    value_slot=wid.channelValueChanged,
                    severity_slot=wid.alarmSeverityChanged,
                    enum_strings_slot=wid.enumStringsChanged,
                    unit_slot=wid.unitChanged,
                    prec_slot=wid.precisionChanged,
                    upper_ctrl_limit_slot=wid.upperCtrlLimitChanged,
                    lower_ctrl_limit_slot=wid.lowerCtrlLimitChanged)
            if write:
                chan.value_signal = wid.send_value_signal
                chan.write_access_slot = wid.writeAccessChanged
            wid._channels.append(chan)
        return wid

    def isSingleBPM(self):
        return len(self.bpm_list) == 1


class BPMsInterface(SiriusMainWindow, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        SiriusMainWindow.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        wid = OperationModes(parent=self, **kwargs)
        self.setCentralWidget(wid)
        self.setWindowTitle(self.prefix)
        self.resize(1500, 1800)
        self.configure_menuBar()

    def configure_menuBar(self):
        menubar = self.menuBar()
        cb = self.create_wid(PyDMCheckbox, propty='OpMode-Sel')
        cb.setVisible(False)

        if self.isSingleBPM():
            menubar.addAction('&Calibration').triggered.connect(
                                                self.open_calibration_window)
        else:
            menubar.addAction('&Open Individual BPMs').triggered.connect(
                                                self.open_single_bpm_window)

    def open_calibration_window(self):
        app = SiriusApplication.instance()
        app.open_window(CalibrationWindow, parent=self,
                        prefix=self.prefix, bpm_list=self.bpm_list)

    def open_single_bpm_window(self):
        app = SiriusApplication.instance()
        app.open_window(SingleBPMSelectionWindow, parent=self,
                        prefix=self.prefix, bpm_list=self.bpm_list)


class BPMsInterfaceTL(BPMsInterface):
    """BPMs interface for Sirius Transport Lines."""

    BPM_DICT = {
        'TB': (
            'TB-01:DI-BPM-1:', 'TB-01:DI-BPM-2:',
            'TB-02:DI-BPM-1:', 'TB-02:DI-BPM-1:',
            'TB-03:DI-BPM:',
            'TB-04:DI-BPM:',
            ),
        'TS': (
            'TS-01:DI-BPM:', 'TS-02:DI-BPM:', 'TS-03:DI-BPM:',
            'TS-04:DI-BPM-1:', 'TS-04:DI-BPM-2:',
            ),
        }

    def __init__(self, parent=None, prefix='', TL=''):
        """Initialize the Instance.

        INPUTS:
            parent = parent widget;
            prefix = prefix for the BPM PVs;
            TL = string especifying the Transport Line ('TB' or 'TS').
        """
        if TL not in self.BPM_DICT.keys():
            raise Exception("TL must be 'TB' or 'TS'")
        bpm_list = self.BPM_DICT[TL]
        super().__init__(parent=parent, prefix=prefix, bpm_list=bpm_list)


class SingleBPMSelectionWindow(SiriusDialog, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        SiriusDialog.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        fl = QFormLayout(self)
        fl.setAlignment(Qt.AlignCenter)
        self.app = SiriusApplication.instance()

        lb = QLabel('BPMs controlled by This interface')
        f = lb.font()
        f.setBold(True)
        lb.setFont(f)
        lb.setAlignment(Qt.AlignCenter)
        fl.addRow(lb)
        fl.addRow('Status', QLabel('BPM Name', self))
        for bpm in self.bpm_list:
            pv_pref = kwargs['prefix'] + bpm
            led = SiriusLedAlert(self, init_channel=pv_pref+'asyn.CNCT')
            pb = QPushButton(bpm[:-1], self)
            pb.clicked.connect(self.open_bpm_window(bpm))
            fl.addRow(led, pb)

    def open_bpm_window(self, bpm):
        def open(bool):
            self.app.open_window(BPMsInterface, parent=self.parent(),
                                 prefix=self.prefix, bpm_list=(bpm,))
        return open


class CalibrationWindow(SiriusDialog, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        SiriusDialog.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        self.fl = QFormLayout(self)
        self.fl.setLabelAlignment(Qt.AlignVCenter)
        lb = QLabel('Acquisition Mode')
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb)
        self._add_row('ACQBPMMode-Sel', 'ACQBPMMode-Sts', 'Offset PosQ')
        lb = QLabel('Offset Parameters')
        f = lb.font()
        f.setBold(True)
        lb.setFont(f)
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb)
        self._add_row('PosQOffset-SP', 'PosQOffset-RB', 'Offset PosQ')
        self._add_row('PosXOffset-SP', 'PosXOffset-RB', 'Offset PosX')
        self._add_row('PosYOffset-SP', 'PosYOffset-RB', 'Offset PosY')
        lb = QLabel('Gain Parameters')
        lb.setFont(f)
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb)
        self._add_row('PosKq-SP', 'PosKq-RB', 'Gain PosQ')
        self._add_row('PosKsum-SP', 'PosKsum-RB', 'Gain Sum')
        self._add_row('PosKx-SP', 'PosKx-RB', 'Gain PosX')
        self._add_row('PosKy-SP', 'PosKy-RB', 'Gain PosY')
        lb = QLabel('Informations')
        lb.setFont(f)
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb)
        self._add_row('INFOHarmonicNumber-SP', 'INFOHarmonicNumber-RB',
                      'Harmonic Number')
        self._add_row('INFOFOFBRate-SP', 'INFOFOFBRate-RB', 'FOFB Rate')
        self._add_row('INFOMONITRate-SP', 'INFOMONITRate-RB', 'Monitor Rate')
        self._add_row('INFOTBTRate-SP', 'INFOTBTRate-RB', 'TbT Rate')

    def _add_row(self, pv1, pv2, label):
        not_enum = pv1.endswith('-SP')
        CLASS_ = PyDMSpinbox if not_enum else PyDMECB
        le = self.create_wid(CLASS_, pv1)
        if not_enum:
            le.showStepExponent = False
        lb = self.create_wid(PyDMLabel, pv2, write=False)
        hl = QHBoxLayout()
        hl.addWidget(le)
        hl.addWidget(lb)
        lb2 = QLabel(label)
        lb2.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb2, hl)


class OperationModes(QTabWidget, _WidgetsCreator):
    def __init__(self, parent=None, **kwargs):
        QTabWidget.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        if self.isSingleBPM():
            wid = ContinuousMonitSingleBPM(parent=self, **kwargs)
        else:
            wid = ContinuousMonitMultiBPM(parent=self, **kwargs)
        self.addTab(wid, 'Continuous Monitoring')
        wid = TrigAcquisitions(parent=self, **kwargs)
        self.addTab(wid, 'Triggered Acquisitions')
        wid = PostMortemWid(parent=self, **kwargs)
        self.addTab(wid, 'Post Mortem')


class ContinuousMonitMultiBPM(QWidget, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        QWidget.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)


class ContinuousMonitSingleBPM(QWidget, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        QWidget.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        gl = QGridLayout(self)
        pv_pref = self.prefix + self.bpm_list[0]
        prps = {}
        prps['colors'] = ['blue', ]
        prps['init_channels'] = [pv_pref+'PosX-Mon', ]
        prps['label'] = 'Position X [nm]'
        plotPosX = self.createPlot(**prps)
        gl.addWidget(plotPosX, 0, 0, 1, 1)

        prps['colors'] = ['red', ]
        prps['init_channels'] = [pv_pref+'PosY-Mon', ]
        prps['label'] = 'Position Y [nm]'
        plotPosY = self.createPlot(**prps)
        gl.addWidget(plotPosY, 1, 0, 1, 1)

        # prps['colors'] = ['black', ]
        # prps['init_channels'] = [pv_pref+'Sum-Mon', ]
        # prps['label'] = 'Sum'
        # plotPosS = self.createPlot(**prps)
        # gl.addWidget(plotPosS, 2, 0, 1, 1)

        prps['colors'] = ['green', ]
        prps['init_channels'] = [pv_pref+'PosQ-Mon', ]
        prps['label'] = 'Skew'
        plotPosQ = self.createPlot(**prps)
        gl.addWidget(plotPosQ, 2, 0, 1, 1)

        prps['colors'] = ['blue', 'red', 'black', 'green']
        prps['init_channels'] = [pv_pref+'AmplA-Mon',
                                 pv_pref+'AmplB-Mon',
                                 pv_pref+'AmplC-Mon',
                                 pv_pref+'AmplD-Mon']
        prps['label'] = 'Antennas'
        plotAmps = self.createPlot(**prps)
        gl.addWidget(plotAmps, 3, 0, 1, 1)

    def createPlot(self, colors=None, init_channels=None, label=None):
        plot = PyDMTimePlot(
                            parent=self,
                            init_y_channels=init_channels,
                            background='w')
        plot.timeSpan = 60
        for i, color in enumerate(colors):
            plot._curves[i].color = color
            plot._curves[i].lineWidth = 2
        pl_item = plot.getPlotItem()
        pl_item.showButtons()
        pl_item.setTitle(label, **{'size': '32px'})
        font = QFont()
        font.setPixelSize(32)
        ax = pl_item.getAxis('left')
        # ax.setLabel(label, **{'font-size': '32px'})
        # ax.showLabel()
        ax.setTickFont(font)
        ax.setStyle(autoExpandTextSpace=False,
                    tickTextWidth=100)
        ax = pl_item.getAxis('bottom')
        ax.setTickFont(font)
        ax.setStyle(autoExpandTextSpace=False,
                    tickTextHeight=30,
                    tickTextOffset=15)
        ax = pl_item.getAxis('right')
        ax.show()
        ax.setStyle(showValues=False)
        ax = pl_item.getAxis('top')
        ax.show()
        ax.setStyle(showValues=False)
        pl_item.showGrid(x=True, y=True)
        # pl_item.titleLabel.setMaximumHeight(100)
        # pl_item.layout.setRowFixedHeight(0, 100)
        # pl_item.titleLabel.setText('PosX-Mon', **labelStyle)
        return plot


class TrigAcquisitions(QWidget, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        QWidget.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        vl = QVBoxLayout(self)
        stack = QStackedWidget(parent=self)
        if self.isSingleBPM:
            multi_pass = MultiPassDataSingleBPM(
                                    parent=self, **kwargs, acq_type='ACQ')
            single_pass = SinglePassDataSingleBPM(parent=self, **kwargs)
        else:
            multi_pass = MultiPassDataMultiBPM(
                                    parent=self, **kwargs, acq_type='ACQ')
            single_pass = SinglePassDataMultiBPM(parent=self, **kwargs)

        stack.addWidget(multi_pass)
        stack.addWidget(single_pass)
        self.stack = stack
        vl.addWidget(stack)
        config = MultiPassConfig(
                parent=self, **kwargs, data_prefix='ACQ')
        config.acq_channel.currentIndexChanged[str].connect(
                                    multi_pass.control_visibility_buttons)
        config.acq_bpm_mode.currentIndexChanged[str].connect(
                                    self.toggle_multi_single)
        vl.addWidget(config)

    def toggle_multi_single(self, text):
        if text.lower().startswith('single'):
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)


class MultiPassDataSingleBPM(QWidget, _WidgetsCreator):
    _PROPS = ('A', 'B', 'C', 'D', 'X', 'Y', 'Sum', 'Q')
    _COLORS = ('blue', 'red', 'black', 'green')

    def __init__(self, parent=None, acq_type='ACQ', **kwargs):
        QWidget.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        self.data_prefix = 'GEN_' if acq_type == 'ACQ' else 'PM_'
        vl = QVBoxLayout(self)
        stack = QStackedWidget(self)
        self.stack = stack
        vl.addWidget(stack)

        hl = QHBoxLayout()
        self.radio_buttons = []
        for i, pos in enumerate(self._PROPS):
            posWid = self.create_prop_widget(i, pos)
            stack.addWidget(posWid)
            rb = QRadioButton(pos, self)
            rb.toggled.connect(self.toggle_button(i))
            if not i:
                rb.setChecked(True)
            self.radio_buttons.append(rb)
            hl.addWidget(rb)
        vl.addItem(hl)

    def toggle_button(self, i):
        def toggle(tog):
            if tog:
                self.stack.setCurrentIndex(i)
        return toggle

    def control_visibility_buttons(self, text):
        bo = not text.startswith('adc')
        for rb in self.radio_buttons[4:]:
            rb.setVisible(bo)
        self.radio_buttons[0].setChecked(True)

    def create_prop_widget(self, ind, prop):
        pv_prefix = self.prefix + self.bpm_list[0] + self.data_prefix + prop
        color = self._COLORS[ind % 4]
        wid = QWidget(self)
        gl = QGridLayout(wid)
        plot_prop = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[pv_prefix + 'ArrayData-Mon'],
            background='w')
        plot_prop._curves[0].color = color
        plot_prop._curves[0].lineWidth = 2
        gl.addWidget(plot_prop, 0, 0)

        fft_amp = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[pv_prefix + 'FFTData.AMP'],
            init_x_channels=[pv_prefix + 'FFTData.WAVN'],
            background='w')
        fft_amp._curves[0].color = color
        fft_amp._curves[0].lineWidth = 2
        gl.addWidget(fft_amp, 0, 1)

        fft_pha = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[pv_prefix + 'FFTData.PHA'],
            init_x_channels=[pv_prefix + 'FFTData.WAVN'],
            background='w')
        fft_pha._curves[0].color = color
        fft_amp._curves[0].lineWidth = 2
        gl.addWidget(fft_pha, 1, 1)

        vl = QVBoxLayout()
        gb = QGroupBox('Statistics', wid)
        fl = QFormLayout(gb)
        fl.addRow('Property', QLabel(prop))
        fl.addRow('Maximum',
                  PyDMLabel(gb, init_channel=pv_prefix+'_STATSMaxValue_RBV'))
        fl.addRow('Minimum',
                  PyDMLabel(gb, init_channel=pv_prefix+'_STATSMinValue_RBV'))
        fl.addRow('Average',
                  PyDMLabel(gb, init_channel=pv_prefix+'_STATSMeanValue_RBV'))
        fl.addRow('Deviation',
                  PyDMLabel(gb, init_channel=pv_prefix+'_STATSSigma_RBV'))
        vl.addWidget(gb)
        pb = QPushButton('Open FFT Config', wid)
        pb.clicked.connect(self.open_fft_config_window(wid, prop))
        vl.addWidget(pb)
        gl.addItem(vl, 1, 0)

        return wid

    def open_fft_config_window(self, wid, prop):
        app = SiriusApplication.instance()

        def open_window():
            app.open_window(
                    FFTConfigs, parent=wid, prefix=self.prefix,
                    bpm_list=self.bpm_list, data_prefix=self.data_prefix+prop)
        return open_window


class MultiPassDataMultiBPM(MultiPassDataSingleBPM):
    pass


class SinglePassDataSingleBPM(QWidget, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        """Initialize object."""
        QWidget.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        vl = QVBoxLayout(self)
        pv_pref = self.prefix + self.bpm_list[0]
        plot_prop = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[pv_pref + 'SP_AArrayData-Mon',
                             pv_pref + 'SP_BArrayData-Mon',
                             pv_pref + 'SP_CArrayData-Mon',
                             pv_pref + 'SP_DArrayData-Mon'],
            background='w')
        plot_prop._curves[0].color = 'blue'
        plot_prop._curves[1].color = 'red'
        plot_prop._curves[2].color = 'black'
        plot_prop._curves[3].color = 'green'
        vl.addWidget(plot_prop)

        self.stack = QStackedWidget()
        vl.addWidget(self.stack)
        plotXY = PyDMTimePlot(
                        self,
                        init_y_channels=[pv_pref + 'SPPosX-Mon',
                                         pv_pref + 'SPPosY-Mon'],
                        background='w')
        plotXY.timeSpan = 60
        plotXY._curves[0].color = 'blue'
        plotXY._curves[1].color = 'red'
        plotXY._curves[0].lineWidth = 2
        plotXY._curves[1].lineWidth = 2
        self.stack.addWidget(plotXY)
        hl = QHBoxLayout()
        plotSum = PyDMTimePlot(
                    self,
                    init_y_channels=[pv_pref + 'SPSum-Mon', ],
                    background='w')
        plotSum.timeSpan = 60
        plotSum._curves[0].color = 'black'
        plotSum._curves[0].lineWidth = 2
        hl.addWidget(plotSum)
        plotQ = PyDMTimePlot(
                    self,
                    init_y_channels=[pv_pref + 'SPPosQ-Mon', ],
                    background='w')
        plotQ.timeSpan = 60
        plotQ._curves[0].color = 'black'
        plotQ._curves[0].lineWidth = 2
        hl.addWidget(plotQ)
        wid = QWidget()
        wid.setLayout(hl)
        self.stack.addWidget(wid)

        plotAmp = PyDMTimePlot(
            parent=self,
            init_y_channels=[pv_pref + 'SPAmplA-Mon',
                             pv_pref + 'SPAmplB-Mon',
                             pv_pref + 'SPAmplC-Mon',
                             pv_pref + 'SPAmplD-Mon'],
            background='w')
        plotAmp._curves[0].color = 'blue'
        plotAmp._curves[1].color = 'red'
        plotAmp._curves[2].color = 'black'
        plotAmp._curves[3].color = 'green'
        self.stack.addWidget(plotAmp)

        hl = QHBoxLayout()
        for i, pos in enumerate(['X and Y', 'Sum and Q', 'Amplitudes']):
            rb = QRadioButton(pos, self)
            rb.toggled.connect(self.toggle_button(i))
            if not i:
                rb.setChecked(True)
            hl.addWidget(rb)
        vl.addItem(hl)

        hl = QHBoxLayout()
        vl.addItem(hl)
        gb = QGroupBox('Positions', self)
        fl = QFormLayout(gb)
        lb = PyDMLabel(gb, init_channel=pv_pref + 'SPPosX-Mon')
        fl.addRow('PosX', lb)
        lb = PyDMLabel(gb, init_channel=pv_pref + 'SPPosY-Mon')
        fl.addRow('PosY', lb)
        lb = PyDMLabel(gb, init_channel=pv_pref + 'SPSum-Mon')
        fl.addRow('Sum', lb)
        lb = PyDMLabel(gb, init_channel=pv_pref + 'SPPosQ-Mon')
        fl.addRow('PosQ', lb)
        hl.addWidget(gb)
        gb = QGroupBox('Processed Antennas', self)
        fl = QFormLayout(gb)
        lb = PyDMLabel(gb, init_channel=pv_pref + 'SPAmplA-Mon')
        fl.addRow('AmplA', lb)
        lb = PyDMLabel(gb, init_channel=pv_pref + 'SPAmplB-Mon')
        fl.addRow('AmplB', lb)
        lb = PyDMLabel(gb, init_channel=pv_pref + 'SPAmplC-Mon')
        fl.addRow('AmplC', lb)
        lb = PyDMLabel(gb, init_channel=pv_pref + 'SPAmplD-Mon')
        fl.addRow('AmplD', lb)
        hl.addWidget(gb)

    def toggle_button(self, i):
        def toggle(tog):
            if tog:
                self.stack.setCurrentIndex(i)
        return toggle


class SinglePassDataMultiBPM(SinglePassDataSingleBPM):
    pass


class FFTConfigs(SiriusDialog, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        SiriusDialog.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        self.fl = QFormLayout(self)
        self.fl.setLabelAlignment(Qt.AlignVCenter)
        self._add_row('FFTData.SPAN', 'Number of points')
        self._add_row('FFTData.INDX', 'Start Index')
        self._add_row('FFTData.MXIX', 'Maximum Index')
        self._add_row('FFTData.WIND', 'Window type', enum=True)
        self._add_row('FFTData.CDIR', 'Direction', enum=True)
        self._add_row('FFTData.ASUB', 'Subtract Avg', enum=True)

    def _add_row(self, pv, label, enum=False):
        CLASS_ = PyDMECB if enum else PyDMSpinbox
        le = self.create_wid(CLASS_, pv)
        if not enum:
            le.showStepExponent = False
        lb = QLabel(label)
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb, le)


class MultiPassConfig(QGroupBox, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        QGroupBox.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        self.setTitle('Acquisition Configurations')
        hl = QHBoxLayout(self)
        gb = QGroupBox(self)
        fl = QFormLayout(gb)
        fl.setLabelAlignment(Qt.AlignVCenter)
        ecb = self.create_wid(PyDMECB, propty='ACQBPMMode-Sel',
                              use_data_prefix=False)
        fl.addRow('BPM Mode Sel', ecb)
        self.acq_bpm_mode = ecb
        sb = self.create_wid(PyDMSpinbox, propty='Shots-SP')
        sb.showStepExponent = False
        fl.addRow('# shots', sb)
        sb = self.create_wid(PyDMSpinbox, propty='TriggerHwDly-SP')
        sb.showStepExponent = False
        fl.addRow('Delay [us]', sb)
        sb = self.create_wid(PyDMSpinbox, propty='SamplesPre-SP')
        sb.showStepExponent = False
        fl.addRow('# Samples Pre', sb)
        sb = self.create_wid(PyDMSpinbox, propty='SamplesPost-SP')
        sb.showStepExponent = False
        fl.addRow('# Samples Pos', sb)
        ecb = self.create_wid(PyDMECB, propty='TriggerRep-Sel')
        fl.addRow('Repetitive', ecb)
        sb = self.create_wid(PyDMSpinbox, propty='UpdateTime-SP')
        sb.showStepExponent = False
        fl.addRow('Update Interval', sb)
        gl = QGridLayout()
        pb1 = self.create_wid(PyDMPB, propty='TriggerEvent-Sel')
        pb1.pressValue = 0
        pb1.setText('Start')
        gl.addWidget(pb1, 0, 0)
        pb2 = self.create_wid(PyDMPB, propty='TriggerEvent-Sel')
        pb2.pressValue = 1
        pb2.setText('Stop')
        gl.addWidget(pb2, 0, 1)
        pb1 = self.create_wid(PyDMPB, propty='TriggerEvent-Sel')
        pb1.pressValue = 2
        pb1.setText('Abort')
        gl.addWidget(pb1, 1, 0)
        pb2 = self.create_wid(PyDMPB, propty='TriggerEvent-Sel')
        pb2.pressValue = 3
        pb2.setText('Reset')
        gl.addWidget(pb2, 1, 1)
        lb = QLabel('COMMANDS', self)
        lb.setAlignment(Qt.AlignVCenter)
        fl.addRow(lb, gl)
        lb = self.create_wid(PyDMLabel, propty='Status-Sts', write=False)
        fl.addRow('Status', lb)
        hl.addWidget(gb)

        gb = QGroupBox(self)
        fl = QFormLayout(gb)
        ecb = self.create_wid(PyDMECB, propty='Channel-Sel')
        self.acq_channel = ecb
        lb = QLabel('Rate', self)
        fl.addRow(lb, ecb)
        self.acq_bpm_mode.currentIndexChanged[str].connect(
                self.set_widgets_visibility([lb, ecb], 'multi'))

        ecb_trig_type = self.create_wid(PyDMECB, propty='Trigger-Sel')
        fl.addRow('Trigger Type', ecb_trig_type)

        lb1 = QLabel('External Trigger Configurations')
        f = lb1.font()
        f.setBold(True)
        lb1.setFont(f)
        lb1.setAlignment(Qt.AlignHCenter)
        fl.addRow(lb1)
        ecb1 = self.create_wid(PyDMECB, propty='TriggerExternalChan-Sel')
        lb2 = QLabel('External Trigger')
        fl.addRow(lb2, ecb1)
        ecb_trig_type.currentIndexChanged[str].connect(
                self.set_widgets_visibility([lb1, lb2, ecb1], 'external'))

        lb = QLabel('Auto Trigger Configurations')
        lb.setFont(f)
        wids = [lb]
        lb.setAlignment(Qt.AlignHCenter)
        fl.addRow(lb)
        ecb = self.create_wid(PyDMECB, propty='TriggerDataChan-Sel')
        wids.append(ecb)
        lb = QLabel('Type of Rate as Trigger', self)
        wids.append(lb)
        fl.addRow(lb, ecb)
        ecb = self.create_wid(PyDMECB, propty='TriggerDataSel-Sel')
        wids.append(ecb)
        lb = QLabel('Channel', self)
        wids.append(lb)
        fl.addRow(lb, ecb)
        ecb = self.create_wid(PyDMECB, propty='TriggerDataPol-Sel')
        wids.append(ecb)
        lb = QLabel('Slope', self)
        wids.append(lb)
        fl.addRow(lb, ecb)
        sb = self.create_wid(PyDMSpinbox, propty='TriggerDataThres-SP')
        sb.showStepExponent = False
        wids.append(sb)
        lb = QLabel('Threshold', self)
        wids.append(lb)
        fl.addRow(lb, sb)
        sb = self.create_wid(PyDMSpinbox, propty='TriggerDataHyst-SP')
        sb.showStepExponent = False
        wids.append(sb)
        lb = QLabel('Hysteresis', self)
        wids.append(lb)
        fl.addRow(lb, sb)
        ecb_trig_type.currentIndexChanged[str].connect(
                self.set_widgets_visibility(wids, 'data'))
        hl.addWidget(gb)

    def set_widgets_visibility(self, wids, selec):
        def toggle(text):
            bo_ = text.lower().startswith(selec)
            for wid in wids:
                wid.setVisible(bo_)
        return toggle


class PostMortemWid(QWidget, _WidgetsCreator):

    def __init__(self, parent=None, **kwargs):
        QWidget.__init__(self, parent=parent)
        _WidgetsCreator.__init__(self, **kwargs)
        vl = QVBoxLayout(self)
        if self.isSingleBPM():
            CL = MultiPassDataSingleBPM
        else:
            CL = MultiPassDataMultiBPM
        data = CL(self, acq_type='ACQ_PM', **kwargs)
        config = MultiPassConfig(self, data_prefix='ACQ_PM', **kwargs)
        vl.addWidget(data)
        vl.addWidget(config)
        config.acq_channel.currentIndexChanged[str].connect(
                                    data.control_visibility_buttons)


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    util.set_style(app)
    bpm_list = ('SI-01M1:DI-BPM:', 'SI-01M2:DI-BPM:')
    wind = BPMsInterface(prefix='ca://'+vaca_prefix, bpm_list=bpm_list)
    wind.show()
    sys.exit(app.exec_())
