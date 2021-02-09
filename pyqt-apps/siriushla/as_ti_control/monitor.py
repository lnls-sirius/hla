"""."""

from qtpy.QtCore import Qt, QPoint
from qtpy.QtGui import QPainter
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QGroupBox, \
    QHBoxLayout, QApplication, QVBoxLayout
import qtawesome as qta

from siriuspy.namesys import SiriusPVName as PVName
from siriuspy.search import LLTimeSearch, HLTimeSearch

from ..widgets import SiriusLedAlert, PyDMLedMultiChannel
from ..util import get_appropriate_color, connect_window
from ..widgets.windows import create_window_from_widget

from .low_level_devices import EVG, FOUT, AFC, EVR, EVE
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

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(4)
        if self.link:
            lay.addWidget(QLabel(self.link, self))
        lay.addWidget(led, alignment=Qt.AlignCenter)


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


class MonitorHL(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__('High Level Monitor', parent=parent)
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

        for sec in ('AS', 'LI', 'TB', 'BO', 'TS', 'SI'):
            lab = QLabel(sec)
            lab.setStyleSheet('font-weight: bold;')
            lay.addWidget(lab, lay.rowCount(), 0, 1, nrcols)
            row = lay.rowCount()
            for i, trig in enumerate(sorted(secs[sec])):
                if i and not i % nrcols:
                    row = lay.rowCount()
                but = HLButton(trig, self)
                lay.addWidget(but, row, i % nrcols)


class MonitorLL(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        super().__init__('Low Level Monitor', parent=parent)
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
        lay.setHorizontalSpacing(16)
        lay.setVerticalSpacing(20)
        align = Qt.AlignHCenter | Qt.AlignTop
        lay.addWidget(g1, 0, 0, 1, len(g3), align)
        for i, g in enumerate(g2):
            lay.addWidget(g, 1, i, align)
        self.g3 = list()
        for i, gs in enumerate(g3):
            for j, g in enumerate(gs):
                if not j:
                    self.g3.append(g)
                lay.addWidget(g, j+2, i)

    def setupdown(self, down):
        return [LLButton(self.prefix+pre, lnk, self) for lnk, pre in down]

    def paintEvent(self, event):
        super().paintEvent(event)
        sz = self.g1.size()
        p1 = self.g1.pos() + QPoint(sz.width()//2, sz.height())
        for i, g2 in enumerate(self.g2):
            sz = g2.size()
            p2 = g2.pos() + QPoint(sz.width()//2, 0)
            self.drawarrow(p1, p2)
            p2 += QPoint(0, sz.height())
            g3 = self.g3[i]
            p3 = g3.pos() + QPoint(g3.size().width()//2, 0)
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


class MonitorWindow(QWidget):

    def __init__(self, parent=None, prefix=''):
        self.prefix = prefix
        super().__init__(parent=parent)
        self._setupui()
        self.setObjectName('ASApp')

    def _setupui(self):
        self.title = QLabel(
            '<h2>Timing Monitor</h2>', alignment=Qt.AlignCenter)
        vl = QVBoxLayout(self)
        vl.addWidget(self.title)
        vl.addWidget(MonitorLL(self, prefix=self.prefix))
        vl.addWidget(MonitorHL(self, prefix=self.prefix))
        self.setStyleSheet("""
            QLed {
                min-height: 1.1em; max-height: 1.1em;
                min-width: 1.1em; max-width: 1.1em;}
        """)
