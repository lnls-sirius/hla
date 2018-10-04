"""Control the Orbit Graphic Displnay."""

from functools import partial as _part
from pyqtgraph import mkPen, InfiniteLine
from qtpy.QtWidgets import QWidget, QLabel, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QComboBox
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
import siriushla.util as _util
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import SiriusSpectrogramView, SiriusConnectionSignal
from siriushla.si_ap_sofb.graphics.base import BaseWidget


class OrbitWidget(BaseWidget):

    def __init__(self, parent, prefix, ctrls=dict(), acc='SI'):
        self._chans = []
        if not ctrls:
            self._chans, ctrls = self.get_default_ctrls(prefix)

        names = ['Line {0:d}'.format(i+1) for i in range(2)]
        super().__init__(parent, prefix, ctrls, names, True, acc)

        self.updater[0].some_changed('val', 'Online Orbit')
        self.updater[0].some_changed('ref', 'Reference Orbit')
        self.findChild(QComboBox, 'ComboBox_val0').setCurrentIndex(3)
        self.findChild(QComboBox, 'ComboBox_ref0').setCurrentIndex(4)

        self.add_buttons_for_images()

    def add_buttons_for_images(self):
        grpbx = QGroupBox('Other Graphics', self)
        vbl = QVBoxLayout(grpbx)
        self.hbl.addWidget(grpbx)
        self.hbl.addStretch(1)
        btn = QPushButton('MultiTurn Graphics', grpbx)
        vbl.addWidget(btn)
        Window = create_window_from_widget(
            MultiTurnWidget, name='MultiTurnWindow', size=(1000, 1800))
        _util.connect_window(
            btn, Window, self,
            sigs=self.updater[0].raw_ref_sig,
            prefix=self.prefix, acc=self.acc)

    def channels(self):
        chans = super().channels()
        chans.extend(self._chans)
        return chans

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


class MultiTurnWidget(QWidget):

    def __init__(self, parent, sigs, prefix, acc='SI'):
        super().__init__(parent)
        self.prefix = prefix
        self.acc = acc
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
        lab = QLabel('Horizontal Orbit', self)
        lab.setStyleSheet("font: 20pt \"Sans Serif\";\nfont-weight: bold;")
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.addWidget(self.spectx)
        vbl.addSpacing(50)
        lab = QLabel('Vertical Orbit', self)
        lab.setStyleSheet("font: 20pt \"Sans Serif\";\nfont-weight: bold;")
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.addWidget(self.specty)

    def setreforbits(self, pln, orb):
        if pln.lower() == 'x':
            self.spectx.setreforbit(orb)
        else:
            self.specty.setreforbit(orb)


class Spectrogram(SiriusSpectrogramView):

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
        print(img.shape)
        if hasattr(self, '_ref_orbit'):
            return img - self._ref_orbit[None, :]
        return img

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            pos = self._image_item.mapFromDevice(ev.pos())
            if pos.y() > 0 and pos.y() <= self._image_item.height():
                self.multiturnidx.send_value_signal[int].emit(int(pos.y()))
        super().mousePressEvent(ev)


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
