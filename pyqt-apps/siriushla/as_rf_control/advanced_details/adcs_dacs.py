"""Advanced details for ADCs and DACs."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QSizePolicy as QSzPlcy, \
    QSpacerItem

from ...widgets import PyDMStateButton, SiriusDialog, SiriusEnumComboBox, \
    SiriusLabel, SiriusLedState, SiriusSpinbox
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


class ADCDACDetails(SiriusDialog):
    """Advanced details for ADCs and DACs."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'ADCs and DACs Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['ADCs and DACs'][self.system]
        else:
            self.syst_dict = self.chs['ADCs and DACs']
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0, 1, 9)

        for k, sub_dict in self.syst_dict.items():
            row = 1
            if k == 'ADC':
                offset = 0
            else:
                offset = 5

            for key, val in sub_dict.items():
                if key == 'Enable':
                    pb_enbl = PyDMStateButton(
                        self, self.prefix+val[1]+'-Sel')
                    led_enbl = SiriusLedState(
                        self, self.prefix+val[1]+'-Sts')
                    lay.addWidget(QLabel(val[0]), row, offset, 1, 2)
                    lay.addWidget(pb_enbl, row, offset+2)
                    lay.addWidget(led_enbl, row, offset+3,
                        alignment=Qt.AlignCenter)
                elif key == 'Cryogenic Load Leveler':
                    lay.addWidget(QLabel(key), row, offset, 1, 2)
                    row += 1
                    for k, v in val.items():
                        lb_gain = SiriusLabel(self, self.prefix+v[1]+'-Sts')
                        lb_gain.showUnits = True
                        lay.addWidget(QLabel(k), row, offset)
                        lay.addWidget(QLabel(v[0]), row, offset+1)
                        lay.addWidget(SiriusEnumComboBox(
                            self, self.prefix+v[1]+'-Sel'),
                            row, offset+2, alignment=Qt.AlignCenter)
                        lay.addWidget(lb_gain, row, offset+3)
                        row += 1
                else:
                    lb_value = SiriusLabel(self, self.prefix+val[1]+'-RB')
                    lb_value.showUnits = True
                    lay.addWidget(QLabel(key), row, offset)
                    lay.addWidget(QLabel(val[0]), row, offset+1)
                    lay.addWidget(
                        SiriusSpinbox(self, self.prefix+val[1]+'-SP'),
                        row, offset+2)
                    lay.addWidget(lb_value, row, offset+3)
                row += 1

        lay.addItem(QSpacerItem(20, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 1, 4)
