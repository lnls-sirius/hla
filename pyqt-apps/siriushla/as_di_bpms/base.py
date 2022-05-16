from functools import partial as _part
import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, \
    QFormLayout, QGroupBox, QLabel
from qtpy.QtGui import QColor
from pydm.widgets import PyDMWaveformPlot, PyDMEnumComboBox
from pydm.widgets.base import PyDMPrimitiveWidget
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.diagbeam.bpm.csdev import Const as _csbpm
from siriushla.widgets import SiriusConnectionSignal, SiriusLabel, \
    SiriusSpinbox, SiriusTimePlot

_BPMDB = _csbpm.get_bpm_database()


class BaseWidget(QWidget):

    def __init__(self, parent=None, prefix='', bpm='', data_prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.bpm = _PVName(bpm)
        self.setObjectName(self.bpm.sec+'App')
        self.data_prefix = data_prefix
        self.bpmdb = _BPMDB
        self._chans = []

    def channels(self):
        return self._chans

    def get_pvname(self, propty, is_data=True):
        addr = self.bpm.substitute(
            prefix=self.prefix,
            propty=(self.data_prefix if is_data else '')+propty)
        return addr

    def _create_formlayout_groupbox(self, title, props):
        grpbx = CustomGroupBox(title, self)
        fbl = QFormLayout(grpbx)
        grpbx.layoutf = fbl
        fbl.setLabelAlignment(Qt.AlignVCenter)
        for prop in props:
            if len(prop) == 2:
                pv1, txt = prop
                isdata = True
            elif len(prop) == 3:
                pv1, txt, isdata = prop
            hbl = QHBoxLayout()
            not_enum = pv1.endswith('-SP')
            pv2 = pv1.replace('-SP', '-RB').replace('-Sel', '-Sts')
            if pv2 != pv1:
                if not_enum:
                    chan1 = self.get_pvname(pv1, is_data=isdata)
                    wid = SiriusSpinbox(self, init_channel=chan1)
                    wid.setStyleSheet("min-width:5em;")
                    wid.showStepExponent = False
                    wid.limitsFromChannel = False
                    pvn = self.data_prefix + pv1
                    wid.setMinimum(self.bpmdb[pvn].get('low', -1e10))
                    wid.setMaximum(self.bpmdb[pvn].get('high', 1e10))
                else:
                    wid = PyDMEnumComboBox(
                        self,
                        init_channel=self.get_pvname(pv1, is_data=isdata))
                    wid.setStyleSheet("min-width:5em;")
                wid.setObjectName(pv1.replace('-', ''))
                hbl.addWidget(wid)

            lab = SiriusLabel(
                self, init_channel=self.get_pvname(pv2, is_data=isdata))
            lab.setObjectName(pv2.replace('-', ''))
            lab.showUnits = True
            lab.setStyleSheet("min-width:5em;")
            hbl.addWidget(lab)
            lab = QLabel(txt)
            lab.setObjectName(pv1.split('-')[0])
            lab.setStyleSheet("min-width:8em;")
            fbl.addRow(lab, hbl)
        return grpbx


class CustomGroupBox(QGroupBox, PyDMPrimitiveWidget):

    def __init__(self, title, parent=None):
        QGroupBox.__init__(self, title, parent)
        PyDMPrimitiveWidget.__init__(self)


def get_custom_widget_class(CLASS):
    class MyWidget(CLASS):

        def __init__(self, parent=None, **kws):
            """Initialize object."""
            super().__init__(parent=parent, **kws)
            self.setFocusPolicy(Qt.StrongFocus)

        def wheelEvent(self, event):
            """Reimplement wheel event to ignore event when out of focus."""
            if not self.hasFocus():
                event.ignore()
            else:
                super().wheelEvent(event)
    return MyWidget


class BaseGraph(BaseWidget):
    CLASS = get_custom_widget_class(PyDMWaveformPlot)
    DATA_CLASS = np.ndarray

    def __init__(self, parent=None, prefix='', bpm='', data_prefix=''):
        super().__init__(
            parent, prefix=prefix, bpm=bpm, data_prefix=data_prefix)
        self.graph = self.CLASS(self)
        self.setupgraph(self.graph)
        self.setupui()

    def setupgraph(self, graph):
        graph.mouseEnabledX = True
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(255, 255, 255))
        graph.setAutoRangeX(True)
        graph.setAutoRangeY(True)
        graph.setMinXRange(0.0)
        graph.setMaxXRange(1.0)
        graph.setAxisColor(QColor(0, 0, 0))
        graph.plotItem.showButtons()
        graph.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        graph.plotItem.getAxis('left').setStyle(
            tickTextOffset=5, autoExpandTextSpace=False, tickTextWidth=30)

    def setupui(self):
        hbl = QHBoxLayout(self)
        hbl.addWidget(self.graph)
        self.vbl = QVBoxLayout()
        hbl.addItem(self.vbl)
        self.vbl.addStretch()

    def setLabel(self, *args, **kwargs):
        self.graph.setLabel(*args, **kwargs)

    def curveAtIndex(self, *args):
        return self.graph.curveAtIndex(*args)

    def _add_channel(self, name):
        cdta = self.graph.curveAtIndex(-1)
        cbx = QCheckBox(name, self)
        plt = cbx.palette()
        plt.setColor(plt.WindowText, cdta.color)
        cbx.setPalette(plt)
        cbx.setChecked(True)
        self.vbl.addWidget(cbx)
        self.vbl.addStretch()
        cbx.toggled.connect(cdta.setVisible)

    def _add_scale(self, channel, scale):
        cdta = self.graph.curveAtIndex(-1)
        chan = SiriusConnectionSignal(channel)
        chan.new_value_signal[self.DATA_CLASS].connect(
            _part(self._apply_scale, cdta, scale))
        self._chans.append(chan)

    def _apply_scale(self, cdta, scale, value):
        if self.DATA_CLASS == np.ndarray:
            cdta.receiveYWaveform(value*scale)
        else:
            cdta.receiveNewValue(value*scale)


class GraphWave(BaseGraph):

    def addChannel(self, **opts):
        scale = opts.pop('add_scale', None)
        self.graph.addChannel(**opts)
        name = opts.get('name', '')
        self._add_channel(name)
        if scale:
            channel = opts.get('y_channel', '')
            self._add_scale(channel, scale)


class GraphTime(BaseGraph):
    CLASS = get_custom_widget_class(SiriusTimePlot)
    DATA_CLASS = float

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph.timeSpan = 100

    def addYChannel(self, **opts):
        scale = opts.pop('add_scale', None)
        ychan = opts['y_channel']
        if scale:
            opts['y_channel'] = 'A'
        self.graph.addYChannel(**opts)
        if scale:
            self._add_scale(ychan, scale)
        name = opts.get('name', '')
        self._add_channel(name)
