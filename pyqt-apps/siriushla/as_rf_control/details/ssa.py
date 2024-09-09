"""SSA Details."""

import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QCheckBox, QGridLayout, QLabel, QPushButton, \
    QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, QVBoxLayout, QWidget

from ...util import connect_window
from ...widgets import PyDMLed, PyDMLedMultiChannel, SiriusDialog, \
    SiriusLabel, SiriusLedAlert, SiriusLedState, SiriusTimePlot
from ..advanced_details import SSACurrentsDetails
from ..util import SEC_2_CHANNELS


class SSADetails(SiriusDialog):
    """SSA Details."""

    def __init__(self, parent, prefix='', section='', num='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.chs = SEC_2_CHANNELS[self.section]
        self.num = num
        self.system = system
        self.setObjectName(self.section+'App')
        if self.section == 'SI':
            self.syst_dict = self.chs['SSADtls'][self.system]
            self.setWindowTitle(f'{self.section} SSA 0{self.num} Details')
        else:
            self.syst_dict = self.chs['SSADtls']
            self.setWindowTitle(f'{self.section} SSA Details')
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)

        dtls = QTabWidget(self)
        dtls.setObjectName(self.section+'Tab')
        dtls.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        wid_diag = QWidget(self)
        wid_diag.setLayout(self._setupDiagLay())
        dtls.addTab(wid_diag, 'Diagnostics')

        wid_graphs = QWidget(self)
        wid_graphs.setLayout(self._setupGraphsLay())
        dtls.addTab(wid_graphs, 'Graphs')

        if self.section == 'SI':
            title = f'<h4>SSA 0{self.num} Details</h4>'
        else:
            title = '<h4>SSA Details</h4>'
        lay.addWidget(QLabel(title, alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _setupDiagLay(self):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Racks
        lay_racks = QGridLayout()
        row = 0
        column = 0
        self.sink_count = 1
        for i in range(1, 5):
            lay_racks.addWidget(QLabel(
                f'<h4>Rack {i}</h4>', alignment=Qt.AlignCenter), row, column)
            lay_racks.addLayout(self._setupRackLay(
                str(i), self.syst_dict['Rack']), row+1, column)
            column += 1
            if column >= 2:
                row += 2
                column = 0

        lay.addLayout(lay_racks, 1, 0, 1, 4)
        lay.addItem(QSpacerItem(0, 9, QSzPlcy.Ignored, QSzPlcy.Fixed), 2, 0)

        # Runtime
        lb_run = SiriusLabel(
            self, self._substitute_pv_macros(
                self.prefix+self.syst_dict['Runtime']))
        lb_run.showUnits = True
        lay.addWidget(QLabel('Runtime', alignment=Qt.AlignRight), 3, 0)
        lay.addWidget(lb_run, 3, 1)
        lay.addWidget(QLabel('-', alignment=Qt.AlignCenter), 3, 2)
        lay.addWidget(QLabel('-', alignment=Qt.AlignCenter), 3, 3)

        # Pre Amp
        lb_preamp = SiriusLabel(
            self, self.prefix+self.syst_dict[f'Pre Amp{self.num}'][0])
        lb_preamp.showUnits = True
        lay.addWidget(QLabel('Pre Amp', alignment=Qt.AlignRight), 4, 0)
        lay.addWidget(lb_preamp, 4, 1)
        lay.addWidget(QLabel('-', alignment=Qt.AlignCenter), 4, 2)
        lay.addWidget(SiriusLedAlert(
            self, self.prefix+self.syst_dict[f'Pre Amp{self.num}'][1]),
            4, 3, alignment=Qt.AlignCenter)

        # In and Out Pwr
        lbs = ['In Pwr Fwd', 'In Pwr Rev', 'Out Pwr Fwd', 'Out Pwr Rev']
        row_general = 5
        for lb in lbs:
            lb_pwr = SiriusLabel(self, self._substitute_pv_macros(
                self.prefix+self.syst_dict[lb][0]))
            lb_pwr.showUnits = True
            lb_hw = SiriusLabel(self, self._substitute_pv_macros(
                self.prefix+self.syst_dict[lb][1]))
            lb_hw.showUnits = True
            lay.addWidget(QLabel(lb, alignment=Qt.AlignRight), row_general, 0)
            lay.addWidget(lb_pwr, row_general, 1)
            lay.addWidget(lb_hw, row_general, 2)
            lay.addWidget(SiriusLedAlert(self,
                self._substitute_pv_macros(self.prefix+self.syst_dict[lb][2])),
                row_general, 3, alignment=Qt.AlignCenter)
            row_general += 1

        # Currents
        pb_curr = QPushButton(
            qta.icon('fa5s.external-link-alt'), ' Currents', self)
        connect_window(pb_curr, SSACurrentsDetails, parent=self,
            prefix=self.prefix, section=self.section, num=self.num,
            system=self.system)
        pb_curr.setStyleSheet('min-width: 6em;')
        lay.addWidget(pb_curr, row_general, 1)


        # Alerts
        lay_alerts = QGridLayout()
        row_alerts = 0
        column = 0
        for _, ls in self.syst_dict['Alerts'].items():
            lay_alerts.addWidget(QLabel(ls[0], alignment=Qt.AlignCenter),
                row_alerts, column)
            lay_alerts.addWidget(SiriusLedAlert(
                self, self.prefix+ls[1]), row_alerts, column+1)
            column += 2
            if column == 6:
                row_alerts += 1
                column = 0

        lay.addItem(QSpacerItem(
            0, 9, QSzPlcy.Ignored, QSzPlcy.Fixed), row_general, 0)
        lay.addLayout(lay_alerts, row_general+1, 0, 1, 4)
        row_general += 2

        return lay

    def _setupGraphsLay(self):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Heat Sinks
        graph_hs, lay_cboxes = self._setup_heat_sink_graph()

        lay.addWidget(QLabel(
            '<h4>Heat Sinks Temperatures</h4>', alignment=Qt.AlignCenter))
        lay.addLayout(lay_cboxes)
        lay.addWidget(graph_hs)

        # Rack Temperatures
        graph_temp, lay_cboxes = self._setup_rack_temp_graph()

        lay.addWidget(QLabel(
            '<h4>Rack Temperatures</h4>', alignment=Qt.AlignCenter))
        lay.addLayout(lay_cboxes)
        lay.addWidget(graph_temp)

        return lay

    def _setupRackLay(self, rack_num, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        tab_wid = QTabWidget(self)
        tab_wid.setObjectName(self.section+'Tab')
        tab_wid.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        # Heat Sinks
        tab_wid.addTab(self._setup_heat_sink_wid(chs_dict), 'Heat Sinks')

        # Temp A and B, Voltage and Current
        wid_other = QWidget()
        lay_other = QGridLayout()
        lay_other.setSpacing(9)
        lay_other.setAlignment(Qt.AlignCenter)
        wid_other.setLayout(lay_other)

        lbs = ['Temp A', 'Temp B', 'Voltage', 'Current']
        for i, lb in enumerate(lbs):
            lb_val = SiriusLabel(self, self._substitute_pv_macros(
                self.prefix+chs_dict[lb], rack_num))
            lb_val.showUnits = True
            lay_other.addWidget(QLabel(
                lb, alignment=Qt.AlignCenter), i, 0)
            lay_other.addWidget(lb_val, i, 1, alignment=Qt.AlignCenter)

        # Status
        led_status = SiriusLedState(
            self, self._substitute_pv_macros(
                self.prefix+chs_dict['Status'], rack_num))
        led_status.setOffColor(PyDMLed.LightGreen)
        led_status.setOnColor(PyDMLed.DarkGreen)

        lay_other.addWidget(QLabel(
            'Status AC', alignment=Qt.AlignCenter), i+1, 0)
        lay_other.addWidget(led_status, i+1, 1, alignment=Qt.AlignCenter)

        tab_wid.addTab(wid_other, 'Other')
        lay.addWidget(tab_wid, 0, 0, 1, 2)

        return lay

    def _setup_heat_sink_wid(self, chs_dict):
        lay = QGridLayout()
        lay.setSpacing(9)
        lay.setAlignment(Qt.AlignTop)

        lay.addWidget(QLabel('TMS', alignment=Qt.AlignCenter), 0, 2)
        lay.addWidget(QLabel('PT-100', alignment=Qt.AlignCenter), 0, 3)

        row = 1
        for _ in range(2):
            suffixes = ['A', 'B']
            for s in suffixes:
                suffix = str(self.sink_count)+s

                lb_temp = SiriusLabel(
                    self, self._substitute_pv_macros(
                        self.prefix+chs_dict['Temp'], suffix))
                lb_temp.showUnits = True
                # pt_100_channels = {}
                # led_pt100 = PyDMLedMultiChannel(self, )

                lay.addWidget(QLabel(
                    f'HeatSink {self.sink_count}{s}',
                    alignment=Qt.AlignRight | Qt.AlignVCenter), row, 0)
                lay.addWidget(lb_temp, row, 1, alignment=Qt.AlignCenter)
                lay.addWidget(SiriusLedAlert(
                    self, self._substitute_pv_macros(
                        self.prefix+chs_dict['Tms'], suffix)),
                    row, 2, alignment=Qt.AlignCenter)
                # lay.addWidget(led_pt100, row, 3, alignment=Qt.AlignCenter)

                row += 1
            self.sink_count += 1

        wid = QWidget(self)
        wid.setLayout(lay)
        return wid

    def _setup_heat_sink_graph(self):
        graph_hs = SiriusTimePlot(self)
        graph_hs.setStyleSheet(
            'min-height:15em;min-width:20em;max-height:40em')
        graph_hs.maxRedrawRate = 2
        graph_hs.setShowXGrid(True)
        graph_hs.setShowYGrid(True)
        graph_hs.setAutoRangeX(True)
        graph_hs.setAutoRangeY(True)
        graph_hs.setBackgroundColor(QColor(255, 255, 255))
        graph_hs.setTimeSpan(1800)
        graph_hs.maxRedrawRate = 2

        lay_cboxes = QGridLayout()
        colors = ['blue', 'red', 'magenta', 'darkGreen', 'darkRed', 'black',
            'darkBlue', 'yellow', 'orangered', 'darkOliveGreen', 'darkMagenta',
            'chocolate', 'cyan', 'darkCyan', 'saddlebrown', 'darkSlateGrey']
        new_sink_count = 1
        cboxes_row = 0
        cboxes_column = 0
        self.curves_hs = {}
        for i in range(len(colors)):
            suffix_ending = ('A' if i % 2 == 0 else 'B')
            suffix = f'{new_sink_count}{suffix_ending}'

            # Table
            cbx = QCheckBox(self)
            cbx.setChecked(True)
            cbx.setStyleSheet('color:'+colors[i]+'; max-width: 1.2em;')
            cbx.stateChanged.connect(self._handle_hs_curves_visibility)
            lb_desc = QLabel(suffix)
            lb_desc.setStyleSheet(
                'min-height: 1.5em; color:'+colors[i]+'; max-width: 8em;'
                'qproperty-alignment: AlignCenter;')
            lay_cboxes.addWidget(cbx, cboxes_row, cboxes_column)
            lay_cboxes.addWidget(lb_desc, cboxes_row, cboxes_column+1)
            cboxes_column += 2
            if cboxes_column == 16:
                cboxes_row += 1
                cboxes_column = 0

            # Graph
            channel = self._substitute_pv_macros(
                self.prefix+self.syst_dict['Rack']['Temp'], suffix)
            graph_hs.addYChannel(y_channel=channel, color=colors[i],
                name=suffix, lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves_hs[suffix] = graph_hs.curveAtIndex(i)
            if i % 2 != 0:
                new_sink_count += 1

        return graph_hs, lay_cboxes

    def _setup_rack_temp_graph(self):
        graph_temp = SiriusTimePlot(self)
        graph_temp.setStyleSheet(
            'min-height:15em;min-width:20em;max-height:40em')
        graph_temp.maxRedrawRate = 2
        graph_temp.setShowXGrid(True)
        graph_temp.setShowYGrid(True)
        graph_temp.setAutoRangeX(True)
        graph_temp.setAutoRangeY(True)
        graph_temp.setBackgroundColor(QColor(255, 255, 255))
        graph_temp.setTimeSpan(1800)
        graph_temp.maxRedrawRate = 2

        lay_cboxes = QGridLayout()
        colors = {'A': ['blue', 'red', 'magenta', 'darkGreen'],
            'B': ['darkRed', 'black', 'darkBlue', 'yellow']}
        cboxes_row = 0
        cboxes_column = 0
        graph_idx = 0
        self.curves_temp = {}
        for i in range(1, 5):
            keys = ['A', 'B']
            for k in keys:
                # Table
                cbx = QCheckBox(self)
                cbx.setChecked(True)
                cbx.setStyleSheet('color:'+colors[k][i-1]+'; max-width: 1.2em;')
                cbx.stateChanged.connect(self._handle_temp_curves_visibility)
                lb_desc = QLabel(f'Rack {i} - Temp {k}')
                lb_desc.setStyleSheet(
                    'min-height: 1.5em; color:'+colors[k][i-1]+';'
                    'max-width: 8em;'
                    'qproperty-alignment: AlignCenter;')
                lay_cboxes.addWidget(cbx, cboxes_row, cboxes_column)
                lay_cboxes.addWidget(lb_desc, cboxes_row, cboxes_column+1)
                cboxes_column += 2
                if cboxes_column == 8:
                    cboxes_row += 1
                    cboxes_column = 0

                # Graph
                channel = self._substitute_pv_macros(
                    self.prefix+self.syst_dict['Rack'][f'Temp {k}'], str(i))
                graph_temp.addYChannel(y_channel=channel, color=colors[k][i-1],
                    name=i, lineStyle=Qt.SolidLine, lineWidth=1)
                self.curves_temp[graph_idx] = graph_temp.curveAtIndex(graph_idx)
                graph_idx += 1

        return graph_temp, lay_cboxes

    def _substitute_pv_macros(self, pv_name, suffix=''):
        pv_name = pv_name.replace('$(NB)', str(self.num))
        if suffix:
            pv_name = pv_name.replace('$(suffix)', suffix)
        return pv_name

    def _handle_hs_curves_visibility(self, state):
        name = self.sender().objectName()
        curve = self.curves_hs[name]
        curve.setVisible(state)

    def _handle_temp_curves_visibility(self, state):
        name = self.sender().objectName()
        curve = self.curves_temp[name]
        curve.setVisible(state)
