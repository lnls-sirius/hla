"""Control the Orbit Graphic Displnay."""

import numpy as _np
from pyqtgraph import functions, mkPen
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, \
    QToolTip, QSpinBox
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from siriuspy.csdevice.orbitcorr import SOFBFactory
from siriushla.widgets import SiriusConnectionSignal
from .base import BaseWidget, Graph, InfLine
from .correctors import CorrectorsWidget


class ShowMatrixWidget(QWidget):

    def __init__(self, parent, prefix, acc):
        super().__init__(parent)
        self.prefix = prefix
        self.acc = acc.upper()
        self._csorb = SOFBFactory.create(acc)
        self._inflines = []
        self.setupui()
        self.mat = SiriusConnectionSignal(prefix+'RespMat-RB')
        self.mat.new_value_signal[_np.ndarray].connect(self._update_graph)
        self.rsize = SiriusConnectionSignal(prefix+'RingSize-RB')
        self.rsize.new_value_signal[int].connect(self._update_horizontal)
        self._update_horizontal(None)
        self._update_graph(None)

    def setupui(self):
        vbl = QVBoxLayout(self)

        lab = QLabel('Response Matrix', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)

        graph = Graph(self)
        vbl.addWidget(graph)

        self.spbox = QSpinBox(self)
        self.spbox.setMaximum(1000)
        self.spbox.setValue(80)
        self.spbox.setKeyboardTracking(False)
        self.spbox.editingFinished.connect(self._update_graph)

        vbl.addWidget(self.spbox)

        graph.setShowLegend(False)
        graph.setLabel('bottom', text='BPM Position', units='m')
        graph.setLabel('left', text='Matrix', units='m/rad')
        for i in range(self._csorb.NR_CORRS):
            color = 'blue'
            if i >= self._csorb.NR_CH:
                color = 'red'
            if i >= self._csorb.NR_CH+self._csorb.NR_CV:
                color = 'black'
            opts = dict(
                y_channel='',
                x_channel='',  # self.prefix+'BPMPosS-Mon',
                name='',
                color=color,
                redraw_mode=2,
                lineStyle=1,
                lineWidth=3,
                symbol='o',
                symbolSize=10)
            graph.addChannel(**opts)
        graph.plotItem.scene().sigMouseMoved.connect(self._show_tooltip)
        self.graph = graph

    def _show_tooltip(self, pos):
        names = self._csorb.BPM_NICKNAMES
        posi = self._csorb.BPM_POS
        unit = 'count'

        graph = self.graph
        curve = graph.curveAtIndex(0)
        posx = curve.scatter.mapFromScene(pos).x()
        if self._csorb.isring():
            posx = posx % self._csorb.C0
        ind = _np.argmin(_np.abs(_np.array(posi)-posx))
        posy = curve.scatter.mapFromScene(pos).y()

        sca, prf = functions.siScale(posy)
        txt = '{0:s}, y = {1:.3f} {2:s}'.format(
                                names[ind], sca*posy, prf+unit)
        QToolTip.showText(
            graph.mapToGlobal(pos.toPoint()),
            txt, graph, graph.geometry(), 500)

    def _update_graph(self, *args):
        sep = self.spbox.value()
        val = self.mat.value
        if val is None:
            return
        val = val.reshape(-1, self._csorb.NR_CORRS)
        for i in range(self._csorb.NR_CORRS):
            cur = self.graph.curveAtIndex(i)
            cur.receiveYWaveform(sep*i + val[:, i])

    def _update_horizontal(self, _):
        val = self.rsize.getvalue()
        if val is None:
            return
        bpm_pos = _np.array(self._csorb.BPM_POS)
        bpm_pos = [bpm_pos + i*self._csorb.C0 for i in range(2*val)]
        bpm_pos = _np.hstack(bpm_pos)
        for i in range(self._csorb.NR_CORRS):
            cur = self.graph.curveAtIndex(i)
            cur.receiveXWaveform(bpm_pos)

        for cur in self._inflines:
            self.graph.removeItem(cur)
        self._inflines = []
        for i in range(2*val+1):
            dic = {'style': 2, 'width': 2, 'color': '000'}
            if i == val:
                dic = {'style': 1, 'width': 3, 'color': '000'}
            pen = mkPen(**dic)
            line = InfLine(pos=i*self._csorb.C0+bpm_pos[0]/2, pen=pen)
            self._inflines.append(line)
            self.graph.addItem(line)


class SingularValues(QWidget):

    def __init__(self, parent, prefix):
        super().__init__(parent)
        self.prefix = prefix
        self._chans = []
        self.setupui()

    def channels(self):
        return self._chans

    def setupui(self):
        vbl = QVBoxLayout(self)
        vbl.setAlignment(Qt.AlignCenter)
        lab = QLabel('Singular Values', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)
        graph = Graph()
        graph.setShowLegend(False)
        graph.setLabel('left', text='Singular Values', units='m/rad')
        graph.setLabel('bottom', text='Index')
        vbl.addWidget(graph)
        opts = dict(
            y_channel=self.prefix+'SingValues-Mon',
            color='black',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=2,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        cur = graph.curveAtIndex(0)
        cur.setSymbolBrush(0, 0, 0)

        pen = mkPen(QColor(150, 150, 150))
        pen.setStyle(2)
        pen.setWidth(3)
        line = InfLine(pos=0, pen=pen, angle=90)
        graph.addItem(line)
        chan = SiriusConnectionSignal(self.prefix+'NrSingValues-RB')
        chan.new_value_signal[int].connect(line.setValue)
        self._chans.append(chan)

        graph.setObjectName('graph_singvalues')
        graph.setStyleSheet("""
            #graph_singvalues{
                min-width:30em;
                min-height:22m;
            }""")


def _main(prefix):
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = prefix + 'SI-Glob:AP-SOFB:'
    wid = OrbitWidget(win, prefix)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix
    import sys
    _main(vaca_prefix)
