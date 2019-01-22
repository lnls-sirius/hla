"""Control the Orbit Graphic Displnay."""

from functools import partial as _part
import numpy as np
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, \
    QHBoxLayout, QGroupBox, QComboBox
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor
import siriushla.util as _util
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import SiriusSpectrogramView, SiriusConnectionSignal

from siriushla.as_ap_sofb.graphics.base import BaseWidget, Graph
from siriushla.as_ap_sofb.graphics.correctors import CorrectorsWidget


class OrbitWidget(BaseWidget):

    def __init__(self, parent, prefix, ctrls=dict(), acc='SI'):
        self._chans = []
        if not ctrls:
            self._chans, ctrls = self.get_default_ctrls(prefix)

        names = ['Line {0:d}'.format(i+1) for i in range(2)]
        super().__init__(parent, prefix, ctrls, names, True, acc)

        txt1, txt2 = 'SinglePass', 'Reference Orbit'
        if self.isring:
            txt1 = 'Online Orbit'

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
        grpbx = QGroupBox('Other Graphics', self)
        vbl = QVBoxLayout(grpbx)
        self.hbl.addWidget(grpbx)
        self.hbl.addStretch(1)

        if self.isring:
            btn = QPushButton('Correctors', grpbx)
            vbl.addWidget(btn)
            Window = create_window_from_widget(
                CorrectorsWidget, name='CorrectorsWindow', size=(67, 60))
            _util.connect_window(
                btn, Window, self, prefix=self.prefix, acc=self.acc)

            btn = QPushButton('MultiTurn Orbit', grpbx)
            vbl.addWidget(btn)
            Window = create_window_from_widget(
                MultiTurnWidget, name='MultiTurnWindow', size=(35, 65))
            _util.connect_window(
                btn, Window, self,
                sigs=self.updater[0].raw_ref_sig, prefix=self.prefix)

            btn = QPushButton('MultiTurn Sum', grpbx)
            vbl.addWidget(btn)
            Window = create_window_from_widget(
                MultiTurnSumWidget, name='MultiTurnSumWindow', size=(35, 65))
            _util.connect_window(btn, Window, self, prefix=self.prefix)

        btn = QPushButton('SinglePass Sum', grpbx)
        vbl.addWidget(btn)
        Window = create_window_from_widget(
            SinglePassSumWidget, name='SinglePassSumWindow', size=(32, 23))
        _util.connect_window(btn, Window, self, prefix=self.prefix)

    def channels(self):
        chans = super().channels()
        chans.extend(self._chans)
        return chans

    @staticmethod
    def get_default_ctrls(prefix, isring=True):
        pvs = [
            'OrbitSmoothSinglePassX-Mon', 'OrbitSmoothSinglePassY-Mon',
            'OrbitOfflineX-RB', 'OrbitOfflineY-RB',
            'OrbitRefX-RB', 'OrbitRefY-RB',
            'BPMOffsetsX-Mon', 'BPMOffsetsY-Mon']
        orbs = [
            'SinglePass', 'Offline Orbit', 'Reference Orbit', 'BPMs Offset']
        if isring:
            pvs.extend([
                'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
                'OrbitMultiTurnX-Mon', 'OrbitMultiTurnY-Mon'])
            orbs.extend(['Online Orbit', 'MultiTurn Orbit'])

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

    def __init__(self, parent, sigs, prefix):
        super().__init__(parent)
        self.prefix = prefix
        self.setupui()
        self.sigs = sigs
        self.fun2setref = {
            'x': _part(self.setreforbits, 'x'),
            'y': _part(self.setreforbits, 'y')}

    def showEvent(self, _):
        for pln, sig in self.sigs.items():
            sig.connect(self.fun2setref[pln])

    def hideEvent(self, _):
        for pln, sig in self.sigs.items():
            sig.disconnect(self.fun2setref[pln])

    def setupui(self):
        vbl = QVBoxLayout(self)
        self.spectx = Spectrogram(
            parent=self,
            prefix=self.prefix,
            image_channel=self.prefix+'OrbitsMultiTurnX-Mon',
            xaxis_channel=self.prefix+'BPMPosS-Cte',
            yaxis_channel=self.prefix+'OrbitMultiTurnTime-Mon')
        self.specty = Spectrogram(
            parent=self,
            prefix=self.prefix,
            image_channel=self.prefix+'OrbitsMultiTurnY-Mon',
            xaxis_channel=self.prefix+'BPMPosS-Cte',
            yaxis_channel=self.prefix+'OrbitMultiTurnTime-Mon')
        self.spectx.normalizeData = True
        self.specty.normalizeData = True
        self.spectx.yaxis.setLabel('time', units='ms')
        self.specty.yaxis.setLabel('time', units='ms')
        self.spectx.xaxis.setLabel('BPM position', units='m')
        self.specty.xaxis.setLabel('BPM position', units='m')
        self.spectx.colorbar.label_format = '{:<8.1f}'
        self.specty.colorbar.label_format = '{:<8.1f}'
        lab = QLabel('Horizontal Orbit', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)
        vbl.addWidget(self.spectx)
        vbl.addSpacing(50)
        lab = QLabel('Vertical Orbit', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)
        vbl.addWidget(self.specty)

    def setreforbits(self, pln, orb):
        if pln.lower() == 'x':
            self.spectx.setreforbit(orb)
        else:
            self.specty.setreforbit(orb)


