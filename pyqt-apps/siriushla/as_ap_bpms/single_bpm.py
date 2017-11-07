import sys
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                             QGridLayout, QTabWidget, QStackedWidget, QDialog,
                             QRadioButton, QGroupBox, QFormLayout, QLabel)
from PyQt5.QtCore import Qt
from pydm.widgets import (PyDMWaveformPlot, PyDMTimePlot, PyDMLineEdit,
                          PyDMSpinbox, PyDMLabel, PyDMCheckbox)
from pydm.widgets import PyDMPushButton as PyDMPB
from pydm.widgets import PyDMEnumComboBox as PyDMECB
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, SiriusDialog
from siriuspy.envars import vaca_prefix


class SingleBPM(SiriusMainWindow):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        wid = OperationModes(parent=self, prefix=prefix)
        self.setCentralWidget(wid)
        self.setWindowTitle(prefix)
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
        plotPosX = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'PosX-Mon'],
            background='w')
        plotPosX.timeSpan = 60
        plotPosX._curves[0].color = 'blue'
        plotPosX._curves[0].lineWidth = 2
        gl.addWidget(plotPosX, 0, 0, 1, 2)

        plotPosY = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'PosY-Mon'],
            background='w')
        plotPosY.timeSpan = 60
        plotPosY._curves[0].color = 'red'
        plotPosY._curves[0].lineWidth = 2
        gl.addWidget(plotPosY, 1, 0, 1, 2)

        plotPosS = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'Sum-Mon'],
            background='w')
        plotPosS.timeSpan = 60
        plotPosS._curves[0].color = 'black'
        plotPosS._curves[0].lineWidth = 2
        gl.addWidget(plotPosS, 2, 0, 1, 1)

        plotPosQ = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'PosQ-Mon'],
            background='w')
        plotPosQ.timeSpan = 60
        plotPosQ._curves[0].color = 'green'
        plotPosQ._curves[0].lineWidth = 2
        gl.addWidget(plotPosQ, 2, 1, 1, 1)

        plotAmps = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'AmplA-Mon',
                             self.prefix+'AmplB-Mon',
                             self.prefix+'AmplC-Mon',
                             self.prefix+'AmplD-Mon'],
            background='w')
        plotAmps.timeSpan = 60
        plotAmps._curves[0].color = 'blue'
        plotAmps._curves[0].lineWidth = 2
        plotAmps._curves[1].color = 'green'
        plotAmps._curves[0].lineWidth = 2
        plotAmps._curves[2].color = 'red'
        plotAmps._curves[0].lineWidth = 2
        plotAmps._curves[3].color = 'black'
        plotAmps._curves[0].lineWidth = 2
        gl.addWidget(plotAmps, 3, 0, 1, 2)


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
        bo = text.startswith('adc')
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
        gl.addWidget(gb, 1, 0)

        return wid


