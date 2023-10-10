"""Graph Widgets."""

import time as _time
import numpy as _np

from qtpy.QtCore import Qt, Slot, Signal, QSize, QThread
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGridLayout, QWidget, QLabel, QHBoxLayout, \
    QComboBox, QToolTip, QSizePolicy as QSzPlcy, QTabWidget

import qtawesome as qta

from pyqtgraph import mkPen, mkBrush

from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from siriushla.util import run_newprocess
from siriushla.widgets import SiriusWaveformPlot

from .base import BaseObject
from .custom_widgets import RefOrbComboBox


class GraphMonitorWidget(QWidget):
    """Graph Monitor Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix):
        super().__init__(parent)
        self.prefix = prefix
        self.setObjectName('SIApp')
        self._setupUi()

    def _setupUi(self):
        tab = QTabWidget(self)
        tab.setObjectName('SITab')
        tab.setStyleSheet("""
            QTabWidget::pane {
                border-right: 2px solid gray;
                border-bottom: 2px solid gray;
                border-left: 2px solid gray;
            }""")
        tab.addTab(self._setupTab('Min.Sum. Threshold'), 'Min.Sum. Threshold')
        tab.addTab(self._setupTab('Position'), 'Position')
        tab.addTab(self._setupTab('Angulation'), 'Angulation')

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(tab)

    def _setupTab(self, intlktype):
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        label = QLabel(
            '<h3>'+intlktype+'</h3>', self, alignment=Qt.AlignCenter)
        lay.addWidget(label, 0, 0)

        if intlktype == 'Min.Sum. Threshold':
            graph = MinSumGraphWidget(self, self.prefix)
            lay.addWidget(graph, 2, 0)
        elif intlktype == 'Position':
            propty_sel = GraphProptySelWidget(self)
            lay.addWidget(propty_sel, 1, 0)

            graphx = PosXGraphWidget(self, self.prefix)
            lay.addWidget(graphx, 2, 0)
            legx = GraphLegendWidget(self, 'Pos', 'X')
            lay.addWidget(legx, 3, 0)
            graphy = PosYGraphWidget(self, self.prefix)
            lay.addWidget(graphy, 4, 0)
            legy = GraphLegendWidget(self, 'Pos', 'Y')
            lay.addWidget(legy, 5, 0)

            propty_sel.propty_intlk_changed.connect(
                graphx.update_propty_intlktype)
            propty_sel.propty_reforb_changed.connect(
                graphx.update_propty_reforb)
            propty_sel.propty_comp_changed.connect(
                graphx.update_propty_comptype)
            propty_sel.propty_intlk_changed.connect(
                graphy.update_propty_intlktype)
            propty_sel.propty_reforb_changed.connect(
                graphy.update_propty_reforb)
            propty_sel.propty_comp_changed.connect(
                graphy.update_propty_comptype)
        elif intlktype == 'Angulation':
            propty_sel = GraphProptySelWidget(self)
            lay.addWidget(propty_sel, 1, 0)

            graphx = AngXGraphWidget(self, self.prefix)
            lay.addWidget(graphx, 2, 0)
            legx = GraphLegendWidget(self, 'Ang', 'X')
            lay.addWidget(legx, 3, 0)
            graphy = AngYGraphWidget(self, self.prefix)
            lay.addWidget(graphy, 4, 0)
            legy = GraphLegendWidget(self, 'Ang', 'Y')
            lay.addWidget(legy, 5, 0)

            propty_sel.propty_intlk_changed.connect(
                graphx.update_propty_intlktype)
            propty_sel.propty_reforb_changed.connect(
                graphx.update_propty_reforb)
            propty_sel.propty_comp_changed.connect(
                graphx.update_propty_comptype)
            propty_sel.propty_intlk_changed.connect(
                graphy.update_propty_intlktype)
            propty_sel.propty_reforb_changed.connect(
                graphy.update_propty_reforb)
            propty_sel.propty_comp_changed.connect(
                graphy.update_propty_comptype)

        return wid


class GraphProptySelWidget(QWidget):
    """Graph Interlock and Comparision Type Selelction Widget."""

    propty_intlk_changed = Signal(str)
    propty_comp_changed = Signal(str)
    propty_reforb_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._choose_plotopt = {
            'Instantaneous': [
                'General', 'Upper', 'Lower', 'Upper | Lower'],
            'Latch': [
                'General', 'Upper', 'Lower', 'Upper | Lower'],
        }
        self._init_intlkval = 'Latch'

        self._setupUi()

    def _setupUi(self):
        self._label_prop = QLabel('Properties: ', self)
        self._label_prop.setStyleSheet(
            'min-width: 8em; max-width: 8em;')

        self._label_intlk = QLabel('Interlock: ', self)
        self._cb_intlk = QComboBox(self)
        self._cb_intlk.setSizePolicy(
            QSzPlcy.Expanding, QSzPlcy.Preferred)
        intlkitems = list(self._choose_plotopt.keys())
        self._cb_intlk.addItems(intlkitems)
        self._cb_intlk.setCurrentText(self._init_intlkval)
        self._cb_intlk.currentTextChanged.connect(
            self.propty_intlk_changed.emit)
        self._cb_intlk.currentTextChanged.connect(
            self._set_plotopt_items)

        self._label_comp = QLabel('', self, alignment=Qt.AlignRight)
        icon = qta.icon('mdi.circle-outline')
        pixmap = icon.pixmap(icon.actualSize(QSize(20, 20)))
        self._label_comp.setPixmap(pixmap)
        self._label_comp.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self._cb_comp = QComboBox(self)
        self._cb_comp.setSizePolicy(
            QSzPlcy.Expanding, QSzPlcy.Preferred)
        compitems = self._choose_plotopt[self._init_intlkval]
        self._cb_comp.addItems(compitems)
        self._cb_comp.currentTextChanged.connect(
            self.propty_comp_changed.emit)

        self._label_reforb = QLabel('Ref.Orb.: ')
        self._cb_reforb = RefOrbComboBox(self)
        self._cb_reforb.refOrbChanged.connect(self.propty_reforb_changed.emit)

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._label_prop, 0, 0)
        lay.addWidget(self._label_intlk, 0, 1)
        lay.addWidget(self._cb_intlk, 0, 2)
        lay.addWidget(self._label_comp, 0, 3)
        lay.addWidget(self._cb_comp, 0, 4)
        lay.addWidget(self._label_reforb, 0, 5)
        lay.addWidget(self._cb_reforb, 0, 6)

    def _set_plotopt_items(self, key):
        self._cb_comp.currentTextChanged.disconnect()
        olditem = self._cb_comp.currentText()
        self._cb_comp.clear()
        newitems = self._choose_plotopt[self._cb_intlk.currentText()]
        self._cb_comp.addItems(newitems)
        if olditem in newitems:
            self._cb_comp.setCurrentText(olditem)
        else:
            self._cb_comp.setCurrentIndex(0)
        self.propty_comp_changed.emit(self._cb_comp.currentText())
        self._cb_comp.currentTextChanged.connect(
            self.propty_comp_changed.emit)


class GraphLegendWidget(QWidget):
    """Graph Legend Widget."""

    def __init__(self, parent=None, metric='', plan=''):
        super().__init__(parent)
        self._metric = metric
        self._plan = plan.upper()

        self._setupUi()

    def _setupUi(self):
        self._label_leg = QLabel('Legend: ', self)

        self._label_symcur = QLabel('', self, alignment=Qt.AlignRight)
        icon_cur = qta.icon(
            'fa5s.window-minimize', offset=(0.0, -0.4), rotated=-45,
            color='red' if self._plan == 'Y' else 'blue')
        pixmap_cur = icon_cur.pixmap(icon_cur.actualSize(QSize(20, 20)))
        self._label_symcur.setPixmap(pixmap_cur)
        self._label_symcur.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self._label_labcur = QLabel(self._metric + self._plan)

        self._label_symlim = QLabel()
        icon_lim = qta.icon(
            'fa5s.window-minimize', 'fa5s.window-minimize',
            options=[
                dict(scale_factor=0.4, offset=(-0.1, 0.0),
                     rotated=-45, color='black'),
                dict(scale_factor=0.4, offset=(0.3, 0.0),
                     rotated=-45, color='black')])
        pixmap_lim = icon_lim.pixmap(icon_lim.actualSize(QSize(20, 20)))
        self._label_symlim.setPixmap(pixmap_lim)
        self._label_symlim.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self._label_lablim = QLabel(self._plan+' Thres RB')

        self._label_sym0 = QLabel('', self, alignment=Qt.AlignRight)
        icon_s0 = qta.icon('mdi.cards-diamond-outline')
        pixmap = icon_s0.pixmap(icon_s0.actualSize(QSize(20, 20)))
        self._label_sym0.setPixmap(pixmap)
        self._label_sym0.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self._label_lab0 = QLabel(self._plan+' Min/Max Intlk Mon')

        self._label_sym1 = QLabel('', self, alignment=Qt.AlignRight)
        icon_s1 = qta.icon('mdi.circle-outline')
        pixmap = icon_s1.pixmap(icon_s1.actualSize(QSize(20, 20)))
        self._label_sym1.setPixmap(pixmap)
        self._label_sym0.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self._label_lab1 = QLabel('X | Y Intlk Mon')

        self._label_symnok = QLabel('', self, alignment=Qt.AlignRight)
        icon_nok = qta.icon('mdi.square', color='red')
        pixmap_nok = icon_nok.pixmap(icon_nok.actualSize(QSize(20, 20)))
        self._label_symnok.setPixmap(pixmap_nok)
        self._label_symnok.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self._label_labnok = QLabel('Intlk On (Limit exceeded)')

        self._label_symok = QLabel()
        icon_ok = qta.icon('mdi.square', color='#00d900')
        pixmap_ok = icon_ok.pixmap(icon_ok.actualSize(QSize(20, 20)))
        self._label_symok.setPixmap(pixmap_ok)
        self._label_symok.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Fixed)
        self._label_labok = QLabel('Intlk Off (All ok)')

        lay = QHBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._label_leg)
        lay.addStretch()
        lay.addWidget(self._label_symcur)
        lay.addWidget(self._label_labcur)
        lay.addStretch()
        lay.addWidget(self._label_symlim)
        lay.addWidget(self._label_lablim)
        lay.addStretch()
        lay.addWidget(self._label_sym0)
        lay.addWidget(self._label_lab0)
        lay.addStretch()
        lay.addWidget(self._label_sym1)
        lay.addWidget(self._label_lab1)
        lay.addStretch()
        lay.addWidget(self._label_symnok)
        lay.addWidget(self._label_labnok)
        lay.addStretch()
        lay.addWidget(self._label_symok)
        lay.addWidget(self._label_labok)


class Graph(BaseObject, SiriusWaveformPlot):
    """BPM orbit interlock data graph."""

    def __init__(self, parent, intlktype):
        """Init."""
        BaseObject.__init__(self)
        SiriusWaveformPlot.__init__(self, parent)
        self.setBackgroundColor(QColor(255, 255, 255))
        self.setAutoRangeX(True)
        self.setAutoRangeY(True)
        self.setShowXGrid(True)
        self.setShowYGrid(True)
        self.plotItem.setLabel('bottom', 's', units='m')
        self._nok_pen = mkPen(QColor('black'))
        self._nok_brush = mkBrush(QColor(255, 0, 0))
        self._ok_pen = mkPen(QColor('black'))
        self._ok_brush = mkBrush(QColor(0, 200, 0))
        self._none_pen = mkPen(QColor('black'))
        self._none_brush = mkBrush(QColor(220, 220, 220))

        self._intlktype = intlktype
        if 'Sum' in intlktype:
            self.title = 'Min.Sum. Threshold'
            ylabel, yunit = 'Sum', 'count'
        elif 'Pos' in intlktype:
            self.title = 'Position '+intlktype[-1]
            ylabel, yunit = 'Position', 'm'
        elif 'Ang' in intlktype:
            self.title = 'Angulation '+intlktype[-1]
            ylabel, yunit = 'Angulation', 'm'
        self.plotItem.setLabel('left', ylabel, units=yunit)

        self._tooltips = [
            '{0}; Pos = {1:5.1f} m'.format(
                self.BPM_NICKNAMES[idx], self.BPM_POS[idx])
            for idx in range(len(self.BPM_NAMES))]
        self._c0 = 518.396  # SI length
        self._x_data = _np.asarray(self.BPM_POS)
        self._has_max = 'Sum' not in intlktype

        curve_idx = 0
        self.addChannel(
            y_channel='MinLim',
            x_channel='Pos', color='black',
            lineStyle=2, lineWidth=2,
            symbol='d', symbolSize=8)
        self.minlim = self.curveAtIndex(curve_idx)
        self._pen_min = None
        self._brush_min = None
        self.minlim.receiveXWaveform(self._x_data)
        self.y_data_min = _np.zeros(self._x_data.size)

        if self._has_max:
            curve_idx += 1
            self.addChannel(
                y_channel='MaxLim',
                x_channel='Pos', color='black',
                lineStyle=3, lineWidth=2,
                symbol='d', symbolSize=8)
            self.maxlim = self.curveAtIndex(curve_idx)
            self._pen_max = None
            self._brush_max = None
            self.maxlim.receiveXWaveform(self._x_data)
            self.y_data_max = _np.zeros(self._x_data.size)

        curve_idx += 1
        name = 'Sum' if 'Sum' in intlktype else intlktype
        color = 'red' if 'Y' in intlktype else 'blue' \
            if 'X' in intlktype else 'black'
        self.addChannel(
            y_channel=name,
            x_channel='Pos', color=color,
            lineStyle=1, lineWidth=3,
            symbol='o', symbolSize=8)
        self.meas = self.curveAtIndex(curve_idx)
        self._pen_meas = None
        self._brush_meas = None
        self.meas.receiveXWaveform(self._x_data)
        self.y_data_meas = _np.zeros(self._x_data.size)

        # connect sigMouseMoved
        self.plotItem.scene().sigMouseMoved.connect(self._handle_mouse_moved)

    @property
    def tooltips(self):
        """Return tooltips."""
        return self._tooltips

    @property
    def x_data(self):
        """Return x_data."""
        return self._x_data

    @property
    def y_data_meas(self):
        """Return y_data for meas curve."""
        return self._y_data_meas

    @y_data_meas.setter
    def y_data_meas(self, new):
        self._y_data_meas = self._set_y_data(new)
        self._redraw_curve(
            self.meas, self._y_data_meas, self._pen_meas, self._brush_meas)

    @property
    def symbols_meas(self):
        """Return symbols for meas curve."""
        return self._symbols_meas

    @symbols_meas.setter
    def symbols_meas(self, new):
        self._symbols_meas = new
        self._pen_meas, self._brush_meas = self._set_symbols(new)

    @property
    def y_data_min(self):
        """Return y_data for min curve."""
        return self._y_data_min

    @y_data_min.setter
    def y_data_min(self, new):
        self._y_data_min = self._set_y_data(new)
        self._redraw_curve(
            self.minlim, self._y_data_min, self._pen_min, self._brush_min)

    @property
    def symbols_min(self):
        """Return symbols for min curve."""
        return self._symbols_min

    @symbols_min.setter
    def symbols_min(self, new):
        self._symbols_min = new
        self._pen_min, self._brush_min = self._set_symbols(new)

    @property
    def y_data_max(self):
        """Return y_data for max curve."""
        return self._y_data_max

    @y_data_max.setter
    def y_data_max(self, new):
        self._y_data_max = self._set_y_data(new)
        self._redraw_curve(
            self.maxlim, self._y_data_max, self._pen_max, self._brush_max)

    @property
    def symbols_max(self):
        """Return symbols for max curve."""
        return self._symbols_max

    @symbols_max.setter
    def symbols_max(self, new):
        self._symbols_max = new
        self._pen_max, self._brush_max = self._set_symbols(new)

    def _set_y_data(self, new):
        if new is None or any([n is None for n in new]):
            return _np.array([0, ])
        return _np.array(new)

    def _set_symbols(self, new):
        if new:
            all_brush, all_pen = [], []
            for sym in new:
                if sym:
                    all_pen.append(self._ok_pen)
                    all_brush.append(self._ok_brush)
                else:
                    all_pen.append(self._nok_pen)
                    all_brush.append(self._nok_brush)
            pen = all_pen
            brush = all_brush
        else:
            pen = None
            brush = None
        return pen, brush

    def _redraw_curve(self, curve, ydata, symbolpen, symbolbrush):
        curve.receiveYWaveform(ydata)
        curve.opts['symbolPen'] = symbolpen
        curve.opts['symbolBrush'] = symbolbrush
        curve.redrawCurve()

    def _handle_mouse_moved(self, pos):
        """Show tooltip at mouse move."""
        posx = self.meas.scatter.mapFromScene(pos).x()
        posx = posx % self._c0
        ind = _np.argmin(_np.abs(_np.array(self._x_data)-posx))
        txt = self.tooltips[ind]
        QToolTip.showText(
            self.mapToGlobal(pos.toPoint()), txt, self, self.geometry(), 500)

    def mouseDoubleClickEvent(self, event):
        """Reimplement mouseDoubleClickEvent."""
        posx = self.meas.xData
        view = self.plotItem.getViewBox()
        pos = view.mapSceneToView(event.pos())
        idx = _np.argmin(_np.abs(posx-pos.x()))
        bpmname = self.BPM_NAMES[idx]
        self._open_detail(bpmname)
        super().mouseDoubleClickEvent(event)

    def _open_detail(self, bpmname):
        """Open BPM detail window."""
        run_newprocess(['sirius-hla-as-di-bpm.py', bpmname])


class _BaseGraphWidget(BaseObject, QWidget):
    """Power supply graph monitor widget."""

    INTLKTYPE = ''
    PROPTY_MEAS_DATA = ''
    PROPTY_MEAS_SYMB = ''
    PROPTY_MIN_DATA = ''
    PROPTY_MIN_SYMB = ''
    PROPTY_MAX_DATA = ''
    PROPTY_MAX_SYMB = ''

    propIntlkTypeChanged = Signal(str)
    propCompTypeChanged = Signal(str)
    refOrbChanged = Signal(_np.ndarray)

    def __init__(self, parent=None, prefix=_vaca_prefix):
        BaseObject.__init__(self, prefix)
        QWidget.__init__(self, parent)

        self._property_intlktype = 'Latch'
        self._property_comptype = 'General'
        self._plan = '' if 'Sum' in self.INTLKTYPE else self.INTLKTYPE[-1]
        self._plan = self._plan.lower()
        self._reforb = _np.zeros(len(self.BPM_NAMES), dtype=float)
        self.update_propty_reforb('ref_orb')

        self._setupUi()

        self._thread = _UpdateGraphThread(
            self.INTLKTYPE, self.PROPTY_MEAS_DATA, self.PROPTY_MEAS_SYMB,
            self.PROPTY_MIN_DATA, self.PROPTY_MIN_SYMB,
            self.PROPTY_MAX_DATA, self.PROPTY_MAX_SYMB,
            self._property_intlktype, self._property_comptype, self._reforb,
            prefix=self.prefix, parent=self)
        self.propIntlkTypeChanged.connect(self._thread.set_propintlktype)
        self.propCompTypeChanged.connect(self._thread.set_propcomptype)
        self.refOrbChanged.connect(self._thread.set_reforb)
        self._thread.dataChanged.connect(self._update_curve)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    @Slot(str)
    def update_propty_intlktype(self, text):
        """Update interlock type property."""
        self._property_intlktype = text
        self.propIntlkTypeChanged.emit(self._property_intlktype)

    @Slot(str)
    def update_propty_comptype(self, text):
        """Update comparision type property."""
        self._property_comptype = text
        self.propCompTypeChanged.emit(self._property_comptype)

    @Slot(str)
    def update_propty_reforb(self, text):
        """Update reference orbit property."""
        self._property_reforb = text
        if text.lower() == 'zero':
            self._reforb = _np.zeros(len(self.BPM_NAMES), dtype=float)
        elif self._plan:
            data = self.get_ref_orb(text)
            self._reforb = _np.array(data[self._plan], dtype=float)
        self.refOrbChanged.emit(self._reforb)

    def _setupUi(self):
        self.graph = Graph(self, self.INTLKTYPE)
        self.graph.setObjectName('graph')

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 6, 0, 0)
        lay.addWidget(self.graph, 0, 0)

        self.setStyleSheet('#graph{min-width:60em;min-height:12em;}')

    def _update_curve(self, curve_symb_data):
        curve, symb, data = curve_symb_data
        setattr(self.graph, 'symbols_'+curve, symb)
        setattr(self.graph, 'y_data_'+curve, data)

    def closeEvent(self, event):
        """Finish thread on close."""
        self._thread.exit_task()
        self._wait_thread()
        super().closeEvent(event)

    def _wait_thread(self):
        init = _time.time()
        try:
            while self._thread.isRunning():
                _time.sleep(0.1)
                if _time.time() - init > 10:
                    raise Exception('Thread will not leave')
        except RuntimeError:
            pass


class _UpdateGraphThread(BaseObject, QThread):
    """Update Graph Thread."""

    UPDATE_FREQ = 0.5  # [Hz]
    dataChanged = Signal(list)

    def __init__(self, intlktype, meas_data, meas_symb,
                 min_data, min_symb, max_data, max_symb,
                 propintlktype, propcomptype, reforb,
                 prefix='', parent=None):
        BaseObject.__init__(self, prefix)
        QThread.__init__(self, parent)

        self.intlktype = intlktype
        self.metric = intlktype[:-1].lower()
        self.meas_data = meas_data
        self.meas_symb = meas_symb
        self.min_data = min_data
        self.min_symb = min_symb
        self.max_data = max_data
        self.max_symb = max_symb
        self._propintlktype = propintlktype
        self._propcomptype = propcomptype
        self._reforb = reforb
        self._refmetric = _np.array(self.calc_intlk_metric(
            self._reforb, metric=self.metric))

        self._quit_task = False

    def set_propintlktype(self, new):
        """Update property intlktype."""
        self._propintlktype = new

    def set_propcomptype(self, new):
        """Update property comptype."""
        self._propcomptype = new

    def set_reforb(self, new):
        """Update reference orbit."""
        self._reforb = new
        self._refmetric = _np.array(self.calc_intlk_metric(
            self._reforb, metric=self.metric))

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Run task."""
        while not self._quit_task:
            _t0 = _time.time()
            self._update_data()
            _dt = _time.time() - _t0

            sleep = 1/self.UPDATE_FREQ - _dt
            if sleep > 0:
                _time.sleep(sleep)

    def _update_data(self):
        if self.meas_data:
            # symb meas
            if self.meas_symb:
                symb_propty = self.meas_symb[
                    self._propintlktype][self._propcomptype]
                if isinstance(symb_propty, dict):
                    for var in symb_propty['var']:
                        self._create_pvs(var)
                    vals = [_np.array(self._get_values(var))
                            for var in symb_propty['var']]
                    symb_values = list(symb_propty['op'](*vals))
                else:
                    self._create_pvs(symb_propty)
                    symb_values = self._get_values(symb_propty)
                symbols_meas = symb_values
            else:
                symbols_meas = None

            # data meas
            self._create_pvs(self.meas_data)
            vals = _np.array(self._get_values(self.meas_data), dtype=float)
            if self.metric in ['pos', 'ang']:
                vals -= self._refmetric
                vals *= self.CONV_NM2M
            else:
                # sum case
                vals *= self.monitsum2intlksum_factor
            y_data_meas = list(vals)

            self.dataChanged.emit(['meas', symbols_meas, y_data_meas])

        if self.min_data:
            # symb min
            self._create_pvs(self.min_data)
            if self.min_symb and self._propintlktype in self.min_symb:
                symb_propty = self.min_symb[self._propintlktype]
                if symb_propty:
                    self._create_pvs(symb_propty)
                    symbols_min = self._get_values(symb_propty)
                else:
                    symbols_min = None
            else:
                symbols_min = None

            # data min
            vals = _np.array(self._get_values(self.min_data), dtype=float)
            if self.metric in ['pos', 'ang']:
                vals -= self._refmetric
                vals *= self.CONV_NM2M
            y_data_min = list(vals)

            self.dataChanged.emit(['min', symbols_min, y_data_min])

        if self.max_data:
            # symb max
            self._create_pvs(self.max_data)
            if self.max_symb and self._propintlktype in self.max_symb:
                symb_propty = self.max_symb[self._propintlktype]
                if symb_propty:
                    self._create_pvs(symb_propty)
                    symbols_max = self._get_values(symb_propty)
                else:
                    symbols_max = None
            else:
                symbols_max = None

            # data max
            vals = _np.array(self._get_values(self.max_data), dtype=float)
            if self.metric in ['pos', 'ang']:
                vals -= self._refmetric
                vals *= self.CONV_NM2M
            y_data_max = list(vals)

            self.dataChanged.emit(['max', symbols_max, y_data_max])


