import re
from qtpy.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLineEdit, \
    QLabel, QHBoxLayout, QGridLayout, QPushButton
from qtpy.QtCore import Qt, Slot
from siriushla.as_di_bpms.base import BaseWidget, GraphTime, GraphWave
from siriushla.as_di_bpms.main import BPMSummary


class SelectBPMs(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm_list=[]):
        super().__init__(parent=parent, prefix=prefix, bpm='')
        self.bpm_dict = {bpm: '' for bpm in bpm_list}
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

        wid = QWidget()
        vbl2 = QVBoxLayout(wid)
        vbl2.setSpacing(15)
        for bpm in sorted(self.bpm_dict.keys()):
            widb = BPMSummary(wid, prefix=self.prefix, bpm=bpm)
            vbl2.addWidget(widb)
            self.bpm_dict[bpm] = widb

        vbl.addWidget(scarea)
        scarea.setWidget(wid)
        self.scarea = scarea

        self.setObjectName('SelectBPMs')
        self.setStyleSheet("""#SelectBPMs{min-width:16em; min-height:12em;}""")

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


class SinglePassSummary(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm_list=[]):
        super().__init__(
            parent=parent, prefix=prefix, bpm='', data_prefix='SP_')
        self.bpm_dict = {bpm: '' for bpm in bpm_list}
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

        scarea = QScrollArea(self)
        scarea.setSizeAdjustPolicy(scarea.AdjustToContents)
        scarea.setWidgetResizable(True)

        wid = QWidget()
        gdl = QGridLayout(wid)
        gdl.setSpacing(15)
        for i, bpm in enumerate(sorted(self.bpm_dict.keys())):
            widb = QWidget(wid)
            vbl2 = QVBoxLayout(widb)
            vbl2.addWidget(QLabel(
                '<h3>'+bpm+'</h3>', alignment=Qt.AlignCenter))
            wbpm = self.create_graph(widb, bpm=bpm, typ='ant')
            vbl2.addWidget(wbpm)

            gdl.addWidget(widb, i // 3, i % 3)
            self.bpm_dict[bpm] = widb
        self.gdl = gdl
        vbl.addWidget(scarea)
        scarea.setWidget(wid)
        self.setStyleSheet('GraphWave{min-width:20em;min-height:15em;}')
        self.scarea = scarea

    def create_graph(self, wid, bpm, typ='pos'):
        text, unit, names, colors = self._get_properties(typ)
        if typ == 'pos':
            unit = unit[1:]
            suff = '-Mon'
            CLASS = GraphTime
        elif typ == 'ant':
            suff = 'ArrayData'
            CLASS = GraphWave
        else:
            suff = '-Mon'
            CLASS = GraphTime

        graph = CLASS(
            wid, prefix=self.prefix, bpm=bpm,
            data_prefix=self.data_prefix)
        graph.maxRedrawRate = 2.1
        graph.graph.plotItem.vb.autoRange()
        self.btnautorange.clicked.connect(graph.graph.plotItem.vb.autoRange)
        graph.setLabel('left', text=text, units=unit)
        for name, cor in zip(names, colors):
            opts = dict(
                y_channel=name+suff,
                name=name[2:],
                color=cor,
                lineStyle=1,
                lineWidth=1)  # NOTE: If > 1: very low performance
            if typ == 'pos':
                opts['y_channel'] = graph.get_pvname(
                    opts['y_channel'], is_data=False)
                graph.addYChannel(add_scale=1e-9, **opts)
            elif typ == 'amp':
                opts['y_channel'] = graph.get_pvname(
                    opts['y_channel'], is_data=False)
                graph.addYChannel(**opts)
            else:
                opts['name'] = text[:3] + name
                opts['y_channel'] = graph.get_pvname(opts['y_channel'])
                graph.addChannel(**opts)
        return graph

    def _get_properties(self, typ='pos'):
        if typ == 'pos':
            text = 'Positions'
            unit = 'nm'
            names = ('SPPosX', 'SPPosY', 'SPPosQ', 'SPSum')
            colors = ('blue', 'red', 'green', 'black')
        elif typ == 'ant':
            text = 'Antennas'
            unit = 'count'
            names = ('A', 'B', 'C', 'D')
            colors = ('blue', 'red', 'green', 'magenta')
        if typ == 'amp':
            text = 'Amplitudes'
            unit = 'count'
            names = ('SPAmplA', 'SPAmplB', 'SPAmplC', 'SPAmplD')
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


class MultiTurnSummary(BaseWidget):

    def __init__(self, parent=None, prefix='', bpm_list=[]):
        super().__init__(
            parent=parent, prefix=prefix, bpm='', data_prefix='GEN_')
        self.bpm_dict = {bpm: '' for bpm in bpm_list}
        self.setupui()
        print('here')

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

        scarea = QScrollArea(self)
        scarea.setSizeAdjustPolicy(scarea.AdjustToContents)
        scarea.setWidgetResizable(True)

        wid = QWidget()
        gdl = QGridLayout(wid)
        gdl.setSpacing(15)
        for i, bpm in enumerate(sorted(self.bpm_dict.keys())):
            widb = QWidget(wid)
            vbl2 = QVBoxLayout(widb)
            vbl2.addWidget(QLabel(
                '<h3>'+bpm+'</h3>', alignment=Qt.AlignCenter))
            wbpm = self.create_graph(widb, bpm=bpm, typ='pos')
            vbl2.addWidget(wbpm)

            gdl.addWidget(widb, i // 3, i % 3)
            self.bpm_dict[bpm] = widb
        self.gdl = gdl
        vbl.addWidget(scarea)
        scarea.setWidget(wid)
        self.setStyleSheet('GraphWave{min-width:20em;min-height:15em;}')
        self.scarea = scarea

    def create_graph(self, wid, bpm, typ='pos'):
        text, unit, names, colors = self._get_properties(typ)
        if typ == 'pos':
            unit = unit[1:]

        graph = GraphWave(
            wid, prefix=self.prefix, bpm=self.bpm,
            data_prefix=self.data_prefix)
        graph.maxRedrawRate = 2.1
        graph.graph.plotItem.vb.autoRange()
        self.btnautorange.clicked.connect(graph.graph.plotItem.vb.autoRange)
        graph.setObjectName('MultiTurnDataGraph')
        graph.setLabel('left', text=text, units=unit)
        for name, cor in zip(names, colors):
            opts = dict(
                y_channel=name+'ArrayData',
                name=text[:3]+name,
                color=cor,
                lineStyle=1,
                lineWidth=1)  # NOTE: If > 1: very low performance
            opts['y_channel'] = self.get_pvname(opts['y_channel'])
            if typ == 'pos':
                graph.addChannel(add_scale=1e-9, **opts)
            else:
                graph.addChannel(**opts)
        return graph

    def _get_properties(self, typ):
        if typ == 'pos':
            text = 'Positions'
            unit = 'nm'
            names = ('X', 'Y', 'Q', 'SUM')
            colors = ('blue', 'red', 'green', 'black')
        else:
            text = 'Antennas'
            unit = 'count'
            names = ('A', 'B', 'C', 'D')
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


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    import sys

    app = SiriusApplication()
    wind = SiriusDialog()
    hbl = QHBoxLayout(wind)
    bpm_names = [
        'SI-07SP:DI-BPM-1', 'SI-07SP:DI-BPM-2',
        'SI-01M1:DI-BPM', 'SI-01M2:DI-BPM',
        'SI-02M1:DI-BPM', 'SI-02M2:DI-BPM',
        'SI-03M1:DI-BPM', 'SI-03M2:DI-BPM',
        'SI-04M1:DI-BPM', 'SI-04M2:DI-BPM',
        'SI-05M1:DI-BPM', 'SI-05M2:DI-BPM',
        'SI-06M1:DI-BPM', 'SI-06M2:DI-BPM',
        ]
    widm = SelectBPMs(bpm_list=bpm_names)
    hbl.addWidget(widm)
    wind.show()
    sys.exit(app.exec_())
