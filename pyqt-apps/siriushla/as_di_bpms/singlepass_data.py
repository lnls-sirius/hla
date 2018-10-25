from functools import partial as _part
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, \
    QGridLayout, QStackedWidget, QLabel, QGroupBox
from qtpy.QtCore import Qt
from siriushla.widgets import SiriusLabel
from siriushla.as_di_bpms.base import BaseWidget, GraphWave, GraphTime


class SinglePassData(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(
            parent=parent, prefix=prefix, bpm=bpm, data_prefix='SP_')
        self.radio_buttons = []
        self.setupui()

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

        graph = self.create_graph(stack1, 'ant')
        vbl.addWidget(graph)
        stats = self.create_statistics(stack1, 'ant')
        vbl.addWidget(stats)

        # ##### Position and Amplitudes Widget ######
        stack2 = QWidget(self.stack)
        self.stack.addWidget(stack2)
        vbl = QVBoxLayout(stack2)

        graph = self.create_graph(stack2, 'pos')
        vbl.addWidget(graph)
        graph = self.create_graph(stack2, 'amp')
        vbl.addWidget(graph)

    def create_statistics(self, wid, typ='pos'):
        text, unit, names, _ = self._get_properties(typ)

        wid = QWidget(wid)
        hbl = QHBoxLayout(wid)
        hbl.addStretch()
        grpbx = QGroupBox('Statistics', wid)
        hbl.addWidget(grpbx)
        hbl.addStretch()

        gdl = QGridLayout(grpbx)
        gdl.setHorizontalSpacing(30)
        gdl.setVerticalSpacing(30)

        stats = ('MeanValue', 'Sigma', 'MinValue', 'MaxValue')
        for j, stat in enumerate(('Average', 'Sigma', 'Minimum', 'Maximum')):
            lab = QLabel(stat, wid)
            lab.setAlignment(Qt.AlignCenter)
            lab.setMinimumWidth(200)
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

    def create_graph(self, wid, typ='pos'):
        text, unit, names, colors = self._get_properties(typ)
        if typ == 'pos':
            unit = unit[1:]
            suff = '-Mon'
            CLASS = GraphTime
        elif typ == 'ant':
            suff = 'ArrayData'
            CLASS = GraphWave
        else:
            suff = '-Mon'
            CLASS = GraphTime

        graph = CLASS(
            wid, prefix=self.prefix, bpm=self.bpm,
            data_prefix=self.data_prefix)
        labsty = {'font-size': '20pt'}
        graph.setLabel('left', text=text, units=unit, **labsty)
        for name, cor in zip(names, colors):
            opts = dict(
                y_channel=name+suff,
                name=name[2:],
                color=cor,
                lineStyle=1,
                lineWidth=1)  # NOTE: If > 1: very low performance
            if typ == 'pos':
                graph.addYChannel(**opts, add_scale=1e-9)
            elif typ == 'amp':
                opts['y_channel'] = self.get_pvname(
                    opts['y_channel'], is_data=False)
                graph.addYChannel(**opts)
            else:
                opts['name'] = text[:3] + name
                opts['y_channel'] = self.get_pvname(opts['y_channel'])
                graph.addChannel(**opts)
        return graph

    def _get_properties(self, typ='pos'):
        if typ == 'pos':
            text = 'Positions'
            unit = 'nm'
            names = ('SPPosX', 'SPPosY', 'SPPosQ', 'SPSum')
            colors = ('blue', 'red', 'green', 'black')
        elif typ == 'ant':
            text = 'Antennas'
            unit = 'count'
            names = ('A', 'B', 'C', 'D')
            colors = ('blue', 'red', 'green', 'magenta')
        if typ == 'amp':
            text = 'Amplitudes'
            unit = 'count'
            names = ('SPAmplA', 'SPAmplB', 'SPAmplC', 'SPAmplD')
            colors = ('blue', 'red', 'green', 'magenta')
        return text, unit, names, colors

    def toggle_button(self, i, tog):
        if tog:
            self.stack.setCurrentIndex(i)


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
    widm = SinglePassData(prefix='ca://', bpm=bpm_name)
    hbl.addWidget(widm)
    wind.show()
    sys.exit(app.exec_())
