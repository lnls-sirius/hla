"""Control the Orbit Graphic Displnay."""

from datetime import datetime as _datetime
from functools import partial as _part
import numpy as _np
from pyqtgraph import mkBrush, mkPen, InfiniteLine
from qtpy.QtWidgets import QWidget, QFileDialog, QLabel, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QSizePolicy, QGroupBox, \
    QFormLayout, QPushButton, QComboBox
from qtpy.QtCore import QSize, Qt, QTimer, QThread, Signal
from qtpy.QtGui import QColor
from pydm.widgets import PyDMWaveformPlot
from siriushla.widgets import SiriusConnectionSignal
import siriuspy.csdevice.orbitcorr as _csorb


class BaseWidget(QWidget):

    def __init__(self, parent, prefix, ctrls, names, is_orb, acc='SI'):
        super(BaseWidget, self).__init__(parent)
        self.line_names = names
        self.controls = ctrls
        self.acc = acc
        self.update_rate = 2.1  # Hz
        self.timer = QTimer()
        self.prefix = prefix
        self.is_orb = is_orb
        self.setup_ui()
        self.timer.start(1000/self.update_rate)

    def setup_ui(self):
        vbl = QVBoxLayout(self)

        graphs = {'x': self._get_graph(), 'y': self._get_graph()}
        vbl.addWidget(graphs['x'])
        vbl.addWidget(graphs['y'])

        self.controllers = []
        self.hbl = QHBoxLayout()
        vbl.addItem(self.hbl)
        self.hbl.addStretch(1)
        for i, _ in enumerate(self.line_names):
            cont = GraphicController(
                self, graphs, self.controls, self.prefix, i,
                self.line_names, self.is_orb, self.acc)
            self.hbl.addWidget(cont)
            self.hbl.addStretch(1)
            self.controllers.append(cont)
            self.timer.timeout.connect(cont.updater.update_graphic)

        for gr in graphs.values():
            for cur in gr.plotItem.curves[4:]:
                cur.setVisible(False)

    def _get_graph(self):
        graph = PyDMWaveformPlot(self)
        graph.maxRedrawRate = 2
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


