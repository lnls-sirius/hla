import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QGridLayout, QTabWidget, QStackedWidget,
                             QRadioButton, QGroupBox, QFormLayout, QLabel)
from PyQt5.QtCore import Qt
from pydm.widgets.waveformplot import PyDMWaveformPlot
from pydm.widgets.timeplot import PyDMTimePlot
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.spinbox import PyDMSpinbox
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.application import PyDMApplication
from siriuspy.envars import vaca_prefix


class SingleBPM(QMainWindow):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        wid = OperationModes(parent=self, prefix=prefix)
        self.setCentralWidget(wid)
        self.setWindowTitle(prefix)


class OperationModes(QTabWidget):
    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        wid = SlowModeWid(parent=self, prefix=prefix)
        self.addTab(wid, 'Continuous Mode')
        wid = AcquisitionModeWid(parent=self, prefix=prefix)
        self.addTab(wid, 'Triggered Acquisitions')
        wid = SinglePassModeWid(parent=self, prefix=prefix)
        self.addTab(wid, 'Single Pass Mode')


class SlowModeWid(QWidget):
    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        gl = QGridLayout(self)
        plotPosX = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'PosX-Mon'],
            background='w')
        gl.addWidget(plotPosX, 0, 0, 1, 2)

        plotPosY = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'PosY-Mon'],
            background='w')
        gl.addWidget(plotPosY, 1, 0, 1, 2)

        plotPosS = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'PosS-Mon'],
            background='w')
        gl.addWidget(plotPosS, 2, 0, 1, 1)

        plotPosQ = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'PosQ-Mon'],
            background='w')
        gl.addWidget(plotPosQ, 2, 1, 1, 1)

        plotAmps = PyDMTimePlot(
            parent=self,
            init_y_channels=[self.prefix+'AmpA-Mon',
                             self.prefix+'AmpB-Mon',
                             self.prefix+'AmpC-Mon',
                             self.prefix+'AmpD-Mon'],
            background='w')
        gl.addWidget(plotAmps, 3, 0, 1, 2)


class AcquisitionModeWid(QWidget):
    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        vl = QVBoxLayout(self)
        stack = QTabWidget(parent=self)
        acqADC = AcquisitionTypeWid(parent=self,
                                    prefix=prefix,
                                    acq_type='ADC')
        stack.addTab(acqADC, 'ADC')
        acqTbT = AcquisitionTypeWid(parent=self,
                                    prefix=prefix,
                                    acq_type='TbT')
        stack.addTab(acqTbT, 'TbT')
        acqFOFB = AcquisitionTypeWid(parent=self,
                                     prefix=prefix,
                                     acq_type='FOFB')
        stack.addTab(acqFOFB, 'FOFB')
        vl.addWidget(stack)
        config = AcquisitionConfigWid(parent=self, prefix=prefix)
        vl.addWidget(config)


