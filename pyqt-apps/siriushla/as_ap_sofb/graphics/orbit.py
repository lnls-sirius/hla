"""Control the Orbit Graphic Displnay."""

from functools import partial as _part
import numpy as _np
from pyqtgraph import functions
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, \
    QHBoxLayout, QGroupBox, QComboBox, QToolTip, QGridLayout
from qtpy.QtCore import Qt, Signal
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.sofb.csdev import SOFBFactory
import siriushla.util as _util
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import SiriusSpectrogramView, SiriusLabel, \
    SiriusConnectionSignal as _ConnSig

from .base import BaseWidget, Graph
from .correctors import CorrectorsWidget


class OrbitWidget(BaseWidget):
    """."""

    def __init__(self, parent, device, prefix='', ctrls=None, acc='SI'):
        """."""
        self._chans = []
        self._csorb = SOFBFactory.create(acc)
        if not ctrls:
            self._chans, ctrls = self.get_default_ctrls(
                device, prefix, acc=acc.upper())

        names = ['Line {0:d}'.format(i+1) for i in range(2)]
        super().__init__(parent, device, ctrls, names, True, prefix, acc)

        txt1, txt2 = 'IOC-SPassOrb', 'IOC-RefOrb'
        if self.acc == 'SI':
            txt1 = 'IOC-SlowOrb'
        elif self.acc == 'BO':
            txt1 = 'IOC-MTurnOrb'

        self.updater[0].some_changed('val', txt1)
        self.updater[0].some_changed('ref', txt2)
        cb1 = self.findChild(QComboBox, 'ComboBox_val0')
        cb2 = self.findChild(QComboBox, 'ComboBox_ref0')
        it1 = cb1.findText(txt1)
        it2 = cb2.findText(txt2)
        cb1.setCurrentIndex(it1)
        cb2.setCurrentIndex(it2)

        self.add_buttons_for_images()

    def add_buttons_for_images(self):
        """."""
        grpbx = QGroupBox('Other Graphs', self)
        gdl = QGridLayout(grpbx)
        gdl.setSpacing(2)
        self.hbl_nameh.addWidget(grpbx)

        btn = QPushButton('Corrs', grpbx)
        gdl.addWidget(btn, 0, 0)
        Window = create_window_from_widget(
            CorrectorsWidget, title=self.acc + ' - Correctors')
        _util.connect_window(
            btn, Window, self, device=self.device,
            prefix=self.prefix, acc=self.acc)

        if self.isring:
            btn = QPushButton('MTurn Orb', grpbx)
            gdl.addWidget(btn, 0, 1)
            Window = create_window_from_widget(
                MultiTurnWidget, title='Multi Turn')
            _util.connect_window(
                btn, Window, self, sigs=self.updater[0].raw_ref_sig,
                device=self.device, prefix=self.prefix, csorb=self._csorb)

            btn = QPushButton('MTurn Sum', grpbx)
            gdl.addWidget(btn, 0, 2)
            Window = create_window_from_widget(
                MultiTurnSumWidget, title='Multi Turn Sum')
            _util.connect_window(
                btn, Window, self, device=self.device, prefix=self.prefix,
                csorb=self._csorb)

        btn = QPushButton('SingPass Sum', grpbx)
        gdl.addWidget(btn, 0, 3)
        Window = create_window_from_widget(
            SinglePassSumWidget, title='Single Pass Sum')
        _util.connect_window(
            btn, Window, self, device=self.device, prefix=self.prefix,
            csorb=self._csorb)

    def channels(self):
        """."""
        chans = super().channels()
        chans.extend(self._chans)
        return chans

    @staticmethod
    def get_default_ctrls(device, prefix='', acc='SI'):
        """."""
        pvs = [
            'SPassOrbX-Mon', 'SPassOrbY-Mon',
            'OfflineOrbX-RB', 'OfflineOrbY-RB',
            'RefOrbX-RB', 'RefOrbY-RB']
        orbs = [
            'IOC-SPassOrb', 'IOC-OfflineOrb', 'IOC-RefOrb']
        if acc.upper() == 'SI':
            pvs.extend(['SlowOrbX-Mon', 'SlowOrbY-Mon'])
            orbs.append('IOC-SlowOrb')
        if acc.upper() in {'SI', 'BO'}:
            pvs.extend(['MTurnIdxOrbX-Mon', 'MTurnIdxOrbY-Mon'])
            orbs.append('IOC-MTurnOrb')

        chans = [_ConnSig(device.substitute(prefix=prefix, propty=pv))
                 for pv in pvs]
        ctrls = dict()
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


