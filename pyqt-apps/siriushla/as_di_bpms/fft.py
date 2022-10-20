from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, \
    QPushButton
from qtpy.QtCore import Qt
from pydm.widgets import PyDMEnumComboBox, PyDMPushButton
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import SiriusConnectionSignal, SiriusSpinbox
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
        CLASS = PyDMEnumComboBox if enum else SiriusSpinbox
        wid = CLASS(self)
        self._make_connections(wid, pv)
        if not enum:
        lab = QLabel(label)
        lab.setStyleSheet("""min-width:8em;""")
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
        graph.setLabel('left', text='Amplitude', units='a.u.')
        graph.setLabel('bottom', text='Frequency', units='Hz')
        for name, cor in zip(names, colors):
            opts = dict(
                y_channel=self.get_pvname(name+'FFTData-RB.AMP'),
                x_channel=self.get_pvname(name+'FFTFreq-RB.AVAL'),
                name=text[:3]+name,
                color=cor,
                lineStyle=1,
                lineWidth=1)  # NOTE: If > 1: very low performance
            graph.addChannel(**opts)
        vbl.addWidget(graph)

        graph = GraphWave(
            self, prefix=self.prefix, bpm=self.bpm,
            data_prefix=self.data_prefix)
        graph.setLabel('left', text='Phase', units='rad')
        graph.setLabel('bottom', text='Frequency', units='Hz')
        for name, cor in zip(names, colors):
            opts = dict(
                y_channel=self.get_pvname(name+'FFTData-RB.PHA'),
                x_channel=self.get_pvname(name+'FFTFreq-RB.AVAL'),
                name=text[:3]+name,
                color=cor,
                lineStyle=1,
                lineWidth=1)  # NOTE: If > 1: very low performance
            graph.addChannel(**opts)
        vbl.addWidget(graph)

        hbl = QHBoxLayout()
        hbl.addStretch()
        vbl.addItem(hbl)
        pb = QPushButton('Open FFT Config', self)
        hbl.addWidget(pb)
        hbl.addStretch()
        Window = create_window_from_widget(
            FFTConfig, title=self.bpm+': FFT Config')
        util.connect_window(
            pb, Window, parent=self, prefix=self.prefix, bpm=self.bpm,
            data_prefix=self.data_prefix, position=self.position)
