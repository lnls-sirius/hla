"""Loop and Ramp Limits advanced details."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel

from ...widgets import SiriusDialog, SiriusLabel, SiriusLineEdit, SiriusSpinbox
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


class LimitsDetails(SiriusDialog):
    """Loop and Ramp Limits advanced details."""

    def __init__(self, parent=None, prefix='', section='', system='', which=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.which = which
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = f'{self.which} Limits Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.which == 'Loop':
            key = 'Loops'
        else:
            key = 'RampDtls'
        if self.section == 'SI':
            self.syst_dict = self.chs[key][self.system]['Control']['Limits']
        else:
            self.syst_dict = self.chs[key]['Control']['Limits']
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0, 1, 4)

        row = 1
        for key, val in self.syst_dict.items():
            lb_val = SiriusLabel(self, self.prefix+val[1]+'-RB')
            lb_val.showUnits = True

            lay.addWidget(QLabel(key), row, 0)
            lay.addWidget(QLabel(val[0]), row, 1, alignment=Qt.AlignCenter)
            lay.addWidget(SiriusSpinbox(
                self, self.prefix+val[1]+'-SP'), row, 2)
            lay.addWidget(lb_val, row, 3)

            self._setupMaxMinEdit(lay, val[1], row+1, True)
            self._setupMaxMinEdit(lay, val[1], row+2, False)

            row += 3

    def _setupMaxMinEdit(self, lay, pv, row, is_max):
        if is_max:
            label = 'MAX'
            ending = '-SP.DRVH'
        else:
            label = 'MIN'
            ending = '-SP.DRVL'

        lb = SiriusLabel(self, self.prefix+pv+ending)
        lb.showUnits = True

        lay.addWidget(QLabel(label, alignment=Qt.AlignCenter), row, 1)
        lay.addWidget(SiriusLineEdit(self, self.prefix+pv+ending), row, 2)
        lay.addWidget(lb, row, 3)