class MultiTurnWidget(QWidget):
    """."""

    def __init__(self, parent, sigs, device, prefix, csorb):
        """."""
        super().__init__(parent)
        self._csorb = csorb
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.setObjectName(csorb.acc + 'App')
        self.setupui()
        self.sigs = sigs
        self.fun2setref = {
            'x': _part(self.setreforbits, 'x'),
            'y': _part(self.setreforbits, 'y')}

    def showEvent(self, _):
        """."""
        for pln, sig in self.sigs.items():
            sig.connect(self.fun2setref[pln])

    def hideEvent(self, _):
        """."""
        for pln, sig in self.sigs.items():
            try:
                sig.disconnect(self.fun2setref[pln])
            except TypeError:
                pass

    def setupui(self):
        """."""
        hbl = QHBoxLayout(self)
        self.spectx = MultiTurnSumWidget(
            self, device=self.device, prefix=self.prefix,
            orbtype='X', csorb=self._csorb)
        self.specty = MultiTurnSumWidget(
            self, device=self.device, prefix=self.prefix,
            orbtype='Y', csorb=self._csorb)
        hbl.addWidget(self.spectx)
        hbl.addSpacing(50)
        hbl.addWidget(self.specty)

    def setreforbits(self, pln, orb):
        """."""
        if pln.lower() == 'x':
            self.spectx.spect.setreforbit(orb)
        else:
            self.specty.spect.setreforbit(orb)


