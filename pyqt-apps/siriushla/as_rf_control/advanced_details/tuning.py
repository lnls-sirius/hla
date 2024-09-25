"""Advanced details related to tuning and plungers."""

import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, QWidget

from ...widgets import PyDMStateButton, SiriusDialog, SiriusEnumComboBox, \
    SiriusLabel, SiriusLedAlert, SiriusLedState, SiriusPushButton, \
    SiriusSpinbox
from ..util import SEC_2_CHANNELS


class TuningDetails(SiriusDialog):
    """Advanced details related to tuning and plungers."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'Tuning Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['TunDtls'][self.system]
        else:
            self.syst_dict = self.chs['TunDtls']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0, 1, 3)

        gbox_gen = QGroupBox('General')
        gbox_gen.setLayout(self._generalLayout(self.syst_dict['General']))
        lay.addWidget(gbox_gen, 1, 0)

        gbox_drv = QGroupBox('Drivers')
        gbox_drv.setLayout(self._driversLayout(self.syst_dict['Drivers']))
        lay.addWidget(gbox_drv, 1, 1)

        auto_man = QTabWidget(self)
        auto_man.setObjectName(self.section+'Tab')
        auto_man.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        wid_man = QWidget(self)
        wid_man.setLayout(self._manualLayout(self.syst_dict['Manual']))
        auto_man.addTab(wid_man, 'Manual')

        wid_auto = QWidget(self)
        wid_auto.setLayout(self._autoLayout(self.syst_dict['Auto']))
        auto_man.addTab(wid_auto, 'Auto')

        lay.addWidget(auto_man, 1, 2)

    def _generalLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        row = 0

        # Tuning Direction
        self._setupAddrLabel(lay, chs_dict, '301', row)
        self._setupButtonLed(lay, chs_dict, '301', row)
        row += 1

        # Auto Tuning Enable
        self._setupAddrLabel(lay, chs_dict, '300', row)
        self._setupButtonLed(lay, chs_dict, '300', row)
        row += 1

        # Amplitudes and Phase Angles
        keys = ['34', '19', '33', '18']
        for key in keys:
            lb = SiriusLabel(self, self.prefix+chs_dict[key][1])
            self._setupAddrLabel(lay, chs_dict, key, row)
            lay.addWidget(lb, row, 3)
            row += 1

        # Tuning Fwd Min
        self._setupAddrLabel(lay, chs_dict, '307', row)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['307'][1]),
            row, 3, alignment=Qt.AlignCenter)
        row += 1

        # Pulses Freq
        lb_freq = SiriusLabel(self, self.prefix+chs_dict['303'][1]+'-RB')
        lb_freq.showUnits = True
        self._setupAddrLabel(lay, chs_dict, '303', row)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['303'][1]+'-SP'),
            row, 2, alignment=Qt.AlignCenter)
        lay.addWidget(lb_freq, row, 3, alignment=Qt.AlignCenter)
        row += 1

        # Moving
        gbox_mv = QGroupBox('Moving')
        lay_mv = QGridLayout()
        lay_mv.setAlignment(Qt.AlignTop)
        lay_mv.setSpacing(9)
        gbox_mv.setLayout(lay_mv)
        mv_dict = chs_dict['Moving']

        lay_mv.addWidget(QLabel(
            'Manual', alignment=Qt.AlignCenter), 0, 1)
        lay_mv.addWidget(QLabel(
            'Auto', alignment=Qt.AlignCenter), 0, 2)
        if self.section == 'SI':
            lay_mv.addWidget(QLabel(
                'Tuner Up', alignment=Qt.AlignCenter), 1, 0)
            lay_mv.addWidget(QLabel(
                'Tuner Down', alignment=Qt.AlignCenter), 2, 0)
        else:
            lay_mv.addWidget(QLabel(
                'Plg 1 Up', alignment=Qt.AlignCenter), 1, 0)
            lay_mv.addWidget(QLabel(
                'Plg 1 Down', alignment=Qt.AlignCenter), 2, 0)
            lay_mv.addWidget(QLabel(
                'Plg 2 Up', alignment=Qt.AlignCenter), 3, 0)
            lay_mv.addWidget(QLabel(
                'Plg 2 Down', alignment=Qt.AlignCenter), 4, 0)

        keys = ['Manual', 'Auto']
        column = 1
        for key in keys:
            row_ = 1
            for _, val in mv_dict[key].items():
                lay_mv.addWidget(SiriusLedState(
                    self, val), row_, column, alignment=Qt.AlignCenter)
                row_ += 1
            column += 1

        lay.addWidget(gbox_mv, row, 0, 1, 4)

        return lay

    def _driversLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        if self.section == 'SI':
            supplies = ['5V', '24V']
        else:
            supplies = ['5V', '48V']
        row = 0
        for sup in supplies:
            lb_supply = QLabel(f'{sup} Supply', alignment=Qt.AlignCenter)
            lb_supply.setStyleSheet('min-width:5em;')
            lb_volt = SiriusLabel(self, self.prefix+chs_dict[sup][0])
            lb_volt.showUnits = True
            lb_volt.setStyleSheet('min-width:7em;')
            lay.addWidget(lb_supply, row, 0)
            lay.addWidget(lb_volt, row, 1)

            if len(chs_dict[sup]) > 1:
                lb_curr = SiriusLabel(self, self.prefix+chs_dict[sup][1])
                lb_curr.showUnits = True
                lb_curr.setStyleSheet('min-width:7em;')
                lay.addWidget(lb_curr, row, 2)
            row += 1

        lay.addItem(QSpacerItem(0, 18, QSzPlcy.Ignored, QSzPlcy.Fixed), row, 0)
        lay.addWidget(QLabel('Drivers'), row+1, 0)
        lay.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict['Enable']+'-Sel'),
            row+1, 1, alignment=Qt.AlignCenter)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['Enable']+'-Sts'),
            row+1, 2, alignment=Qt.AlignCenter)
        row += 2

        drivers = ['1', '2']
        for d in drivers:
            gbox = QGroupBox(f'Driver {d}')
            gbox_lay = QGridLayout()
            gbox.setLayout(gbox_lay)

            lb_status = SiriusLabel(self, self.prefix+chs_dict[d][0])
            lb_status.showUnits = True

            gbox_lay.addWidget(QLabel(
                'Status'), 0, 0, alignment=Qt.AlignCenter)
            gbox_lay.addWidget(lb_status, 0, 1)
            if self.section == 'SI':
                lb_curr = SiriusLabel(self, self.prefix+chs_dict[d][1])
                lb_curr.showUnits = True
                gbox_lay.addWidget(QLabel(
                    'Current'), 1, 0, alignment=Qt.AlignCenter)
                gbox_lay.addWidget(lb_curr, 1, 1, alignment=Qt.AlignCenter)
            else:
                gbox_lay.addWidget(QLabel('Fault'), 1, 0)
                gbox_lay.addWidget(SiriusLedAlert(
                    self, self.prefix+chs_dict[d][1]),
                    1, 1, alignment=Qt.AlignCenter)

            lay.addWidget(gbox, row, 0, 1, 3)
            row += 1

        return lay

    def _manualLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Number of Pulses
        lb_num = SiriusLabel(self, self.prefix+chs_dict['302'][1]+'-RB')
        lb_num.showUnits = True
        self._setupAddrLabel(lay, chs_dict, '302', 0)
        lay.addWidget(SiriusSpinbox(
            self, self.prefix+chs_dict['302'][1]+'-SP'), 0, 2)
        lay.addWidget(lb_num, 0, 3, alignment=Qt.AlignCenter)

        # Move and Move Dir
        keys = ['306', '305']
        if self.section == 'BO':
            keys.extend(['315', '314'])

        row = 1
        for i, key in enumerate(keys):
            self._setupAddrLabel(lay, chs_dict, key, row)
            if i % 2 == 0:
                lay.addWidget(SiriusEnumComboBox(
                    self, self.prefix+chs_dict[key][1]+'-Sel'),
                    row, 2, alignment=Qt.AlignCenter)
                lay.addWidget(SiriusLedState(
                    self, self.prefix+chs_dict[key][1]+'-Sts'),
                    row, 3, alignment=Qt.AlignCenter)
            else:
                self._setupButtonLed(lay, chs_dict, key, row)
            row += 1

        # Tuning Reset
        self._setupAddrLabel(lay, chs_dict, '307', row)
        pb_reset = SiriusPushButton(
            label='', icon=qta.icon('fa5s.sync'), releaseValue=0,
            parent=self, init_channel=self.prefix+chs_dict['307'][1])
        pb_reset.setStyleSheet(
            'min-width:25px; max-width:25px; icon-size:20px;')
        lay.addWidget(pb_reset, row, 2, alignment=Qt.AlignCenter)
        row += 1

        return lay

    def _autoLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Tuning Margins, Forward Min and Delay
        keys = ['309', '310', '308', '311']
        row = 0
        for key in keys:
            label = SiriusLabel(self, self.prefix+chs_dict[key][1]+'-RB')
            label.showUnits = True
            self._setupAddrLabel(lay, chs_dict, key, row)
            lay.addWidget(SiriusSpinbox(
                self, self.prefix+chs_dict[key][1]+'-SP'), row, 2)
            lay.addWidget(label, row, 3)
            row += 1

        # Trigger Enable
        lb_trig = SiriusLabel(self, self.prefix+chs_dict['313'][1]+'-Sts')
        lb_trig.showUnits = True
        self._setupAddrLabel(lay, chs_dict, '313', row)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['313'][1]+'-Sel'),
            row, 2, alignment=Qt.AlignCenter)
        lay.addWidget(lb_trig, row, 3, alignment=Qt.AlignCenter)
        row += 1

        # Filter Enable
        self._setupAddrLabel(lay, chs_dict, '312', row)
        self._setupButtonLed(lay, chs_dict, '312', row)
        row += 1

        # On Top Ramp
        self._setupAddrLabel(lay, chs_dict, '316', row)
        self._setupButtonLed(lay, chs_dict, '316', row)

        return lay

    def _setupAddrLabel(self, lay, chs_dict, addr, row):
        lay.addWidget(QLabel(addr.split()[0]), row, 0)
        lay.addWidget(QLabel(chs_dict[addr][0]), row, 1)

    def _setupButtonLed(self, lay, chs_dict, addr, row):
        lay.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict[addr][1]+'-Sel'), row, 2)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict[addr][1]+'-Sts'),
            row, 3, alignment=Qt.AlignCenter)
