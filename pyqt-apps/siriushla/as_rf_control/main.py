from qtpy.QtWidgets import QWidget, QFormLayout, QLabel, QTabWidget, \
    QHBoxLayout, QSizePolicy as QSzPlcy
from qtpy.QtCore import Qt
from pydm.widgets import PyDMLabel
from siriushla.widgets import SiriusMainWindow, SiriusLedState, SiriusLedAlert


class RFStatus(SiriusMainWindow):
    """RF Status Window."""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self.setObjectName('BOApp')
        self.setWindowTitle('RF - P5Cav Status')
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h2>RF - P5Cav Status</h2>', self,
                       alignment=Qt.AlignCenter)

        # RF Enable
        lb_enbl = QLabel('RF Enable: ', self)
        self.led_RfEnbl = SiriusLedState(
            parent=self, init_channel='RA-RaBO01:RF-LLRFPreAmp:PinSw-Mon')
        self.led_RfEnbl.onColor = SiriusLedState.LightGreen
        self.led_RfEnbl.offColor = SiriusLedState.Red

        # RF Generator Frequency
        lb_freq = QLabel('Frequency [Hz]: ', self)
        self.lb_GenFreq = PyDMLabel(
            parent=self, init_channel='RF-Gen:GeneralFreq-RB')

        # Temperatures
        lb_temp = QLabel('Temperatures [°C]: ', self)
        self.lb_Cell1T = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:Cylin1T-Mon')
        self.lb_Cell1T.setStyleSheet('max-width: 4em;')
        self.lb_Cell2T = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:Cylin2T-Mon')
        self.lb_Cell2T.setStyleSheet('max-width: 4em;')
        self.lb_Cell3T = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:Cylin3T-Mon')
        self.lb_Cell3T.setStyleSheet('max-width: 4em;')
        self.lb_Cell4T = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:Cylin4T-Mon')
        self.lb_Cell4T.setStyleSheet('max-width: 4em;')
        self.lb_Cell5T = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:Cylin5T-Mon')
        self.lb_Cell5T.setStyleSheet('max-width: 4em;')
        flay_temp = QFormLayout()
        flay_temp.addRow('Cell 1: ', self.lb_Cell1T)
        flay_temp.addRow('Cell 2: ', self.lb_Cell2T)
        flay_temp.addRow('Cell 3: ', self.lb_Cell3T)
        flay_temp.addRow('Cell 4: ', self.lb_Cell4T)
        flay_temp.addRow('Cell 5: ', self.lb_Cell5T)

        # Ramp Enable status
        lb_rmpenbl = QLabel('Ramp Enable: ', self)
        self.led_RampEnbl = SiriusLedState(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpEnbl-Sts')

        # Specific statuses
        self.tab = QTabWidget(self)
        self.tab.addTab(self._setupNormalStatusesWidget(), 'Normal')
        self.tab.addTab(self._setupRampStatusesWidget(), 'Ramp')

        cw = QWidget()
        self.setCentralWidget(cw)
        lay = QFormLayout(cw)
        lay.setFormAlignment(Qt.AlignHCenter)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(label)
        lay.addRow(lb_enbl, self.led_RfEnbl)
        lay.addRow(lb_freq, self.lb_GenFreq)
        lay.addRow(lb_temp, flay_temp)
        lay.addRow(lb_rmpenbl, self.led_RampEnbl)
        lay.addRow(self.tab)

        self.setStyleSheet("""
            QLed{
                min-width: 1.29em; max-width: 1.29em;
            }
        """)
        self.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)

    def _setupNormalStatusesWidget(self):
        # Cavity Power
        lb_Pwr = QLabel('Cavity Power [mV]: ', self)
        self.lb_Pwr = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:CAV:AMP')
        # lb_Pwr = QLabel('Cavity Power [W]: ', self)
        # self.lb_Pwr = PyDMLabel(
        #     parent=self, init_channel='BO-05D:RF-P5Cav:Cell3Pwr-Mon')

        # Cavity Reflected Power
        lb_ReflPwr = QLabel('Cavity Reflected Power [mV]: ', self)
        self.lb_ReflPwr = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:REVCAV:AMP')
        # lb_ReflPwr = QLabel('Cavity Reflected Power [W]: ', self)
        # self.lb_ReflPwr = PyDMLabel(
        #     parent=self, init_channel='BO-05D:RF-P5Cav:PwrRev-Mon')

        # Cavity Gap Voltage
        lb_vgap = QLabel('Cavity Gap Voltage [mV]: ', self)
        self.lb_VGap = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:CAV:AMP')
        # lb_vgap = QLabel('Cavity Gap Voltage [kV]: ', self)
        # self.lb_VGap = PyDMLabel(
        #     parent=self, init_channel='BO-05D:RF-P5Cav:VCav')
        lb_auxvgap = QLabel('/')
        lb_auxvgap.setStyleSheet('max-width:1em;')
        self.lb_VGapRef = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:SL:REF:AMP')
        self.lb_VGapRef.setStyleSheet('max-width: 4em;')
        hlay_vgap = QHBoxLayout()
        hlay_vgap.addWidget(self.lb_VGap)
        hlay_vgap.addWidget(lb_auxvgap)
        hlay_vgap.addWidget(self.lb_VGapRef)

        # Cavity Phase
        lb_phs = QLabel('Cavity Phase [°]: ', self)
        self.lb_Phs = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:SL:INP:PHS')
        self.lb_Phs.setStyleSheet('max-width: 4em;')
        lb_auxphs = QLabel('/')
        lb_auxphs.setStyleSheet('max-width:1em;')
        self.lb_PhsRef = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:SL:REF:PHS')
        self.lb_PhsRef.setStyleSheet('max-width: 4em;')
        hlay_phs = QHBoxLayout()
        hlay_phs.addWidget(self.lb_Phs)
        hlay_phs.addWidget(lb_auxphs)
        hlay_phs.addWidget(self.lb_PhsRef)

        # Detune
        lb_detune = QLabel('Detune [°]: ')
        self.lb_Detune = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:DTune-RB')

        wid = QWidget()
        lay = QFormLayout(wid)
        lay.setFormAlignment(Qt.AlignHCenter)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(lb_Pwr, self.lb_Pwr)
        lay.addRow(lb_ReflPwr, self.lb_ReflPwr)
        lay.addRow(lb_vgap, hlay_vgap)
        lay.addRow(lb_phs, hlay_phs)
        lay.addRow(lb_detune, self.lb_Detune)
        return wid

    def _setupRampStatusesWidget(self):
        # Cavity Power
        lb_rmppwr = QLabel('Cavity Power [mV]: ', self)
        self.lb_RmpPwr = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RAMP:TOP')
        # lb_rmppwr = QLabel('Cavity Power [W]: ', self)
        # self.lb_RmpPwr = PyDMLabel(
        #     parent=self, init_channel='BR-RF-DLLRF-01:RAMP:TOP:W')

        # Cavity Reflected Power
        lb_rmpreflpwr = QLabel('Cavity Reflected Power [mV]: ', self)
        self.lb_RmpRefPwr = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:TOP:REVCAV:AMP')
        # lb_rmpreflpwr = QLabel('Cavity Reflected Power [W]: ', self)
        # self.lb_RmpRefPwr = PyDMLabel(
        #     parent=self, init_channel='BO-05D:RF-P5Cav:PwrRevTop-Mon')

        # Cavity Gap Voltage
        lb_rmpvcav = QLabel('Cavity Gap Voltage [mV]: ', self)
        self.lb_RmpVCav = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RAMP:TOP')
        # lb_rmpvcav = QLabel('Cavity Gap Voltage [kV]: ', self)
        # self.lb_RmpVCav = PyDMLabel(
        #     parent=self, init_channel='BR-RF-DLLRF-01:RmpVoltTop-Mon')

        # Ramp Ready
        lb_rmprdy = QLabel('Ramp Ready: ', self)
        self.led_RmpReady = SiriusLedAlert(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpReady-Mon')

        wid = QWidget()
        lay = QFormLayout(wid)
        lay.setFormAlignment(Qt.AlignHCenter)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(lb_rmppwr, self.lb_RmpPwr)
        lay.addRow(lb_rmpreflpwr, self.lb_RmpRefPwr)
        lay.addRow(lb_rmpvcav, self.lb_RmpVCav)
        lay.addRow(lb_rmprdy, self.led_RmpReady)
        return wid
