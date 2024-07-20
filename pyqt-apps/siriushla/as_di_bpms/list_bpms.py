import re
from qtpy.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLineEdit, \
    QLabel, QHBoxLayout, QGridLayout, QPushButton
from qtpy.QtCore import Qt, Slot
from siriushla.as_di_bpms.base import BaseWidget, GraphTime, GraphWave, \
    get_custom_widget_class
from siriushla.widgets import PyDMLedMultiChannel
from siriushla.util import connect_newprocess


class BPMSummary(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm=''):
        super().__init__(parent=parent, prefix=prefix, bpm=bpm)
        self.setObjectName(self.bpm.sec+'App')
        self.setupui()

    def setupui(self):
        hbl = QHBoxLayout(self)
        hbl.setContentsMargins(0, 0, 0, 0)
        chan2vals = {'RFFEasyn.CNCT': 1, 'ADCAD9510PllStatus-Mon': 1}
        chan2vals = {self.get_pvname(k): v for k, v in chan2vals.items()}
        led = PyDMLedMultiChannel(self, channels2values=chan2vals)
        led.setToolTip(self.bpm)
        hbl.addWidget(led)
        connect_newprocess(
            led, ['sirius-hla-as-di-bpm.py', '-p', self.prefix, self.bpm],
            parent=self, signal=led.clicked)


