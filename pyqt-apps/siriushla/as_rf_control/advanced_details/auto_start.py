"""Advanced details related to automatic start."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QLabel, QVBoxLayout

from ...widgets import PyDMStateButton, SiriusDialog, SiriusEnumComboBox, \
    SiriusLabel, SiriusLedAlert, SiriusLedState
from ..util import SEC_2_CHANNELS


class AutoStartDetails(SiriusDialog):
    """Advanced details related to automatic start."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'Auto Start Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['AutoStart'][self.system]
        else:
            self.syst_dict = self.chs['AutoStart']
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # General
        gbox_gen = QGroupBox('General')
        gen_lay = QGridLayout()
        gbox_gen.setLayout(gen_lay)

        # # Enable
        self._setupButtonLed(gen_lay, '22', 0)

        # # Start
        gen_lay.addWidget(QLabel('23'), 1, 0)
        gen_lay.addWidget(QLabel(self.syst_dict['23'][0]), 1, 1)
        gen_lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+self.syst_dict['23'][1]+'-Sel'),
            1, 2, alignment=Qt.AlignRight)
        gen_lay.addWidget(SiriusLabel(
            self, self.prefix+self.syst_dict['23'][1]+'-Sts',
            alignment=Qt.AlignCenter), 1, 3)

        # # EPS
        self._setupButtonLed(gen_lay, '400', 2)

        # # Bypass
        self._setupButtonLed(gen_lay, '401', 3)

        # Diagnostics
        gbox_diag = QGroupBox('Diagnostics')
        diag_lay = QGridLayout()
        gbox_diag.setLayout(diag_lay)

        # # State Start
        lb_state = SiriusLabel(self, self.syst_dict['Diag']['500'][1])
        lb_state.showUnits = True
        diag_lay.addWidget(QLabel('500'), 0, 0)
        diag_lay.addWidget(QLabel(self.syst_dict['Diag']['500'][0]), 0, 1)
        diag_lay.addWidget(lb_state, 0, 2)

        # # LEDs
        row = 1
        for key in self.syst_dict['Diag'].keys():
            if key != '500':
                self._setupLabelLed(
                    diag_lay, key, self.syst_dict['Diag'], row, key == '401')
                row += 1

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(gbox_gen)
        lay.addWidget(gbox_diag)

    def _setupButtonLed(self, lay, key, row):
        lay.addWidget(QLabel(key), row, 0)
        lay.addWidget(QLabel(self.syst_dict[key][0]), row, 1)
        lay.addWidget(PyDMStateButton(
            self, self.prefix+self.syst_dict[key][1]+'-Sel'),
            row, 2, alignment=Qt.AlignCenter)
        lay.addWidget(SiriusLedState(
            self, self.prefix+self.syst_dict[key][1]+'-Sts'),
            row, 3, alignment=Qt.AlignCenter)

    def _setupLabelLed(self, lay, key, chs_dict, row, is_alert):
        if is_alert:
            led = SiriusLedAlert(self, self.prefix+chs_dict[key][1])
        else:
            led = SiriusLedState(self, self.prefix+chs_dict[key][1])

        lay.addWidget(QLabel(key), row, 0)
        lay.addWidget(QLabel(chs_dict[key][0]), row, 1)
        lay.addWidget(led, row, 2, alignment=Qt.AlignCenter)
