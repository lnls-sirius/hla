import sys
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QRadioButton,
                             QGridLayout, QTabWidget, QStackedWidget, QLabel,
                             QGroupBox, QFormLayout, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from pydm.widgets import (PyDMWaveformPlot, PyDMTimePlot, PyDMLineEdit,
                          PyDMSpinbox, PyDMLabel, PyDMCheckbox)
from pydm.widgets import PyDMPushButton as PyDMPB
from pydm.widgets import PyDMEnumComboBox as PyDMECB
from siriuspy.envars import vaca_prefix
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, SiriusDialog
from siriushla import util


class SingleBPM(SiriusMainWindow):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        wid = OperationModes(parent=self, prefix=prefix)
        self.setCentralWidget(wid)
        self.setWindowTitle(prefix)
        self.resize(1500, 1800)
        self.configure_menuBar()

    def configure_menuBar(self):
        menubar = self.menuBar()
        cb = PyDMCheckbox(self, init_channel=self.prefix+'OpMode-Sel')
        cb.setVisible(False)

        calibr = menubar.addAction('&Calibration')
        calibr.triggered.connect(self.open_calibration_window)

    def open_calibration_window(self):
        app = SiriusApplication.instance()
        app.open_window(CalibrationWindow, parent=self, prefix=self.prefix)


class CalibrationWindow(SiriusDialog):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        self.fl = QFormLayout(self)
        self.fl.setLabelAlignment(Qt.AlignVCenter)
        lb = QLabel('Acquisition Mode')
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb)
        self._add_row('ACQBPMMode-Sel', 'ACQBPMMode-Sts', 'Offset PosQ')
        lb = QLabel('Offset Parameters')
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb)
        self._add_row('PosQOffset-SP', 'PosQOffset-RB', 'Offset PosQ')
        self._add_row('PosXOffset-SP', 'PosXOffset-RB', 'Offset PosX')
        self._add_row('PosYOffset-SP', 'PosYOffset-RB', 'Offset PosY')
        lb = QLabel('Gain Parameters')
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb)
        self._add_row('PosKq-SP', 'PosKq-RB', 'Gain PosQ')
        self._add_row('PosKsum-SP', 'PosKsum-RB', 'Gain Sum')
        self._add_row('PosKx-SP', 'PosKx-RB', 'Gain PosX')
        self._add_row('PosKy-SP', 'PosKy-RB', 'Gain PosY')
        lb = QLabel('Informations')
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb)
        self._add_row('INFOHarmonicNumber-SP', 'INFOHarmonicNumber-RB',
                      'Harmonic Number')
        self._add_row('INFOFOFBRate-SP', 'INFOFOFBRate-RB', 'FOFB Rate')
        self._add_row('INFOMONITRate-SP', 'INFOMONITRate-RB', 'Monitor Rate')
        self._add_row('INFOTBTRate-SP', 'INFOTBTRate-RB', 'TbT Rate')

    def _add_row(self, pv1, pv2, label):
        CLASS_ = PyDMLineEdit if pv1.endswith('-SP') else PyDMECB
        le = CLASS_(self, init_channel=self.prefix+pv1)
        lb = PyDMLabel(self, init_channel=self.prefix+pv2)
        hl = QHBoxLayout()
        hl.addWidget(le)
        hl.addWidget(lb)
        lb2 = QLabel(label)
        lb2.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb2, hl)


class OperationModes(QTabWidget):
    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        wid = ContinuousMonit(parent=self, prefix=prefix)
        self.addTab(wid, 'Continuous Monitoring')
        wid = TrigAcquisitions(parent=self, prefix=prefix)
        self.addTab(wid, 'Triggered Acquisitions')
        wid = PostMortemWid(parent=self, prefix=prefix)
        self.addTab(wid, 'Post Mortem')


class ContinuousMonit(QWidget):
    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        gl = QGridLayout(self)
        prps = {}
        prps['colors'] = ['blue', ]
        prps['init_channels'] = [self.prefix+'PosX-Mon', ]
        prps['label'] = 'Position X [nm]'
        plotPosX = self.createPlot(**prps)
        gl.addWidget(plotPosX, 0, 0, 1, 1)

        prps['colors'] = ['red', ]
        prps['init_channels'] = [self.prefix+'PosY-Mon', ]
        prps['label'] = 'Position Y [nm]'
        plotPosY = self.createPlot(**prps)
        gl.addWidget(plotPosY, 1, 0, 1, 1)

        # prps['colors'] = ['black', ]
        # prps['init_channels'] = [self.prefix+'Sum-Mon', ]
        # prps['label'] = 'Sum'
        # plotPosS = self.createPlot(**prps)
        # gl.addWidget(plotPosS, 2, 0, 1, 1)

        prps['colors'] = ['green', ]
        prps['init_channels'] = [self.prefix+'PosQ-Mon', ]
        prps['label'] = 'Skew'
        plotPosQ = self.createPlot(**prps)
        gl.addWidget(plotPosQ, 2, 0, 1, 1)

        prps['colors'] = ['blue', 'red', 'black', 'green']
        prps['init_channels'] = [self.prefix+'AmplA-Mon',
                                 self.prefix+'AmplB-Mon',
                                 self.prefix+'AmplC-Mon',
                                 self.prefix+'AmplD-Mon']
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


