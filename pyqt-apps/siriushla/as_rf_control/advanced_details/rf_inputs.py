"""Advanced details for monitoring RF Inputs."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QSizePolicy as QSzPlcy, \
    QSpacerItem

from ...widgets import SiriusDialog, SiriusLabel
from ..util import SEC_2_CHANNELS


class RFInputsDetails(SiriusDialog):
    """Advanced details for monitoring RF Inputs."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'RF Inputs Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['RF Inputs'][self.system]
        else:
            self.syst_dict = self.chs['RF Inputs']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setVerticalSpacing(9)
        lay.setHorizontalSpacing(18)

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0, 1, 9)
        lay.addWidget(QLabel('In-Phase', alignment=Qt.AlignCenter), 1, 2)
        lay.addWidget(QLabel('Quadrature', alignment=Qt.AlignCenter), 1, 3)
        lay.addWidget(QLabel('Amp', alignment=Qt.AlignCenter), 1, 4)
        lay.addWidget(QLabel('Phase', alignment=Qt.AlignCenter), 1, 5)
        lay.addItem(QSpacerItem(24, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 1, 6)
        lay.addWidget(QLabel('Power', alignment=Qt.AlignCenter), 1, 7, 1, 2)

        row = 2
        for key, dic in self.syst_dict.items():
            lay.addWidget(QLabel(
                key, alignment=Qt.AlignCenter), row, 0)
            lay.addWidget(QLabel(
                dic['Label'], alignment=Qt.AlignLeft), row, 1)
            column = 2
            for k, val in dic.items():
                if k != 'Label' and val != '-':
                    lb = SiriusLabel(self, self.prefix+val)
                    lb.showUnits = True
                    lay.addWidget(lb, row, column)
                    column += 1
                elif val == '-':
                    lay.addWidget(QLabel(
                        '-', alignment=Qt.AlignCenter), row, column)
                    column += 1
                if column == 6:
                    column += 1
            row += 1