class MinSumGraphWidget(_BaseGraphWidget):
    """MinSum Graph Widget."""

    INTLKTYPE = 'MinSum'
    PROPTY_MEAS_DATA = 'Sum-Mon'
    PROPTY_MEAS_SYMB = ''
    PROPTY_MIN_DATA = 'IntlkLmtMinSum-RB'
    PROPTY_MIN_SYMB = ''
    PROPTY_MAX_DATA = ''
    PROPTY_MAX_SYMB = ''


class PosXGraphWidget(_BaseGraphWidget):
    """Position Graph Widget."""

    INTLKTYPE = 'PosX'
    PROPTY_MEAS_DATA = 'IntlkPosX-Mon'
    PROPTY_MEAS_SYMB = {
        'Instantaneous': {
            'General': 'Intlk-Mon',
            'Upper': 'IntlkPosUpper-Mon',
            'Lower': 'IntlkPosLower-Mon',
            'Upper | Lower': {
                'var': ['IntlkPosUpper-Mon', 'IntlkPosLower-Mon'],
                'op': _np.logical_or},
        },
        'Latch': {
            'General': 'IntlkLtc-Mon',
            'Upper': 'IntlkPosUpperLtc-Mon',
            'Lower': 'IntlkPosLowerLtc-Mon',
            'Upper | Lower': {
                'var': ['IntlkPosUpperLtc-Mon', 'IntlkPosLowerLtc-Mon'],
                'op': _np.logical_or},
        },
    }
    PROPTY_MIN_DATA = 'IntlkLmtPosMinX-RB'
    PROPTY_MIN_SYMB = {
        'Instantaneous': 'IntlkPosLowerX-Mon',
        'Latch': 'IntlkPosLowerLtcX-Mon'}
    PROPTY_MAX_DATA = 'IntlkLmtPosMaxX-RB'
    PROPTY_MAX_SYMB = {
        'Instantaneous': 'IntlkPosUpperX-Mon',
        'Latch': 'IntlkPosUpperLtcX-Mon'}


