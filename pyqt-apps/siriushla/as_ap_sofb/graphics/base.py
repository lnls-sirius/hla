"""Control the Orbit Graphic Displnay."""

from datetime import datetime as _datetime
from functools import partial as _part
import numpy as _np

from qtpy.QtWidgets import QWidget, QFileDialog, QLabel, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QSizePolicy, QGroupBox, QPushButton, QComboBox, \
    QToolTip, QGridLayout
from qtpy.QtCore import Qt, QTimer, QThread, Signal, QObject
from qtpy.QtGui import QColor
from pyqtgraph import mkBrush, mkPen, InfiniteLine, functions
import qtawesome as qta

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.sofb.csdev import SOFBFactory

from siriushla.widgets import SiriusConnectionSignal as _ConnSig, \
    SiriusWaveformPlot


class BaseWidget(QWidget):
    """."""

    DEFAULT_DIR = '/home/sirius/mounts/screens-iocs'

    def __init__(self, parent, device, ctrls, names, is_orb, prefix='',
                 acc='SI'):
        """."""
        super(BaseWidget, self).__init__(parent)
        self.setObjectName(acc.upper()+'App')
        self.EXT = f'.{acc.lower()}dorb'
        self.EXT_FLT = f'Sirius Delta Orbit Files (*.{acc.lower()}dorb)'
        self.line_names = names
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.controls = ctrls
        self._csorb = SOFBFactory.create(acc)
        self.update_rate = 2.1  # Hz
        self.last_dir = self.DEFAULT_DIR
        self.is_orb = is_orb
        self.timer = QTimer()
        self.thread = QThread()
        self.updater = []
        self.graph = {'x': None, 'y': None}
        for _ in range(2):
            upd = UpdateGraph(ctrls, is_orb, acc)
            upd.moveToThread(self.thread)
            self.timer.timeout.connect(upd.update_graphic)
            self.updater.append(upd)

        self.setupui()
        self.connect_signals()

        prefx, prefy = ('BPMX', 'BPMY') if self.is_orb else ('CH', 'CV')
        self.enbl_pvs = {
            'x': _ConnSig(self.devpref.substitute(propty=prefx+'EnblList-RB')),
            'y': _ConnSig(self.devpref.substitute(propty=prefy+'EnblList-RB'))}
        for pln, signal in self.enbl_pvs.items():
            sig = signal.new_value_signal[_np.ndarray]
            for upd in self.updater:
                sig.connect(_part(upd.set_enbl_list, pln))

        self.enbl_pvs_set = {
            'x': _ConnSig(self.devpref.substitute(propty=prefx+'EnblList-SP')),
            'y': _ConnSig(self.devpref.substitute(propty=prefy+'EnblList-SP'))}

        self.thread.start()
        self.timer.start(1000/self.update_rate)

    @property
    def acc(self):
        """."""
        return self._csorb.acc

    @property
    def acc_idx(self):
        """."""
        return self._csorb.acc_idx

    @property
    def isring(self):
        """."""
        return self._csorb.isring

    def channels(self):
        """."""
        chans = list(self.enbl_pvs.values())
        chans.extend(self.enbl_pvs_set.values())
        return chans

    def setupui(self):
        """."""
        vbl = QVBoxLayout(self)
        vbl.setAlignment(Qt.AlignCenter)

        graphx = self.uigetgraph('x', (45, 15))
        graphy = self.uigetgraph('y', (45, 15))
        suf = 'Orbit' if self.is_orb else 'Correctors'
        lab = QLabel(
            '<h2>Horizontal ' + suf + '</h2>', self, alignment=Qt.AlignLeft)
        lab.setStyleSheet("""min-height:1.5em; max-height:1.5em;""")
        self.hbl_nameh = QHBoxLayout()
        vbl.addItem(self.hbl_nameh)
        self.hbl_nameh.addWidget(lab)
        self.hbl_nameh.addStretch(1)
        vbl.addWidget(graphx)
        vbl.addSpacing(30)
        lab = QLabel(
            '<h2>Vertical ' + suf + '</h2>', self, alignment=Qt.AlignLeft)
        lab.setStyleSheet("""min-height:1.5em; max-height:1.5em;""")
        self.hbl_namev = QHBoxLayout()
        vbl.addItem(self.hbl_namev)
        self.hbl_namev.addWidget(lab)
        self.hbl_namev.addStretch(1)
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

    def uigetgraph(self, pln, size):
        """."""
        graph = Graph(self)
        graph.doubleclick.connect(_part(self._set_enable_list, pln))
        graph.plotItem.scene().sigMouseMoved.connect(
            _part(self._show_tooltip, pln=pln))
        if self.is_orb:
            xlabel = 'BPM '
        elif pln.lower().endswith('x'):
            xlabel = 'CH '
        else:
            xlabel = 'CV '
        xlabel += 'Position'
        graph.setLabel('bottom', text=xlabel, units='m')
        lab = 'Orbit' if self.is_orb else 'Kick Angle'
        unit = 'm' if self.is_orb else 'rad'
        graph.setLabel('left', text=lab, units=unit)
        graph.setObjectName(lab.replace(' ', '')+pln)
        view = graph.getAxis('left').linkedView()
        for i, lname in enumerate(self.line_names):
            opts = dict(
                y_channel='A',
                x_channel='B',
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
            view.addItem(cpstd)
            cmstd = InfiniteLine(pos=0.0, pen=pen, angle=0)
            self.updater[i].ave_mstd[pln].connect(cmstd.setValue)
            view.addItem(cmstd)
            pen.setStyle(2)
            cave = InfiniteLine(pos=0.0, pen=pen, angle=0)
            self.updater[i].ave[pln].connect(cave.setValue)
            view.addItem(cave)
            cdta = graph.curveAtIndex(-1)
            self.updater[i].data_sig[pln].connect(
                _part(self._update_waveform, cdta, pln, i))
            cdta.setVisible(not i)
            cdta.curve.setZValue(-4*i)
            cdta.scatter.setZValue(-4*i)
            for j, cur in enumerate((cpstd, cmstd, cave), 1):
                cur.setZValue(-4*i - j)
                cur.setVisible(False)
            graph.plotItem.legend.removeItem('')
        graph.setStyleSheet("""
            #{0}{{
                min-width:{1}em;
                min-height:{2}em;
            }}""".format(lab.replace(' ', '')+pln, size[0], size[1]))
        return graph

    def uicreate_groupbox(self, idx):
        """."""
        grpbx = QGroupBox(self.line_names[idx], self)
        grpbx.setCheckable(True)
        grpbx.setChecked(not idx)
        grpbx.toggled.connect(self.updater[idx].set_visible)
        vbl = QVBoxLayout(grpbx)
        gdl = QGridLayout()
        gdl.setSpacing(4)
        vbl.addLayout(gdl)

        if self.is_orb:
            lbl_orb = self.uicreate_label('Show', grpbx)
            lbl_ref = self.uicreate_label('as diff to:', grpbx)
            cbx_ref = self.uicreate_combobox(grpbx, 'ref', idx)
            cbx_orb = self.uicreate_combobox(grpbx, 'val', idx)
            gdl.addWidget(lbl_orb, 0, 0)
            gdl.addWidget(lbl_ref, 1, 0)
            gdl.addWidget(cbx_orb, 0, 1)
            gdl.addWidget(cbx_ref, 1, 1)

            pb_save = QPushButton('', grpbx)
            pb_save.clicked.connect(_part(self._save_difference, idx))
            pb_save.setObjectName('butt')
            pb_save.setStyleSheet('#butt {max-width: 40px; icon-size: 35px;}')
            pb_save.setIcon(qta.icon('fa5.save'))
            pb_save.setToolTip('Save diff to file')
            gdl.addWidget(pb_save, 0, 2, 2, 1)

        unit = 'm' if self.is_orb else 'rad'
        for pln in ('x', 'y'):
            wid = QWidget(grpbx)
            vbl.addWidget(wid)
            vbl.setSpacing(2)
            hbl = QHBoxLayout(wid)
            hbl.setSpacing(0)
            cbx = QCheckBox('{0:s}:'.format(pln.upper()), wid)
            cbx.setObjectName(pln + 'checkbox')
            cbx.setChecked(False)
            hbl.addWidget(cbx)

            lab_avg = Label(unit, '-100.00 mrad', wid)
            self.updater[idx].ave[pln].connect(lab_avg.setFloat)
            lab_avg.setStyleSheet("""min-width:4.5em;""")
            lab_avg.setAlignment(Qt.AlignRight)
            hbl.addWidget(lab_avg)
            hbl.addWidget(QLabel(
                " <html><head/><body><p>&#177;</p></body></html> ", wid))
            lab_std = Label(unit, '100.00 mrad', wid)
            self.updater[idx].std[pln].connect(lab_std.setFloat)
            lab_std.setStyleSheet("""min-width:4.5em;""")
            lab_std.setAlignment(Qt.AlignLeft)
            hbl.addWidget(lab_std)

            hbl.addWidget(QLabel('(pp. ', wid))
            lab_p2p = Label(unit, '100.00 mrad', wid)
            self.updater[idx].p2p[pln].connect(lab_p2p.setFloat)
            lab_p2p.setStyleSheet("""min-width:4.5em;""")
            lab_p2p.setAlignment(Qt.AlignLeft)
            hbl.addWidget(lab_p2p)
            hbl.addWidget(QLabel(')', wid))
        return grpbx

    def uicreate_combobox(self, parent, orb_tp, idx):
        """."""
        combo = QComboBox(parent)
        combo.setObjectName('ComboBox_' + orb_tp + str(idx))
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        combo.setSizePolicy(sz_pol)
        combo.setMaxVisibleItems(10)
        for name in sorted(self.controls.keys()):
            combo.addItem(name)
        combo.addItem('Zero')
        combo.currentTextChanged.connect(_part(
            self.updater[idx].some_changed, orb_tp))
        combo.setCurrentIndex(0)
        return combo

    def uicreate_label(self, lab, parent):
        """."""
        label = QLabel(lab, parent)
        sz_pol = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        label.setSizePolicy(sz_pol)
        label.setStyleSheet("""min-width:2.5em;""")
        label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        return label

    def connect_signals(self):
        """."""
        for i in range(len(self.line_names)):
            grpbx = self.findChild(QGroupBox, 'GroupBox' + str(i))
            for pln in ('x', 'y'):
                curve = self.graph[pln].curveAtIndex(i)
                lines = self.graph[pln].getAxis('left').linkedView().addedItems
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

    def _show_tooltip(self, pos, pln='x'):
        unit = 'rad'
        if self.is_orb:
            names = self._csorb.bpm_nicknames
            posi = self._csorb.bpm_pos
            unit = 'm'
        elif pln == 'x':
            names = self._csorb.ch_nicknames
            posi = self._csorb.ch_pos
        else:
            names = self._csorb.cv_nicknames
            posi = self._csorb.cv_pos

        graph = self.graph[pln]
        curve = graph.curveAtIndex(0)
        posx = curve.scatter.mapFromScene(pos).x()
        if self._csorb.isring:
            posx = posx % self._csorb.circum
        ind = _np.argmin(_np.abs(_np.array(posi)-posx))
        posy = curve.scatter.mapFromScene(pos).y()

        sca, prf = functions.siScale(posy)
        txt = '{0:s}, y = {1:.3f} {2:s}'.format(
            names[ind], sca*posy, prf+unit)
        QToolTip.showText(
            graph.mapToGlobal(pos.toPoint()),
            txt, graph, graph.geometry(), 500)

    def _set_enable_list(self, pln, idx):
        val = self.enbl_pvs[pln].getvalue()
        val[idx] = not val[idx]
        self.enbl_pvs_set[pln].send_value_signal[_np.ndarray].emit(val)

    def _update_enable_list(self, pln, array, curve=None, idx=None):
        # cor = (255, 255, 255)
        # cor = (0, 200, 0)
        cor = (0, 0, 0)
        offbrs = mkBrush(*cor)
        offpen = mkPen(*cor)
        offsimb = 's'
        simb = 'o'
        offsz = 15
        size = 10
        trcs = []
        if curve is None:
            for i in range(len(self.line_names)):
                trcs.append((i, self.graph[pln].curveAtIndex(i)))
        else:
            trcs.append((idx, curve))
        for i, trc in trcs:
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

    def _update_waveform(self, curve, plane, idx, data):
        bpm_pos = self._csorb.bpm_pos
        if not self.is_orb and plane == 'x':
            bpm_pos = self._csorb.ch_pos
        elif not self.is_orb and plane == 'y':
            bpm_pos = self._csorb.cv_pos
        bpm_pos = _np.array(bpm_pos)

        data = _np.asarray(data)
        enbl = _np.asarray(self.enbl_pvs[plane].value, dtype=bool)
        if enbl is not None and enbl.size > 1:
            sz = min(enbl.size, data.size)
            self._update_enable_list(plane, enbl[:sz], curve, idx)
            nring = sz // bpm_pos.size
            if nring > 1:
                bpm_pos = [
                    bpm_pos + i*self._csorb.circum for i in range(nring)]
                bpm_pos = _np.hstack(bpm_pos)
            curve.receiveXWaveform(bpm_pos)
            curve.receiveYWaveform(data[:sz])
        else:
            curve.receiveXWaveform(bpm_pos)
            curve.receiveYWaveform(data)

    def _save_difference(self, idx):
        updater = self.updater[idx]
        valx = updater.vectors['val']['x']
        refx = updater.vectors['ref']['x']
        valy = updater.vectors['val']['y']
        refy = updater.vectors['ref']['y']
        if valx is None or refx is None or valy is None or refy is None:
            return
        sz = min(valx.size, refx.size, valy.size, refy.size)
        diffx = valx[:sz] - refx[:sz]
        diffy = valy[:sz] - refy[:sz]
        header = '# This is an orbit variation, not a pure orbit. \n'
        header += '# ' + _datetime.now().strftime('%Y/%m/%d-%H:%M:%S') + '\n'
        header += '# ' + 'BPMX [um]         BPMY [um]             Name' + '\n'
        filename = QFileDialog.getSaveFileName(
            caption='Define a File Name to Save the Orbit',
            directory=self.last_dir, filter=self.EXT_FLT)
        fname = filename[0]
        if not fname:
            return
        fname += '' if fname.endswith(self.EXT) else self.EXT
        data = _np.array([diffx, diffy, self._csorb.bpm_names], dtype=object)
        _np.savetxt(
            fname, data.T, header=header, fmt='%+18.8e %+18.8e      %s')
        self.last_dir = fname.rsplit('/', 1)[0]


class UpdateGraph(QObject):
    """Worker to update graphics."""
    avex = Signal([float])
    stdx = Signal([float])
    p2px = Signal([float])
    ave_pstdx = Signal([float])
    ave_mstdx = Signal([float])
    data_sigx = Signal([_np.ndarray])
    ref_sigx = Signal([_np.ndarray])
    avey = Signal([float])
    stdy = Signal([float])
    p2py = Signal([float])
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
        self._csorb = SOFBFactory.create(acc)
        self.is_orb = is_orb
        self._isvisible = True
        text = sorted(ctrls)[0]
        self.current_text = {'val': text, 'ref': text}
        self.ave = {'x': self.avex, 'y': self.avey}
        self.p2p = {'x': self.p2px, 'y': self.p2py}
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
        nbpms = self._csorb.nr_bpms * self._csorb.MAX_RINGSZ
        szx = nbpms if self.is_orb else self._csorb.nr_ch
        szy = nbpms if self.is_orb else self._csorb.nr_cv
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
        """."""
        if text not in (self.ctrls.keys() | {'Zero'}):
            return
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
        """."""
        self._isvisible = boo

    def set_enbl_list(self, pln, enbls):
        """."""
        self.enbl_list[pln] = _np.array(enbls, dtype=bool)

    def _update_vectors(self, orb_tp, pln, orb):
        self.vectors[orb_tp][pln] = orb
        if orb_tp == 'ref' and orb is not None:
            self.raw_ref_sig[pln].emit(orb)

    def update_graphic(self, pln=None):
        """."""
        if not self._isvisible:
            return
        plns = ('x', 'y') if pln is None else (pln, )
        for pln in plns:
            orb = self.vectors['val'][pln]
            ref = self.vectors['ref'][pln]
            if orb is None or ref is None:
                return
            sz = min(orb.size, ref.size)
            diff = (orb[:sz] - ref[:sz]) * self.UNIT

            enbl = self.enbl_list[pln]
            if enbl is not None:
                sz = min(sz, enbl.size)
                mask = diff[:sz][enbl[:sz]]
            else:
                mask = diff
            ave = float(mask.mean()) if mask.size > 0 else 0.0
            p2p = float(mask.max() - mask.min()) if mask.size > 1 else 0.0
            std = float(mask.std(ddof=1)) if mask.size > 1 else 0.0

            self.data_sig[pln].emit(diff)
            self.ave[pln].emit(ave)
            self.std[pln].emit(std)
            self.p2p[pln].emit(p2p)
            self.ave_pstd[pln].emit(ave-std)
            self.ave_mstd[pln].emit(ave+std)


class Label(QLabel):
    """."""

    FMT = '{0:.2f}'

    def __init__(self, unit, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.unit = unit

    def setFloat(self, val):
        """."""
        sc, prf = functions.siScale(val)
        val *= sc
        text = self.FMT.format(val)
        text += ' ' + prf + self.unit
        super().setText(text)


class Graph(SiriusWaveformPlot):
    """."""

    doubleclick = Signal(int)

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.addAxis(plot_data_item=None, name='left', orientation='left')
        self.setObjectName('graph')
        self.setStyleSheet('#graph {min-height: 13em; min-width: 20em;}')
        self.maxRedrawRate = 2
        self.mouseEnabledX = True
        self.setShowXGrid(True)
        self.setShowYGrid(True)
        self.setBackgroundColor(QColor(255, 255, 255))
        self.setShowLegend(True)
        self.setAutoRangeX(True)
        self.setAutoRangeY(True)
        self.setMinXRange(0.0)
        self.setMaxXRange(1.0)
        self.setAxisColor(QColor(0, 0, 0))
        self.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        self.plotItem.getAxis('left').setStyle(tickTextOffset=5)

    def mouseDoubleClickEvent(self, ev):
        """."""
        if ev.button() == Qt.LeftButton:
            posx = self.curveAtIndex(0).xData
            vb = self.plotItem.getViewBox()
            pos = vb.mapSceneToView(ev.pos())
            i = _np.argmin(_np.abs(posx-pos.x()))
            self.doubleclick.emit(i)
        super().mouseDoubleClickEvent(ev)


class InfLine(InfiniteLine):
    """."""

    def __init__(self, conv=1, pos=None, **kwargs):
        """."""
        if pos is not None:
            pos *= conv
        super().__init__(pos=pos, **kwargs)
        self.conv = conv

    def setValue(self, value):
        """."""
        super().setValue(value*self.conv)
