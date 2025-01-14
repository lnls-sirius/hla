"""Base module."""

from functools import partial as _part
import numpy as np

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, \
    QFormLayout, QGroupBox, QLabel, QSizePolicy as QSzPlcy
from qtpy.QtGui import QColor

from siriuspy.namesys import SiriusPVName as _PVName

from siriushla.widgets import SiriusConnectionSignal, SiriusLabel, \
    SiriusSpinbox, SiriusTimePlot, SiriusWaveformPlot, SiriusLedState, \
    SiriusLedAlert, PyDMStateButton, SiriusEnumComboBox, SiriusPushButton, \
    SiriusLineEdit, pydmwidget_factory


class BaseWidget(QWidget):

    def __init__(self, parent=None, prefix='', bpm='', data_prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.bpm = _PVName(bpm)
        self.is_pbpm = self.bpm.dev == 'PBPM'
        self.setObjectName(self.bpm.sec+'App')
        self.data_prefix = data_prefix
        self._chans = []

    def channels(self):
        return self._chans

    def get_pvname(self, propty, is_data=True):
        addr = self.bpm.substitute(
            prefix=self.prefix,
            propty=(self.data_prefix if is_data else '')+propty)
        return addr

    def _create_formlayout_groupbox(self, title, props):
        if title:
            grpbx = CustomGroupBox(title, self)
        else:
            grpbx = QWidget(self)
        fbl = QFormLayout(grpbx)
        grpbx.layoutf = fbl
        fbl.setLabelAlignment(Qt.AlignVCenter)
        for prop in props:
            if len(prop) == 2:
                pvs, txt = prop
                isdata, prec, widgets = True, None, None
            elif len(prop) == 3:
                pvs, txt, aux = prop
                if isinstance(aux, bool):
                    isdata, prec, widgets = aux, None, None
                elif isinstance(aux, int):
                    isdata, prec, widgets = True, aux, None
                elif isinstance(aux, dict):
                    isdata = aux.get('isdata', True)
                    prec = aux.get('prec', None)
                    widgets = aux.get('widgets', None)
                else:
                    isdata, prec, widgets = True, None, aux

            if isinstance(pvs, str):
                pv1 = pvs
                pv2 = pv1.replace('-SP', '-RB').replace('-Sel', '-Sts')
                pvs = [pv1, ]
                if pv2 != pv1:
                    pvs.append(pv2)
            else:
                pv1 = pvs[0]

            if widgets is None:
                if pv2 != pv1:
                    if pv1.endswith('-SP'):
                        widgets = ['spin', 'label']
                    else:
                        widgets = ['combo', 'label']
                else:
                    widgets = ['label', ]

            lab = QLabel(txt)
            lab.setObjectName(pv1.split('-')[0])
            lab.setStyleSheet("min-width:10em;")

            hbl = QHBoxLayout()
            for i, wid in enumerate(widgets):
                hbl.addWidget(self._get_widget(wid, pvs[i], isdata, prec))

            fbl.addRow(lab, hbl)

        return grpbx

    def _get_widget(self, widtype, pvname, isdata, prec):
        pvname = self.get_pvname(pvname, is_data=isdata)

        if widtype == 'combo':
            wid = SiriusEnumComboBox(self, pvname)
            wid.setStyleSheet("QWidget{min-width:5em;}")
        elif widtype == 'spin':
            wid = SiriusSpinbox(self, pvname)
            wid.setStyleSheet("QWidget{min-width:5em;}")
            if prec is not None:
                wid.precisionFromPV = False
                wid.precision = prec
        elif widtype == 'lineedit':
            wid = SiriusLineEdit(self, pvname)
            wid.setStyleSheet("QWidget{min-width:5em;}")
            wid.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Preferred)
            if prec is not None:
                wid.precisionFromPV = False
                wid.precision = prec
        elif widtype == 'label':
            wid = SiriusLabel(self, pvname)
            wid.showUnits = True
            if prec is not None:
                wid.precisionFromPV = False
                wid.precision = prec
            wid.setStyleSheet("QLabel{min-width:6em;}")
        elif widtype == 'ledstate':
            wid = SiriusLedState(self, pvname)
        elif widtype == 'ledalert':
            wid = SiriusLedAlert(self, pvname)
        elif widtype == 'statebutton':
            wid = PyDMStateButton(self, pvname)
        elif isinstance(widtype, (list, tuple)):
            if widtype[0] == 'pushbutton':
                kws = dict(
                    label=widtype[1], icon=widtype[2],
                    pressValue=widtype[3] if len(widtype) > 3 else 1,
                    init_channel=pvname)
                if len(widtype) > 4:
                    kws['releaseValue'] = widtype[4]
                wid = SiriusPushButton(self, **kws)
                wid.setDefault(False)
                wid.setAutoDefault(False)
            elif widtype[0] == 'ledstate':
                wid = SiriusLedState(self, pvname)
                wid.offColor = widtype[1]
                wid.onColor = widtype[2]
            elif widtype[0] == 'ledalert':
                wid = SiriusLedAlert(self, pvname)
                wid.offColor = widtype[1]
                wid.onColor = widtype[2]
        else:
            raise NotImplementedError(f'widget not defined for type {widtype}')
        wid.setObjectName(str(pvname).replace('-', ''))
        return wid

    def basic_rule(self, channel, flag, val=0):
        chan = self.get_pvname(channel)
        opr = '==' if flag else '!='
        val = str(val)
        rules = (
            '[{"name": "VisRule", "property": "Visible", ' +
            '"expression": "ch[0] '+opr+' '+val+'", "channels": ' +
            '[{"channel": "'+chan+'", "trigger": true}]}]')
        return rules


CustomGroupBox = pydmwidget_factory(QGroupBox, pydm_class='primi')


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
    CLASS = get_custom_widget_class(SiriusWaveformPlot)
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