class GraphicController(QWidget):
    """Control the Orbit Graphic Displnay."""
    DEFAULT_DIR = '/home/fac/sirius-iocs/si-ap-sofb'
    EXT = '.txt'
    EXT_FLT = 'Text Files (*.txt)'

    def __init__(
            self, parent, graphs, ctrls, prefix, index, names, is_orb,
            acc='SI'):
        """Initialize the instance."""
        super().__init__(parent)
        self.last_dir = self.DEFAULT_DIR
        self.prefix = prefix
        self.acc = acc
        self.idx = index
        self.line_names = names
        self.is_orb = is_orb
        self.updater = UpdateGraphThread(ctrls, is_orb, acc)

        self.graphs = graphs

        self.offbrush = mkBrush(100, 100, 100)
        self.offpen = mkPen(100, 100, 100)
        cor = self.idx * 255
        cor //= len(self.line_names)
        rcor = QColor(255, cor, cor)
        bcor = QColor(cor, cor, 255)
        self.brush = {'x': mkBrush(bcor), 'y': mkBrush(rcor)}
        self.pen = {'x': mkPen(bcor), 'y': mkPen(rcor)}

        self.curve_data = dict()

        self.setup_ui()

        prefx, prefy = ('BPMX', 'BPMY') if self.is_orb else ('CH', 'CV')
        self.enbl_pvs = {
            'x': SiriusConnectionSignal(self.prefix+prefx+'EnblList-RB'),
            'y': SiriusConnectionSignal(self.prefix+prefy+'EnblList-RB')}
        for pln, sig in self.enbl_pvs.items():
            sig.new_value_signal[_np.ndarray].connect(
                _part(self._update_enable_list, pln))

        self.updater.start()

        self.cbx_show.setChecked(not self.idx)

    def channels(self):
        return list(self.enbl_pvs.values())

    def setup_ui(self):
        hbl = QHBoxLayout(self)
        cbx = QCheckBox(self)
        hbl.addWidget(cbx)
        cbx.setChecked(True)
        self.cbx_show = cbx
        self.cbx_show.toggled.connect(self.updater.set_visible)

        grpbx = QGroupBox(self.line_names[self.idx], self)
        hbl.addWidget(grpbx)
        fbl = QFormLayout(grpbx)

        if self.is_orb:
            lbl_orb = self._create_label('Show', grpbx)
            lbl_ref = self._create_label('as diff to:', grpbx)
            cbx_ref = self._create_combo_box(grpbx, 'ref')
            cbx_orb = self._create_combo_box(grpbx, 'val')
            fbl.addRow(lbl_orb, cbx_orb)
            fbl.addRow(lbl_ref, cbx_ref)
            self.combo = {'ref': cbx_ref, 'val': cbx_orb}

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
        for name in sorted(self.updater.ctrls.keys()):
            combo.addItem(name)
        combo.addItem('Zero')
        combo.currentTextChanged.connect(
            _part(self.updater.some_changed, orb_tp))
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

        lab_avg = Label('0.000', wid)
        self.updater.ave[pln].connect(lab_avg.setFloat)
        lab_avg.setAlignment(Qt.AlignCenter)
        lab_avg.setMinimumSize(QSize(120, 0))
        hbl.addWidget(lab_avg)

        hbl.addWidget(QLabel(
            "<html><head/><body><p>&#177;</p></body></html>", wid))

        lab_std = Label('0.000', wid)
        self.updater.std[pln].connect(lab_std.setFloat)
        lab_std.setMinimumSize(QSize(120, 0))
        lab_std.setAlignment(Qt.AlignCenter)
        hbl.addWidget(lab_std)

        opts = self._get_curve_opts(pln)
        self.graphs[pln].addChannel(**opts)
        pen = mkPen(opts['color'], width=opts['lineWidth'])
        pen.setStyle(4)
        cpstd = InfiniteLine(pos=0.0, pen=pen, angle=0)
        cmstd = InfiniteLine(pos=0.0, pen=pen, angle=0)
        pen.setStyle(2)
        cave = InfiniteLine(pos=0.0, pen=pen, angle=0)
        self.graphs[pln].addItem(cpstd)
        self.graphs[pln].addItem(cmstd)
        self.graphs[pln].addItem(cave)
        self.graphs[pln].plotItem.legend.removeItem('')

        cdta = self.graphs[pln].curveAtIndex(slice(-1, None, None))[0]
        self.cbx_show.toggled.connect(cdta.setVisible)
        cdta.curve.setZValue(-4*self.idx)
        cdta.scatter.setZValue(-4*self.idx)
        for i, cur in enumerate((cpstd, cmstd, cave), 1):
            cbx.toggled.connect(cur.setVisible)
            cur.setZValue(-4*self.idx - i)

        self.curve_data[pln] = cdta
        self.updater.data_sig[pln].connect(cdta.receiveYWaveform)
        self.updater.ave[pln].connect(cave.setValue)
        self.updater.ave_pstd[pln].connect(cpstd.setValue)
        self.updater.ave_mstd[pln].connect(cmstd.setValue)
        return wid

    def _get_curve_opts(self, pln):
        pref = 'BPM' if self.is_orb else 'CH' if pln == 'x' else 'CV'
        opts = dict(
            y_channel='ca://A',
            x_channel=self.prefix + pref + 'PosS-Cte',
            name=self.line_names[self.idx],
            color=self.pen[pln].color(),
            redraw_mode=2,
            lineStyle=1,
            lineWidth=2 if self.idx else 3,
            symbol='o',
            symbolSize=10)
        return opts

    def _update_enable_list(self, pln, array):
        enbl_list = _np.array(array, dtype=bool)
        brush = self.brush[pln]
        pen = self.pen[pln]
        trace = self.curve_data[pln]
        mask_brush = [(brush if v else self.offbrush) for v in enbl_list]
        mask_pen = [(pen if v else self.offpen) for v in enbl_list]
        trace.opts['symbolBrush'] = mask_brush
        trace.opts['symbolPen'] = mask_pen
        self.updater.set_enbl_list(pln, enbl_list)

    def _save_difference(self):
        valx = self.updater.vectors['val']['x']
        refx = self.updater.vectors['ref']['x']
        valy = self.updater.vectors['val']['y']
        refy = self.updater.vectors['ref']['y']
        if None in (valx, refx, valy, refy):
            return
        diffx = valx - refx
        diffy = valy - refy
        header = '# ' + _datetime.now().strftime('%Y/%M/%d-%H:%M:%S') + '\n'
        filename = QFileDialog.getSaveFileName(
            caption='Define a File Name to Save the Orbit',
            directory=self.last_dir, filter=self.EXT_FLT)
        fname = filename[0]
        fname += '' if fname.endswith(self.EXT) else self.EXT
        _np.savetxt(fname, _np.vstack([diffx, diffy]).T, header=header)


