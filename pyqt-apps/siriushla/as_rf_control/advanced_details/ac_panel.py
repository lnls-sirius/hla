"""SSA's AC Panel Details."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QSizePolicy as QSzPlcy, \
    QSpacerItem

from ...widgets import SiriusDialog, SiriusLabel
from ..util import SEC_2_CHANNELS


class ACPanelDetails(SiriusDialog):
    """SSA's AC Panel Details."""

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
            self.syst_dict = self.chs['ACPanel'][self.system]
            self.title = f"""
                {self.section}{self.system} SSA 0{self.num} AC Panel Details
                """
        else:
            self.syst_dict = self.chs['ACPanel']
            self.title = f'{self.section} SSA AC Panel Details'
        self.setWindowTitle(self.title)
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0, 1, 7)
        lay.addItem(QSpacerItem(0, 18, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)

        # Phases
        row = 3
        for i in range(1, 4):
            lay.addWidget(QLabel(
                f'<h4>Phase {i}</h4>', alignment=Qt.AlignCenter), row, 0)
            column = 1
            for _, val in self.syst_dict['Phs'].items():
                lb = SiriusLabel(
                    self, self._substitute_macros(self.prefix+val, i))
                lb.showUnits = True
                lay.addWidget(lb, row, column)
                column += 1
            row += 1

        lay.addWidget(QLabel(
            '<h4>Current</h4>', alignment=Qt.AlignCenter), 2, 1)
        lay.addWidget(QLabel(
            '<h4>Voltage</h4>', alignment=Qt.AlignCenter), 2, 2)
        lay.addWidget(QLabel(
            '<h4>THD</h4>', alignment=Qt.AlignCenter), 2, 3)
        lay.addItem(QSpacerItem(9, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 2, 4)

        # Line Voltage
        row = 3
        for key, val in self.syst_dict['LineVolt'].items():
            lb = SiriusLabel(self, self._substitute_macros(self.prefix+val))
            lb.showUnits = True
            lay.addWidget(QLabel(
                f'<h4>Line Voltage {key}</h4>',
                alignment=Qt.AlignCenter), row, 5)
            lay.addWidget(lb, row, 6)
            row += 1

        lay.addItem(QSpacerItem(0, 18, QSzPlcy.Ignored, QSzPlcy.Fixed), row, 0)
        row += 1
        old_row = row

        grid_lay = QGridLayout()
        grid_lay.setSpacing(9)
        grid_lay.setAlignment(Qt.AlignTop)
        row = 0

        # Current N
        lb_curr = SiriusLabel(
            self, self._substitute_macros(self.prefix+self.syst_dict['CurrN']))
        lb_curr.showUnits = True
        grid_lay.addWidget(QLabel(
            '<h4>Current N</h4>', alignment=Qt.AlignCenter), row, 0)
        grid_lay.addWidget(lb_curr, row, 1)
        row += 1

        # Frequency
        lb_freq = SiriusLabel(
            self, self._substitute_macros(self.prefix+self.syst_dict['Freq']))
        lb_freq.showUnits = True
        grid_lay.addWidget(QLabel(
            '<h4>Frequency</h4>', alignment=Qt.AlignCenter), row, 0)
        grid_lay.addWidget(lb_freq, row, 1)
        row += 1

        # Power Factor
        lb_pwr = SiriusLabel(
            self, self._substitute_macros(
                self.prefix+self.syst_dict['Pwr Factor']))
        lb_pwr.showUnits = True
        grid_lay.addWidget(QLabel(
            '<h4>Power Factor</h4>', alignment=Qt.AlignCenter), row, 0)
        grid_lay.addWidget(lb_pwr, row, 1)

        # Power S, Power P and Power Q
        row = 0
        for key, val in self.syst_dict['Pwr'].items():
            lb = SiriusLabel(self, self._substitute_macros(self.prefix+val))
            lb.showUnits = True
            grid_lay.addWidget(QLabel(
                f'<h4>Power {key}</h4>', alignment=Qt.AlignCenter), row, 2)
            grid_lay.addWidget(lb, row, 3)
            row += 1

        lay.addLayout(grid_lay, old_row, 0, 1, 7)

    def _substitute_macros(self, pv_name, phs_num=''):
        pv_name = pv_name.replace('$(NB)', str(self.num))
        if phs_num:
            pv_name = pv_name.replace('$(phs_num)', str(phs_num))
        return pv_name
