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
from siriushla.widgets import SiriusSpectrogramView, SiriusConnectionSignal, \
    SiriusLabel

from siriushla.as_ap_sofb.graphics.base import BaseWidget, Graph
from siriushla.as_ap_sofb.graphics.correctors import CorrectorsWidget


class OrbitWidget(BaseWidget):
    """."""

    def __init__(self, parent, prefix, ctrls=None, acc='SI'):
        """."""
        self._chans = []
        if not ctrls:
            self._chans, ctrls = self.get_default_ctrls(prefix)

        names = ['Line {0:d}'.format(i+1) for i in range(2)]
        super().__init__(parent, prefix, ctrls, names, True, acc)

        txt1, txt2 = 'SPassOrb', 'RefOrb'
        if self.isring:
            txt1 = 'SlowOrb'

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
        self.hbl.addWidget(grpbx)
        self.hbl.addStretch(1)

        btn = QPushButton('Corrs', grpbx)
        gdl.addWidget(btn, 0, 0)
        Window = create_window_from_widget(
            CorrectorsWidget, title='Correctors')
        _util.connect_window(
            btn, Window, self, prefix=self.prefix, acc=self.acc)

        if self.isring:
            btn = QPushButton('MultiTurn Orb', grpbx)
            gdl.addWidget(btn, 1, 0)
            Window = create_window_from_widget(
                MultiTurnWidget, title='Multi Turn')
            _util.connect_window(
                btn, Window, self,
                sigs=self.updater[0].raw_ref_sig, prefix=self.prefix)

            btn = QPushButton('MultTurn Sum', grpbx)
            gdl.addWidget(btn, 1, 1)
            Window = create_window_from_widget(
                MultiTurnSumWidget, title='Multi Turn Sum')
            _util.connect_window(btn, Window, self, prefix=self.prefix)

        btn = QPushButton('SingPass Sum', grpbx)
        gdl.addWidget(btn, 0, 1)
        Window = create_window_from_widget(
            SinglePassSumWidget, title='Single Pass Sum')
        _util.connect_window(
            btn, Window, self, prefix=self.prefix, acc=self.acc)

    def channels(self):
        """."""
        chans = super().channels()
        chans.extend(self._chans)
        return chans

    @staticmethod
    def get_default_ctrls(prefix, isring=True):
        """."""
        pvs = [
            'SPassOrbX-Mon', 'SPassOrbY-Mon',
            'OfflineOrbX-RB', 'OfflineOrbY-RB',
            'RefOrbX-RB', 'RefOrbY-RB']
        orbs = [
            'SPassOrb', 'OfflineOrb', 'RefOrb']
        if isring:
            pvs.extend([
                'SlowOrbX-Mon', 'SlowOrbY-Mon',
                'MTurnIdxOrbX-Mon', 'MTurnIdxOrbY-Mon'])
            orbs.extend(['SlowOrb', 'MTurnOrb'])

        chans = [SiriusConnectionSignal(prefix+pv) for pv in pvs]
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

    def __init__(self, parent, sigs, prefix):
        """."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.setObjectName(self.prefix.sec+'App')
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
            sig.disconnect(self.fun2setref[pln])

    def setupui(self):
        """."""
        hbl = QHBoxLayout(self)
        self.spectx = MultiTurnSumWidget(self, self.prefix, orbtype='X')
        self.specty = MultiTurnSumWidget(self, self.prefix, orbtype='Y')
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

    def __init__(self, parent, prefix, orbtype='sum'):
        """."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.orbtype = orbtype.lower()
        self.setObjectName(self.prefix.sec+'App')
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
            prefix=self.prefix,
            image_channel=self.prefix+img_propty,
            xaxis_channel=self.prefix+'BPMPosS-Mon',
            yaxis_channel=self.prefix+'MTurnTime-Mon')
        self.spect.new_data_sig.connect(self.update_graph)
        self.spect.normalizeData = True
        self.spect.yaxis.setLabel('Time', units='s')
        self.spect.xaxis.setLabel('BPM Position', units='m')
        self.spect.colorbar.label_format = '{:<8.1f}'
        lab = QLabel(lbl_text + ' Orbit', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)
        vbl.addWidget(self.spect)

        vbl.addSpacing(50)
        lab = QLabel(
            'Average ' + lbl_text + ' vs Time', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)
        graph = Graph(self)
        vbl.addWidget(graph)
        graph.setLabel('bottom', text='Time', units='s')
        graph.setLabel('left', text='Avg ' + lbl_text, units=unit)
        opts = dict(
            y_channel='A',
            x_channel=self.prefix+'MTurnTime-Mon',
            name='',
            color=color,
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        graph.setShowLegend(False)
        self.curve = graph.curveAtIndex(0)

        if not self.orbtype.startswith('sum'):
            return

        vbl.addSpacing(50)
        wid = QWidget(self)
        lab = QLabel(
            lbl_text + ' orbit at index:', wid,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        lab.setStyleSheet("font-weight: bold;")
        pdmlab = SiriusLabel(
            wid, init_channel=self.prefix+'MTurnIdx-RB')
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
            y_channel=self.prefix+orb_propty,
            x_channel=self.prefix+'BPMPosS-Mon',
            name='',
            color=color,
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        graph.setShowLegend(False)

    def update_graph(self, data):
        """."""
        scale = 1e-6
        if self.orbtype.startswith('sum'):
            scale = 1
        self.curve.receiveYWaveform(scale*data.mean(axis=1))


class Spectrogram(SiriusSpectrogramView):
    """."""

    new_data_sig = Signal(_np.ndarray)

    def __init__(self, prefix='', **kwargs):
        """."""
        self._reforb = None
        super().__init__(**kwargs)
        self.setObjectName('graph')
        self.setStyleSheet('#graph {min-height: 15em; min-width: 25em;}')
        self.prefix = prefix
        self.multiturnidx = SiriusConnectionSignal(
                                self.prefix + 'MTurnIdx-SP')

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

    def __init__(self, parent, prefix, acc):
        """."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.setObjectName(self.prefix.sec+'App')
        self.acc = acc.upper()
        self._csorb = SOFBFactory.create(acc)
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
            y_channel=self.prefix+'SPassSum-Mon',
            x_channel=self.prefix+'BPMPosS-Mon',
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
    from siriuspy.envars import VACA_PREFIX
    import sys
    _main(VACA_PREFIX)
