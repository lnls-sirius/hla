"""Advanced details related to calibration equations and constants."""

from pydm.widgets.display_format import DisplayFormat
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem

from ...widgets import SiriusDialog, SiriusLabel
from ..util import SEC_2_CHANNELS


class CalEqDetails(SiriusDialog):
    """Advanced details related to calibration equations and constants."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'Calibration Equations Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['Equations'][self.system]
        else:
            self.syst_dict = self.chs['Equations']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0, 1, 3)

        row = 1
        column = 0
        for key, dic in self.syst_dict.items():
            if key != 'VGap' and key != 'Rsh':
                gbox = QGroupBox(key)
                gbox.setLayout(self._genericStatisticsLayout(dic))
                lay.addWidget(gbox, row, column)
                column += 1
                if column == 3:
                    column = 0
                    row += 1

        gbox_vgap = QGroupBox('VGap')
        gbox_vgap.setLayout(self._vgapLayout(self.syst_dict['VGap']))
        lay.addWidget(gbox_vgap, row, column)
        column += 1
        if column == 3:
            column = 0
            row += 1

        # Rsh
        lay_extra = QGridLayout()
        lay_extra.setVerticalSpacing(12)

        lb_rsh = SiriusLabel(self, self.prefix+self.syst_dict['Rsh'])
        lb_rsh.showUnits = True

        lay_extra.addItem(
            QSpacerItem(0, 18, QSzPlcy.Ignored, QSzPlcy.Fixed), 0, 0)
        lay_extra.addWidget(QLabel(
            'C4*F^4 + C3*F^3 + C2*F^2 + C1*F + C0',
            alignment=Qt.AlignCenter), 1, 0, 1, 2)
        lay_extra.addWidget(QLabel(
            'Rsh (Ohm)', alignment=Qt.AlignRight | Qt.AlignVCenter),
            2, 0)
        lay_extra.addWidget(lb_rsh, 2, 1, alignment=Qt.AlignCenter)

        lay.addLayout(lay_extra, row, column, alignment=Qt.AlignHCenter)

    def _genericStatisticsLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Header
        labels = ['C0', 'C1', 'C2', 'C3', 'C4', 'OFS']
        for i in range(len(labels)):
            lay.addWidget(QLabel(
                labels[i], alignment=Qt.AlignCenter), 0, i+1)

        # Body
        row = 1
        for key, val in chs_dict.items():
            if key != 'OFS':
                column = 1
                for i in range(len(labels)-1):
                    lb = SiriusLabel(
                        self, self.prefix+val+f'-RB.[{i}]')
                    lb.precisionFromPV = False
                    lb.precision = 3
                    lb.displayFormat = DisplayFormat.Exponential
                    lay.addWidget(QLabel(
                        key, alignment=Qt.AlignCenter), row, 0)
                    lay.addWidget(lb, row, column)
                    column += 1

                lb_ofs = SiriusLabel(self, self.prefix+chs_dict['OFS']+'-RB')
                lb_ofs.precisionFromPV = 0
                lb_ofs.precision = 3
                lb_ofs.displayFormat = DisplayFormat.Exponential
                lay.addWidget(lb_ofs, row, len(labels))

                row += 1

        return lay

    def _vgapLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Headers
        labels = ['C0', 'C1', 'C2', 'C3', 'C4']
        for i in range(len(labels)):
            lay.addWidget(QLabel(labels[i], alignment=Qt.AlignCenter), 0, i)
            lay.addWidget(QLabel(labels[i], alignment=Qt.AlignCenter), 2, i)

        # Bodies
        column = 0
        for i in range(len(labels)):
            for i, key in enumerate(['Hw to Amp', 'Amp to Hw']):
                lb = SiriusLabel(
                    self, self.prefix+chs_dict[key]+f'-RB.[{i}]')
                lb.precisionFromPV = False
                lb.precision = 3
                lb.displayFormat = DisplayFormat.Exponential

                row = 1 if i == 0 else 3
                lay.addWidget(lb, row, column)
            column += 1

        return lay
