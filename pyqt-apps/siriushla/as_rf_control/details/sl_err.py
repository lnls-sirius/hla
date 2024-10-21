"""Slow Loop Control Error Details."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem, QVBoxLayout

from ...widgets import SiriusDialog, SiriusLabel, SiriusTimePlot, \
    SiriusWaveformPlot
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


class SlowLoopErrorDetails(SiriusDialog):
    """Slow Loop Control Error Details."""

    def __init__(self, parent=None, prefix='', section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.setWindowTitle('Slow Loop Control Error Details')
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(20)

        self.title = QLabel(
            '<h3>Slow Loop Control Error Details</h3>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(self.title)

        if self.section == 'SI':
            for key, chs_dict in self.chs['SL']['ErrDtls'].items():
                self._setupDetails(lay, key, chs_dict)
        else:
            self._setupDetails(lay, None, self.chs['SL']['ErrDtls'])

    def _setupDetails(self, lay, key, chs_dict):
        if key:
            lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
            lay.addWidget(QLabel(
                f'<h4>LLRF {key}</h4>', self, alignment=Qt.AlignCenter))

        lay_llrf = QHBoxLayout()
        lay_llrf.setAlignment(Qt.AlignTop)
        lay_llrf.setSpacing(0)

        lay_table = QGridLayout()
        lay_table.setAlignment(Qt.AlignVCenter)
        lay_table.setSpacing(9)
        lay_table.addWidget(QLabel(
            '<h4>Reference<h4>', self, alignment=Qt.AlignCenter), 1, 0)
        lay_table.addWidget(QLabel(
            '<h4>Input</h4>', self, alignment=Qt.AlignCenter), 2, 0)
        lay_table.addWidget(QLabel(
            '<h4>Error</h4>', self, alignment=Qt.AlignCenter), 3, 0)

        # I
        lb_iref = SiriusLabel(self, self.prefix+chs_dict['IRef'])
        lb_iref.showUnits = True
        lb_iinp = SiriusLabel(self, self.prefix+chs_dict['IInp'])
        lb_iinp.showUnits = True
        lb_ierr = SiriusLabel(self, self.prefix+chs_dict['IErr'])
        lb_ierr.showUnits = True
        lay_table.addWidget(QLabel(
            '<h4>I</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        lay_table.addWidget(lb_iref, 1, 1)
        lay_table.addWidget(lb_iinp, 2, 1)
        lay_table.addWidget(lb_ierr, 3, 1)

        # Q
        lb_qref = SiriusLabel(self, self.prefix+chs_dict['QRef'])
        lb_qref.showUnits = True
        lb_qinp = SiriusLabel(self, self.prefix+chs_dict['QInp'])
        lb_qinp.showUnits = True
        lb_qerr = SiriusLabel(self, self.prefix+chs_dict['QErr'])
        lb_qerr.showUnits = True
        lay_table.addWidget(QLabel(
            '<h4>Q</h4>', self, alignment=Qt.AlignCenter), 0, 2)
        lay_table.addWidget(lb_qref, 1, 2)
        lay_table.addWidget(lb_qinp, 2, 2)
        lay_table.addWidget(lb_qerr, 3, 2)

        lay_llrf.addLayout(lay_table)
        lay_llrf.addItem(QSpacerItem(15, 0, QSzPlcy.Fixed, QSzPlcy.Ignored))

        # Graphs
        self.setupGraphFasor(lay_llrf, chs_dict)
        self.setupGraphTime(lay_llrf, key, "Amp")
        self.setupGraphTime(lay_llrf, key, "Phs")

        lay.addLayout(lay_llrf)

    def setupGraphFasor(self, lay_llrf, chs_dict):
        graph_iq = SiriusWaveformPlot(
            parent=self, background=QColor(255, 255, 255))
        graph_iq.setStyleSheet(
            'min-height: 15em; min-width: 20em; max-height:15em;')
        graph_iq.maxRedrawRate = 2
        graph_iq.mouseEnabledX = True
        graph_iq.setShowXGrid(True)
        graph_iq.setShowYGrid(True)
        graph_iq.setShowLegend(True)
        graph_iq.setAutoRangeX(False)
        graph_iq.setAutoRangeY(False)
        graph_iq.setAxisColor(QColor(0, 0, 0))
        axx = graph_iq.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph_iq.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)

        lbl_axis = ["Q", "I"]
        channels = {
            'Input': {
                'X': self.prefix+chs_dict['IInp'],
                'Y': self.prefix+chs_dict['QInp']
            },
            'Reference': {
                'X': self.prefix+chs_dict['IRef'],
                'Y': self.prefix+chs_dict['QRef']
            }
        }
        graph_iq.setMinXRange(-1.0)
        graph_iq.setMaxXRange(1.0)
        graph_iq.setMinYRange(-1.0)
        graph_iq.setMaxYRange(1.0)

        graph_iq.setYLabels([lbl_axis[0]])
        graph_iq.setXLabels([lbl_axis[1]])
        graph_iq.setPlotTitle("I & Q Fasor")

        opts = dict(
            y_channel=channels['Input']['Y'],
            x_channel=channels['Input']['X'],
            name='Input',
            color='red',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph_iq.addChannel(**opts)

        opts = dict(
            y_channel=channels['Reference']['Y'],
            x_channel=channels['Reference']['X'],
            name='Reference',
            color='blue',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph_iq.addChannel(**opts)

        lay_llrf.addWidget(graph_iq)

    def setupGraphTime(self, lay_llrf, key, mode):
        graph = SiriusTimePlot(self)
        graph.setStyleSheet('min-height:15em;min-width:20em;max-height:15em;')
        graph.timeSpan = 120
        graph.maxRedrawRate = 2
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.backgroundColor = QColor(255, 255, 255)
        graph.setShowLegend(True)
        graph.setAxisColor(QColor(0, 0, 0))
        graph.setXLabels(["Time"])
        axx = graph.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)

        chs_dict = self.chs['SL']['Over']
        if self.section == 'SI':
            chs_dict = chs_dict[key]

        if mode == 'Amp':
            title = 'Amplitude'
            channels = {
                'Input': self.prefix+chs_dict['AInp'],
                'Reference': self.prefix+chs_dict['ARef']
            }
        else:
            title = 'Phase'
            channels = {
                'Input': self.prefix+chs_dict['PInp'],
                'Reference': self.prefix+chs_dict['PRef']
            }

        graph.setPlotTitle(title)
        graph.setYLabels([title])

        opts = dict(
            y_channel=channels['Input'],
            name='Input',
            color='red',
            lineStyle=1,
            lineWidth=3)
        graph.addYChannel(**opts)

        opts = dict(
            y_channel=channels['Reference'],
            name='Reference',
            color='blue',
            lineStyle=1,
            lineWidth=3)
        graph.addYChannel(**opts)

        lay_llrf.addWidget(graph)
