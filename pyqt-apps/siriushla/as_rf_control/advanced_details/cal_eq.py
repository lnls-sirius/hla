"""Advanced details related to calibration equations and constants."""

from pydm.widgets.display_format import DisplayFormat
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem

from ...widgets import SiriusDialog, SiriusLabel
from ..custom_widgets import RFTitleFrame
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


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
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        title_frame = RFTitleFrame(self, self.system)
        lay_title = QGridLayout(title_frame)
        lay_title.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0)
        lay.addWidget(title_frame, 0, 0, 1, 3)

        row = 1
        column = 0
        invalid_keys = ['VGap', 'r/Q', 'Q0', 'Rsh']
        for key, dic in self.syst_dict.items():
            if key not in invalid_keys:
                gbox = QGroupBox(key)
                gbox.setLayout(self._genericStatisticsLayout(dic))
                lay.addWidget(gbox, row, column)
                column += 1
                if column == 3:
                    column = 0
                    row += 1

        if self.section == 'BO':
            gbox_vgap = QGroupBox('VGap')
            gbox_vgap.setLayout(self._vgapLayout(self.syst_dict['VGap']))
            lay.addWidget(gbox_vgap, row, column)
            column += 1
            if column == 3:
                column = 0
                row += 1

        lay_extra = QGridLayout()
        lay_extra.setVerticalSpacing(12)

        lay_extra.addItem(
            QSpacerItem(0, 18, QSzPlcy.Ignored, QSzPlcy.Fixed), 0, 0)
        lay_extra.addWidget(QLabel(
            'C0 + C1*F + C2*F^2 + C3*F^3 + C4*F^4',
            alignment=Qt.AlignCenter), 1, 0, 1, 2)
        if self.section == 'SI':
            lb_rq = SiriusLabel(self, self.prefix+self.syst_dict['r/Q'])
            lb_rq.showUnits = True
            lb_q0 = SiriusLabel(self, self.prefix+self.syst_dict['Q0'])
            lb_q0.showUnits = True
            lay_extra.addWidget(QLabel(
                'r/Q', alignment=Qt.AlignRight | Qt.AlignVCenter),
                2, 0)
            lay_extra.addWidget(lb_rq, 2, 1, alignment=Qt.AlignCenter)
            lay_extra.addWidget(QLabel(
                'Q0', alignment=Qt.AlignRight | Qt.AlignVCenter),
                3, 0)
            lay_extra.addWidget(lb_q0, 3, 1, alignment=Qt.AlignCenter)
        else:
            lb_rsh = SiriusLabel(self, self.prefix+self.syst_dict['Rsh'])
            lb_rsh.showUnits = True
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
        labels = ['C0', 'C1', 'C2', 'C3', 'C4']
        for i in range(len(labels)):
            lay.addWidget(QLabel(
                labels[i], alignment=Qt.AlignCenter), 0, i+1)

        # Body
        row = 1
        for key, val in chs_dict.items():
            if key != 'OFS':
                column = 1
                lay.addWidget(QLabel(
                    f'<h4>{key}</h4>', alignment=Qt.AlignCenter), row, 0)
                for i in range(len(labels)):
                    lb = SiriusLabel(
                        self, self.prefix+val+f'-RB.[{i}]')
                    lb.precisionFromPV = False
                    lb.precision = 2
                    lb.displayFormat = DisplayFormat.Exponential
                    lay.addWidget(lb, row, column)
                    column += 1
                row += 1

        lb_ofs = SiriusLabel(self, self.prefix+chs_dict['OFS']+'-RB')
        lb_ofs.precisionFromPV = 0
        lb_ofs.precision = 2
        lay.addWidget(QLabel('<h4>OFS</h4>', alignment=Qt.AlignCenter), row, 0)
        lay.addWidget(lb_ofs, row, 1, 1, 5, alignment=Qt.AlignLeft)

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
            for j, key in enumerate(['Hw to Amp', 'Amp to Hw']):
                lb = SiriusLabel(
                    self, self.prefix+chs_dict[key]+f'-RB.[{i}]')
                lb.precisionFromPV = False
                lb.precision = 2
                lb.displayFormat = DisplayFormat.Exponential

                row = 1 if j == 0 else 3
                lay.addWidget(lb, row, column)
            column += 1

        return lay
