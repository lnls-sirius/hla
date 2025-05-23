"""Advanced details for monitoring RF Inputs."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QSizePolicy as QSzPlcy, \
    QSpacerItem, QFrame

from ...widgets import SiriusDialog, SiriusLabel
from ..custom_widgets import RFTitleFrame
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


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
            self.syst_dict_2 = self.chs['Quench Ratio'][self.system]
        else:
            self.syst_dict = self.chs['RF Inputs']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay.setAlignment(Qt.AlignTop)
        lay.setVerticalSpacing(9)
        lay.setHorizontalSpacing(18)

        title_frame = RFTitleFrame(self, self.system)
        lay_title = QGridLayout(title_frame)
        lay_title.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0)
        lay.addWidget(title_frame, 0, 0, 1, 9)

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

        # Ratio Calculation
        if self.section == 'SI':
            quench_ratio = SiriusLabel(
                self, self.prefix+self.syst_dict_2['Quench Cond 1'])
            quench_ratio.showUnits = True
            quench_ratio._keep_unit = True

            equench_ratio = SiriusLabel(
                self, self.prefix+self.syst_dict_2['E-quench'])
            equench_ratio.showUnits = True
            equench_ratio._keep_unit = True

            lay.addWidget(self.horizontal_separator(), row, 0, 1, 9)
            row += 1
            lay.addWidget(QLabel(
                'Quench Condition 1 (Rev Cav/Fwd Cav)', alignment=Qt.AlignRight), 
                row, 0, 1, 2)
            lay.addWidget(quench_ratio, row, 4, 1, 6, alignment=Qt.AlignLeft)
            row += 1
            lay.addWidget(QLabel(
                'E-Quench (Fwd Cav/V Cav)', alignment=Qt.AlignRight), 
                row, 0, 1, 2)
            lay.addWidget(equench_ratio, row, 4, 1, 6, alignment=Qt.AlignLeft)
            row += 1
            lay.addWidget(self.horizontal_separator(), row, 0, 1, 9)

    def horizontal_separator(self):
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            return line