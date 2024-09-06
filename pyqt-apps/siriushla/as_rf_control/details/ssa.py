"""SSA Details."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, QWidget

from ...widgets import PyDMLed, PyDMLedMultiChannel, SiriusDialog, \
    SiriusLabel, SiriusLedAlert, SiriusLedState
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
        self.setWindowTitle(f'{self.section} SSA 0{self.num} Details')
        if self.section == 'SI':
            self.syst_dict = self.chs['SSADtls'][self.system]
        else:
            self.syst_dict = self.chs['SSADtls']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        lay.addWidget(QLabel(
            f'<h4>SSA 0{self.num} Details</h4>',
            alignment=Qt.AlignCenter), 0, 0, 1, 4)

        # Racks
        lay_racks = QGridLayout()
        row = 0
        column = 0
        self.sink_count = 1
        for i in range(1, 5):
            gbox_rack = QGroupBox(f'Rack {i}')
            gbox_rack.setLayout(self._setupRackLay(
                str(i), self.syst_dict['Rack']))
            lay_racks.addWidget(gbox_rack, row, column)
            column += 1
            if column >= 2:
                row += 1
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
            self, self.prefix+self.syst_dict[f'Pre Amp {self.num}'][0])
        lb_preamp.showUnits = True
        lay.addWidget(QLabel('Pre Amp', alignment=Qt.AlignRight), 4, 0)
        lay.addWidget(lb_preamp, 4, 1)
        lay.addWidget(QLabel('-', alignment=Qt.AlignCenter), 4, 2)
        lay.addWidget(SiriusLedAlert(
            self, self.prefix+self.syst_dict[f'Pre Amp {self.num}'][1]),
            4, 3, alignment=Qt.AlignCenter)

        # In and Out Pwr
        lbs = ['In Pwr Fwd', 'In Pwr Rev', 'Out Pwr Fwd', 'Out Pwr Rev']
        row = 5
        for lb in lbs:
            lb_pwr = SiriusLabel(self, self._substitute_pv_macros(
                self.prefix+self.syst_dict[lb][0]))
            lb_pwr.showUnits = True
            lb_hw = SiriusLabel(self, self._substitute_pv_macros(
                self.prefix+self.syst_dict[lb][1]))
            lb_hw.showUnits = True
            lay.addWidget(QLabel(lb, alignment=Qt.AlignRight), row, 0)
            lay.addWidget(lb_pwr, row, 1)
            lay.addWidget(lb_hw, row, 2)
            lay.addWidget(SiriusLedAlert(self,
                self._substitute_pv_macros(self.prefix+self.syst_dict[lb][2])),
                row, 3, alignment=Qt.AlignCenter)
            row += 1

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

        tab_wid.addTab(wid_other, 'Other')
        lay.addWidget(tab_wid, 0, 0, 1, 2)

        # Status
        led_status = SiriusLedState(
            self, self._substitute_pv_macros(
                self.prefix+chs_dict['Status'], rack_num))
        led_status.setOffColor(PyDMLed.LightGreen)
        led_status.setOnColor(PyDMLed.DarkGreen)

        lay.addWidget(QLabel(
            'Status AC', alignment=Qt.AlignCenter), 1, 0)
        lay.addWidget(led_status, 1, 1, alignment=Qt.AlignCenter)

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
                pt_100_channels = {}
                led_pt100 = PyDMLedMultiChannel(self, )

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

    def _substitute_pv_macros(self, pv_name, suffix=''):
        pv_name = pv_name.replace('$(NB)', str(self.num))
        if suffix:
            pv_name = pv_name.replace('$(suffix)', suffix)
        return pv_name
