"""Custom widgets."""

from functools import partial as _part

import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QToolTip, QPushButton, QGridLayout, \
    QWidget

import qtawesome as qta

from siriuspy.clientarch.time import Time as _Time

from siriushla.widgets import SiriusTimePlot


class MyTimePlot(SiriusTimePlot):
    """Reimplement SiriusTimePlot."""

    def mouseMoveEvent(self, ev):
        pos = ev.pos()
        txt = ''
        for idx, curve in enumerate(self._curves):
            if idx == 0:
                posx = curve.scatter.mapFromScene(pos).x()
                txt = _Time(timestamp=posx).get_iso8601() + '\n'
            idx = _np.where(_np.isclose(
                curve.curve.xData-posx, 0, atol=0.15))[0]
            if list(idx):
                posy = curve.curve.yData[idx][0]
                txt += '{0}: {1}\n'.format(curve.name(), posy)

        QToolTip.showText(
            self.mapToGlobal(pos), txt, self, self.geometry(), 1000)
        super().mouseMoveEvent(ev)


class GraphItem(QWidget):
    """Graph Item Widget."""

    def __init__(self, parent=None, delete_slot=None, index=0,
                 pvname2data=dict()):
        super().__init__(parent)
        self.delete_slot = delete_slot
        self.index = index
        self.pvname2data = pvname2data
        self._setupUi()

    def _setupUi(self):
        self.graph = MyTimePlot(background='w')
        self.graph.getViewBox().setMouseEnabled(x=True)
        self.graph.showLegend = True
        self.graph.showXGrid = True
        self.graph.showYGrid = True
        for pvname, data in self.pvname2data.items():
            self._add_curve_2_graph(pvname, data)

        self.but = QPushButton(qta.icon('fa5s.times'), '', self)
        self.but.clicked.connect(_part(self.delete_slot, self.index))

        lay = QGridLayout(self)
        lay.addWidget(self.graph, 0, 0)
        lay.addWidget(self.but, 0, 1, alignment=Qt.AlignCenter)

    def _add_curve_2_graph(self, pvname, data):
        data_size = len(data['timestamp'])
        if data_size > self.graph.bufferSize:
            self.graph.setBufferSize(data_size)

        data_duration = data['timestamp'][-1] - data['timestamp'][0]
        if data_duration > self.graph.timeSpan:
            self.graph.setTimeSpan(data_duration)

        self.graph.addYChannel(
            y_channel='FAKE', axis='left', name=pvname,
            lineWidth=1)
        self.graph.setYLabels([data['unit'], ])
        curve = self.graph.curveAtIndex(-1)
        self.graph.fill_curve_buffer(
            curve, data['timestamp'], data['value'])
        curve.redrawCurve()
