from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, \
    QPushButton
from qtpy.QtCore import Qt
from pydm.widgets import PyDMSpinbox, PyDMEnumComboBox, PyDMPushButton
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import SiriusConnectionSignal
from siriushla.as_di_bpms.base import BaseWidget, GraphWave
from siriushla import util


class FFTConfig(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm='', data_prefix='ACQ',
                 position=True):
        super().__init__(
            parent=parent, prefix=prefix, bpm=bpm, data_prefix=data_prefix)
        self.position = False
        self.setupui()

    def setupui(self):
        self.fl = QFormLayout(self)
        self.fl.setLabelAlignment(Qt.AlignVCenter)
        self._add_row('FFTData-RB.SPAN', 'Number of points')
        self._add_row('FFTData-RB.INDX', 'Start Index')
        self._add_row('FFTData-RB.MXIX', 'Maximum Index')
        self._add_row('FFTData-RB.WIND', 'Window type', enum=True)
        self._add_row('FFTData-RB.CDIR', 'Direction', enum=True)
        self._add_row('FFTData-RB.ASUB', 'Subtract Avg', enum=True)

        pb = PyDMPushButton(self, label='Calculate', pressValue=1)
        self._make_connections(pb, 'FFTData-RB.PROC')
        self.fl.addRow(pb)

    def _add_row(self, pv, label, enum=False):
        CLASS = PyDMEnumComboBox if enum else PyDMSpinbox
        wid = CLASS(self)
        self._make_connections(wid, pv)
        if not enum:
            wid.showStepExponent = False
        lab = QLabel(label)
        self.fl.addRow(lab, wid)

    def _make_connections(self, wid, pv):
        if self.position:
            names = ('X', 'Y', 'Q', 'SUM')
        else:
            names = ('A', 'B', 'C', 'D')
        wid.channel = self.get_pvname(names[0]+pv)
        for name in names[1:]:
            chan = SiriusConnectionSignal(self.get_pvname(name+pv))
            wid.send_value_signal[int].connect(
                chan.send_value_signal[int].emit)
            wid.send_value_signal[float].connect(
                chan.send_value_signal[float].emit)
            chan.new_value_signal[int].connect(wid.channelValueChanged)
            chan.new_value_signal[float].connect(wid.channelValueChanged)
            self._chans.append(chan)


class FFTData(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm='', data_prefix='ACQ',
                 position=True):
        super().__init__(
            parent=parent, prefix=prefix, bpm=bpm, data_prefix=data_prefix)
        self.position = position
        self.setupui()

    def setupui(self):
        if self.position:
            text = 'Positions'
            names = ('X', 'Y', 'Q', 'SUM')
            colors = ('blue', 'red', 'green', 'black')
        else:
            text = 'Antennas'
            names = ('A', 'B', 'C', 'D')
            colors = ('blue', 'red', 'green', 'magenta')

        vbl = QVBoxLayout(self)

        graph = GraphWave(
            self, prefix=self.prefix, bpm=self.bpm,
            data_prefix=self.data_prefix)
        labsty = {'font-size': '20pt'}
        graph.setLabel('left', text='Amplitude', units='a.u.', **labsty)
        graph.setLabel('bottom', text='Frequency', units='Hz', **labsty)
        for name, cor in zip(names, colors):
            opts = dict(
                y_channel=self.get_pvname(name+'FFTData-RB.AMP'),
                x_channel=self.get_pvname(name+'FFTFreq-RB.AVAL'),
                name=text[:3]+name,
                color=cor,
                lineStyle=1,
                lineWidth=3)
            graph.addChannel(**opts)
            print(self.get_pvname(name+'FFTData-RB.AMP'))
        vbl.addWidget(graph)

        graph = GraphWave(
            self, prefix=self.prefix, bpm=self.bpm,
            data_prefix=self.data_prefix)
        labsty = {'font-size': '20pt'}
        graph.setLabel('left', text='Phase', units='rad', **labsty)
        graph.setLabel('bottom', text='Frequency', units='Hz', **labsty)
        for name, cor in zip(names, colors):
            opts = dict(
                y_channel=self.get_pvname(name+'FFTData-RB.PHA'),
                x_channel=self.get_pvname(name+'FFTFreq-RB.AVAL'),
                name=text[:3]+name,
                color=cor,
                lineStyle=1,
                lineWidth=3)
            graph.addChannel(**opts)
        vbl.addWidget(graph)

        hbl = QHBoxLayout()
        hbl.addStretch()
        vbl.addItem(hbl)
        pb = QPushButton('Open FFT Config', self)
        hbl.addWidget(pb)
        hbl.addStretch()
        Window = create_window_from_widget(FFTConfig, 'FFTConfig')
        util.connect_window(
            pb, Window, parent=self, prefix=self.prefix, bpm=self.bpm,
            data_prefix=self.data_prefix, position=self.position)


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriushla.util import set_style
    import sys

    app = SiriusApplication()
    set_style(app)
    wind = SiriusDialog()
    wind.resize(1400, 1400)
    hbl = QHBoxLayout(wind)
    bpm_name = 'SI-07SP:DI-BPM-1'
    widm = FFTData(bpm=bpm_name, data_prefix='GEN_', position=False)
    hbl.addWidget(widm)
    wind.show()
    sys.exit(app.exec_())
