from qtpy.QtCore import Qt, QPoint
from qtpy.QtGui import QPainter
from qtpy.QtWidgets import QLabel, QPushButton, QWidget, QGridLayout, \
    QGroupBox, QVBoxLayout, QHBoxLayout, QApplication
import qtawesome as qta

from siriuspy.namesys import SiriusPVName as PVName
from siriuspy.search import LLTimeSearch, HLTimeSearch
from siriushla.widgets import SiriusLedAlert, SiriusMainWindow, \
    PyDMLedMultiChannel
from siriushla.util import get_appropriate_color, connect_window
from siriushla.widgets.windows import create_window_from_widget
if __name__ == '__main__':
    from siriushla.as_ti_control import AFC, EVE, EVR, EVG, FOUT, \
        HLTriggerDetailed
else:
    from .afc import AFC
    from .evg import EVG
    from .evr_eve import EVR, EVE
    from .fout import FOUT
    from .hl_trigger import HLTriggerDetailed


class LLButton(QWidget):

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
        clss = self._dic[self.prefix.dev]

        props = ['DevEnbl', 'Network', 'LinkStatus', 'IntlkStatus']
        suffs = ['-Sts', '-Mon', '-Mon', '-Mon']
        chng = [True, True, True, False]
        if self.prefix.dev == 'EVG':
            props[2] = 'RFStatus'
            props[3] = 'ACStatus'
            chng[3] = True
        elif self.prefix.dev == 'AMCFPGAEVR':
            props[1] = 'RefClkLocked'
            props = props[:-1]
        elif self.prefix.dev == 'Fout':
            props = props[:-1]

        channels2values = dict()
        for i, prop in enumerate(props):
            pvn = self.prefix.substitute(propty=prop+suffs[i])
            channels2values[pvn] = 1 if chng[i] else 0
        led = PyDMLedMultiChannel(
             parent=self, channels2values=channels2values)
        led.setToolTip(self.prefix)
        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        Window = create_window_from_widget(
            clss, title=self.prefix.device_name, icon=icon)
        connect_window(
            led, Window, None, signal=led.clicked, prefix=self.prefix + ':')

        lay = QHBoxLayout(self)
        lay.addWidget(lbl0)
        lay.addWidget(led)


class HLButton(QWidget):

    def __init__(self, trigger, parent=None):
        super().__init__(parent=parent)
        hl = QHBoxLayout()
        self.setLayout(hl)
        self.layout().setContentsMargins(0, 0, 0, 0)
        led = SiriusLedAlert(self)
        led.setToolTip(trigger)
        led.channel = trigger.substitute(propty='Status-Mon')
        self.layout().addWidget(led)
        icon = qta.icon('mdi.timer', color=get_appropriate_color(trigger.sec))
        Window = create_window_from_widget(
            HLTriggerDetailed, title=trigger, icon=icon)
        led.clicked.connect(lambda: QApplication.instance().open_window(
            Window, parent=None, prefix=trigger + ':'))


class SummaryHL(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__('High Level Summary', parent=parent)
        self._setupui()
        self.setObjectName('ASApp')

    def _setupui(self):
        lay = QGridLayout()
        self.setLayout(lay)
        hltrigs = HLTimeSearch.get_hl_triggers()
        secs = set(map(lambda x: x.sec, hltrigs))
        secs = {sec: [] for sec in secs}
        nrcols = 10
        for trig in hltrigs:
            secs[trig.sec].append(trig)

        for sec in sorted(secs):
            lab = QLabel(sec)
            lab.setStyleSheet('font-weight: bold;')
            lay.addWidget(lab, lay.rowCount(), 0, 1, nrcols)
            row = lay.rowCount()
            for i, trig in enumerate(sorted(secs[sec])):
                if i and not i % nrcols:
                    row = lay.rowCount()
                but = HLButton(trig, self)
                lay.addWidget(but, row, i % nrcols)


class SummaryLL(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        super().__init__('Low Level Summary', parent=parent)
        self.prefix = prefix
        self._setupui()
        self.setObjectName('ASApp')

    def _setupui(self):
        evg = LLTimeSearch.get_device_names({'dev': 'EVG'})
        g1 = LLButton(self.prefix+evg[0], '', self)
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
        lay.setColumnMinimumWidth(0, 100)
        lay.setColumnMinimumWidth(1, 120)

    def setupdown(self, down):
        return [LLButton(self.prefix+pre, lnk, self) for lnk, pre in down]

    def paintEvent(self, event):
        super().paintEvent(event)
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
        self.drawline(p1, p2, 0)
        self.drawline(p2, p1, 10, True)
        self.drawline(p2, p1, -10, True)

    def drawline(self, p1, p2, angle, tip=False):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.blue)
        pen = painter.pen()
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.blue)
        painter.translate(p1)
        painter.rotate(angle)
        pt = (p2-p1)
        if tip:
            pt /= (pt.x()**2 + pt.y()**2)**0.5 / 10
        # painter.scale(scale, scale)
        # painter.drawLine(QPoint(0, 0), (p2-p1)*scale)
        painter.drawLine(QPoint(0, 0), pt)
        return painter


class SummaryWindow(SiriusMainWindow):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        self._setupui()
        self.setObjectName('ASApp')
        self.setWindowIcon(
            qta.icon('mdi.timer', color=get_appropriate_color('AS')))

    def _setupui(self):
        wid = QWidget(self)
        self.setCentralWidget(wid)
        gl = QGridLayout(wid)
        gl.addWidget(QLabel(
            '<h1>Timing Summary</h1>', alignment=Qt.AlignCenter), 0, 0, 1, 2)
        gl.addWidget(SummaryLL(self, prefix=self.prefix), 1, 0)
        gl.addWidget(SummaryHL(self, prefix=self.prefix), 1, 1)


if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import SiriusMainWindow

    props = {'detailed', 'state', 'pulses', 'duration'}
    app = SiriusApplication()
    win = SummaryWindow()
    win.show()
    sys.exit(app.exec_())
