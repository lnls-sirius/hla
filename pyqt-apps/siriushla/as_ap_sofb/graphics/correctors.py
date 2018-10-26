"""Control the Correctors Graphic Displnay."""

from pyqtgraph import mkPen
from qtpy.QtWidgets import QCheckBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox
from qtpy.QtGui import QColor
from siriushla.widgets import SiriusConnectionSignal
from siriushla.as_ap_sofb.graphics.base import BaseWidget, InfLine


class CorrectorsWidget(BaseWidget):

    def __init__(self, parent, prefix, ctrls=dict(), acc='SI'):
        self._chans = []
        if not ctrls:
            self._chans, ctrls = self.get_default_ctrls(prefix)

        names = ('DeltaKicks', 'Kicks')
        super().__init__(parent, prefix, ctrls, names, False, acc)

        self.updater[0].some_changed('val', 'Delta Kicks')
        self.updater[0].some_changed('ref', 'Zero')
        self.updater[1].some_changed('val', 'Kicks')
        self.updater[1].some_changed('ref', 'Zero')

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
                maxkick = InfLine(
                    conv=1e-6, pos=0.0, pen=pen, angle=0, name=name)
                minkick = InfLine(conv=-1e-6, pos=0.0, pen=pen, angle=0)
                self.graph[pln].addItem(maxkick)
                self.graph[pln].addItem(minkick)
                chan = SiriusConnectionSignal(self.prefix + pvi + corr + '-RB')
                self._chans.append(chan)
                chan.new_value_signal[float].connect(maxkick.setValue)
                chan.new_value_signal[float].connect(minkick.setValue)
                chb.toggled.connect(maxkick.setVisible)
                chb.toggled.connect(minkick.setVisible)

    def channels(self):
        chans = super().channels()
        chans.extend(self._chans)
        return chans

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


def _main(prefix):
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = prefix + 'SI-Glob:AP-SOFB:'
    wid = CorrectorsWidget(win, prefix)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix
    import sys
    _main(vaca_prefix)