class MultiTurnSumWidget(QWidget):

    def __init__(self, parent, prefix):
        super().__init__(parent)
        self.prefix = prefix
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        self.spect = Spectrogram(
            parent=self,
            prefix=self.prefix,
            image_channel=self.prefix+'OrbitsMultiTurnSum-Mon',
            xaxis_channel=self.prefix+'BPMPosS-Cte',
            yaxis_channel=self.prefix+'OrbitMultiTurnTime-Mon')
        self.spect.new_data_sig.connect(self.update_graph)
        self.spect.normalizeData = True
        self.spect.yaxis.setLabel('time', units='ms')
        self.spect.xaxis.setLabel('BPM position', units='m')
        self.spect.colorbar.label_format = '{:<8.1f}'
        lab = QLabel('Sum Orbit', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)
        vbl.addWidget(self.spect)
        vbl.addSpacing(50)

        lab = QLabel('Sum Accross BPMs', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)
        graph = Graph(self)
        vbl.addWidget(graph)
        graph.setLabel('bottom', text='time', units='ms')
        graph.setLabel('left', text='Sum', units='count')
        opts = dict(
            y_channel='A',
            x_channel=self.prefix+'OrbitMultiTurnTime-Mon',
            name='',
            color=QColor(255, 255, 255),
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)
        self.curve = graph.curveAtIndex(0)

    def update_graph(self, data):
        self.curve.receiveYWaveform(data.mean(axis=1))


class Spectrogram(SiriusSpectrogramView):
    new_data_sig = Signal(np.ndarray)

    def __init__(self, prefix='', **kwargs):
        super().__init__(**kwargs)
        self.prefix = prefix

    def channels(self):
        chans = super().channels()
        self.multiturnidx = SiriusConnectionSignal(
            self.prefix + 'OrbitMultiTurnIdx-SP')
        chans.append(self.multiturnidx)
        return chans

    def setreforbit(self, orb):
        self._ref_orbit = orb
        self.needs_redraw = True

    def process_image(self, img):
        if hasattr(self, '_ref_orbit'):
            return img - self._ref_orbit[None, :]
        self.new_data_sig.emit(img)
        return img

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            pos = self._image_item.mapFromDevice(ev.pos())
            if pos.y() > 0 and pos.y() <= self._image_item.height():
                self.multiturnidx.send_value_signal[int].emit(int(pos.y()))
        super().mouseDoubleClickEvent(ev)


class SinglePassSumWidget(QWidget):

    def __init__(self, parent, prefix):
        super().__init__(parent)
        self.prefix = prefix
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)

        lab = QLabel('Single Pass Sum BPMs', self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        vbl.addWidget(lab)

        graph = Graph(self)
        vbl.addWidget(graph)
        graph.setLabel('bottom', text='time', units='ms')
        graph.setLabel('left', text='Sum', units='count')
        opts = dict(
            y_channel=self.prefix+'OrbitSmoothSinglePassSum-Mon',
            x_channel=self.prefix+'BPMPosS-Cte',
            name='',
            color=QColor(255, 255, 255),
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph.addChannel(**opts)


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
    from siriuspy.envars import vaca_prefix
    import sys
    _main(vaca_prefix)
