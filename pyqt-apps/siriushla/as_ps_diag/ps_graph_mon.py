"""PS Graph Monitor."""
from copy import deepcopy as _dcopy
import numpy as _np
from epics import PV as _PV

from qtpy.QtCore import Qt, QSize, QTimer, Slot, Signal
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGridLayout, QWidget, QLabel, QHBoxLayout, \
    QComboBox, QToolTip, QSpacerItem, QSizePolicy as QSzPlcy, QApplication, \
    QGraphicsScene, QInputDialog, QAction, QMenu
import qtawesome as qta
from pyqtgraph import mkPen, mkBrush
from pydm.widgets import PyDMWaveformPlot

from siriuspy.util import get_strength_label
from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName
from siriuspy.search import PSSearch as _PSSearch, \
    MASearch as _MASearch
from siriuspy.pwrsupply.csdev import Const as _PSConst

from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from siriushla.widgets import SiriusMainWindow


class PSGraphMonWindow(SiriusMainWindow):
    """Power supply graph monitor window."""

    def __init__(self, parent=None, prefix=_vaca_prefix, filters=''):
        super().__init__(parent)
        self.setWindowTitle('Power Supplies Graph Monitor')
        self._prefix = prefix
        self._filters = filters
        if not filters:
            self.setObjectName('ASApp')
            filters = {'sec': 'SI', 'dis': 'PS', 'dev': 'CH'}
        else:
            self.setObjectName(filters['sec']+'App')
        self._psnames = _PSSearch.get_psnames(filters)
        self._setupUi()

    def _setupUi(self):
        aux_label = '' if not self._filters \
            else ' - '+self._filters['sec']+' '+self._filters['dev']
        self._label = QLabel('<h3>PS Graph Monitor'+aux_label+'</h3>',
                             self, alignment=Qt.AlignCenter)

        self.propty_sel = PSGraphProptySelWidget(self)

        self.graph = PSGraphMonWidget(
            self, self._prefix, self._psnames)
        self.propty_sel.propty_symb_changed.connect(
            self.graph.update_property_symb)
        self.propty_sel.propty_line_changed.connect(
            self.graph.update_property_line)

        if not self._filters:
            self.dev_sel = PSGraphDevicesSelWidget(self, self._psnames)
            self.propty_sel.change_matype(self.dev_sel.magfunc)
            self.dev_sel.matype_changed.connect(self.propty_sel.change_matype)
            self.dev_sel.psnames_changed.connect(self.graph.update_psnames)

        cw = QWidget()
        lay = QGridLayout(cw)
        lay.setVerticalSpacing(9)
        lay.addWidget(self._label, 0, 0, 1, 2)
        if not self._filters:
            lay.addWidget(self.dev_sel, 1, 0)
            lay.addItem(
                QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), 1, 1)
        lay.addWidget(self.propty_sel, 2, 0)
        lay.addItem(
            QSpacerItem(1, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), 2, 1)
        lay.addWidget(self.graph, 3, 0, 1, 2)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 1)
        self.setCentralWidget(cw)

    def contextMenuEvent(self, event):
        point = event.pos()
        menu = self.graph.contextMenuEvent(event, return_menu=True)
        menu.popup(self.mapToGlobal(point))