class TrigAcquisitions(QWidget):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        vl = QVBoxLayout(self)
        stack = QStackedWidget(parent=self)
        acq_multi_pass = MultiPassData(
                                    parent=self, prefix=prefix, acq_type='ACQ')
        stack.addWidget(acq_multi_pass)
        acq_single_pass = SinglePassData(
                                    parent=self, prefix=prefix)
        stack.addWidget(acq_single_pass)
        self.stack = stack
        vl.addWidget(stack)
        config = MultiPassConfig(
                                parent=self, prefix=prefix, acq_type='ACQ')
        config.acq_channel.currentIndexChanged[str].connect(
                                    acq_multi_pass.control_visibility_buttons)
        config.acq_bpm_mode.currentIndexChanged[str].connect(
                                    self.toggle_multi_single)
        vl.addWidget(config)

    def toggle_multi_single(self, text):
        if text.lower().startswith('single'):
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)


class MultiPassData(QWidget):
    _PROPS = ('A', 'B', 'C', 'D', 'X', 'Y', 'Sum', 'Q')
    _COLORS = ('blue', 'red', 'black', 'green')

    def __init__(self, parent=None, prefix='', acq_type='ACQ'):
        self.prefix = prefix
        self.acq_type = acq_type
        self.data_prefix = 'GEN_' if acq_type == 'ACQ' else 'PM_'
        super().__init__(parent=parent)
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
        pv_prefix = self.prefix + self.data_prefix + prop
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
        pb.clicked.connect(self.open_fft_config_window(wid, pv_prefix))
        vl.addWidget(pb)
        gl.addItem(vl, 1, 0)

        return wid

    def open_fft_config_window(self, wid, pv_prefix):
        app = SiriusApplication.instance()

        def open_window():
            app.open_window(FFTConfigs, parent=wid, prefix=pv_prefix)
        return open_window