class MultiTurnSumWidget(QWidget):
    """."""

    ratio_sum_avg = Signal(str)
    ratio_sum_std = Signal(str)

    def __init__(self, parent, device, prefix='', orbtype='sum', csorb=None):
        """."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.orbtype = orbtype.lower()
        self._csorb = csorb
        self.setObjectName(self.device.sec+'App')
        self.multiturnidx = _ConnSig(
            self.devpref.substitute(propty='MTurnIdx-SP'))
        self.setupui()

    def setupui(self):
        """."""
        vbl = QVBoxLayout(self)
        if self.orbtype.startswith('sum'):
            img_propty = 'MTurnSum-Mon'
            orb_propty = 'MTurnIdxSum-Mon'
            unit = 'count'
            color = 'black'
        elif self.orbtype.startswith('x'):
            img_propty = 'MTurnOrbX-Mon'
            orb_propty = 'MTurnIdxOrbX-Mon'
            unit = 'm'
            color = 'blue'
        else:
            img_propty = 'MTurnOrbY-Mon'
            orb_propty = 'MTurnIdxOrbY-Mon'
            unit = 'm'
            color = 'red'
        lbl_text = img_propty.split('-')[0]

        self.spect = Spectrogram(
            parent=self,
            device=self.device,
            prefix=self.prefix,
            image_channel=self.devpref.substitute(propty=img_propty),
            xaxis_channel=self.devpref.substitute(propty='BPMPosS-Mon'),
            yaxis_channel=self.devpref.substitute(propty='MTurnTime-Mon'))
        self.spect.new_data_sig.connect(self.update_graph)
        self.spect.normalizeData = True
        self.spect.yaxis.setLabel('Time', units='s')
        self.spect.xaxis.setLabel('BPM Position', units='m')
        self.spect.colorbar.label_format = '{:<8.1f}'
        lab = QLabel(lbl_text + ' Orbit', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)
        vbl.addWidget(self.spect)

        vbl.addStretch()
        lab = QLabel(
            'Average ' + lbl_text + ' vs Time', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        hbl = QHBoxLayout()
        hbl.addStretch()
        hbl.addWidget(lab)
        hbl.addStretch()
        if self.orbtype.startswith('sum'):
            hbl.addWidget(QLabel('  Eff [%] =', self))
            ratio_avg = QLabel('000.0', self, alignment=Qt.AlignRight)
            ratio_std = QLabel('000.0', self, alignment=Qt.AlignLeft)
            hbl.addWidget(ratio_avg, alignment=Qt.AlignRight)
            hbl.addWidget(QLabel(
                '<html><head/><body><p>&#177;</p></body></html>', self))
            hbl.addWidget(ratio_std, alignment=Qt.AlignLeft)
            hbl.addStretch()
            self.ratio_sum_avg.connect(ratio_avg.setText)
            self.ratio_sum_std.connect(ratio_std.setText)
        vbl.addLayout(hbl)

        graph = Graph(self)
        graph.setLabel('bottom', text='Time', units='s')
        graph.setLabel('left', text='Avg ' + lbl_text, units=unit)
        opts = dict(
            y_channel='A',
            x_channel=self.devpref.substitute(propty='MTurnTime-Mon'),
            name='',
            color=color,
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        graph.setShowLegend(False)
        graph.plotItem.scene().sigMouseMoved.connect(self._show_tooltip_time)
        self.curve = graph.curveAtIndex(0)
        self.graph_time = graph
        vbl.addWidget(graph)

        if not self.orbtype.startswith('sum'):
            return

        vbl.addStretch()
        wid = QWidget(self)
        lab = QLabel(
            lbl_text + ' orbit at index:', wid,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        lab.setStyleSheet("font-weight: bold;")
        pdmlab = SiriusLabel(
            wid, self.devpref.substitute(propty='MTurnIdx-RB'))
        pdmlab.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        pdmlab.setStyleSheet('min-width:4em;')
        wid.setLayout(QHBoxLayout())
        wid.layout().addStretch()
        wid.layout().addWidget(lab)
        wid.layout().addWidget(pdmlab)
        wid.layout().addStretch()
        vbl.addWidget(wid)
        graph = Graph(self)
        vbl.addWidget(graph)
        graph.setLabel('bottom', text='BPM Position', units='m')
        graph.setLabel('left', text='Sum', units='count')
        opts = dict(
            y_channel=self.devpref.substitute(propty=orb_propty),
            x_channel=self.devpref.substitute(propty='BPMPosS-Mon'),
            name='',
            color=color,
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        graph.setShowLegend(False)
        graph.plotItem.scene().sigMouseMoved.connect(self._show_tooltip)
        self.graph = graph

    def mouseDoubleClickEvent(self, ev):
        """."""
        if ev.button() != Qt.LeftButton:
            return super().mouseDoubleClickEvent(ev)
        graph = self.graph_time
        curve = graph.curveAtIndex(0)
        posx = curve.scatter.mapFromScene(ev.pos()).x()
        times = curve.getData()[0]
        if times is None:
            return super().mouseDoubleClickEvent(ev)
        ind = _np.argmin(_np.abs(times-posx))
        self.multiturnidx.send_value_signal[int].emit(int(ind))
        super().mouseDoubleClickEvent(ev)

    def _show_tooltip(self, pos):
        names = self._csorb.bpm_nicknames
        posi = self._csorb.bpm_pos
        unit = 'count'

        graph = self.graph
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

    def _show_tooltip_time(self, pos):
        graph = self.graph_time
        curve = graph.curveAtIndex(0)
        posx = curve.scatter.mapFromScene(pos).x()
        times = curve.getData()[0]
        if times is None:
            return
        ind = _np.argmin(_np.abs(times-posx))
        txt = f'index = {ind:d}'
        QToolTip.showText(
            graph.mapToGlobal(pos.toPoint()),
            txt, graph, graph.geometry(), 500)

    def update_graph(self, data):
        """."""
        scale = 1e-6
        if self.orbtype.startswith('sum'):
            scale = 1
        datay = scale*data.mean(axis=1)
        self.curve.receiveYWaveform(datay)
        if self.orbtype.startswith('sum') and datay.size > 6:
            ratios = datay[-5:]/datay[0]*100
            self.ratio_sum_avg.emit(f'{ratios.mean():.1f}')
            self.ratio_sum_std.emit(f'{ratios.std():.1f}')


class Spectrogram(SiriusSpectrogramView):
    """."""

    new_data_sig = Signal(_np.ndarray)

    def __init__(self, device, prefix='', **kwargs):
        """."""
        self._reforb = None
        super().__init__(**kwargs)
        self.setObjectName('graph')
        self.setStyleSheet('#graph {min-height: 15em; min-width: 20em;}')
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.multiturnidx = _ConnSig(
            self.devpref.substitute(propty='MTurnIdx-SP'))

    def channels(self):
        """."""
        chans = super().channels()
        chans.append(self.multiturnidx)
        return chans

    def setreforbit(self, orb):
        """."""
        self._reforb = orb
        self.needs_redraw = True

    def process_image(self, img):
        """."""
        if self._reforb is not None and img.shape[1] == self._reforb.size:
            img = img - self._reforb[None, :]
        self.new_data_sig.emit(img)
        return img

    def mouseDoubleClickEvent(self, ev):
        """."""
        if ev.button() == Qt.LeftButton:
            pos = self._image_item.mapFromDevice(ev.pos())
            if pos.y() > 0 and pos.y() <= self._image_item.height():
                self.multiturnidx.send_value_signal[int].emit(int(pos.y()))
        super().mouseDoubleClickEvent(ev)


class SinglePassSumWidget(QWidget):
    """."""

    def __init__(self, parent, device, csorb, prefix=''):
        """."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.devpref = self.device.substitute(prefix=prefix)
        self.setObjectName(csorb.acc+'App')
        self._csorb = csorb
        self.setupui()

    def setupui(self):
        """."""
        vbl = QVBoxLayout(self)

        lab = QLabel('SinglePass Sum BPMs', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)

        graph = Graph(self)
        vbl.addWidget(graph)
        graph.setLabel('bottom', text='BPM Position', units='m')
        graph.setLabel('left', text='Sum', units='count')
        opts = dict(
            y_channel=self.devpref.substitute(propty='SPassSum-Mon'),
            x_channel=self.devpref.substitute(propty='BPMPosS-Mon'),
            name='',
            color='black',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        graph.plotItem.scene().sigMouseMoved.connect(self._show_tooltip)
        graph.setShowLegend(False)
        self.graph = graph

    def _show_tooltip(self, pos):
        names = self._csorb.bpm_nicknames
        posi = self._csorb.bpm_pos
        unit = 'count'

        graph = self.graph
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
