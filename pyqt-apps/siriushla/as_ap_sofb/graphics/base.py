"""Control the Orbit Graphic Displnay."""

import pathlib as _pathlib
from datetime import datetime as _datetime
from functools import partial as _part
import numpy as _np
from pyqtgraph import mkBrush, mkPen, InfiniteLine, functions
from qtpy.QtWidgets import QWidget, QFileDialog, QLabel, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QSizePolicy, QGroupBox, \
    QFormLayout, QPushButton, QComboBox
from qtpy.QtCore import QSize, Qt, QTimer, QThread, Signal, QObject
from qtpy.QtGui import QColor, QFont
from pydm.widgets import PyDMWaveformPlot
from siriushla.widgets import SiriusConnectionSignal
from siriuspy.csdevice.orbitcorr import OrbitCorrDev


class BaseWidget(QWidget):
    DEFAULT_DIR = _pathlib.Path.home().as_posix()
    EXT = '.txt'
    EXT_FLT = 'Text Files (*.txt)'

    def __init__(self, parent, prefix, ctrls, names, is_orb, acc='SI'):
        super(BaseWidget, self).__init__(parent)
        self.line_names = names
        self.controls = ctrls
        self._csorb = OrbitCorrDev(acc)
        self._isring = self._csorb.acc_idx in self._csorb.Rings
        self.update_rate = 2.1  # Hz
        self.last_dir = self.DEFAULT_DIR
        self.prefix = prefix
        self.is_orb = is_orb
        self.timer = QTimer()
        self.thread = QThread()
        self.updater = []
        for _ in range(2):
            upd = UpdateGraph(ctrls, is_orb, acc)
            upd.moveToThread(self.thread)
            self.timer.timeout.connect(upd.update_graphic)
            self.updater.append(upd)

        self.setupui()
        self.connect_signals()

        prefx, prefy = ('BPMX', 'BPMY') if self.is_orb else ('CH', 'CV')
        self.enbl_pvs = {
            'x': SiriusConnectionSignal(self.prefix+prefx+'EnblList-RB'),
            'y': SiriusConnectionSignal(self.prefix+prefy+'EnblList-RB')}
        for pln, signal in self.enbl_pvs.items():
            sig = signal.new_value_signal[_np.ndarray]
            sig.connect(_part(self._update_enable_list, pln))
            for upd in self.updater:
                sig.connect(_part(upd.set_enbl_list, pln))

        self.enbl_pvs_set = {
            'x': SiriusConnectionSignal(self.prefix+prefx+'EnblList-SP'),
            'y': SiriusConnectionSignal(self.prefix+prefy+'EnblList-SP')}

        self.thread.start()
        self.timer.start(1000/self.update_rate)

    @property
    def acc(self):
        return self._csorb.acc

    @property
    def acc_idx(self):
        return self._csorb.acc_idx

    @property
    def isring(self):
        return self._isring

    def channels(self):
        chans = list(self.enbl_pvs.values())
        chans.extend(self.enbl_pvs_set.values())
        return chans

    def setupui(self):
        vbl = QVBoxLayout(self)

        graphx = self.uigetgraph('x')
        graphy = self.uigetgraph('y')
        suf = 'Orbit' if self.is_orb else 'Correctors'
        lab = QLabel('Horizontal ' + suf, self)
        lab.setStyleSheet("font: 20pt \"Sans Serif\";\nfont-weight: bold;")
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.addWidget(graphx)
        vbl.addSpacing(30)
        lab = QLabel('Vertical ' + suf, self)
        lab.setStyleSheet("font: 20pt \"Sans Serif\";\nfont-weight: bold;")
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.addWidget(graphy)
        self.graph = {'x': graphx, 'y': graphy}

        self.hbl = QHBoxLayout()
        vbl.addItem(self.hbl)
        self.hbl.addStretch(1)
        for i, _ in enumerate(self.line_names):
            grpbx = self.uicreate_groupbox(i)
            grpbx.setObjectName('GroupBox'+str(i))
            self.hbl.addWidget(grpbx)
            self.hbl.addStretch(1)

    def uigetgraph(self, pln):
        graph = Graph(self)
        graph.doubleclick.connect(_part(self._set_enable_list, pln))

        labsty = {'font-size': '20pt'}
        graph.setLabel('bottom', text='BPM position', units='m', **labsty)
        lab = 'Orbit' if self.is_orb else 'Kick Angle'
        unit = 'm' if self.is_orb else 'rad'
        graph.setLabel('left', text=lab, units=unit, **labsty)

        pref = 'BPM' if self.is_orb else 'CH' if pln == 'x' else 'CV'
        for i, lname in enumerate(self.line_names):
            opts = dict(
                y_channel='ca://A',
                x_channel=self.prefix + pref + 'PosS-Cte',
                name=lname,
                color=self._get_color(pln, i),
                redraw_mode=2,
                lineStyle=1,
                lineWidth=2 if i else 3,
                symbol='o',
                symbolSize=10)
            graph.addChannel(**opts)
            pen = mkPen(opts['color'], width=opts['lineWidth'])
            pen.setStyle(4)
            cpstd = InfiniteLine(pos=0.0, pen=pen, angle=0)
            self.updater[i].ave_pstd[pln].connect(cpstd.setValue)
            graph.addItem(cpstd)
            cmstd = InfiniteLine(pos=0.0, pen=pen, angle=0)
            self.updater[i].ave_mstd[pln].connect(cmstd.setValue)
            graph.addItem(cmstd)
            pen.setStyle(2)
            cave = InfiniteLine(pos=0.0, pen=pen, angle=0)
            self.updater[i].ave[pln].connect(cave.setValue)
            graph.addItem(cave)
            cdta = graph.curveAtIndex(-1)
            self.updater[i].data_sig[pln].connect(cdta.receiveYWaveform)
            cdta.setVisible(not i)
            cdta.curve.setZValue(-4*i)
            cdta.scatter.setZValue(-4*i)
            for j, cur in enumerate((cpstd, cmstd, cave), 1):
                cur.setZValue(-4*i - j)
                cur.setVisible(not i)
            graph.plotItem.legend.removeItem('')
        return graph

    def uicreate_groupbox(self, idx):
        grpbx = QGroupBox(self.line_names[idx], self)
        grpbx.setCheckable(True)
        grpbx.setChecked(not idx)
        grpbx.toggled.connect(self.updater[idx].set_visible)
        fbl = QFormLayout(grpbx)

        if self.is_orb:
            lbl_orb = self.uicreate_label('Show', grpbx)
            lbl_ref = self.uicreate_label('as diff to:', grpbx)
            cbx_ref = self.uicreate_combobox(grpbx, 'ref', idx)
            cbx_orb = self.uicreate_combobox(grpbx, 'val', idx)
            fbl.addRow(lbl_orb, cbx_orb)
            fbl.addRow(lbl_ref, cbx_ref)

            pb_save = QPushButton('Save diff to file', grpbx)
            pb_save.clicked.connect(_part(self._save_difference, idx))
            fbl.addRow(QLabel(grpbx), pb_save)

        lab = QLabel('Statistics', grpbx)
        lab.setAlignment(Qt.AlignCenter)
        fbl.addRow(lab)
        unit = 'm' if self.is_orb else 'rad'
        for pln in ('x', 'y'):
            wid = QWidget(grpbx)
            fbl.addRow(wid)
            hbl = QHBoxLayout(wid)
            cbx = QCheckBox('{0:s}:'.format(pln.upper()), wid)
            cbx.setObjectName(pln + 'checkbox')
            cbx.setChecked(True)
            hbl.addWidget(cbx)

            lab_avg = Label(unit, '0.000', wid)
            self.updater[idx].ave[pln].connect(lab_avg.setFloat)
            lab_avg.setAlignment(Qt.AlignCenter)
            lab_avg.setMinimumSize(QSize(120, 0))
            hbl.addWidget(lab_avg)
            hbl.addWidget(QLabel(
                "<html><head/><body><p>&#177;</p></body></html>", wid))
            lab_std = Label(unit, '0.000', wid)
            self.updater[idx].std[pln].connect(lab_std.setFloat)
            lab_std.setMinimumSize(QSize(120, 0))
            lab_std.setAlignment(Qt.AlignCenter)
            hbl.addWidget(lab_std)
        return grpbx

    def uicreate_combobox(self, parent, orb_tp, idx):
        combo = QComboBox(parent)
        combo.setObjectName('ComboBox_' + orb_tp + str(idx))
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setHorizontalStretch(0)
        sz_pol.setVerticalStretch(0)
        sz_pol.setHeightForWidth(combo.sizePolicy().hasHeightForWidth())
        combo.setSizePolicy(sz_pol)
        combo.setMinimumSize(QSize(0, 0))
        combo.setEditable(True)
        combo.setMaxVisibleItems(10)
        for name in sorted(self.controls.keys()):
            combo.addItem(name)
        combo.addItem('Zero')
        combo.currentTextChanged.connect(_part(
            self.updater[idx].some_changed, orb_tp))
        combo.setCurrentIndex(0)
        return combo

    def uicreate_label(self, lab, parent):
        label = QLabel(lab, parent)
        sz_pol = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sz_pol.setHorizontalStretch(0)
        sz_pol.setVerticalStretch(0)
        sz_pol.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
        label.setSizePolicy(sz_pol)
        label.setMinimumSize(QSize(60, 0))
        label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        return label

    def connect_signals(self):
        for i in range(len(self.line_names)):
            grpbx = self.findChild(QGroupBox, 'GroupBox' + str(i))
            for pln in ('x', 'y'):
                curve = self.graph[pln].curveAtIndex(i)
                lines = self.graph[pln].plotItem.items
                lines = [x for x in lines if isinstance(x, InfiniteLine)]
                cbx = grpbx.findChild(QCheckBox, pln + 'checkbox')
                grpbx.toggled.connect(curve.setVisible)
                grpbx.toggled.connect(cbx.setChecked)
                for j in range(3):
                    cbx.toggled.connect(lines[3*i + j].setVisible)

    def _get_color(self, pln, idx):
        cor = idx * 255
        cor //= len(self.line_names)
        cor += 0
        return QColor(255, cor, 0) if pln == 'y' else QColor(0, cor, 255)

    def _set_enable_list(self, pln, idx):
        val = self.enbl_pvs_set[pln].getvalue()
        val[idx] = not val[idx]
        self.enbl_pvs_set[pln].send_value_signal[_np.ndarray].emit(val)

    def _update_enable_list(self, pln, array):
        # cor = (255, 255, 255)
        # cor = (0, 200, 0)
        cor = (0, 0, 0)
        offbrs = mkBrush(*cor)
        offpen = mkPen(*cor)
        offsimb = 's'
        simb = 'o'
        offsz = 15
        size = 10
        for i in range(len(self.line_names)):
            trc = self.graph[pln].curveAtIndex(i)
            cor = self._get_color(pln, i)
            brs = mkBrush(cor)
            pen = mkPen(cor)
            brss, pens, simbs, sizes = [], [], [], []
            for v in array:
                if v:
                    brss.append(brs)
                    pens.append(pen)
                    simbs.append(simb)
                    sizes.append(size)
                else:
                    brss.append(offbrs)
                    pens.append(offpen)
                    simbs.append(offsimb)
                    sizes.append(offsz)
            trc.opts['symbolBrush'] = brss
            trc.opts['symbolPen'] = pens
            # trc.opts['symbol'] = simbs  # pyqtgraph bug does not allow this
            trc.opts['symbolSize'] = sizes

    def _save_difference(self, idx):
        updater = self.updater[idx]
        valx = updater.vectors['val']['x']
        refx = updater.vectors['ref']['x']
        valy = updater.vectors['val']['y']
        refy = updater.vectors['ref']['y']
        if valx is None or refx is None or valy is None or refy is None:
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


