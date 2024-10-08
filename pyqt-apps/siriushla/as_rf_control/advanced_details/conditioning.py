"""Conditioning advanced details."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel

from ...widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedState, SiriusSpinbox
from ..util import SEC_2_CHANNELS


class ConditioningDetails(SiriusDialog):
    """Conditioning advanced details."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'Conditioning Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['Conditioning'][self.system]
        else:
            self.syst_dict = self.chs['Conditioning']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0, 1, 4)

        # Pulse Enable
        self._setupLedState(lay, '200', 1, True)

        # Auto Cond Enable
        self._setupLedState(lay, '201', 2, True)

        # Duty Cycle
        self._setupLabelEdit(lay, '202', 3)

        # Duty Cycle RB
        lb_condfreq = SiriusLabel(self, self.prefix+self.syst_dict['530'][1])
        lb_condfreq.showUnits = True
        lay.addWidget(QLabel('530'), 4, 0)
        lay.addWidget(QLabel(self.syst_dict['530'][0]), 4, 1)
        lay.addWidget(lb_condfreq, 4, 3, alignment=Qt.AlignCenter)

        row = 5
        if self.section == 'BO':
            relay_keys = [
                'CGC Fast Relay', 'Relay Setpoint RB', 'Relay Hysteria RB']
            for key in relay_keys:
                lb_relay = SiriusLabel(
                    self, self.prefix+self.syst_dict['Relay'][key]+'-RB')
                lb_relay.showUnits = True

                lay.addWidget(QLabel(key), row, 1)
                if key.split()[-1] != 'RB':
                    lay.addWidget(SiriusSpinbox(
                        self, self.prefix+self.syst_dict['Relay'][key]+'-SP'),
                        row, 2)
                lay.addWidget(lb_relay, row, 3)
                row += 1

        # Vacuum
        self._setupLedState(lay, '79', row, False)

    def _setupLedState(self, lay, key, row, has_button):
        lay.addWidget(QLabel(key), row, 0)
        lay.addWidget(QLabel(self.syst_dict[key][0]), row, 1)

        ending = ''
        if has_button:
            lay.addWidget(PyDMStateButton(
                self, self.prefix+self.syst_dict[key][1]+'-Sel'),
                row, 2, alignment=Qt.AlignCenter)
            ending = '-Sts'

        lay.addWidget(SiriusLedState(
            self, self.prefix+self.syst_dict[key][1]+ending),
            row, 3, alignment=Qt.AlignCenter)

    def _setupLabelEdit(self, lay, key, row):
        label = SiriusLabel(self, self.prefix+self.syst_dict[key][1]+'-RB')
        label.showUnits = True

        lay.addWidget(QLabel(key), row, 0)
        lay.addWidget(QLabel(self.syst_dict[key][0]), row, 1)
        lay.addWidget(SiriusSpinbox(
            self, self.prefix+self.syst_dict[key][1]+'-SP'), row, 2)
        lay.addWidget(label, row, 3, alignment=Qt.AlignCenter)