class SinglePassData(QWidget):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        vl = QVBoxLayout(self)

        plot_prop = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[self.prefix + 'SP_AArrayData-Mon',
                             self.prefix + 'SP_BArrayData-Mon',
                             self.prefix + 'SP_CArrayData-Mon',
                             self.prefix + 'SP_DArrayData-Mon'],
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
                        init_y_channels=[self.prefix + 'SPPosX-Mon',
                                         self.prefix + 'SPPosY-Mon'],
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
                    init_y_channels=[self.prefix + 'SPSum-Mon', ],
                    background='w')
        plotSum.timeSpan = 60
        plotSum._curves[0].color = 'black'
        plotSum._curves[0].lineWidth = 2
        hl.addWidget(plotSum)
        plotQ = PyDMTimePlot(
                    self,
                    init_y_channels=[self.prefix + 'SPPosQ-Mon', ],
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
            init_y_channels=[self.prefix + 'SPAmplA-Mon',
                             self.prefix + 'SPAmplB-Mon',
                             self.prefix + 'SPAmplC-Mon',
                             self.prefix + 'SPAmplD-Mon'],
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
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPPosX-Mon')
        fl.addRow('PosX', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPPosY-Mon')
        fl.addRow('PosY', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPSum-Mon')
        fl.addRow('Sum', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPPosQ-Mon')
        fl.addRow('PosQ', lb)
        hl.addWidget(gb)
        gb = QGroupBox('Processed Antennas', self)
        fl = QFormLayout(gb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPAmplA-Mon')
        fl.addRow('AmplA', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPAmplB-Mon')
        fl.addRow('AmplB', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPAmplC-Mon')
        fl.addRow('AmplC', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPAmplD-Mon')
        fl.addRow('AmplD', lb)
        hl.addWidget(gb)

    def toggle_button(self, i):
        def toggle(tog):
            if tog:
                self.stack.setCurrentIndex(i)
        return toggle


class FFTConfigs(SiriusDialog):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=None)
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
        le = CLASS_(self, init_channel=self.prefix+pv)
        if not enum:
            le.showStepExponent = False
        lb = QLabel(label)
        lb.setAlignment(Qt.AlignCenter)
        self.fl.addRow(lb, le)


class MultiPassConfig(QGroupBox):

    def __init__(self, parent=None, prefix='', acq_type='ACQ'):
        self.prefix = prefix
        self.data_prefix = acq_type
        pv_pref = prefix + acq_type
        super().__init__(parent=parent)
        self.setTitle('Acquisition Configurations')
        hl = QHBoxLayout(self)
        gb = QGroupBox(self)
        fl = QFormLayout(gb)
        fl.setLabelAlignment(Qt.AlignVCenter)
        ecb = PyDMECB(self, init_channel=prefix+'ACQBPMMode-Sel')
        fl.addRow('BPM Mode Sel', ecb)
        self.acq_bpm_mode = ecb
        # lb = PyDMLabel(self, init_channel=prefix+'ACQBPMMode-Sts')
        # fl.addRow('BPM Mode Sts', lb)
        sb = PyDMSpinbox(self, init_channel=pv_pref+'Shots-SP')
        sb.showStepExponent = False
        fl.addRow('# shots', sb)
        sb = PyDMSpinbox(self, init_channel=pv_pref+'TriggerHwDly-SP')
        sb.showStepExponent = False
        fl.addRow('Delay [us]', sb)
        sb = PyDMSpinbox(self, init_channel=pv_pref+'SamplesPre-SP')
        sb.showStepExponent = False
        fl.addRow('# Samples Pre', sb)
        sb = PyDMSpinbox(self, init_channel=pv_pref+'SamplesPost-SP')
        sb.showStepExponent = False
        fl.addRow('# Samples Pos', sb)
        ecb = PyDMECB(self, init_channel=pv_pref+'TriggerRep-Sel')
        fl.addRow('Repetitive', ecb)
        sb = PyDMSpinbox(self, init_channel=pv_pref+'UpdateTime-SP')
        sb.showStepExponent = False
        fl.addRow('Update Interval', sb)
        gl = QGridLayout()
        pb1 = PyDMPB(self, init_channel=pv_pref+'TriggerEvent-Sel')
        pb1.pressValue = 0
        pb1.setText('Start')
        gl.addWidget(pb1, 0, 0)
        pb2 = PyDMPB(self, init_channel=pv_pref+'TriggerEvent-Sel')
        pb2.pressValue = 1
        pb2.setText('Stop')
        gl.addWidget(pb2, 0, 1)
        pb1 = PyDMPB(self, init_channel=pv_pref+'TriggerEvent-Sel')
        pb1.pressValue = 2
        pb1.setText('Abort')
        gl.addWidget(pb1, 1, 0)
        pb2 = PyDMPB(self, init_channel=pv_pref+'TriggerEvent-Sel')
        pb2.pressValue = 3
        pb2.setText('Reset')
        gl.addWidget(pb2, 1, 1)
        fl.addRow('Events', gl)
        lb = PyDMLabel(self, init_channel=pv_pref+'Status-Sts')
        fl.addRow('Status', lb)
        hl.addWidget(gb)

        gb = QGroupBox(self)
        fl = QFormLayout(gb)
        ecb = PyDMECB(self, init_channel=pv_pref+'Channel-Sel')
        self.acq_channel = ecb
        lb = QLabel('Rate', self)
        fl.addRow(lb, ecb)
        self.acq_bpm_mode.currentIndexChanged[str].connect(
                            self.set_widgets_visibility([lb, ecb], 'multi'))
        ecb_trig_type = PyDMECB(self, init_channel=pv_pref+'Trigger-Sel')
        fl.addRow('Trigger Type', ecb_trig_type)
        lb1 = QLabel('External Trigger Configurations')
        lb1.setAlignment(Qt.AlignHCenter)
        fl.addRow(lb1)
        ecb1 = PyDMECB(self, init_channel=pv_pref+'TriggerExternalChan-Sel')
        lb2 = QLabel('External Trigger')
        fl.addRow(lb2, ecb1)
        ecb_trig_type.currentIndexChanged[str].connect(
                    self.set_widgets_visibility([lb1, lb2, ecb1], 'external'))
        lb = QLabel('Auto Trigger Configurations')
        wids = [lb]
        lb.setAlignment(Qt.AlignHCenter)
        fl.addRow(lb)
        ecb = PyDMECB(self, init_channel=pv_pref+'TriggerDataChan-Sel')
        wids.append(ecb)
        lb = QLabel('Type of Rate as Trigger', self)
        wids.append(lb)
        fl.addRow(lb, ecb)
        ecb = PyDMECB(self, init_channel=pv_pref+'TriggerDataSel-Sel')
        wids.append(ecb)
        lb = QLabel('Channel', self)
        wids.append(lb)
        fl.addRow(lb, ecb)
        ecb = PyDMECB(self, init_channel=pv_pref+'TriggerDataPol-Sel')
        wids.append(ecb)
        lb = QLabel('Slope', self)
        wids.append(lb)
        fl.addRow(lb, ecb)
        sb = PyDMSpinbox(self,
                         init_channel=pv_pref+'TriggerDataThres-SP')
        sb.showStepExponent = False
        wids.append(sb)
        lb = QLabel('Threshold', self)
        wids.append(lb)
        fl.addRow(lb, sb)
        sb = PyDMSpinbox(self,
                         init_channel=pv_pref+'TriggerDataHyst-SP')
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


class PostMortemWid(QWidget):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        vl = QVBoxLayout(self)
        data = MultiPassData(self, prefix=prefix, acq_type='ACQ_PM')
        config = MultiPassConfig(self, prefix=prefix, acq_type='ACQ_PM')
        vl.addWidget(data)
        vl.addWidget(config)
        config.acq_channel.currentIndexChanged[str].connect(
                                    data.control_visibility_buttons)


if __name__ == '__main__':
    app = SiriusApplication()
    util.set_style(app)
    wind = SingleBPM(prefix='ca://'+vaca_prefix + 'SI-01M1:DI-BPM:')
    wind.show()
    sys.exit(app.exec_())