class Label(QLabel):
    FMT = '{0:8.3g}'

    def setFloat(self, text):
        super().setText(self.FMT.format(text))


class UpdateGraphThread(QThread):
    """Thread to update graphics."""
    avex = Signal([float])
    stdx = Signal([float])
    ave_pstdx = Signal([float])
    ave_mstdx = Signal([float])
    data_sigx = Signal([_np.ndarray])
    avey = Signal([float])
    stdy = Signal([float])
    ave_pstdy = Signal([float])
    ave_mstdy = Signal([float])
    data_sigy = Signal([_np.ndarray])

    def __init__(self, ctrls, is_orb, acc='SI'):
        """Initialize object."""
        super().__init__()
        self.moveToThread(self)
        self.ctrls = ctrls
        self.acc = acc
        self.consts = _csorb.get_consts(acc)
        self.is_orb = is_orb
        self._isvisible = True
        text = sorted(ctrls)[0]
        self.current_text = {'val': text, 'ref': text}
        self.ave = {'x': self.avex, 'y': self.avey}
        self.std = {'x': self.stdx, 'y': self.stdy}
        self.ave_pstd = {'x': self.ave_pstdx, 'y': self.ave_pstdy}
        self.ave_mstd = {'x': self.ave_mstdx, 'y': self.ave_mstdy}
        self.data_sig = {'x': self.data_sigx, 'y': self.data_sigy}
        self.slots = {
            'val': {
                'x': _part(self._update_vectors, 'val', 'x'),
                'y': _part(self._update_vectors, 'val', 'y')},
            'ref': {
                'x': _part(self._update_vectors, 'ref', 'x'),
                'y': _part(self._update_vectors, 'ref', 'y')}}
        szx = self.consts.NR_BPMS if self.is_orb else self.consts.NR_CH
        szy = self.consts.NR_BPMS if self.is_orb else self.consts.NR_CV
        self.vectors = {
            'val': {
                'x': _np.zeros(szx, dtype=float),
                'y': _np.zeros(szy, dtype=float)},
            'ref': {
                'x': _np.zeros(szx, dtype=float),
                'y': _np.zeros(szy, dtype=float)}}
        self.enbl_list = {
            'x': _np.ones(szx, dtype=bool),
            'y': _np.ones(szy, dtype=bool)}
        sig_x = self.ctrls[self.current_text['ref']]['x']['signal']
        sig_y = self.ctrls[self.current_text['ref']]['y']['signal']
        sig_x[_np.ndarray].connect(self.slots['ref']['x'])
        sig_y[_np.ndarray].connect(self.slots['ref']['y'])
        sig_x = self.ctrls[self.current_text['val']]['x']['signal']
        sig_y = self.ctrls[self.current_text['val']]['y']['signal']
        sig_x[_np.ndarray].connect(self.slots['val']['x'])
        sig_y[_np.ndarray].connect(self.slots['val']['y'])

    def some_changed(self, orb_tp, text):
        slot_x = self.slots[orb_tp]['x']
        slot_y = self.slots[orb_tp]['y']

        if self.current_text[orb_tp] != 'Zero':
            sig_x = self.ctrls[self.current_text[orb_tp]]['x']['signal']
            sig_y = self.ctrls[self.current_text[orb_tp]]['y']['signal']
            sig_x[_np.ndarray].disconnect(slot_x)
            sig_y[_np.ndarray].disconnect(slot_y)

        self.current_text[orb_tp] = text
        if self.current_text[orb_tp] != 'Zero':
            sig_x = self.ctrls[text]['x']['signal']
            sig_y = self.ctrls[text]['y']['signal']
            sig_x[_np.ndarray].connect(slot_x)
            sig_y[_np.ndarray].connect(slot_y)
            slot_y(self.ctrls[text]['y']['getvalue']())
            slot_x(self.ctrls[text]['x']['getvalue']())
        else:
            if self.vectors[orb_tp]['x'] is not None:
                slot_x(self.vectors[orb_tp]['x']*0)
            if self.vectors[orb_tp]['y'] is not None:
                slot_y(self.vectors[orb_tp]['y']*0)

    def set_visible(self, boo):
        self._isvisible = boo

    def set_enbl_list(self, pln, enbls):
        self.enbl_list[pln] = enbls

    def _update_vectors(self, orb_tp, pln, orb):
        self.vectors[orb_tp][pln] = orb

    def update_graphic(self, pln=None):
        if not self._isvisible:
            return
        unit = 1/1000 if self.is_orb else 1  # um, urad
        pln = ('x', 'y') if pln is None else (pln, )
        for pln in pln:
            orb = self.vectors['val'][pln]
            ref = self.vectors['ref'][pln]
            if orb is None or ref is None:
                return
            diff = unit * (orb - ref)
            if self.enbl_list[pln] is not None:
                mask = diff[self.enbl_list[pln]]
            else:
                mask = diff
            ave = float(mask.mean())
            std = float(mask.std(ddof=1))

            self.data_sig[pln].emit(diff)
            self.ave[pln].emit(ave)
            self.std[pln].emit(std)
            self.ave_pstd[pln].emit(ave-std)
            self.ave_mstd[pln].emit(ave+std)