class AcquisitionTypeWid(QWidget):
    _processed_props = ('PosX', 'PosY', 'PosS', 'PosQ',
                        'AmpA', 'AmpB', 'AmpC', 'AmpD')
    _raw_props = ('AntA', 'AntB', 'AntC', 'AntD')
    _type_props = {'TbT': _processed_props,
                   'FOFB': _processed_props,
                   'ADC': _raw_props}

    def __init__(self, parent=None, prefix='', acq_type='TbT'):
        self.prefix = prefix
        self.acq_type = acq_type
        super().__init__(parent=parent)
        vl = QVBoxLayout(self)
        stack = QStackedWidget(self)
        self.stack = stack
        vl.addWidget(stack)

        hl = QHBoxLayout()
        for i, pos in enumerate(self._type_props[acq_type]):
            posWid = self.create_prop_widget(pos)
            stack.addWidget(posWid)
            rb = QRadioButton(pos, self)
            rb.toggled.connect(self.toggle_button(i))
            if not i:
                rb.setChecked(True)
            hl.addWidget(rb)
        vl.addItem(hl)

    def toggle_button(self, i):
        def toggle(tog):
            if tog:
                self.stack.setCurrentIndex(i)
        return toggle

    def create_prop_widget(self, prop):
        pv_prefix = self.prefix + self.acq_type + prop
        wid = QWidget(self)
        gl = QGridLayout(wid)
        plot_prop = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[pv_prefix + '-Mon'],
            background='w')
        gl.addWidget(plot_prop, 0, 0)

        fft_amp = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[pv_prefix + 'FFT.AMP'],
            init_x_channels=[pv_prefix + 'FFT.FREQ'],
            background='w')
        gl.addWidget(fft_amp, 0, 1)

        fft_pha = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[pv_prefix + 'FFT.PHA'],
            init_x_channels=[pv_prefix + 'FFT.FREQ'],
            background='w')
        gl.addWidget(fft_pha, 1, 1)

        gb = QGroupBox('Statistics', wid)
        fl = QFormLayout(gb)
        fl.addRow('Property', QLabel(prop))
        fl.addRow('FFT # Points',
                  PyDMLineEdit(gb, init_channel=pv_prefix + 'FFT.SPAN'))
        fl.addRow('Maximum', PyDMLabel(gb, init_channel=pv_prefix + 'Max'))
        fl.addRow('Minimum', PyDMLabel(gb, init_channel=pv_prefix + 'Min'))
        fl.addRow('Average', PyDMLabel(gb, init_channel=pv_prefix + 'Avg'))
        fl.addRow('Deviation', PyDMLabel(gb, init_channel=pv_prefix + 'Std'))
        gl.addWidget(gb, 1, 0)

        return wid


class AcquisitionConfigWid(QGroupBox):
    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        self.setTitle('Acquisition Configurations')
        hl = QHBoxLayout(self)
        gb = QGroupBox(self)
        fl = QFormLayout(gb)
        ecb = PyDMECB(self, init_channel=self.prefix+'AcqRate-Sel')
        fl.addRow('Rate', ecb)
        sb = PyDMSpinbox(self, init_channel=self.prefix+'AcqNrShots-SP')
        fl.addRow('# shots', sb)
        sb = PyDMSpinbox(self, init_channel=self.prefix+'AcqDelay-SP')
        fl.addRow('Delay [us]', sb)
        sb = PyDMSpinbox(self, init_channel=self.prefix+'AcqNrSmplsPre-SP')
        fl.addRow('# Samples Pre', sb)
        sb = PyDMSpinbox(self, init_channel=self.prefix+'AcqNrSmplsPos-SP')
        fl.addRow('# Samples Pos', sb)
        ecb = PyDMECB(self, init_channel=self.prefix+'AcqTrigType-Sel')
        fl.addRow('Trigger Type', ecb)
        ecb = PyDMECB(self, init_channel=self.prefix+'AcqTrigRep-Sel')
        fl.addRow('Rearm Trigger', ecb)
        pb1 = PyDMPushButton(self, init_channel=self.prefix+'AcqStart-Cmd')
        pb1.setText('Start')
        pb2 = PyDMPushButton(self, init_channel=self.prefix+'AcqStop-Cmd')
        pb2.setText('Stop')
        fl.addRow(pb1, pb2)
        lb = PyDMLabel(self, init_channel=self.prefix+'AcqState-Sts')
        fl.addRow('Status', lb)
        hl.addWidget(gb)

        gb = QGroupBox(self)
        fl = QFormLayout(gb)
        ecb = PyDMECB(self, init_channel=self.prefix+'AcqTrigExt-Sel')
        fl.addRow('External Trigger', ecb)
        lb = QLabel('Auto Trigger Configurations')
        lb.setAlignment(Qt.AlignHCenter)
        fl.addRow(lb)
        ecb = PyDMECB(self, init_channel=self.prefix+'AcqTrigAuto-Sel')
        fl.addRow('Type of Rate as Trigger', ecb)
        ecb = PyDMECB(self, init_channel=self.prefix+'AcqTrigAutoCh-Sel')
        fl.addRow('Channel', ecb)
        ecb = PyDMECB(self, init_channel=self.prefix+'AcqTrigAutoSlope-Sel')
        fl.addRow('Slope', ecb)
        sb = PyDMSpinbox(self, init_channel=self.prefix+'AcqTrigAutoThres-SP')
        fl.addRow('Threshold', sb)
        sb = PyDMSpinbox(self, init_channel=self.prefix+'AcqTrigAutoHyst-SP')
        fl.addRow('Hysteresis', sb)
        hl.addWidget(gb)


