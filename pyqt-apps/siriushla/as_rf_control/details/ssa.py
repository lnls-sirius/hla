"""SSA Details."""

import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QCheckBox, QGridLayout, QGroupBox, QHBoxLayout, \
    QLabel, QPushButton, QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, \
    QVBoxLayout, QWidget

from ...util import connect_window
from ...widgets import PyDMLed, PyDMLedMultiChannel, SiriusDialog, \
    SiriusLabel, SiriusLedAlert, SiriusLedState, SiriusTimePlot
from ..advanced_details import ACPanelDetails, SSACurrentsDetails
from ..custom_widgets import RFTitleFrame
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


class SSADetailsSI(SiriusDialog):
    """SSA Details for storage ring."""

    def __init__(self, parent, prefix='', num='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = 'SI'
        self.chs = SEC_2_CHANNELS[self.section]
        self.num = num
        self.system = system
        self.setObjectName(self.section+'App')
        self.syst_dict = self.chs['SSADtls'][self.system]
        title = f'{self.section}{self.system} SSA 0{self.num} Details'
        self.setWindowTitle(title)
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)

        title_frame = RFTitleFrame(self, self.system)
        lay_title = QHBoxLayout(title_frame)
        lay_title.addWidget(QLabel(
            f'<h4>SSA 0{self.num} Details</h4>', alignment=Qt.AlignCenter))

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

        lay.addWidget(title_frame)
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
        buttons_lay = QHBoxLayout()
        pb_curr = QPushButton(
            qta.icon('fa5s.external-link-alt'), ' Currents', self)
        connect_window(pb_curr, SSACurrentsDetails, parent=self,
            prefix=self.prefix, section=self.section, num=self.num,
            system=self.system)
        pb_curr.setStyleSheet('min-width: 6em;')
        buttons_lay.addWidget(pb_curr)

        # AC Panel
        pb_acpnl = QPushButton(
            qta.icon('fa5s.external-link-alt'), ' AC Panel', self)
        connect_window(pb_acpnl, ACPanelDetails, parent=self,
            prefix=self.prefix, section=self.section, num=self.num,
            system=self.system)
        pb_acpnl.setStyleSheet('min-width: 6em;')
        buttons_lay.addWidget(pb_acpnl)

        lay.addLayout(buttons_lay, row_general, 0, 1, 4)

        # Alerts
        lay_alerts = QGridLayout()
        row_alerts = 0
        column = 0
        for _, ls in self.syst_dict['Alerts'].items():
            lay_alerts.addWidget(QLabel(ls[0], alignment=Qt.AlignCenter),
                row_alerts, column)
            lay_alerts.addWidget(SiriusLedAlert(
                self, self.prefix+self._substitute_pv_macros(ls[1])),
                row_alerts, column+1)
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
                pt_100_channels = {
                    self._substitute_pv_macros(
                        self.prefix+chs_dict['PT-100'][0], suffix): 0,
                    self._substitute_pv_macros(
                        self.prefix+chs_dict['PT-100'][1], suffix): 0
                }
                led_pt100 = PyDMLedMultiChannel(self, pt_100_channels)

                lay.addWidget(QLabel(
                    f'HeatSink {self.sink_count}{s}',
                    alignment=Qt.AlignRight | Qt.AlignVCenter), row, 0)
                lay.addWidget(lb_temp, row, 1, alignment=Qt.AlignCenter)
                lay.addWidget(SiriusLedAlert(
                    self, self._substitute_pv_macros(
                        self.prefix+chs_dict['Tms'], suffix)),
                    row, 2, alignment=Qt.AlignCenter)
                lay.addWidget(led_pt100, row, 3, alignment=Qt.AlignCenter)

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
            cbx.setObjectName(suffix)
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
                cbx.setObjectName(f'{graph_idx+1}{k}')
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
                self.curves_temp[f'{graph_idx+1}{k}'] = graph_temp.curveAtIndex(
                    graph_idx)
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


