"""Temperature Variations advanced details."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGridLayout, QGroupBox, QLabel, \
    QVBoxLayout, QWidget

from pyqtgraph import InfiniteLine, mkPen

from pydm.widgets.channel import PyDMChannel

from ...widgets import SiriusDialog, SiriusLabel, SiriusTimePlot, \
    SiriusLineEdit
from ..custom_widgets import RFTitleFrame
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


class TempVariationDetails(SiriusDialog):
    """Temperature Variations advanced details."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'CM Temp Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['TempVariations'][self.system]
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)

        title_frame = RFTitleFrame(self, self.system)
        lay_title = QVBoxLayout(title_frame)
        lay_title.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))

        wid_temp_var = QWidget(self)
        wid_temp_var.setMinimumSize(1300, 500)
        wid_temp_var.setMaximumSize(1300, 500)
        wid_temp_var.setLayout(
            self._TempMonLayout(self.syst_dict))

        lay.addWidget(title_frame)
        lay.addWidget(wid_temp_var)

    def _TempMonLayout(self, chs_dict):
        main_layout = QGridLayout()

        gbox_temp = QGroupBox('Temperature Variation')
        lay_var = QGridLayout()
        gbox_temp.setLayout(lay_var)

        pen = mkPen(color='k', width=2, style=Qt.DashLine)

        graph_temp = SiriusTimePlot(self)
        graph_temp.setShowXGrid(True)
        graph_temp.setShowYGrid(True)
        graph_temp.setShowLegend(True)
        graph_temp.setAutoRangeX(True)
        graph_temp.setAutoRangeY(True)
        graph_temp.setBackgroundColor(QColor(255, 255, 255))
        graph_temp.setTimeSpan(1800)
        graph_temp.maxRedrawRate = 2

        self.ref_lines = {}
        self.ref_channels = {}

        tags_a = ['BT110', 'BT111', 'BT112']
        tags_b = ['BT210', 'BT211', 'BT212']

        tags = tags_a if self.system == "A" else tags_b
        addr = 'TempRate'
        lims = ['Max', 'Min']
        for tag in tags:
            graph_temp.addYChannel(
                y_channel=self.prefix+chs_dict['Temp'][tag][addr][0],
                color=chs_dict['Temp'][tag][addr][1], name=tag,
                lineStyle=Qt.SolidLine, lineWidth=1)

            self.ref_lines[tag] = {}
            self.ref_channels[tag] = {}

            for lim in lims:
                pv_lim = self.prefix+chs_dict['Temp'][tag][lim]
                line = InfiniteLine(
                    pos=0, angle=0, pen=pen)
                graph_temp.addItem(line)
                self.ref_lines[tag][lim] = line
                channel = PyDMChannel(
                    address=pv_lim,
                    value_slot=lambda val, t=tag, l=lim: self._getTempLim(t, l, val)
                )
                channel.connect()
                self.ref_channels[tag][lim] = channel

        graph_temp.setLabel('left', 'K/min')

        lay_var.addWidget(graph_temp, 0, 0)

        gbox_delta = QGroupBox('Delta')
        lay_delta = QGridLayout()
        gbox_delta.setLayout(lay_delta)

        graph_delta = SiriusTimePlot(self)
        graph_delta.setShowXGrid(True)
        graph_delta.setShowYGrid(True)
        graph_delta.setShowLegend(True)
        graph_delta.setAutoRangeX(True)
        graph_delta.setAutoRangeY(True)
        graph_delta.setBackgroundColor(QColor(255, 255, 255))
        graph_delta.setTimeSpan(1800)
        graph_delta.maxRedrawRate = 2

        self.ref_lines_delta = {}
        self.ref_channels_delta = {}

        delta = 'Delta A' if self.system == "A" else 'Delta B'

        graph_delta.addYChannel(
            y_channel=self.prefix+chs_dict[delta]['Diff'],
            color='green', name='Diff',
            lineStyle=Qt.SolidLine, lineWidth=1)

        for lim in lims:
            pv_lim_delta = self.prefix+chs_dict[delta][lim]
            line_delta = InfiniteLine(
                pos=0, angle=0, pen=pen)
            graph_delta.addItem(line_delta)
            self.ref_lines_delta[lim] = line_delta
            channel_delta = PyDMChannel(
                address=pv_lim_delta,
                value_slot=lambda val, l=lim: self._getDeltaLim(l, val)
            )
            channel_delta.connect()
            self.ref_channels_delta[lim] = channel_delta

        graph_delta.setLabel('left', 'K')

        lay_delta.addWidget(graph_delta, 0, 0)

        gbox_interval = QGroupBox('Interval Time Setpoint')
        gbox_interval.setFixedSize(400, 70)
        lay_interval = QGridLayout()
        gbox_interval.setLayout(lay_interval)

        interval = 'Interval A' if self.system == "A" else 'Interval B'

        interval_time_lbl = QLabel(f'<h4>{interval}</h4>',
                                   alignment=Qt.AlignCenter)
        interval_time_sp = SiriusLineEdit(self,
                                       init_channel=self.prefix+chs_dict[interval])
        interval_time_rb = SiriusLabel(self,
                                       init_channel=self.prefix+chs_dict[interval])

        lay_interval.addWidget(interval_time_lbl, 0, 0, alignment=Qt.AlignCenter)
        lay_interval.addWidget(interval_time_sp, 0, 1, alignment=Qt.AlignCenter)
        lay_interval.addWidget(interval_time_rb, 0, 2, alignment=Qt.AlignCenter)

        main_layout.addWidget(gbox_temp, 1, 0)
        main_layout.addWidget(gbox_delta, 1, 1)
        main_layout.addWidget(gbox_interval, 0, 0, alignment=Qt.AlignLeft)

        return main_layout

    def _getTempLim(self, tag, lim, value):
        if value is not None:
            self.ref_lines[tag][lim].setPos(float(value))

    def _getDeltaLim(self, lim, value):
        if value is not None:
            self.ref_lines_delta[lim].setPos(float(value))