class PosYGraphWidget(_BaseGraphWidget):
    """Position Graph Widget."""

    INTLKTYPE = 'PosY'
    PROPTY_MEAS_DATA = 'IntlkPosY-Mon'
    PROPTY_MEAS_SYMB = {
        'Instantaneous': {
            'General': 'Intlk-Mon',
            'Upper': 'IntlkPosUpper-Mon',
            'Lower': 'IntlkPosLower-Mon',
            'Upper | Lower': {
                'var': ['IntlkPosUpper-Mon', 'IntlkPosLower-Mon'],
                'op': _np.logical_or},
        },
        'Latch': {
            'General': 'IntlkLtc-Mon',
            'Upper': 'IntlkPosUpperLtc-Mon',
            'Lower': 'IntlkPosLowerLtc-Mon',
            'Upper | Lower': {
                'var': ['IntlkPosUpperLtc-Mon', 'IntlkPosLowerLtc-Mon'],
                'op': _np.logical_or},
        },
    }
    PROPTY_MIN_DATA = 'IntlkLmtPosMinY-RB'
    PROPTY_MIN_SYMB = {
        'Instantaneous': 'IntlkPosLowerY-Mon',
        'Latch': 'IntlkPosLowerLtcY-Mon',
    }
    PROPTY_MAX_DATA = 'IntlkLmtPosMaxY-RB'
    PROPTY_MAX_SYMB = {
        'Instantaneous': 'IntlkPosUpperY-Mon',
        'Latch': 'IntlkPosUpperLtcY-Mon',
    }


