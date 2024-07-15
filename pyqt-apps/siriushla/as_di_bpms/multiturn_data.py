from functools import partial as _part
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, \
    QGridLayout, QStackedWidget, QLabel, QGroupBox, QPushButton
from qtpy.QtCore import Qt
from siriushla.widgets import SiriusConnectionSignal, SiriusLabel
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_di_bpms.base import BaseWidget, GraphWave
from siriushla import util


class MultiTurnData(BaseWidget):

    def __init__(self, parent=None, acq_type='ACQ', prefix='', bpm=''):
        self.acq_type = acq_type
        data_prefix = 'GEN_' if acq_type == 'ACQ' else 'PM_'
        super().__init__(
            parent=parent, prefix=prefix, bpm=bpm, data_prefix=data_prefix)

        self.samplespre = SiriusConnectionSignal(self.get_pvname(
            acq_type+'SamplesPre-RB', is_data=False))
        self.samplespost = SiriusConnectionSignal(self.get_pvname(
            acq_type+'SamplesPost-RB', is_data=False))
        self.shots = SiriusConnectionSignal(self.get_pvname(
            acq_type+'Shots-RB', is_data=False))

        self._chans.extend([self.samplespre, self.samplespost, self.shots])
        self.radio_buttons = []
        self.setupui()

    @property
    def nrsamplespershot(self):
        if self.samplespost.connected and self.samplespre.connected:
            return self.samplespost.getvalue() + self.samplespre.getvalue()

    @property
    def nrsamples(self):
        val = self.nrsamplespershot
        if val and self.shots.connected:
            return self.nrsamplespershot*self.shots.getvalue()

    def setupui(self):
        vbl = QVBoxLayout(self)
        self.stack = QStackedWidget(self)
        vbl.addWidget(self.stack)

        rbA = QRadioButton('Antennas', self)
        rbP = QRadioButton('Positions', self)
        rbA.toggled.connect(_part(self.toggle_button, 0))
        rbP.toggled.connect(_part(self.toggle_button, 1))
        self.radio_buttons.append(rbA)
        self.radio_buttons.append(rbP)
        rbA.setChecked(True)
        hbl = QHBoxLayout()
        hbl.addStretch()
        hbl.addWidget(rbA)
        hbl.addStretch()
        hbl.addWidget(rbP)
        hbl.addStretch()
        vbl.addItem(hbl)

        # ##### Antennas Widget ######
        stack1 = QWidget(self.stack)
        self.stack.addWidget(stack1)
        vbl = QVBoxLayout(stack1)

        graph = self.create_graph(stack1, False)
        vbl.addWidget(graph)
        stats = self.create_statistics(stack1, False)
        vbl.addWidget(stats)

        # ##### Position Widget ######
        stack2 = QWidget(self.stack)
        self.stack.addWidget(stack2)
        vbl = QVBoxLayout(stack2)

        graph = self.create_graph(stack2, True)
        vbl.addWidget(graph)
        stats = self.create_statistics(stack2, True)
        vbl.addWidget(stats)

        self.setStyleSheet("""
            #MultiTurnDataGraph{
                min-width:48em;
                min-height:24em;
            }
            QLabel{
                min-width:6em; max-width:6em;
                min-height:1.5em; max-height:1.5em;
            }""")

    def create_statistics(self, wid, position=True):
        text, unit, names, _ = self._get_properties(position)

        wid = QWidget(wid)
        hbl = QHBoxLayout(wid)
        hbl.addStretch()
        grpbx = QGroupBox('Statistics', wid)
        hbl.addWidget(grpbx)
        hbl.addStretch()

        gdl = QGridLayout(grpbx)
        gdl.setHorizontalSpacing(20)
        gdl.setVerticalSpacing(20)

        stats = ('MeanValue', 'Sigma', 'MinValue', 'MaxValue')
        for j, stat in enumerate(('Average', 'Sigma', 'Minimum', 'Maximum')):
            lab = QLabel(stat, wid)
            lab.setAlignment(Qt.AlignCenter)
            gdl.addWidget(lab, 0, j+1)
        for i, name in enumerate(names):
            lab = QLabel(text[:3] + name, wid)
            lab.setAlignment(Qt.AlignCenter)
            gdl.addWidget(lab, i+1, 0)
            for j, stat in enumerate(stats):
                lab = SiriusLabel(wid, init_channel=self.get_pvname(
                    name+'_STATS'+stat+'_RBV'))
                lab.setAlignment(Qt.AlignCenter)
                lab.unit_changed(unit)
                lab.showUnits = True
                lab.precisionFromPV = False
                lab.precision = 3
                gdl.addWidget(lab, i+1, j+1)
        return wid

    def create_graph(self, wid, position=True):
        text, unit, names, colors = self._get_properties(position)
        if position:
            unit = unit[1:]

        graph = GraphWave(
            wid, prefix=self.prefix, bpm=self.bpm,
            data_prefix=self.data_prefix)
        graph.setObjectName('MultiTurnDataGraph')
        graph.setLabel('left', text=text, units=unit)
        for name, cor in zip(names, colors):
            opts = dict(
                y_channel=name+'ArrayData',
                name=text[:3]+name,
                color=cor,
                lineStyle=1,
                lineWidth=1)  # NOTE: If > 1: very low performance
            opts['y_channel'] = self.get_pvname(opts['y_channel'])
            if position:
                graph.addChannel(add_scale=1e-9, **opts)
            else:
                graph.addChannel(**opts)
        return graph

    def _get_properties(self, position=True):
        if position:
            text = 'Positions'
            unit = 'nm'
            names = ('X', 'Y', 'Q', 'SUM')
            colors = ('blue', 'red', 'green', 'black')
        else:
            text = 'Antennas'
            unit = 'count'
            names = ('A', 'B', 'C', 'D')
            colors = ('blue', 'red', 'green', 'magenta')
        return text, unit, names, colors

    def toggle_button(self, i, tog):
        if tog:
            self.stack.setCurrentIndex(i)

    def control_visibility_buttons(self, text):
        bo = not text.startswith('adc')
        self.radio_buttons[1].setVisible(bo)
        self.radio_buttons[0].setChecked(True)