class PSGraphDevicesSelWidget(QWidget):
    """Power supply selection widget."""

    psnames_changed = Signal(list)
    matype_changed = Signal(str)

    def __init__(self, parent, psnames):
        super().__init__(parent)

        self._psnames = psnames

        self._choose_sec = ['TB', 'BO', 'TS', 'SI']

        self._choose_sub = ['All', ]
        self._choose_sub.extend(['{0:02d}.*'.format(i+1) for i in range(20)])
        self._choose_sub.extend(['.*M1', '.*M2',
                                 '.*C1', '.*C2', '.*C3', '.*C4',
                                 '.*SA', '.*SB', '.*SP'])

        self._choose_dev = {
            sec: ['CH', 'CV', 'C(H|V)'] for sec in self._choose_sec}
        self._choose_dev['SI'].extend(
            ['QS', 'QFA', 'QFB', 'QFP', 'QF.*',
             'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2', 'QD.*',
             'Q1', 'Q2', 'Q3', 'Q4', 'Q[1-4]',
             'Q(D|F).*', 'Q(F|D|[1-4]).*'])

        self.magfunc = _PSSearch.conv_psname_2_magfunc(self._psnames[0])

        self._setupUi()

    def _setupUi(self):
        self._label_dev = QLabel('Power supply: ', self)
        self._label_dev.setStyleSheet(
            'min-width: 8em; max-width: 8em;')

        self.cb_sec = QComboBox(self)
        for item in self._choose_sec:
            self.cb_sec.addItem(item)
        self.cb_sec.setCurrentText('SI')
        self.cb_sec.currentTextChanged.connect(
            self._handle_cb_visibility)
        self.cb_sec.currentTextChanged.connect(
            self._set_psnames)

        self.cb_sub = QComboBox(self)
        self.cb_sub.setEditable(True)
        self.cb_sub.setMaxVisibleItems(10)
        for item in self._choose_sub:
            self.cb_sub.addItem(item)
        self.cb_sub.currentTextChanged.connect(
            self._set_psnames)

        glay_choose = QGridLayout()
        glay_choose.addWidget(self.cb_sub, 0, 0)
        self.cb_dev = dict()
        for sec in self._choose_sec:
            visible = sec == 'SI'

            self.cb_dev[sec] = QComboBox(self)
            self.cb_dev[sec].setMaxVisibleItems(10)
            self.cb_dev[sec].setVisible(visible)
            for item in self._choose_dev[sec]:
                self.cb_dev[sec].addItem(item)
            self.cb_dev[sec].currentTextChanged.connect(
                self._set_psnames)

            glay_choose.addWidget(self.cb_dev[sec], 0, 1)

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._label_dev, 0, 0)
        lay.addWidget(self.cb_sec, 0, 1)
        lay.addLayout(glay_choose, 0, 2)

    def _set_psnames(self):
        sec = self.cb_sec.currentText()
        if sec == 'SI':
            sub = self.cb_sub.currentText()
            sub = sub if sub != 'All' else '.*'
        else:
            sub = '.*'
        dev = self.cb_dev[sec].currentText()

        self._psnames = _PSSearch.get_psnames(
            {'sec': sec, 'sub': '(?!Fam)'+sub, 'dis': 'PS', 'dev': dev})

        if self._psnames and self.sender() == self.cb_dev[sec]:
            self.magfunc = _PSSearch.conv_psname_2_magfunc(self._psnames[0])
            self.matype_changed.emit(self.magfunc)

        self.psnames_changed.emit(self._psnames)

    def _handle_cb_visibility(self):
        current_sec = self.sender().currentText()
        self.cb_sub.setVisible(current_sec == 'SI')
        for sec in self._choose_sec:
            self.cb_dev[sec].setVisible(current_sec == sec)


class PSGraphProptySelWidget(QWidget):
    """Power supply property selection widget."""

    propty_symb_changed = Signal(str)
    propty_line_changed = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self._magfunc = None
        self._intstr_propty = ''
        self._intstr_suffix = ['-Mon', '-SP', '-RB', 'Ref-Mon']

        self._choose_prop_symb = [
            'DiagStatus-Mon', 'IntlkSoft-Mon', 'IntlkHard-Mon',
            'PwrState-Sel', 'PwrState-Sts', 'OpMode-Sel', 'OpMode-Sts',
            'CtrlMode-Mon', 'CtrlLoop-Sel', 'CtrlLoop-Sts', 'CycleEnbl-Mon']
        self._choose_prop_line = [
            'Current-Mon', 'Current-SP', 'Current-RB', 'CurrentRef-Mon',
            'DiagCurrentDiff-Mon', 'WfmSyncPulseCount-Mon',
            'PRUCtrlQueueSize-Mon']
        for suf in self._intstr_suffix:
            self._choose_prop_line.append(self._intstr_propty+suf)

        self._setupUi()

    def _setupUi(self):
        self._label_prop = QLabel('Properties: ', self)
        self._label_prop.setStyleSheet(
            'min-width: 8em; max-width: 8em;')

        self._label_symb = QLabel()
        icon = qta.icon('mdi.record-circle-outline')
        pixmap = icon.pixmap(icon.actualSize(QSize(20, 20)))
        self._label_symb.setPixmap(pixmap)
        self._label_symb.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self.cb_prop_symb = QComboBox(self)
        self.cb_prop_symb.currentTextChanged.connect(
            self.propty_symb_changed.emit)
        self.cb_prop_symb.setSizePolicy(
            QSzPlcy.Expanding, QSzPlcy.Preferred)
        self.cb_prop_symb.setMaxVisibleItems(10)
        for item in self._choose_prop_symb:
            self.cb_prop_symb.addItem(item)
        hbox_prop_symb = QHBoxLayout()
        hbox_prop_symb.addWidget(self._label_symb)
        hbox_prop_symb.addWidget(self.cb_prop_symb)

        self._label_line = QLabel()
        icon = qta.icon('mdi.pulse')
        pixmap = icon.pixmap(icon.actualSize(QSize(20, 20)))
        self._label_line.setPixmap(pixmap)
        self._label_line.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self.cb_prop_line = QComboBox(self)
        self.cb_prop_line.currentTextChanged.connect(
            self.propty_line_changed.emit)
        self.cb_prop_line.setSizePolicy(
            QSzPlcy.Expanding, QSzPlcy.Preferred)
        self.cb_prop_line.setMaxVisibleItems(10)
        for item in self._choose_prop_line:
            self.cb_prop_line.addItem(item)
        hbox_prop_line = QHBoxLayout()
        hbox_prop_line.addWidget(self._label_line)
        hbox_prop_line.addWidget(self.cb_prop_line)

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._label_prop, 0, 0)
        lay.addLayout(hbox_prop_symb, 0, 1)
        lay.addLayout(hbox_prop_line, 0, 2)

    def change_matype(self, magfunc):
        currindex = self.cb_prop_line.currentIndex()
        for suf in self._intstr_suffix:
            index = self.cb_prop_line.findText(self._intstr_propty+suf)
            self.cb_prop_line.removeItem(index)

        self._magfunc = magfunc

        self._intstr_propty = get_strength_label(self._magfunc)
        for suf in self._intstr_suffix:
            self.cb_prop_line.addItem(self._intstr_propty+suf)
        self.cb_prop_line.setCurrentIndex(currindex)


