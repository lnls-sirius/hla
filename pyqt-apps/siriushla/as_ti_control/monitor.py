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

    def __init__(self, device, link, prefix='', parent=None):
        super().__init__(parent)
        self.device = PVName(device)
        self.link = link
        self.prefix = prefix
        self._dic = {
            'EVG': EVG, 'EVR': EVR, 'EVE': EVE, 'AMCFPGAEVR': AFC,
            'Fout': FOUT}
        self.setupui()

    def setupui(self):
        if self.device.dev == 'Fout':
            name = self.device.dev + (
                '-' + self.device.idx if self.device.idx else '')
        elif self.device.dev == 'AMCFPGAEVR':
            name = 'AFCTI-' + (
                'TL' if 'TL' in self.device.sub else self.device.sub[:2])
        elif self.device.sec == 'LA':
            if 'RaCtrl' in self.device.sub:
                name = 'PS-TL'
            elif 'BIH01' in self.device.sub:
                name = 'LI-Diag'
            else:
                name = 'LI-Glob'
        elif self.device.sec == 'PA':
            name = 'PS-' + ('BO' if self.device.idx == '1' else 'SI')
        elif self.device.sec == 'RA':
            name = 'RF-' + ('BO' if 'BO' in self.device.sub else 'SI')
        elif 'RaInj' in self.device.sub:
            name = 'PU'
        elif 'BbB' in self.device.sub:
            name = 'DI-BbB'
        elif 'Diag' in self.device.sub:
            name = 'DI-' + (
                'DCCT' if self.device.sub[:2] == '14' else
                'Tune' if self.device.sub[:2] == '18' else
                'TL' if self.device.sub[:2] == '20' else '?')
        elif self.device.sec == 'BA':
            name = self.device.sec + '-' + self.device.sub
        else:
            name = self.device.dev
        clss = self._dic[self.device.dev]

        props = ['DevEnbl', 'Network', 'LinkStatus', 'IntlkStatus']
        suffs = ['-Sts', '-Mon', '-Mon', '-Mon']
        chng = [True, True, True, False]
        if self.device.dev == 'EVG':
            props[2] = 'RFStatus'
            props[3] = 'ACStatus'
            chng[3] = True
        elif self.device.dev == 'AMCFPGAEVR':
            props[1] = 'RefClkLocked'
            props = props[:-1]
        elif self.device.dev == 'Fout':
            props = props[:-1]

        channels2values = dict()
        for i, prop in enumerate(props):
            pvn = self.device.substitute(prefix=self.prefix, propty=prop+suffs[i])
            channels2values[pvn] = 1 if chng[i] else 0
        led = PyDMLedMultiChannel(
             parent=self, channels2values=channels2values)
        led.setToolTip(self.device)
        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        Window = create_window_from_widget(
            clss, title=self.device.device_name, icon=icon)
        connect_window(
            led, Window, None, signal=led.clicked,
            device=self.device, prefix=self.prefix)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(4)
        lay.addWidget(QLabel(name, self, alignment=Qt.AlignCenter))
        lay.addWidget(led, alignment=Qt.AlignCenter)


class HLButton(QWidget):

    def __init__(self, trigger, prefix='', parent=None):
        super().__init__(parent=parent)
        self.trigger = trigger
        self.prefix = prefix
        hl = QHBoxLayout()
        self.setLayout(hl)
        self.layout().setContentsMargins(0, 0, 0, 0)
        led = SiriusLedAlert(self)
        led.setToolTip(trigger)
        led.channel = trigger.substitute(
            prefix=self.prefix, propty='Status-Mon')
        self.layout().addWidget(led)
        icon = qta.icon('mdi.timer', color=get_appropriate_color(trigger.sec))
        Window = create_window_from_widget(
            HLTriggerDetailed, title=trigger, icon=icon)
        led.clicked.connect(lambda: QApplication.instance().open_window(
            Window, parent=None, device=trigger, prefix=prefix))


class MonitorHL(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        super().__init__('High Level Monitor', parent=parent)
        self.prefix = prefix
        self._setupui()
        self.setObjectName('ASApp')

    def _setupui(self):
        lay = QGridLayout()
        self.setLayout(lay)
        hltrigs = HLTimeSearch.get_hl_triggers()
        secs = sorted(set(map(lambda x: x.sec, hltrigs)))
        secs = {sec: [] for sec in secs}
        nrcols = 10
        for trig in hltrigs:
            secs[trig.sec].append(trig)

        for sec, trigs in secs.items():
            lab = QLabel(sec)
            lab.setStyleSheet('font-weight: bold;')
            lay.addWidget(lab, lay.rowCount(), 0, 1, nrcols)
            row = lay.rowCount()
            for i, trig in enumerate(sorted(trigs)):
                if i and not i % nrcols:
                    row = lay.rowCount()
                but = HLButton(trig, self.prefix, self)
                lay.addWidget(but, row, i % nrcols)


class MonitorLL(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        super().__init__('Low Level Monitor', parent=parent)
        self.prefix = prefix
        self._setupui()
        self.setObjectName('ASApp')

    def _setupui(self):
        evg = PVName(LLTimeSearch.get_evg_name())
        g1 = LLButton(evg, '', self.prefix, self)
        self.g1 = g1

        fouts = LLTimeSearch.get_evg2fout_mapping()
        fouts = [(out, down) for out, down in fouts.items()]

        g2 = self.setupdown(fouts)
        self.g2 = g2

        g3 = list()
        trgsrcs = LLTimeSearch.get_fout2trigsrc_mapping()
        for _, down in fouts:
            downs = trgsrcs[down.device_name]
            downs = sorted([(ou, dwn) for ou, dwn in downs.items()])
            g3.append(self.setupdown(downs))

        lay = QGridLayout(self)
        lay.setHorizontalSpacing(12)
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
        return [LLButton(pre, lnk, self.prefix, self) for lnk, pre in down]

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
        super().__init__(parent=parent)
        self.prefix = prefix
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