class SinglePassData(QWidget):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        gl = QGridLayout(self)

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
        gl.addWidget(plot_prop, 0, 0)

        vl = QVBoxLayout()
        self.stack = QStackedWidget(self)
        plotXY = PyDMTimePlot(
                        self, init_y_channels=[self.prefix + 'SPPosX-Mon',
                                               self.prefix + 'SPPosY-Mon'])
        plotXY.timeSpan = 60
        plotXY._curves[0].color = 'blue'
        plotXY._curves[1].color = 'red'
        plotXY._curves[0].lineWidth = 2
        plotXY._curves[1].lineWidth = 2
        gl.addWidget(plot_prop, 0, 0)
        self.stack.addWidget(plotXY)
        plotSum = PyDMTimePlot(
                    self, init_y_channels=[self.prefix + 'SPSum-Mon', ])
        plotSum.timeSpan = 60
        plotSum._curves[0].color = 'black'
        plotSum._curves[0].lineWidth = 2
        self.stack.addWidget(plotSum)
        plotSum = PyDMTimePlot(
                    self, init_y_channels=[self.prefix + 'SPPosQ-Mon', ])
        plotSum.timeSpan = 60
        plotSum._curves[0].color = 'black'
        plotSum._curves[0].lineWidth = 2
        self.stack.addWidget(plotSum)

        hl = QHBoxLayout()
        for i, pos in enumerate(['X and Y', 'Sum', 'Q']):
            rb = QRadioButton(pos, self)
            rb.toggled.connect(self.toggle_button(i))
            if not i:
                rb.setChecked(True)
            hl.addWidget(rb)
        vl.addItem(hl)

        gb = QGroupBox('Positions', self)
        fl = QFormLayout(gb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPPosX-Mon')
        fl.addRow('PosX', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPPosY-Mon')
        fl.addRow('PosY', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPSum-Mon')
        fl.addRow('PosS', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SPPosQ-Mon')
        fl.addRow('PosQ', lb)
        gl.addWidget(gb, 2, 0)
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
        gl.addWidget(gb, 2, 1)

    def toggle_button(self, i):
        def toggle(tog):
            if tog:
                self.stack.setCurrentIndex(i)
        return toggle


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
        ecb = PyDMECB(self, init_channel=pv_pref+'BPMMode-Sel')
        fl.addRow('BPM Mode Sel', ecb)
        self.acq_bpm_mode = ecb
        lb = PyDMLabel(self, init_channel=pv_pref+'BPMMode-Sts')
        fl.addRow('BPM Mode Sts', lb)
        ecb = PyDMECB(self, init_channel=pv_pref+'Channel-Sel')
        self.acq_channel = ecb
        fl.addRow('Rate', ecb)
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
        ecb = PyDMECB(self, init_channel=pv_pref+'Trigger-Sel')
        fl.addRow('Trigger Type', ecb)
        ecb = PyDMECB(self, init_channel=pv_pref+'TriggerRep-Sel')
        fl.addRow('Repetitive', ecb)
        sb = PyDMSpinbox(self, init_channel=pv_pref+'UpdateTime-SP')
        sb.showStepExponent = False
        fl.addRow('Update Interval', sb)
        pb1 = PyDMPB(self, init_channel=pv_pref+'TriggerEvent-Sel')
        pb1.pressValue = 0
        pb1.setText('Start')
        pb2 = PyDMPB(self, init_channel=pv_pref+'TriggerEvent-Sel')
        pb2.pressValue = 1
        pb2.setText('Stop')
        fl.addRow(pb1, pb2)
        pb1 = PyDMPB(self, init_channel=pv_pref+'TriggerEvent-Sel')
        pb1.pressValue = 2
        pb1.setText('Abort')
        pb2 = PyDMPB(self, init_channel=pv_pref+'TriggerEvent-Sel')
        pb2.pressValue = 3
        pb2.setText('Reset')
        fl.addRow(pb1, pb2)
        lb = PyDMLabel(self, init_channel=pv_pref+'Status-Sts')
        fl.addRow('Status', lb)
        hl.addWidget(gb)

        gb = QGroupBox(self)
        fl = QFormLayout(gb)
        ecb = PyDMECB(self, init_channel=pv_pref+'TriggerExternalChan-Sel')
        fl.addRow('External Trigger', ecb)
        lb = QLabel('Auto Trigger Configurations')
        lb.setAlignment(Qt.AlignHCenter)
        fl.addRow(lb)
        ecb = PyDMECB(self, init_channel=pv_pref+'TriggerDataChan-Sel')
        fl.addRow('Type of Rate as Trigger', ecb)
        ecb = PyDMECB(self, init_channel=pv_pref+'TriggerDataSel-Sel')
        fl.addRow('Channel', ecb)
        ecb = PyDMECB(self, init_channel=pv_pref+'TriggerDataPol-Sel')
        fl.addRow('Slope', ecb)
        sb = PyDMSpinbox(self,
                         init_channel=pv_pref+'TriggerDataThres-SP')
        fl.addRow('Threshold', sb)
        sb = PyDMSpinbox(self,
                         init_channel=pv_pref+'TriggerDataHyst-SP')
        fl.addRow('Hysteresis', sb)
        hl.addWidget(gb)


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
    wind = SingleBPM(prefix='ca://'+vaca_prefix + 'SI-01M1:DI-BPM:')
    wind.show()
    sys.exit(app.exec_())