class SelectBPMs(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm_list=[]):
        super().__init__(parent=parent, prefix=prefix, bpm='')
        self.bpm_dict = {bpm: '' for bpm in bpm_list}
        self.setObjectName(bpm_list[0][:2] + 'App')
        is_si = all(map(lambda x: x.sec, bpm_list))
        self.ncols = 8 if is_si else 10
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('<h2>BPMs List</h2>', alignment=Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.addSpacing(20)

        search = QLineEdit(parent=self)
        search.setPlaceholderText("Search for BPMs...")
        search.textEdited.connect(self._filter_bpms)
        vbl.addWidget(search)

        scarea = QScrollArea(self)
        scarea.setSizeAdjustPolicy(scarea.AdjustToContents)
        scarea.setWidgetResizable(True)

        scr_ar_wid = QWidget()
        scr_ar_wid.setObjectName('scrollarea')
        scr_ar_wid.setStyleSheet(
            '#scrollarea {background-color: transparent;}')
        gdl = QGridLayout(scr_ar_wid)
        for i, bpm in enumerate(sorted(self.bpm_dict.keys())):
            widb = BPMSummary(scr_ar_wid, prefix=self.prefix, bpm=bpm)
            gdl.addWidget(widb, i // self.ncols, i % self.ncols)
            self.bpm_dict[bpm] = widb

        vbl.addWidget(scarea)
        scarea.setWidget(scr_ar_wid)
        self.scarea = scarea

    @Slot(str)
    def _filter_bpms(self, text):
        """Filter power supply widgets based on text inserted at line edit."""
        try:
            pattern = re.compile(text, re.I)
        except Exception:  # Ignore malformed patterns?
            pattern = re.compile("malformed")

        for bpm, wid in self.bpm_dict.items():
            wid.setVisible(bool(pattern.search(bpm)))
        # Sroll to top
        self.scarea.verticalScrollBar().setValue(0)


class AcqDataSummary(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm_list=[], mode='pos'):
        super().__init__(
            parent=parent, prefix=prefix, bpm='', data_prefix='GEN')
        self.bpm_dict = {bpm: '' for bpm in bpm_list}
        self.mode = mode.lower()
        self._name = bpm_list[0][:2] + 'App'
        self.setObjectName(self._name)
        self.setStyleSheet('#'+self._name+'{min-width:65em;min-height:38em;}')
        self.setupui()

    def setupui(self):
        vbl = QVBoxLayout(self)
        lab = QLabel('<h2>BPMs List</h2>', alignment=Qt.AlignCenter)
        vbl.addWidget(lab)
        vbl.addSpacing(20)

        hbl = QHBoxLayout()
        search = QLineEdit(parent=self)
        search.setPlaceholderText("Search for BPMs...")
        search.textEdited.connect(self._filter_bpms)
        hbl.addWidget(search)
        hbl.addStretch()
        self.btnautorange = QPushButton('Auto Range graphics', self)
        hbl.addWidget(self.btnautorange)
        vbl.addItem(hbl)

        sa_class = get_custom_widget_class(QScrollArea)
        scarea = sa_class(self)
        scarea.setSizeAdjustPolicy(scarea.AdjustToContents)
        scarea.setWidgetResizable(True)

        wid = QWidget()
        wid.setObjectName('scrollarea')
        wid.setStyleSheet('#scrollarea {background-color: transparent;}')
        gdl = QGridLayout(wid)
        gdl.setSpacing(15)
        for i, bpm in enumerate(sorted(self.bpm_dict.keys())):
            widb = QWidget(wid)
            vbl2 = QVBoxLayout(widb)
            vbl2.addWidget(QLabel(
                '<h3>'+bpm+'</h3>', alignment=Qt.AlignCenter))
            wbpm = self.create_graph(widb, bpm=bpm, typ=self.mode)
            vbl2.addWidget(wbpm)
            gdl.addWidget(widb, i // 3, i % 3)
            self.bpm_dict[bpm] = widb
        self.gdl = gdl
        vbl.addWidget(scarea)
        scarea.setWidget(wid)
        self.scarea = scarea

    def create_graph(self, wid, bpm, typ='pos'):
        text, unit, names, colors = self._get_properties(typ)
        if typ.startswith('pos'):
            unit = unit[1:]

        graph = GraphWave(
            wid, prefix=self.prefix, bpm=bpm,
            data_prefix=self.data_prefix)
        graph.maxRedrawRate = 2.1
        graph.graph.plotItem.vb.autoRange()
        self.btnautorange.clicked.connect(graph.graph.plotItem.vb.autoRange)
        graph.setObjectName('MultiTurnDataGraph')
        graph.setLabel('left', text=text, units=unit)
        for name, cor in zip(names, colors):
            opts = dict(
                y_channel=name+'Data',
                name=name,
                color=cor,
                lineStyle=1,
                lineWidth=1)  # NOTE: If > 1: very low performance
            opts['y_channel'] = graph.get_pvname(opts['y_channel'])
            if typ.startswith('pos'):
                graph.addChannel(add_scale=1e-9, **opts)
            else:
                graph.addChannel(**opts)
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph{min-width: 18em; min-height: 12em;}')
        return graph

    def _get_properties(self, typ):
        if typ.startswith('pos'):
            text = 'Positions'
            unit = 'nm'
            names = ('PosX', 'PosY', 'PosQ', 'Sum')
            colors = ('blue', 'red', 'green', 'black')
        else:
            text = 'Antennas'
            unit = 'count'
            names = ('AmplA', 'AmplB', 'AmplC', 'AmplD')
            colors = ('blue', 'red', 'green', 'magenta')
        return text, unit, names, colors

    @Slot(str)
    def _filter_bpms(self, text):
        """Filter power supply widgets based on text inserted at line edit."""
        try:
            pattern = re.compile(text, re.I)
        except Exception:
            return

        for i in range(self.gdl.rowCount()):
            for j in range(self.gdl.columnCount()):
                self.gdl.removeItem(self.gdl.itemAtPosition(i, j))
        wids = []
        for bpm, wid in self.bpm_dict.items():
            mat = bool(pattern.search(bpm))
            wid.setVisible(mat)
            if mat:
                wids.append(wid)

        for i, wid in enumerate(wids):
            self.gdl.addWidget(wid, i // 3, i % 3)
        # Sroll to top
        self.scarea.verticalScrollBar().setValue(0)
