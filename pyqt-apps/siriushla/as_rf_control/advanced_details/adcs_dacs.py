"""Advanced details for ADCs and DACs."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QSizePolicy as QSzPlcy, \
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget

from ...widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedState, SiriusSpinbox, SiriusEnumComboBox
from ..util import SEC_2_CHANNELS


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
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        dtls = QTabWidget(self)
        dtls.setObjectName(self.section+'Tab')
        dtls.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        wid_input = QWidget(self)
        wid_input.setLayout(self._rfInputLayout(self.syst_dict['Input']))
        dtls.addTab(wid_input, 'RF Inputs')

        wid_controls = QWidget(self)
        wid_controls.setLayout(
            self._controlsLayout(self.syst_dict['Control']))
        dtls.addTab(wid_controls, 'Controls')

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _rfInputLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setVerticalSpacing(9)
        lay.setHorizontalSpacing(18)

        lay.addWidget(QLabel('In-Phase', alignment=Qt.AlignCenter), 0, 2)
        lay.addWidget(QLabel('Quadrature', alignment=Qt.AlignCenter), 0, 3)
        lay.addWidget(QLabel('Amp', alignment=Qt.AlignCenter), 0, 4)
        lay.addWidget(QLabel('Phase', alignment=Qt.AlignCenter), 0, 5)
        lay.addItem(QSpacerItem(24, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 6)
        lay.addWidget(QLabel('Power', alignment=Qt.AlignCenter), 0, 7, 1, 2)

        row = 1
        for key, dic in chs_dict.items():
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

        return lay

    def _controlsLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        for k, sub_dict in chs_dict.items():
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

        return lay