class AngXGraphWidget(_BaseGraphWidget):
    """Angulation Graph Widget."""

    INTLKTYPE = 'AngX'
    PROPTY_MEAS_DATA = 'IntlkAngX-Mon'
    PROPTY_MEAS_SYMB = {
        'Instantaneous': {
            'General': 'Intlk-Mon',
            'Upper': 'IntlkAngUpper-Mon',
            'Lower': 'IntlkAngLower-Mon',
            'Upper | Lower': {
                'var': ['IntlkAngUpper-Mon', 'IntlkAngLower-Mon'],
                'op': _np.logical_or},
        },
        'Latch': {
            'General': 'IntlkLtc-Mon',
            'Upper': 'IntlkAngUpperLtc-Mon',
            'Lower': 'IntlkAngLowerLtc-Mon',
            'Upper | Lower': {
                'var': ['IntlkAngUpperLtc-Mon', 'IntlkAngLowerLtc-Mon'],
                'op': _np.logical_or},
        },
    }
    PROPTY_MIN_DATA = 'IntlkLmtAngMinX-RB'
    PROPTY_MIN_SYMB = {
        'Instantaneous': 'IntlkAngLowerX-Mon',
        'Latch': 'IntlkAngLowerLtcX-Mon',
    }
    PROPTY_MAX_DATA = 'IntlkLmtAngMaxX-RB'
    PROPTY_MAX_SYMB = {
        'Instantaneous': 'IntlkAngUpperX-Mon',
        'Latch': 'IntlkAngUpperLtcX-Mon',
    }


