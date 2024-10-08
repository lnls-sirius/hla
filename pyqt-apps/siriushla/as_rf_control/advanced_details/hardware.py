"""Advanced details related to the hardware."""

from pydm.widgets import PyDMEnumComboBox
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QLabel, QVBoxLayout

from ...widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedAlert, SiriusLedState, SiriusPushButton, SiriusScaleIndicator
from ..util import SEC_2_CHANNELS


class HardwareDetails(SiriusDialog):
    """Advanced details related to the hardware."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'Hardware Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['Hardware'][self.system]
        else:
            self.syst_dict = self.chs['Hardware']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setHorizontalSpacing(18)
        lay.setVerticalSpacing(9)

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter), 0, 0, 1, 5)

        # FPGA Temps
        gbox_fpga = QGroupBox('FPGA Temps', self)
        self._setupLabelsLayout(gbox_fpga, True, self.syst_dict['FPGA'])

        # Mo1000 Temps
        gbox_mo1000 = QGroupBox('Mo1000 Temps', self)
        self._setupLabelsLayout(gbox_mo1000, False, self.syst_dict['Mo1000'])

        # Mi125 Temps
        gbox_mi125 = QGroupBox('Mi125 Temps', self)
        self._setupLabelsLayout(gbox_mi125, False, self.syst_dict['Mi125'])

        # GPIO
        gbox_gpio = QGroupBox('GPIO', self)
        self._setupLabelsLayout(gbox_gpio, False, self.syst_dict['GPIO'])

        # Clock Src, Loop Trigger and PLL
        gbox_pll = QGroupBox(self)
        lay_pll = QGridLayout(gbox_pll)
        lay_pll.setSpacing(9)
        lay_pll.setAlignment(Qt.AlignTop)

        cb_clock = PyDMEnumComboBox(
            self, self.prefix+self.syst_dict['Clock Src'])
        pb_trig = SiriusPushButton(
            self, self.prefix+self.syst_dict['Loop Trigger'], 'Loop Trigger')
        pb_trig.setStyleSheet('min-width: 6em')
        led_pll = SiriusLedState(self, self.prefix+self.syst_dict['PLL'])
        pb_init = SiriusPushButton(
            self, self.prefix+self.syst_dict['FPGA Init'], 'Init')
        lay_pll.addWidget(QLabel(
            'Clock Src', alignment=Qt.AlignRight | Qt.AlignVCenter), 0, 0)
        lay_pll.addWidget(cb_clock, 0, 1, alignment=Qt.AlignCenter)
        lay_pll.addWidget(QLabel(
            'Loop Trigger', alignment=Qt.AlignRight | Qt.AlignVCenter), 1, 0)
        lay_pll.addWidget(pb_trig, 1, 1)
        lay_pll.addWidget(QLabel(
            'PLL', alignment=Qt.AlignRight | Qt.AlignVCenter), 2, 0)
        lay_pll.addWidget(led_pll, 2, 1, alignment=Qt.AlignCenter)
        lay_pll.addWidget(QLabel(
            'Init', alignment=Qt.AlignRight | Qt.AlignVCenter), 3, 0)
        lay_pll.addWidget(pb_init, 3, 1, alignment=Qt.AlignCenter)

        # Cavity Type
        gbox_type = QGroupBox(self)
        lay_type = QGridLayout(gbox_type)
        lay_type.setSpacing(9)
        lay_type.setSpacing(Qt.AlignTop)
        lay_type.addWidget(QLabel('Cavity Type'), 0, 0)
        lay_type.addWidget(SiriusLabel(
            self, self.prefix+self.syst_dict['Cav Type']), 0, 1)

        # Errors
        gbox_err = QGroupBox('Errors', self)
        lay_err = QGridLayout(gbox_err)
        lay_err.setSpacing(9)
        lay_err.setAlignment(Qt.AlignTop)
        labels = ['EAPI', 'Mo1000', 'Mi125', 'SysMon',
            'GPIO', 'VCXO', 'Loops', 'RecPlay']
        self._setupByteMonitor(
            lay_err, True, labels, self.prefix+self.syst_dict['Errors'])

        # Internal Errors
        gbox_interr = QGroupBox('Internal Errors', self)
        lay_interr = QGridLayout(gbox_interr)
        lay_interr.setSpacing(9)
        lay_interr.setAlignment(Qt.AlignTop)
        labels = ['Loop Set', 'Loop Get', 'Loop Set Inconsistency',
            'Phs Ref Inconsistency', 'Amd Ref Inconsistency', 'Diag Get']
        self._setupByteMonitor(lay_interr, True, labels,
            self.prefix+self.syst_dict['Int. Errors'])
        pb_clear = SiriusPushButton(
            self, self.prefix+self.syst_dict['Int. Err. Clear'])
        pb_clear.setText('Clear')
        lay_interr.addWidget(pb_clear, len(labels)+1, 0)

        # Init
        gbox_init = QGroupBox('Init', self)
        lay_init = QGridLayout(gbox_init)
        lay_init.setSpacing(9)
        lay_init.setAlignment(Qt.AlignTop)
        labels = ['GPIO', 'DACS', 'Mo1000', 'Mi125', 'Intercore FIFO', 'FPGA',
            'Cav Type', 'Double Write', 'Initial Settings', 'Disable Cavity B']
        self._setupByteMonitor(
            lay_init, False, labels, self.prefix+self.syst_dict['Init'])

        # Versions
        gbox_vers = QGroupBox('Versions', self)
        self._setupLabelsLayout(gbox_vers, False, self.syst_dict['Versions'])

        lay_vbox = QVBoxLayout()
        lay_vbox.setSpacing(9)
        lay_vbox.addWidget(gbox_mo1000)
        lay_vbox.addWidget(gbox_mi125)
        lay_vbox.addWidget(gbox_gpio)
        lay_vbox.addWidget(gbox_pll)
        lay_vbox.addWidget(gbox_type)

        lay.addWidget(gbox_fpga, 1, 0)
        lay.addWidget(gbox_vers, 2, 0, 1, 5)
        lay.addLayout(lay_vbox, 1, 1)
        lay.addWidget(gbox_err, 1, 2)
        lay.addWidget(gbox_interr, 1, 3)
        lay.addWidget(gbox_init, 1, 4)

    def _setupLabelsLayout(self, gbox, isFPGA, chs_dict):
        lay = QGridLayout(gbox)
        lay.setSpacing(9)
        lay.setAlignment(Qt.AlignTop)
        row = 0
        for key, val in chs_dict.items():
            lb_value = SiriusLabel(self, self.prefix+val)
            lb_value.showUnits = True
            lay.addWidget(QLabel(key, alignment=Qt.AlignRight), row, 0)
            lay.addWidget(lb_value, row, 1)
            row += 1
            if isFPGA and key.split()[-1] == 'Min':
                scale = SiriusScaleIndicator(self, self.prefix+val)
                lay.addWidget(scale, row, 1)
                row += 1

    def _setupByteMonitor(self, lay, isAlert, labels, pv):
        for bit in range(len(labels)):
            if isAlert:
                led = SiriusLedAlert(self, pv, bit)
            else:
                led = SiriusLedState(self, pv, bit)
            lay.addWidget(led, bit, 0, alignment=Qt.AlignHCenter)
            lay.addWidget(QLabel(labels[bit]), bit, 1)