class UpdateGraph(QObject):
    """Worker to update graphics."""
    avex = Signal([float])
    stdx = Signal([float])
    ave_pstdx = Signal([float])
    ave_mstdx = Signal([float])
    data_sigx = Signal([_np.ndarray])
    ref_sigx = Signal([_np.ndarray])
    avey = Signal([float])
    stdy = Signal([float])
    ave_pstdy = Signal([float])
    ave_mstdy = Signal([float])
    data_sigy = Signal([_np.ndarray])
    ref_sigy = Signal([_np.ndarray])

    UNIT = 1e-6  # orbit is in um and strength in urad

    def __init__(self, ctrls, is_orb, acc='SI'):
        """Initialize object."""
        super().__init__()
        self.ctrls = ctrls
        self.acc = acc
        self._csorb = OrbitCorrDev(acc)
        self.is_orb = is_orb
        self._isvisible = True
        text = sorted(ctrls)[0]
        self.current_text = {'val': text, 'ref': text}
        self.ave = {'x': self.avex, 'y': self.avey}
        self.std = {'x': self.stdx, 'y': self.stdy}
        self.ave_pstd = {'x': self.ave_pstdx, 'y': self.ave_pstdy}
        self.ave_mstd = {'x': self.ave_mstdx, 'y': self.ave_mstdy}
        self.data_sig = {'x': self.data_sigx, 'y': self.data_sigy}
        self.raw_ref_sig = {'x': self.ref_sigx, 'y': self.ref_sigy}
        self.slots = {
            'val': {
                'x': _part(self._update_vectors, 'val', 'x'),
                'y': _part(self._update_vectors, 'val', 'y')},
            'ref': {
                'x': _part(self._update_vectors, 'ref', 'x'),
                'y': _part(self._update_vectors, 'ref', 'y')}}
        szx = self._csorb.NR_BPMS if self.is_orb else self._csorb.NR_CH
        szy = self._csorb.NR_BPMS if self.is_orb else self._csorb.NR_CV
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
        self.enbl_list[pln] = _np.array(enbls, dtype=bool)

    def _update_vectors(self, orb_tp, pln, orb):
        self.vectors[orb_tp][pln] = orb
        if orb_tp == 'ref' and orb is not None:
            self.raw_ref_sig[pln].emit(orb)

    def update_graphic(self, pln=None):
        if not self._isvisible:
            return
        plns = ('x', 'y') if pln is None else (pln, )
        for pln in plns:
            orb = self.vectors['val'][pln]
            ref = self.vectors['ref'][pln]
            if orb is None or ref is None:
                return
            diff = (orb - ref) * self.UNIT
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


