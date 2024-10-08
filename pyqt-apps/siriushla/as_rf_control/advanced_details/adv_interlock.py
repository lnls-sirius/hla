"""Advanced details related to interlocks."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, QVBoxLayout, QWidget

from ...widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedAlert, SiriusLedState, SiriusPushButton, SiriusSpinbox
from ..util import SEC_2_CHANNELS


class AdvancedInterlockDetails(SiriusDialog):
    """Advanced details related to interlocks."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'Advanced Interlock Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['AdvIntlk'][self.system]
        else:
            self.syst_dict = self.chs['AdvIntlk']
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

        wid_diag = QWidget(self)
        wid_diag.setLayout(
            self._diagnosticsLayout(self.syst_dict['Diagnostics']))
        dtls.addTab(wid_diag, 'Diagnostics')

        wid_bypass = QWidget(self)
        wid_bypass.setLayout(self._bypassLayout(self.syst_dict['Bypass']))
        dtls.addTab(wid_bypass, 'Interlock Bypass')

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _diagnosticsLayout(self, chs_dict):
        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # General
        gbox_gen = QGroupBox()
        gbox_gen.setLayout(self._genDiagLayout(chs_dict['General']))

        # Levels
        gbox_lvls = QGroupBox('Levels')
        lay_lvls = QGridLayout()
        lay_lvls.setAlignment(Qt.AlignTop)
        lay_lvls.setSpacing(9)
        gbox_lvls.setLayout(lay_lvls)

        row = 0
        for key, val in chs_dict['Levels'].items():
            lb = SiriusLabel(self, self.prefix+val+'-RB')
            lb.showUnits = True
            lay_lvls.addWidget(QLabel(f'Limit {key}'), row, 0)
            lay_lvls.addItem(QSpacerItem(
                9, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), row, 1)
            lay_lvls.addWidget(SiriusSpinbox(
                self, self.prefix+val+'-SP'), row, 2)
            lay_lvls.addWidget(lb, row, 3)
            row += 1

        # GPIO Inputs
        gbox_inp = QGroupBox('GPIO Inputs')
        lay_inp = QGridLayout()
        lay_inp.setAlignment(Qt.AlignTop)
        lay_inp.setSpacing(9)
        gbox_inp.setLayout(lay_inp)

        labels = ['LLRF1', 'LLRF2', 'PLC', 'RF On State', 'Vacuum In',
            'End Sw Up 1', 'End Sw Dw 1', 'VCXO Power', 'VCXO Ref',
            'VCXO Locked', 'Spare', 'End Sw Up 2', 'End Sw Dw 2']
        self._setupByteMonitor(lay_inp, labels, chs_dict['GPIO']['Inp'])
        lay_inp.addWidget(SiriusLabel(
            self, self.prefix+chs_dict['GPIO']['Inp']),
            0, 0, 1, 2, alignment=Qt.AlignCenter)

        # GPIO Interlock
        gbox_intlk = QGroupBox('GPIO Interlock')
        lay_intlk = QGridLayout()
        lay_intlk.setAlignment(Qt.AlignTop)
        lay_intlk.setSpacing(9)
        gbox_intlk.setLayout(lay_intlk)

        labels = ['LLRF 2 Standby', 'Pin Diode', 'FDL Trigger', 'PLC',
            'Ext LLRF']
        self._setupByteMonitor(
            lay_intlk, labels, self.prefix+chs_dict['GPIO']['Intlk'])
        lay_intlk.addWidget(SiriusLabel(
            self, self.prefix+chs_dict['GPIO']['Intlk']),
            0, 0, 1, 2, alignment=Qt.AlignCenter)

        # GPIO Outputs
        gbox_out = QGroupBox('GPIO Outputs')
        lay_out = QGridLayout()
        lay_out.setAlignment(Qt.AlignTop)
        lay_out.setSpacing(9)
        gbox_out.setLayout(lay_out)

        labels = ['Pulse', 'TTL1 Dir PLA', 'TTL2 Pulse PLA', 'TTL3 Dir PLB',
            'TTL4 Pulse PLB', 'Ilk PLC', 'Ilk PinSw', 'VCXO En', 'VCXO Clk',
            'VCXO Data', 'Ilk LLRF']
        self._setupByteMonitor(
            lay_out, labels, self.prefix+chs_dict['GPIO']['Out'])
        lay_out.addWidget(SiriusLabel(
            self, self.prefix+chs_dict['GPIO']['Out']),
            0, 0, 1, 2, alignment=Qt.AlignCenter)

        lay.addWidget(gbox_gen)
        lay.addWidget(gbox_lvls)
        lay.addWidget(gbox_inp)
        lay.addWidget(gbox_intlk)
        lay.addWidget(gbox_out)

        return lay

    def _genDiagLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Interlocks Delay
        lb_dly = SiriusLabel(self, self.prefix+chs_dict['Delay']+'-RB')
        lb_dly.showUnits = True

        lay.addWidget(QLabel('Interlocks Delay'), 0, 0)
        lay.addWidget(SiriusSpinbox(
            self, self.prefix+chs_dict['Delay']+'-SP'), 0, 1)
        lay.addWidget(lb_dly, 0, 2)

        # HW Interlock
        lay.addWidget(QLabel('HW Interlock'), 1, 0)
        lay.addWidget(SiriusLedAlert(
            self, self.prefix+chs_dict['HW']), 1, 2, alignment=Qt.AlignCenter)

        # Manual Interlock, End Switches and Logic Inversions
        keys = ['Manual', 'EndSw', 'Beam Inv', 'Vacuum Inv']
        row = 3
        for key in keys:
            lay.addWidget(QLabel(chs_dict[key][0]), row, 0)
            lay.addWidget(PyDMStateButton(
                self, self.prefix+chs_dict[key][1]+'-Sel'), row, 1)
            lay.addWidget(SiriusLedState(
                self, self.prefix+chs_dict[key][1]+'-Sts'),
                row, 2, alignment=Qt.AlignCenter)
            row += 1

        return lay

    def _setupByteMonitor(self, lay, labels, channel):
        for bit in range(len(labels)):
            lay.addWidget(QLabel(labels[bit]), bit+1, 0)
            lay.addWidget(SiriusLedState(
                self, channel, bit), bit+1, 1, alignment=Qt.AlignCenter)

    def _bypassLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        labels = ['Diagnostics', 'Ext LLRF', 'Tx PLC', 'FDL Trigger',
            'Pin Diode', 'Loops Standby']

        column = 2
        for lb in labels:
            lay.addWidget(QLabel(
                lb, alignment=Qt.AlignCenter), 0, column)
            column += 2

        for i in range(1, column):
            if i % 2 == 0 or i == 1:
                lay.setColumnStretch(i, 1)
        lay.setColumnMinimumWidth(1, 120)

        row = 1
        for key, val in chs_dict.items():
            lay.addWidget(QLabel(key.split()[0]), row, 0)
            lay.addWidget(QLabel(val[0]), row, 1)
            column = 2
            for bit in reversed(range(len(labels))):
                lay_state = QHBoxLayout()
                pb = PyDMStateButton(self, self.prefix+val[1]+'-Sel', bit=bit)
                lay_state.addWidget(pb, alignment=Qt.AlignRight)
                lay_state.addWidget(SiriusLedState(
                    self, self.prefix+val[1]+'-Sts', bit),
                    alignment=Qt.AlignLeft)
                lay.addLayout(lay_state, row, column)
                lay.addItem(QSpacerItem(
                    9, 0, QSzPlcy.Ignored, QSzPlcy.Fixed), row, column+1)
                column += 2
            lay.addWidget(SiriusPushButton(
                self, self.prefix+val[1]+'-Sel', 'All Zero', releaseValue=0),
                row, column)
            lay.addWidget(SiriusPushButton(
                self, self.prefix+val[1]+'-Sel', 'All One', releaseValue=63),
                row, column+1)
            row += 1

        return lay