class OrbitWidget(BaseWidget):

    def __init__(self, parent, prefix, ctrls=dict(), acc='SI'):
        self._chans = []
        if not ctrls:
            self._chans, ctrls = self.get_default_ctrls(prefix)

        names = ['Line {0:d}'.format(i+1) for i in range(2)]
        super().__init__(parent, prefix, ctrls, names, True, acc)

        self.controllers[0].updater.some_changed('val', 'Online Orbit')
        self.controllers[0].updater.some_changed('ref', 'Reference Orbit')
        self.controllers[0].combo['val'].setCurrentIndex(3)
        self.controllers[0].combo['ref'].setCurrentIndex(4)

    def channels(self):
        return self._chans

    @staticmethod
    def get_default_ctrls(prefix):
        pvs = [
            'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
            'OrbitSmoothSinglePassX-Mon', 'OrbitSmoothSinglePassY-Mon',
            'OrbitMultiTurnX-Mon', 'OrbitMultiTurnY-Mon',
            'OrbitOfflineX-RB', 'OrbitOfflineY-RB',
            'OrbitRefX-RB', 'OrbitRefY-RB',
            'BPMOffsetsX-Mon', 'BPMOffsetsY-Mon']
        chans = [SiriusConnectionSignal(prefix+pv) for pv in pvs]
        ctrls = dict()
        orbs = [
            'Online Orbit', 'SinglePass', 'MultiTurn Orbit',
            'Offline Orbit', 'Reference Orbit', 'BPMs Offset']
        pvs = iter(chans)
        for orb in orbs:
            pvi = next(pvs)
            pvj = next(pvs)
            ctrls[orb] = {
                'x': {
                    'signal': pvi.new_value_signal,
                    'getvalue': pvi.getvalue},
                'y': {
                    'signal': pvj.new_value_signal,
                    'getvalue': pvj.getvalue}}
        return chans, ctrls