class Label(QLabel):
    FMT = '{0:.2f}'

    def __init__(self, unit, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit = unit

    def setFloat(self, val):
        sc, prf = functions.siScale(val)
        val *= sc
        text = self.FMT.format(val)
        text += ' ' + prf + self.unit
        super().setText(text)


class Graph(PyDMWaveformPlot):
    doubleclick = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxRedrawRate = 2
        self.mouseEnabledX = True
        self.setShowXGrid(True)
        self.setShowYGrid(True)
        self.setBackgroundColor(QColor(255, 255, 255))
        # self.setBackgroundColor(QColor(239, 235, 231))
        self.setShowLegend(True)
        self.setAutoRangeX(True)
        self.setAutoRangeY(True)
        self.setMinXRange(0.0)
        self.setMaxXRange(1.0)
        self.plotItem.showButtons()
        font = QFont()
        font.setPixelSize(26)
        self.plotItem.getAxis('bottom').tickFont = font
        self.plotItem.getAxis('bottom').setPen(QColor(0, 0, 0))
        self.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        self.plotItem.getAxis('bottom').setHeight(80)
        self.plotItem.getAxis('left').tickFont = font
        self.plotItem.getAxis('left').setPen(QColor(0, 0, 0))
        self.plotItem.getAxis('left').setStyle(tickTextOffset=5)
        self.plotItem.getAxis('left').setWidth(100)

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            posx = self.curveAtIndex(0).xData
            vb = self.plotItem.getViewBox()
            pos = vb.mapSceneToView(ev.pos())
            i = _np.argmin(_np.abs(posx-pos.x()))
            self.doubleclick.emit(i)
        super().mouseDoubleClickEvent(ev)


class InfLine(InfiniteLine):

    def __init__(self, conv=1, pos=None, **kwargs):
        if pos is not None:
            pos *= conv
        super().__init__(pos=pos, **kwargs)
        self.conv = conv

    def setValue(self, value):
        super().setValue(value*self.conv)
