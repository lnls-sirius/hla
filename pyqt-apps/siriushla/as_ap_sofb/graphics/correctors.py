"""Control the Correctors Graphic Displnay."""

from pyqtgraph import mkPen
from qtpy.QtWidgets import QCheckBox, QLabel, QHBoxLayout, QGroupBox, \
    QSizePolicy as QSzPol
from qtpy.QtGui import QColor
from siriushla.widgets import SiriusConnectionSignal as _ConnSig, SiriusLabel
from siriushla.as_ap_sofb.graphics.base import BaseWidget, InfLine


class CorrectorsWidget(BaseWidget):

    def __init__(self, parent, device, prefix='', ctrls=dict(), acc='SI'):
        self._chans = []
        if not ctrls:
            self._chans, ctrls = self.get_default_ctrls(device, prefix)

        names = ('DeltaKicks', 'Kicks')
        super().__init__(parent, device, ctrls, names, False, prefix, acc)

        self.updater[0].some_changed('val', 'Delta Kicks')
        self.updater[0].some_changed('ref', 'Zero')
        self.updater[1].some_changed('val', 'Kicks')
        self.updater[1].some_changed('ref', 'Zero')

        if acc in {'SI', 'BO'}:
            self.add_RF_kicks()
        self.add_kicklimits_curves()

    def add_RF_kicks(self):
        grpbx = QGroupBox('RF', self)
        vbl = QHBoxLayout(grpbx)
        self.hbl_nameh.addWidget(grpbx)

        hbl = QHBoxLayout()
        vbl.addLayout(hbl)
        lbl = QLabel('Frequency', grpbx)
        hbl.addWidget(lbl)
        lbl = SiriusLabel(
            grpbx, self.devpref.substitute(propty='KickRF-Mon'))
        lbl.showUnits = True
        lbl.setSizePolicy(QSzPol.Fixed, QSzPol.Preferred)
        lbl.setStyleSheet('min-width: 8em;')
        hbl.addWidget(lbl)

        hbl = QHBoxLayout()
        vbl.addLayout(hbl)
        lbl = QLabel('Delta Freq.', grpbx)
        hbl.addWidget(lbl)
        lbl = SiriusLabel(
            grpbx, self.devpref.substitute(propty='DeltaKickRF-Mon'))
        lbl.showUnits = True
        lbl.setSizePolicy(QSzPol.Fixed, QSzPol.Preferred)
        lbl.setStyleSheet('min-width: 6em;')
        hbl.addWidget(lbl)

    def add_kicklimits_curves(self):
        grpbx = QGroupBox('Show Kick Limits', self)
        vbl = QHBoxLayout(grpbx)
        self.hbl_namev.addStretch(1)
        self.hbl_namev.addWidget(grpbx)
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
                chan = _ConnSig(
                    self.devpref.substitute(propty=pvi + corr + '-RB'))
                self._chans.append(chan)
                chan.new_value_signal[float].connect(maxkick.setValue)
                chan.new_value_signal[float].connect(minkick.setValue)
                chb.toggled.connect(maxkick.setVisible)
                chb.toggled.connect(minkick.setVisible)
            chb.setChecked(False)

    def channels(self):
        chans = super().channels()
        chans.extend(self._chans)
        return chans

    @staticmethod
    def get_default_ctrls(device, prefix=''):
        basename = device.substitute(prefix=prefix)
        chans = [
            _ConnSig(basename.substitute(propty='DeltaKickCH-Mon')),
            _ConnSig(basename.substitute(propty='DeltaKickCV-Mon')),
            _ConnSig(basename.substitute(propty='KickCH-Mon')),
            _ConnSig(basename.substitute(propty='KickCV-Mon'))]
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