class CorrectorsWidget(BaseWidget):

    def __init__(self, parent, prefix, ctrls=dict(), acc='SI'):
        self._chans = []
        if not ctrls:
            self._chans, ctrls = self.get_default_ctrls(prefix)

        names = ('DeltaKicks', 'Kicks')
        super().__init__(parent, prefix, ctrls, names, False, acc)

        self.controllers[0].updater.some_changed('val', 'Delta Kicks')
        self.controllers[0].updater.some_changed('ref', 'Zero')
        self.controllers[1].updater.some_changed('val', 'Kicks')
        self.controllers[1].updater.some_changed('ref', 'Zero')

        self.add_kicklimits_curves()

    def add_kicklimits_curves(self):
        grpbx = QGroupBox('Show Kick Limits', self)
        vbl = QVBoxLayout(grpbx)
        self.hbl.addWidget(grpbx)
        self.hbl.addStretch(1)
        chcbox1 = QCheckBox('Kicks', grpbx)
        chcbox2 = QCheckBox('Delta Kicks', grpbx)
        chcbox1.setChecked(True)
        chcbox2.setChecked(True)
        vbl.addWidget(chcbox1)
        vbl.addWidget(chcbox2)

        chcboxs = (chcbox1, chcbox2)
        names = ('Max Kicks', 'Max dKickx')
        pvs = ('MaxKick', 'MaxDeltaKick')
        stys = (4, 2)
        wids = (3, 2)
        plns = ('x', 'y')
        corrs = ('CH', 'CV')
        for chb, name, pvi, sty, wid in zip(chcboxs, names, pvs, stys, wids):
            pen = mkPen(QColor(0, 0, 0))
            pen.setStyle(sty)
            pen.setWidth(wid)
            for pln, corr in zip(plns, corrs):
                maxkick = InfiniteLine(
                    pos=0.0, pen=pen, angle=0, name=name)
                minkick = NegativeLine(pos=0.0, pen=pen, angle=0)
                self.controllers[0].graphs[pln].addItem(maxkick)
                self.controllers[0].graphs[pln].addItem(minkick)
                chan = SiriusConnectionSignal(self.prefix + pvi + corr + '-RB')
                self._chans.append(chan)
                chan.new_value_signal[float].connect(maxkick.setValue)
                chan.new_value_signal[float].connect(minkick.setValue)
                chb.toggled.connect(maxkick.setVisible)
                chb.toggled.connect(minkick.setVisible)

    def channels(self):
        return self._chans

    @staticmethod
    def get_default_ctrls(prefix):
        chans = [
            SiriusConnectionSignal(prefix+'DeltaKicksCH-Mon'),
            SiriusConnectionSignal(prefix+'DeltaKicksCV-Mon'),
            SiriusConnectionSignal(prefix+'KicksCH-Mon'),
            SiriusConnectionSignal(prefix+'KicksCV-Mon')]
        ctrls = {
            'Delta Kicks': {
                'x': {
                    'signal': chans[0].new_value_signal,
                    'getvalue': chans[0].getvalue},
                'y': {
                    'signal': chans[1].new_value_signal,
                    'getvalue': chans[1].getvalue}},
            'Kicks': {
                'x': {
                    'signal': chans[2].new_value_signal,
                    'getvalue': chans[2].getvalue},
                'y': {
                    'signal': chans[3].new_value_signal,
                    'getvalue': chans[3].getvalue}},
            }
        return chans, ctrls


class NegativeLine(InfiniteLine):
    def __init__(self, pos=None, **kwargs):
        if pos is not None:
            pos *= -1
        super().__init__(pos=pos, **kwargs)

    def setValue(self, value):
        super().setValue(-value)


def _main(prefix):
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + prefix + 'SI-Glob:AP-SOFB:'
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