class AngYGraphWidget(_BaseGraphWidget):
    """Angulation Graph Widget."""

    INTLKTYPE = 'AngY'
    PROPTY_MEAS_DATA = 'IntlkAngY-Mon'
    PROPTY_MEAS_SYMB = {
        'Instantaneous': {
            'General': 'Intlk-Mon',
            'Upper': 'IntlkAngUpper-Mon',
            'Lower': 'IntlkAngLower-Mon',
            'Upper | Lower': {
                'var': ['IntlkAngUpper-Mon', 'IntlkAngLower-Mon'],
                'op': _np.logical_or},
        },
        'Latch': {
            'General': 'IntlkLtc-Mon',
            'Upper': 'IntlkAngUpperLtc-Mon',
            'Lower': 'IntlkAngLowerLtc-Mon',
            'Upper | Lower': {
                'var': ['IntlkAngUpperLtc-Mon', 'IntlkAngLowerLtc-Mon'],
                'op': _np.logical_or},
        },
    }
    PROPTY_MIN_DATA = 'IntlkLmtAngMinY-RB'
    PROPTY_MIN_SYMB = {
        'Instantaneous': 'IntlkAngLowerY-Mon',
        'Latch': 'IntlkAngLowerLtcY-Mon',
    }
    PROPTY_MAX_DATA = 'IntlkLmtAngMaxY-RB'
    PROPTY_MAX_SYMB = {
        'Instantaneous': 'IntlkAngUpperY-Mon',
        'Latch': 'IntlkAngUpperLtcY-Mon',
    }
