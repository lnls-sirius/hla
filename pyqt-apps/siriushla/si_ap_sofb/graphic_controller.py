"""Control the Orbit Graphic Displnay."""

from datetime import datetime as _datetime
from functools import partial as _part
import numpy as _np
from pyqtgraph import mkBrush, mkPen
from PyQt5.QtWidgets import (
    QWidget, QFileDialog, QLabel, QCheckBox, QVBoxLayout,
    QHBoxLayout, QSpacerItem, QSizePolicy, QGroupBox, QFormLayout, QPushButton,
    QComboBox)
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QColor
from pydm.widgets import PyDMWaveformPlot
from siriushla.widgets import SiriusConnectionSignal
from siriuspy.csdevice.orbitcorr import get_consts

Consts = get_consts('SI')


class OrbitWidget(QWidget):

    def __init__(self, parent, prefix, ctrls, n):
        super(OrbitWidget, self).__init__(parent)
        self.num_controls = n
        self.controls = ctrls
        self.prefix = prefix
        self.setup_ui()

    def setup_ui(self):
        vbl = QVBoxLayout(self)

        self.graph_x = self._get_graph()
        vbl.addWidget(self.graph_x)
        self.graph_y = self._get_graph()
        vbl.addWidget(self.graph_y)

        self.controllers = []
        hbl = QHBoxLayout()
        vbl.addItem(hbl)
        hbl.addItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        for i in range(self.num_controls):
            cont = GraphicOrbitController(
                self, self.graph_x, self.graph_y,
                self.controls, self.prefix, i, self.num_controls)
            hbl.addWidget(cont)
            hbl.addItem(QSpacerItem(
                40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self.controllers.append(cont)

        for cur in self.graph_x.plotItem.curves[4:]:
            cur.setVisible(False)
        for cur in self.graph_y.plotItem.curves[4:]:
            cur.setVisible(False)

    def _get_graph(self):
        graph = PyDMWaveformPlot(self)
        graph.maxRedrawRate = 3
        graph.mouseEnabledX = True
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(255, 255, 255))
        graph.setShowLegend(True)
        graph.setAutoRangeX(True)
        graph.setAutoRangeY(True)
        graph.setMinXRange(0.0)
        graph.setMaxXRange(1.0)
        graph.plotItem.showButtons()
        return graph


class GraphicOrbitController(QWidget):
    """Control the Orbit Graphic Displnay."""

    DEFAULT_DIR = '/home/fac/sirius-iocs/si-ap-sofb'
    EXT = '.txt'
    EXT_FLT = 'Text Files (*.txt)'
    FMT = '{0:8.3g}'

    def __init__(
            self, parent, graphx, graphy, ctrls, prefix, index, num_controls):
        """Initialize the instance."""
        super().__init__(parent)
        self.last_dir = self.DEFAULT_DIR
        self.update_rate = 4  # Hz
        self.ctrls = ctrls
        self.prefix = prefix
        text = sorted(ctrls.keys())[0]
        self.idx = index
        self.num_controls = num_controls

        self.current_text = {'orb': text, 'ref': text}
        self.graphs = {'x': graphx, 'y': graphy}
        self.orbits = {
            'orb': {
                'x': _np.zeros(Consts.NR_BPMS, dtype=float),
                'y': _np.zeros(Consts.NR_BPMS, dtype=float)},
            'ref': {
                'x': _np.zeros(Consts.NR_BPMS, dtype=float),
                'y': _np.zeros(Consts.NR_BPMS, dtype=float)},
            }
        self.slots = {
            'orb': {
                'x': _part(self._update_orbit, 'orb', 'x'),
                'y': _part(self._update_orbit, 'orb', 'y')},
            'ref': {
                'x': _part(self._update_orbit, 'ref', 'x'),
                'y': _part(self._update_orbit, 'ref', 'y')}}

        self.offbrush = mkBrush(100, 100, 100)
        self.offpen = mkPen(100, 100, 100)
        cor = self.idx * 255
        cor //= self.num_controls
        rcor = QColor(255, cor, cor)
        bcor = QColor(cor, cor, 255)
        self.brush = {
            'x': mkBrush(bcor),
            'y': mkBrush(rcor)}
        self.pen = {
            'x': mkPen(bcor),
            'y': mkPen(rcor)}

        self.curve_data = dict()
        self.lab_avg = dict()
        self.lab_std = dict()
        self.set_data_value = dict()
        self.set_ave_value = dict()
        self.set_stdm_value = dict()
        self.set_stdp_value = dict()
        self.enbl_list = {
            'x': _np.ones(Consts.NR_BPMS, dtype=bool),
            'y': _np.ones(Consts.NR_BPMS, dtype=bool)}

        self.setup_ui()

        self.enbl_pvs = {
            'x': SiriusConnectionSignal(self.prefix+'BPMXEnblList-RB'),
            'y': SiriusConnectionSignal(self.prefix+'BPMYEnblList-RB')}
        for pln, sig in self.enbl_pvs.items():
            sig.new_value_signal[_np.ndarray].connect(
                _part(self._update_enable_list, pln))

        self.timer_update_stat = QTimer()
        self.timer_update_stat.timeout.connect(self._update_graphic)
        self.timer_update_stat.start(1000/self.update_rate)  # in miliseconds

        sig_x = self.ctrls[self.current_text['ref']]['x']['signal']
        sig_y = self.ctrls[self.current_text['ref']]['y']['signal']
        sig_x[_np.ndarray].connect(self.slots['ref']['x'])
        sig_y[_np.ndarray].connect(self.slots['ref']['y'])
        sig_x = self.ctrls[self.current_text['orb']]['x']['signal']
        sig_y = self.ctrls[self.current_text['orb']]['y']['signal']
        sig_x[_np.ndarray].connect(self.slots['orb']['x'])
        sig_y[_np.ndarray].connect(self.slots['orb']['y'])

        self.cbx_show.setChecked(not self.idx)

    def channels(self):
        return list(self.enbl_pvs.values())

    def setup_ui(self):
        hbl = QHBoxLayout(self)
        cbx = QCheckBox(self)
        hbl.addWidget(cbx)
        cbx.setChecked(True)
        self.cbx_show = cbx
        grpbx = QGroupBox("Line {0:d}".format(self.idx+1), self)
        hbl.addWidget(grpbx)
        fbl = QFormLayout(grpbx)

        lbl_orb = self._create_label('Show', grpbx)
        lbl_ref = self._create_label('as diff to:', grpbx)
        cbx_ref = self._create_combo_box(grpbx, 'ref')
        cbx_orb = self._create_combo_box(grpbx, 'orb')
        fbl.addRow(lbl_orb, cbx_orb)
        fbl.addRow(lbl_ref, cbx_ref)

        pb_save = QPushButton('Save diff to file', grpbx)
        pb_save.clicked.connect(self._save_difference)
        self.cbx_show.toggled.connect(pb_save.setEnabled)
        fbl.addRow(QLabel(grpbx), pb_save)

        lab = QLabel('Statistics', grpbx)
        lab.setAlignment(Qt.AlignCenter)
        fbl.addRow(lab)
        for pln in ('x', 'y'):
            wid = self._create_curves(pln)
            fbl.addRow(wid)

    def _create_combo_box(self, parent, orb_tp):
        combo = QComboBox(parent)
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setHorizontalStretch(0)
        sz_pol.setVerticalStretch(0)
        sz_pol.setHeightForWidth(combo.sizePolicy().hasHeightForWidth())
        combo.setSizePolicy(sz_pol)
        combo.setMinimumSize(QSize(0, 0))
        combo.setEditable(True)
        combo.setMaxVisibleItems(10)
        for name in sorted(self.ctrls.keys()):
            combo.addItem(name)
        combo.currentTextChanged.connect(_part(self._some_changed, orb_tp))
        combo.setCurrentIndex(0)
        self.cbx_show.toggled.connect(combo.setEnabled)
        return combo

    def _create_label(self, lab, parent):
        label = QLabel(lab, parent)
        sz_pol = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sz_pol.setHorizontalStretch(0)
        sz_pol.setVerticalStretch(0)
        sz_pol.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
        label.setSizePolicy(sz_pol)
        label.setMinimumSize(QSize(60, 0))
        label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        return label

    def _create_curves(self, pln):
        wid = QWidget(self)
        hbl = QHBoxLayout(wid)
        cbx = QCheckBox('{0:s}:'.format(pln.upper()), wid)
        cbx.setChecked(True)
        self.cbx_show.toggled.connect(cbx.setChecked)
        self.cbx_show.toggled.connect(cbx.setEnabled)

        hbl.addWidget(cbx)

        lab_avg = QLabel('0.000', wid)
        lab_avg.setAlignment(Qt.AlignCenter)
        lab_avg.setMinimumSize(QSize(120, 0))
        hbl.addWidget(lab_avg)
        self.lab_avg[pln] = lab_avg

        hbl.addWidget(QLabel(
            "<html><head/><body><p>&#177;</p></body></html>", wid))

        lab_std = QLabel('0.000', wid)
        lab_std.setMinimumSize(QSize(120, 0))
        lab_std.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab_std)
        self.lab_std[pln] = lab_std

        opts = dict(
            y_channel='ca://A', x_channel=self.prefix + 'PosS-Cte',
            name='Line {0:d}'.format(self.idx+1),
            color=self.pen[pln].color(),
            redraw_mode=2,
            lineStyle=1,
            lineWidth=2 if self.idx else 3,
            symbol='o',
            symbolSize=10)
        self.graphs[pln].addChannel(**opts)
        opts.update(name='', lineStyle=4, symbol=None)
        self.graphs[pln].addChannel(**opts)
        self.graphs[pln].addChannel(**opts)
        opts.update(lineStyle=2)
        self.graphs[pln].addChannel(**opts)
        self.graphs[pln].plotItem.legend.removeItem('')

        curves = self.graphs[pln].curveAtIndex(slice(-4, None, None))
        cdta, cstdm, cstdp, cave = curves
        self.cbx_show.toggled.connect(cdta.setVisible)
        for i, cur in enumerate(curves):
            cur.curve.setZValue(-4*self.idx - i)
            cur.scatter.setZValue(-4*self.idx - i)
            if i:
                cbx.toggled.connect(cur.setVisible)

        self.curve_data[pln] = cdta
        self.set_data_value[pln] = cdta.receiveYWaveform
        self.set_ave_value[pln] = cave.receiveYWaveform
        self.set_stdm_value[pln] = cstdm.receiveYWaveform
        self.set_stdp_value[pln] = cstdp.receiveYWaveform

        return wid

    def _some_changed(self, orb_tp, text):
        slot_x = self.slots[orb_tp]['x']
        slot_y = self.slots[orb_tp]['y']

        sig_x = self.ctrls[self.current_text[orb_tp]]['x']['signal']
        sig_y = self.ctrls[self.current_text[orb_tp]]['y']['signal']
        sig_x[_np.ndarray].disconnect(slot_x)
        sig_y[_np.ndarray].disconnect(slot_y)

        self.current_text[orb_tp] = text
        sig_x = self.ctrls[text]['x']['signal']
        sig_y = self.ctrls[text]['y']['signal']
        sig_x[_np.ndarray].connect(slot_x)
        sig_y[_np.ndarray].connect(slot_y)

        slot_x(self.ctrls[text]['x']['getvalue']())
        slot_y(self.ctrls[text]['y']['getvalue']())

    def _update_enable_list(self, pln, array):
        enbl_list = _np.array(array, dtype=bool)
        brush = self.brush[pln]
        pen = self.pen[pln]
        trace = self.curve_data[pln]
        mask_brush = [(brush if v else self.offbrush) for v in enbl_list]
        mask_pen = [(pen if v else self.offpen) for v in enbl_list]
        trace.opts['symbolBrush'] = mask_brush
        trace.opts['symbolPen'] = mask_pen
        self.enbl_list[pln] = enbl_list
        if not self.timer_update_stat.isActive():
            self._update_graphic(pln)

    def _update_orbit(self, orb_tp, pln, orb):
        self.orbits[orb_tp][pln] = orb
        if not self.timer_update_stat.isActive():
            self._update_graphic(pln)

    def _update_graphic(self, pln=None):
        unit = 1/1000  # um
        pln = ('x', 'y') if pln is None else (pln, )
        for pln in pln:
            if not self.curve_data[pln].isVisible():
                return
            diff = unit * (self.orbits['orb'][pln] - self.orbits['ref'][pln])
            enbl_list = self.enbl_list[pln]
            mask = diff[enbl_list]
            ave = float(mask.mean())
            std = float(mask.std(ddof=1))

            self.lab_avg[pln].setText(self.FMT.format(ave))
            self.lab_std[pln].setText(self.FMT.format(std))
            ave = _np.array(len(diff)*[ave])
            self.set_data_value[pln](diff)
            self.set_ave_value[pln](ave)
            self.set_stdm_value[pln](ave-std)
            self.set_stdp_value[pln](ave+std)

    def _save_difference(self):
        diffx = self.orbits['orb']['x'] - self.orbits['ref']['x']
        diffy = self.orbits['orb']['y'] - self.orbits['ref']['y']
        header = '# ' + _datetime.now().strftime('%Y/%M/%d-%H:%M:%S') + '\n'
        filename = QFileDialog.getSaveFileName(
                            caption='Define a File Name to Save the Orbit',
                            directory=self.last_dir,
                            filter=self.EXT_FLT)
        fname = filename[0]
        fname += '' if fname.endswith(self.EXT) else self.EXT
        _np.savetxt(fname, _np.vstack([diffx, diffy]).T, header=header)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + pref+'SI-Glob:AP-SOFB:'
    pvs = [
        'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
        'OrbitOfflineX-RB', 'OrbitOfflineY-RB',
        'OrbitRefX-RB', 'OrbitRefY-RB']
    chans = []
    for pv in pvs:
        chans.append(SiriusConnectionSignal(prefix+pv))
    win._channels = chans
    ctrls = {
        'Online Orbit': {
            'x': {
                'signal': chans[0].new_value_signal,
                'getvalue': chans[0].getvalue},
            'y': {
                'signal': chans[1].new_value_signal,
                'getvalue': chans[1].getvalue}},
        'Offline Orbit': {
            'x': {
                'signal': chans[2].new_value_signal,
                'getvalue': chans[2].getvalue},
            'y': {
                'signal': chans[3].new_value_signal,
                'getvalue': chans[3].getvalue}},
        'Reference Orbit': {
            'x': {
                'signal': chans[4].new_value_signal,
                'getvalue': chans[4].getvalue},
            'y': {
                'signal': chans[5].new_value_signal,
                'getvalue': chans[5].getvalue}}}
    wid = OrbitWidget(win, prefix, ctrls, 3)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
