from qtpy.QtCore import Qt, QPoint
from qtpy.QtGui import QPainter
from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, QWidget, \
    QVBoxLayout, QGridLayout, QHBoxLayout
from siriuspy.namesys import SiriusPVName as PVName
from siriuspy.search import HLTimeSearch, LLTimeSearch
from siriushla.widgets import SiriusLedAlert
from siriushla.util import connect_window
from siriushla.widgets.windows import create_window_from_widget
if __name__ == '__main__':
    from siriushla.as_ti_control import AFC, EVE, EVR, EVG, FOUT
else:
    from .afc import AFC
    from .evg import EVG
    from .evr_eve import EVR, EVE
    from .fout import FOUT


class Button(QWidget):

    def __init__(self, prefix, link, parent=None):
        super().__init__(parent)
        self.prefix = PVName(prefix)
        self.link = link
        self._dic = {
            'EVG': EVG, 'EVR': EVR, 'EVE': EVE, 'AMCFPGAEVR': AFC,
            'Fout': FOUT}
        self.setupui()

    def setupui(self):
        lbl0 = QLabel(self.link, self)

        name = self.prefix.sub + '-'
        if self.prefix.dev == 'AMCFPGAEVR':
            name += 'AMC'
        else:
            name += self.prefix.dev
        if self.prefix.idx:
            name += '-' + self.prefix.idx
        but = QPushButton(name, self)
        but.setAutoDefault(False)
        but.setDefault(False)
        clss = self._dic[self.prefix.dev]
        Window = create_window_from_widget(clss, title=self.prefix.device_name)
        connect_window(but, Window, self, prefix=self.prefix + ':')

        prop1 = 'Network'
        pp1 = 'Net'
        prop2 = 'LinkStatus'
        pp2 = 'Link'
        if self.prefix.dev == 'EVG':
            prop2 = 'RFStatus'
            pp2 = 'RFSts'
        elif self.prefix.dev == 'AMCFPGAEVR':
            prop1 = 'RefClkLocked'
            pp1 = 'Lckd'
        pv1 = self.prefix.substitute(propty=prop1+'-Mon')
        pv2 = self.prefix.substitute(propty=prop2+'-Mon')
        lbl1 = QLabel(pp1, self)
        lbl2 = QLabel(pp2, self)
        led1 = SiriusLedAlert(self, init_channel=pv1)
        led1.onColor, led1.offColor = led1.offColor, led1.onColor
        led2 = SiriusLedAlert(self, init_channel=pv2)
        led2.onColor, led2.offColor = led2.offColor, led2.onColor

        lay = QGridLayout(self)
        lay.addWidget(lbl0, 0, 0, 1, 5, Qt.AlignCenter)
        lay.addWidget(but, 1, 0, 1, 5)
        lay.addWidget(lbl1, 2, 0)
        lay.addWidget(led1, 2, 1)
        lay.addWidget(lbl2, 2, 3)
        lay.addWidget(led2, 2, 4)


class Summary(QWidget):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent=parent)
        self.prefix = prefix
        self.setupui()
        self.setObjectName('ASApp')

    def setupui(self):
        evg = LLTimeSearch.get_device_names({'dev': 'EVG'})
        g1 = Button(self.prefix+evg[0], '', self)
        self.g1 = g1

        downs = LLTimeSearch.get_device_names({'dev': 'Fout'})
        link = list(LLTimeSearch.In2OutMap[downs[0].dev])[0]
        downs2 = list()
        for down in downs:
            out = LLTimeSearch.get_evg_channel(down.substitute(propty=link))
            downs2.append((out.propty, down.device_name))

        g2 = self.setupdown(downs2)
        self.g2 = g2

        g3 = list()
        trgsrcs = LLTimeSearch.get_fout2trigsrc_mapping()
        for _, down in downs2:
            downs = trgsrcs[down.device_name]
            downs = sorted([(ou, dwn) for ou, dwn in downs.items()])
            g3.append(self.setupdown(downs))

        lay = QGridLayout(self)
        lay.setVerticalSpacing(30)
        align = Qt.AlignVCenter | Qt.AlignLeft
        lay.addWidget(g1, 0, 0, len(g3), 1, align)
        for i, g in enumerate(g2):
            lay.addWidget(g, i, 1, align)
        self.g3 = list()
        for i, gs in enumerate(g3):
            for j, g in enumerate(gs):
                if not j:
                    self.g3.append(g)
                lay.addWidget(g, i, j+2)
        lay.setColumnMinimumWidth(0, 300)
        lay.setColumnMinimumWidth(1, 200)

    def setupdown(self, down):
        return [Button(self.prefix+pre, lnk, self) for lnk, pre in down]

    def paintEvent(self, event):
        sz = self.g1.size()
        p1 = self.g1.pos() + QPoint(sz.width(), sz.height()//2)
        for i, g2 in enumerate(self.g2):
            sz = g2.size()
            p2 = g2.pos() + QPoint(0, sz.height()//2)
            self.drawarrow(p1, p2)
            p2 += QPoint(sz.width(), 0)
            g3 = self.g3[i]
            p3 = g3.pos() + QPoint(0, g3.size().height()//2)
            self.drawarrow(p2, p3)

    def drawarrow(self, p1, p2):
        line = self.drawline(p1, p2, 0)
        line = self.drawline(p2, p1, 10, True)
        line = self.drawline(p2, p1, -10, True)

    def drawline(self, p1, p2, angle, tip=False):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.blue)
        pen = painter.pen()
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.blue)
        painter.translate(p1)
        painter.rotate(angle)
        pt = (p2-p1)
        if tip:
            pt /= (pt.x()**2 + pt.y()**2)**0.5 / 20
        # painter.scale(scale, scale)
        # painter.drawLine(QPoint(0, 0), (p2-p1)*scale)
        painter.drawLine(QPoint(0, 0), pt)
        return painter

if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import SiriusMainWindow

    props = {'detailed', 'state', 'pulses', 'duration'}
    app = SiriusApplication()
    win = SiriusMainWindow()
    wid = Summary(parent=win)
    win.setCentralWidget(wid)
    win.show()
    sys.exit(app.exec_())