class SSADetailsBO(SiriusDialog):
    """SSA Details for booster ring."""

    def __init__(self, parent, prefix=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = 'BO'
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.syst_dict = self.chs['SSADtls']
        self.setWindowTitle(f'{self.section} SSA Details')
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(9)
        lay.setAlignment(Qt.AlignTop)

        title_frame = RFTitleFrame(self)
        lay_title = QHBoxLayout(title_frame)
        lay_title.addWidget(QLabel(
            '<h4>SSA Details</h4>', alignment=Qt.AlignCenter))

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

        lay.addWidget(title_frame)
        lay.addWidget(dtls)

    def _setupDiagLay(self):
        lay = QGridLayout()
        lay.setSpacing(9)
        lay.setAlignment(Qt.AlignTop)

        # Temperatures
        gbox_temp = QGroupBox('Temperatures')
        lay_temp = QGridLayout()
        gbox_temp.setLayout(lay_temp)
        lay_temp.addWidget(QLabel(
            '<h4>TMS</h4>', alignment=Qt.AlignCenter), 1, 2)
        lay_temp.addWidget(QLabel(
            '<h4>PT-100</h4>', alignment=Qt.AlignCenter), 1, 3)

        for i in range(1, 7):
            lb_temp = SiriusLabel(
                self, self._substitute_pv_macros(
                    self.prefix+self.syst_dict['HeatSink']['Temp'], i))
            lb_temp.showUnits = True
            pt_100_channels = {
                self._substitute_pv_macros(
                    self.prefix+self.syst_dict['HeatSink']['PT-100'][0], i): 0,
                self._substitute_pv_macros(
                    self.prefix+self.syst_dict['HeatSink']['PT-100'][1], i): 0
            }
            led_pt100 = PyDMLedMultiChannel(self, pt_100_channels)

            lay_temp.addWidget(QLabel(
                f'<h4>HeatSink {i}</h4>', alignment=Qt.AlignCenter), i+1, 0)
            lay_temp.addWidget(lb_temp, i+1, 1, alignment=Qt.AlignCenter)
            lay_temp.addWidget(SiriusLedAlert(
                self, self._substitute_pv_macros(
                    self.prefix+self.syst_dict['HeatSink']['TMS'], i)),
                i+1, 2, alignment=Qt.AlignCenter)
            lay_temp.addWidget(led_pt100, i+1, 3, alignment=Qt.AlignCenter)
            row = i+2

        lb_temp = SiriusLabel(
            self, self.prefix+self.syst_dict['PreAmp']['Temp'])
        lb_temp.showUnits = True

        lay_temp.addWidget(QLabel(
            '<h4>PreAmp 01</h4>', alignment=Qt.AlignCenter), row, 0)
        lay_temp.addWidget(lb_temp, row, 1, alignment=Qt.AlignCenter)
        lay_temp.addWidget(QLabel('-', alignment=Qt.AlignCenter), row, 2)
        lay_temp.addWidget(SiriusLedState(
            self, self.prefix+self.syst_dict['PreAmp']['PT-100']),
            row, 3, alignment=Qt.AlignCenter)
        lay.addWidget(gbox_temp, 0, 0, 1, 3)

        # AC Panel
        gbox_ac = QGroupBox('AC Panel')
        lay_ac = QGridLayout()
        gbox_ac.setLayout(lay_ac)

        lb_volt = SiriusLabel(self, self.prefix+self.syst_dict['AC']['Volt'])
        lb_volt.showUnits = True
        lb_curr = SiriusLabel(self, self.prefix+self.syst_dict['AC']['Curr'])
        lb_curr.showUnits = True

        lay_ac.addWidget(QLabel(
            '<h4>AC/DC Panel Interlock</h4>',
            alignment=Qt.AlignRight | Qt.AlignVCenter), 0, 0)
        lay_ac.addWidget(SiriusLedAlert(
            self, self.prefix+self.syst_dict['AC']['Intlk']),
            0, 1, alignment=Qt.AlignCenter)
        lay_ac.addWidget(QLabel(
            '<h4>Control Mode</h4>',
            alignment=Qt.AlignRight | Qt.AlignVCenter), 1, 0)
        lay_ac.addWidget(SiriusLabel(
            self, self.prefix+self.syst_dict['AC']['Ctrl']),
            1, 1, alignment=Qt.AlignCenter)
        lay_ac.addWidget(QLabel(
            '<h4>300 Vdc Enable</h4>',
            alignment=Qt.AlignRight | Qt.AlignVCenter), 2, 0)
        lay_ac.addWidget(SiriusLedState(
            self, self.prefix+self.syst_dict['AC']['300Vdc']),
            2, 1, alignment=Qt.AlignCenter)
        lay_ac.addWidget(QLabel(
            '<h4>AC/DC Voltage</h4>',
            alignment=Qt.AlignRight | Qt.AlignVCenter), 3, 0)
        lay_ac.addWidget(lb_volt, 3, 1)
        lay_ac.addWidget(QLabel(
            '<h4>AC/DC Current</h4>',
            alignment=Qt.AlignRight | Qt.AlignVCenter), 4, 0)
        lay_ac.addWidget(lb_curr, 4, 1)
        lay.addWidget(gbox_ac, 1, 0, 3, 1)

        # Others
        lb_pwr = SiriusLabel(self, self.prefix+self.syst_dict['Pwr'])
        lb_pwr.showUnits = True
        pb_curr = QPushButton(
            qta.icon('fa5s.external-link-alt'), ' Currents', self)
        connect_window(pb_curr, SSACurrentsDetails, parent=self,
            prefix=self.prefix, section=self.section, num='',
            system='')

        lay.addWidget(QLabel(
            '<h4>Rotameter Flow</h4>', alignment=Qt.AlignCenter), 1, 1)
        lay.addWidget(SiriusLedAlert(
            self, self.prefix+self.syst_dict['Rot']),
            1, 2, alignment=Qt.AlignCenter)
        lay.addWidget(QLabel(
            '<h4>Power</h4>', alignment=Qt.AlignCenter), 2, 1)
        lay.addWidget(lb_pwr, 2, 2)
        lay.addWidget(pb_curr, 3, 1, alignment=Qt.AlignHCenter)

        return lay

    def _setupGraphsLay(self):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        graph_hs = SiriusTimePlot(self)
        graph_hs.maxRedrawRate = 2
        graph_hs.setShowXGrid(True)
        graph_hs.setShowYGrid(True)
        graph_hs.setAutoRangeX(True)
        graph_hs.setAutoRangeY(True)
        graph_hs.setBackgroundColor(QColor(255, 255, 255))
        graph_hs.setTimeSpan(1800)
        graph_hs.maxRedrawRate = 2

        lay_cboxes = QGridLayout()
        colors = ['blue', 'red', 'magenta', 'darkGreen', 'darkRed', 'darkBlue']
        column = 0
        self.curves_hs = {}
        for i in range(len(colors)):
            # Table
            name = f'H{i+1}'
            cbx = QCheckBox(self)
            cbx.setChecked(True)
            cbx.setObjectName(name)
            cbx.setStyleSheet('color:'+colors[i]+'; max-width: 1.2em;')
            cbx.stateChanged.connect(self._handle_hs_curves_visibility)
            lb_desc = QLabel(name)
            lb_desc.setStyleSheet(
                'min-height: 1.5em; color:'+colors[i]+'; max-width: 8em;'
                'qproperty-alignment: AlignCenter;')
            lay_cboxes.addWidget(cbx, 0, column)
            lay_cboxes.addWidget(lb_desc, 0, column+1)
            column += 2

            # Graph
            channel = self._substitute_pv_macros(
                self.prefix+self.syst_dict['HeatSink']['Temp'], i+1)
            graph_hs.addYChannel(y_channel=channel, color=colors[i], name=name,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves_hs[name] = graph_hs.curveAtIndex(i)

        lay.addWidget(QLabel(
            '<h4>Heat Sinks Temperatures</h4>', alignment=Qt.AlignCenter))
        lay.addLayout(lay_cboxes)
        lay.addWidget(graph_hs)

        return lay

    def _substitute_pv_macros(self, pv_name, hs_num=''):
        if hs_num:
            pv_name = pv_name.replace('$(hs_num)', str(hs_num))
        return pv_name

    def _handle_hs_curves_visibility(self, state):
        name = self.sender().objectName()
        curve = self.curves_hs[name]
        curve.setVisible(state)