class PSGraph(PyDMWaveformPlot):
    """Power supply data graph."""

    def __init__(self, parent=None, psnames=list(), y_data=list(),
                 symbols=list(), color='blue'):
        """Init."""
        super().__init__(parent)
        self.setBackgroundColor(QColor(255, 255, 255))
        self.setAutoRangeX(True)
        self.setAutoRangeY(True)
        self.setShowXGrid(True)
        self.setShowYGrid(True)
        self.plotItem.setLabel('bottom', 's', units='m')
        self._nok_pen = mkPen(QColor(color))
        self._nok_brush = mkBrush(QColor(255, 0, 0))
        self._ok_pen = mkPen(QColor(color))
        self._ok_brush = mkBrush(QColor(0, 200, 0))
        self._none_pen = mkPen(QColor(color))
        self._none_brush = mkBrush(QColor(220, 220, 220))
        self._all_pen = [self._nok_pen, ]
        self._all_brush = [self._nok_brush, ]

        self.addChannel(
            y_channel='Mean', x_channel='Pos', color='black',
            lineStyle=2, lineWidth=2)
        self.mean = self.curveAtIndex(0)

        self.addChannel(
            y_channel='Kicks', x_channel='Pos', color=color,
            lineWidth=2, symbol='o', symbolSize=10)
        self.curve = self.curveAtIndex(1)

        self.psnames = psnames
        self.symbols = symbols
        self.y_data = y_data

        # try to fix bug in pyqtgraph
        self.sceneObj.mouseReleaseEvent = self._sceneObj_mouseReleaseEvent

    @property
    def psnames(self):
        """Return psnames."""
        return _dcopy(self._psnames)

    @psnames.setter
    def psnames(self, new):
        if not new:
            self._psnames = new
            self._x_data = _np.array([0, ])
            self._tooltips = ['', ]
            self._sector = ''
        else:
            self._x_data = _np.array(_MASearch.get_mapositions(map(
                lambda x: x.substitute(dis='MA'), new)))
            self._psnames = [psn for _, psn in sorted(zip(self._x_data, new))]
            self._x_data = _np.sort(self._x_data)
            self._tooltips = [
                psn.get_nickname(dev=True) for psn in self._psnames]
            self._sector = SiriusPVName(new[0]).sec

        if self._sector == 'TB':
            self._c0 = 21.2477
        elif self._sector == 'TS':
            self._c0 = 26.8933
        elif self._sector == 'BO':
            self._c0 = 496.8
        elif self._sector == 'SI':
            self._c0 = 518.396
        else:
            self._c0 = 1.0

        self.curve.receiveXWaveform(self._x_data)
        self.mean.receiveXWaveform(self._x_data)

    @property
    def sector(self):
        """Return sector."""
        return self._sector

    @property
    def tooltips(self):
        """Return tooltips."""
        return self._tooltips

    @property
    def x_data(self):
        """Return x_data."""
        return self._x_data

    @property
    def y_data(self):
        """Return y_data."""
        return self._y_data

    @y_data.setter
    def y_data(self, new):
        if not new or any([n is None for n in new]):
            self._y_data = _np.array([0, ])
        else:
            self._y_data = _np.array(new)

        self.curve.receiveYWaveform(self._y_data)
        self.curve.opts['symbolPen'] = self._all_pen
        self.curve.opts['symbolBrush'] = self._all_brush
        self.curve.redrawCurve()

        self.mean.receiveYWaveform(
            _np.array([_np.mean(self._y_data)]*len(self._y_data)))
        self.mean.redrawCurve()

    @property
    def symbols(self):
        """Return symbols."""
        return self._symbols

    @symbols.setter
    def symbols(self, new):
        self._symbols = new
        if new:
            all_brush, all_pen = [], []
            for sym in self._symbols:
                if sym:
                    all_pen.append(self._ok_pen)
                    all_brush.append(self._ok_brush)
                else:
                    all_pen.append(self._nok_pen)
                    all_brush.append(self._nok_brush)
            self._all_pen = all_pen
            self._all_brush = all_brush
        else:
            self._all_pen = [self._none_pen, ]
            self._all_brush = [self._none_brush, ]

    def mouseMoveEvent(self, event):
        """Reimplement mouseMoveEvent."""
        pos = event.pos()
        posx = self.curve.scatter.mapFromScene(pos).x()
        posx = posx % self._c0
        ind = _np.argmin(_np.abs(_np.array(self._x_data)-posx))
        txt = '{0:s}, x = {1:.3f} m'.format(self.tooltips[ind], posx)
        QToolTip.showText(
            self.mapToGlobal(pos), txt, self, self.geometry(), 500)
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Reimplement mouseDoubleClickEvent."""
        posx = self.curve.xData
        view = self.plotItem.getViewBox()
        pos = view.mapSceneToView(event.pos())
        idx = _np.argmin(_np.abs(posx-pos.x()))
        psname = self._psnames[idx]
        self._open_ps_detail(psname)
        super().mouseDoubleClickEvent(event)

    def _open_ps_detail(self, psname):
        """Open PSDetailWindow."""
        app = QApplication.instance()
        app.open_window(PSDetailWindow, parent=self, **{'psname': psname})

    def _sceneObj_mouseReleaseEvent(self, event):
        """Copy sceneObj.mouseReleaseEvent and fix bug."""
        sceneObj = self.sceneObj
        if sceneObj.mouseGrabberItem() is None:
            if event.button() in sceneObj.dragButtons:
                if sceneObj.sendDragEvent(event, final=True):
                    event.accept()
                sceneObj.dragButtons.remove(event.button())
            else:
                cev = [e for e in sceneObj.clickEvents
                       if int(e.button()) == int(event.button())]
                if cev:  # change: handle IndexError raised when cev is empty
                    if sceneObj.sendClickEvent(cev[0]):
                        event.accept()
                    sceneObj.clickEvents.remove(cev[0])

        if int(event.buttons()) == 0:
            sceneObj.dragItem = None
            sceneObj.dragButtons = []
            sceneObj.clickEvents = []
            sceneObj.lastDrag = None
        QGraphicsScene.mouseReleaseEvent(sceneObj, event)

        sceneObj.sendHoverEvents(event)


class PSGraphMonWidget(QWidget):
    """Power supply graph monitor widget."""

    _pvs = dict()

    def __init__(self, parent=None, prefix=_vaca_prefix, psnames=''):
        super().__init__(parent)

        self._prefix = prefix
        self._psnames = psnames
        self._property_line = 'Current-Mon'
        self._property_symb = 'DiagStatus-Mon'

        self.propsymb_2_defval = {
            'DiagStatus-Mon': 0,
            'IntlkSoft-Mon': 0,
            'IntlkHard-Mon': 0,
            'PwrState-Sel': _PSConst.PwrStateSel.On,
            'PwrState-Sts': _PSConst.PwrStateSts.On,
            'OpMode-Sel': _PSConst.OpMode.SlowRef,
            'OpMode-Sts': _PSConst.States.SlowRef,
            'CtrlMode-Mon': _PSConst.Interface.Remote,
            'CtrlLoop-Sel': _PSConst.OpenLoop.Closed,
            'CtrlLoop-Sts': _PSConst.OpenLoop.Closed,
            'CycleEnbl-Mon': _PSConst.DsblEnbl.Enbl}

        self._setupUi()
        self._create_commands()

        self._timer = QTimer()
        self._timer.timeout.connect(self._update_graph)
        self._timer.setInterval(250)
        self._timer.start()

    def _setupUi(self):
        self.graph = PSGraph(self)
        self.graph.setObjectName('graph')
        self._update_graph()

        lay = QGridLayout(self)
        lay.addWidget(self.graph, 0, 0)

        self.setStyleSheet('#graph{min-width:60em;min-height:12em;}')

    def update_psnames(self, psnames):
        self._psnames = _dcopy(psnames)
        self._update_graph()

    @Slot(str)
    def update_property_line(self, text):
        self._property_line = text

    @Slot(str)
    def update_property_symb(self, text):
        self._property_symb = text

    def _update_graph(self):
        self._create_pvs(self._property_line)
        self._create_pvs(self._property_symb)
        self.graph.psnames = _dcopy(self._psnames)
        self._psnames = self.graph.psnames
        self.graph.symbols = self._get_values(self._property_symb)
        self.graph.y_data = self._get_values(self._property_line)

    # ---------- pv handler methods ----------

    def _create_pvs(self, propty):
        new_pvs = dict()
        for psn in self._psnames:
            pvname = self._prefix+psn+':'+propty
            if pvname in PSGraphMonWidget._pvs:
                continue
            new_pvs[pvname] = _PV(pvname, connection_timeout=0.05)
        PSGraphMonWidget._pvs.update(new_pvs)

    def _get_values(self, propty):
        if not self._psnames:
            return []

        for psn in self._psnames:
            pvname = self._prefix+psn+':'+propty
            PSGraphMonWidget._pvs[pvname].wait_for_connection()

        values = list()
        for psn in self._psnames:
            pvname = self._prefix+psn+':'+propty
            val = PSGraphMonWidget._pvs[pvname].get()
            val = val if val is not None else 0
            if propty in self.propsymb_2_defval.keys():
                defval = self.propsymb_2_defval[propty]
                val = 1 if val == defval else 0
            values.append(val)
        return values

    def _set_values(self, propty, value):
        for psn in self._psnames:
            pvname = self._prefix+psn+':'+propty
            pv = PSGraphMonWidget._pvs[pvname]
            if pv.wait_for_connection():
                pv.put(value)

    def _cmd_set_opmode_slowref(self):
        """Set power supplies OpMode to SlowRef."""
        self._create_pvs('OpMode-Sel')
        self._set_values('OpMode-Sel', _PSConst.OpMode.SlowRef)

    def _cmd_turn_on(self):
        """Turn power supplies on."""
        self._create_pvs('PwrState-Sel')
        self._set_values('PwrState-Sel', _PSConst.PwrStateSel.On)

    def _cmd_turn_off(self):
        """Turn power supplies off."""
        self._create_pvs('PwrState-Sel')
        self._set_values('PwrState-Sel', _PSConst.PwrStateSel.Off)

    def _cmd_set_current(self):
        """Set power supplies current."""
        self._create_pvs('Current-SP')
        value, ok = QInputDialog.getDouble(
            self, "Insert current setpoint", "Value")
        if ok:
            self._set_values('Current-SP', value)

    def _cmd_reset(self):
        """Reset power supplies."""
        self._create_pvs('Reset-Cmd')
        self._set_values('Reset-Cmd', 1)

    def _create_commands(self):
        self.cmd_turnon_act = QAction("Turn On", self)
        self.cmd_turnon_act.triggered.connect(self._cmd_turn_on)

        self.cmd_turnoff_act = QAction("Turn Off", self)
        self.cmd_turnoff_act.triggered.connect(self._cmd_turn_off)

        self.cmd_setslowref_act = QAction("Set OpMode to SlowRef", self)
        self.cmd_setslowref_act.triggered.connect(self._cmd_set_opmode_slowref)

        self.cmd_setcurrent_act = QAction("Set Current SP", self)
        self.cmd_setcurrent_act.triggered.connect(self._cmd_set_current)

        self.cmd_reset_act = QAction("Reset Interlocks", self)
        self.cmd_reset_act.triggered.connect(self._cmd_reset)

    def contextMenuEvent(self, event, return_menu=False):
        """Show a custom context menu."""
        point = event.pos()
        if not self.graph.geometry().contains(point) or return_menu:
            menu = QMenu("Actions", self)
            menu.addAction(self.cmd_turnon_act)
            menu.addAction(self.cmd_turnoff_act)
            menu.addAction(self.cmd_setslowref_act)
            menu.addAction(self.cmd_setcurrent_act)
            menu.addAction(self.cmd_reset_act)
            if return_menu:
                return menu
            else:
                menu.popup(self.mapToGlobal(point))