class SinglePassModeWid(QWidget):
    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        vl = QVBoxLayout(self)
        vl.addWidget(SinglePassDataWid(self, prefix=prefix))
        vl.addWidget(SinglePassConfigWid(self, prefix=prefix))


class SinglePassDataWid(QWidget):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        gl = QGridLayout(self)

        plot_prop = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[self.prefix + 'SglAntA-Mon'],
            background='w')
        gl.addWidget(plot_prop, 0, 0)

        plot_prop = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[self.prefix + 'SglAntB-Mon'],
            background='w')
        gl.addWidget(plot_prop, 0, 1)

        plot_prop = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[self.prefix + 'SglAntC-Mon'],
            background='w')
        gl.addWidget(plot_prop, 1, 0)

        plot_prop = PyDMWaveformPlot(
            parent=self,
            init_y_channels=[self.prefix + 'SglAntD-Mon'],
            background='w')
        gl.addWidget(plot_prop, 1, 1)

        gb = QGroupBox('Positions', self)
        fl = QFormLayout(gb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SglPosX-Mon')
        fl.addRow('PosX', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SglPosY-Mon')
        fl.addRow('PosY', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SglPosS-Mon')
        fl.addRow('PosS', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SglPosQ-Mon')
        fl.addRow('PosQ', lb)
        gl.addWidget(gb, 2, 0)
        gb = QGroupBox('Processed Antennas', self)
        fl = QFormLayout(gb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SglAmpA-Mon')
        fl.addRow('AmpA', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SglAmpB-Mon')
        fl.addRow('AmpB', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SglAmpC-Mon')
        fl.addRow('AmpC', lb)
        lb = PyDMLabel(gb, init_channel=self.prefix + 'SglAmpD-Mon')
        fl.addRow('AmpD', lb)
        gl.addWidget(gb, 2, 1)


class SinglePassConfigWid(QGroupBox):
    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        self.setTitle('Single Pass Measurement Configuration')
        hl = QHBoxLayout(self)
        gb = QGroupBox(self)
        fl = QFormLayout(gb)
        sb = PyDMSpinbox(self, init_channel=self.prefix+'SglDelay-SP')
        fl.addRow('Delay [us]', sb)
        ecb = PyDMECB(self, init_channel=self.prefix+'SglTrigType-Sel')
        fl.addRow('Trigger Type', ecb)
        ecb = PyDMECB(self, init_channel=self.prefix+'SglTrigExt-Sel')
        fl.addRow('External Trigger', ecb)
        pb1 = PyDMPushButton(self, init_channel=self.prefix+'SglStart-Cmd')
        pb1.setText('Start')
        pb2 = PyDMPushButton(self, init_channel=self.prefix+'SglStop-Cmd')
        pb2.setText('Stop')
        fl.addRow(pb1, pb2)
        lb = PyDMLabel(self, init_channel=self.prefix+'SglState-Sts')
        fl.addRow('Status', lb)
        hl.addWidget(gb)

        gb = QGroupBox(self)
        fl = QFormLayout(gb)
        lb = QLabel('Auto Trigger Configurations')
        lb.setAlignment(Qt.AlignHCenter)
        fl.addRow(lb)
        ecb = PyDMECB(self, init_channel=self.prefix+'SglTrigAutoCh-Sel')
        fl.addRow('Channel', ecb)
        ecb = PyDMECB(self, init_channel=self.prefix+'SglTrigAutoSlope-Sel')
        fl.addRow('Slope', ecb)
        sb = PyDMSpinbox(self, init_channel=self.prefix+'SglTrigAutoThres-SP')
        fl.addRow('Threshold', sb)
        sb = PyDMSpinbox(self, init_channel=self.prefix+'SglTrigAutoHyst-SP')
        fl.addRow('Hysteresis', sb)
        hl.addWidget(gb)

if __name__ == '__main__':
    app = PyDMApplication()
    wind = SingleBPM(prefix=vaca_prefix + 'SI-01M1:DI-BPM:')
    wind.show()
    sys.exit(app.exec_())
