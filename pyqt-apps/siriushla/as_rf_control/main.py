from functools import partial as _part
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QWidget, QLabel, \
    QSizePolicy as QSzPlcy, QRadioButton, QSpacerItem, \
    QGridLayout, QVBoxLayout, QHBoxLayout, QFormLayout
from qtpy.QtCore import Qt
from pydm.widgets import PyDMLabel, PyDMWaveformPlot
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
        cw = QWidget()
        self.setCentralWidget(cw)

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
        self.wid_Stat = self._setupStaticStatusesWidget()
        self.wid_Ramp = self._setupRampStatusesWidget()
        self.wid_Ramp.setVisible(False)
        self.stack = QGridLayout()
        self.stack.addWidget(self.wid_Stat, 0, 0)
        self.stack.addWidget(self.wid_Ramp, 0, 0)

        lb_show = QLabel('Show ', self,
                         alignment=Qt.AlignRight | Qt.AlignVCenter)
        lb_show.setStyleSheet('font-weight:normal;')
        self.rb_Stat = QRadioButton('Static', self)
        self.rb_Stat.toggled.connect(_part(self._toogleWidgets, 0))
        self.rb_Stat.setStyleSheet('max-width: 4em;')
        self.rb_Stat.setChecked(True)
        self.rb_Ramp = QRadioButton('Ramp', self)
        self.rb_Ramp.toggled.connect(_part(self._toogleWidgets, 1))
        self.rb_Ramp.setStyleSheet('max-width: 4em;')
        lb_params = QLabel('params', self,
                           alignment=Qt.AlignLeft | Qt.AlignVCenter)
        lb_params.setStyleSheet('font-weight:normal;')
        vlay_params = QVBoxLayout()
        vlay_params.setSpacing(6)
        vlay_params.addWidget(self.rb_Stat)
        vlay_params.addWidget(self.rb_Ramp)
        hlay_params = QHBoxLayout()
        hlay_params.setAlignment(Qt.AlignVCenter)
        hlay_params.setSpacing(15)
        hlay_params.addWidget(lb_show)
        hlay_params.addLayout(vlay_params)
        hlay_params.addWidget(lb_params)

        lay = QFormLayout(cw)
        lay.setFormAlignment(Qt.AlignHCenter)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(label)
        lay.addRow(lb_enbl, self.led_RfEnbl)
        lay.addRow(lb_freq, self.lb_GenFreq)
        lay.addRow(lb_temp, flay_temp)
        lay.addRow(lb_rmpenbl, self.led_RampEnbl)
        lay.addItem(QSpacerItem(10, 1, QSzPlcy.Fixed, QSzPlcy.Ignored))
        lay.addRow(hlay_params)
        lay.addItem(QSpacerItem(10, 1, QSzPlcy.Fixed, QSzPlcy.Ignored))
        lay.addRow(self.stack)

        self.setStyleSheet("""
            QLed{
                min-width: 1.29em; max-width: 1.29em;
            }
            .QLabel{
                font-weight: bold;
            }
        """)
        self.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)

    def _setupStaticStatusesWidget(self):
        # Power
        lb_CavPwr = QLabel('Cavity Power [W]: ', self)
        self.lb_CavPwr = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:Cell3Pwr-Mon')

        # Forward Power
        lb_FwdPwr = QLabel('Forward Power [W]: ', self)
        self.lb_FwdPwr = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:PwrFwd-Mon')

        # Reverse Power
        lb_RevPwr = QLabel('Reverse Power [W]: ', self)
        self.lb_RevPwr = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:PwrRev-Mon')

        # Gap Voltage
        lb_vgap = QLabel('Cavity Gap Voltage [kV]: ', self)
        self.lb_VGap = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:VCav')

        # Phase
        lb_phs = QLabel('Cavity Phase [°]: ', self)
        self.lb_Phs = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:SL:INP:PHS')

        # Detune
        lb_detune = QLabel('Detune [°]: ')
        self.lb_Detune = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:DTune-RB')

        # Slow Loop Errors
        lb_SLErr = QLabel('Control Loop Errors (Slow Loop) ', self,
                          alignment=Qt.AlignCenter)
        lb_SLErrVgap = QLabel('Gap Voltage [mV]: ', self)
        self.lb_SLErrVgap = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:SL:ERR:AMP')
        lb_SLErrPhs = QLabel('Phase [°]: ', self)
        self.lb_SLErrPhs = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:SL:ERR:PHS')

        wid = QWidget()
        lay = QFormLayout(wid)
        lay.setFormAlignment(Qt.AlignHCenter)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(lb_CavPwr, self.lb_CavPwr)
        lay.addRow(lb_FwdPwr, self.lb_FwdPwr)
        lay.addRow(lb_RevPwr, self.lb_RevPwr)
        lay.addRow(lb_vgap, self.lb_VGap)
        lay.addRow(lb_phs, self.lb_Phs)
        lay.addRow(lb_detune, self.lb_Detune)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lb_SLErr)
        lay.addRow(lb_SLErrVgap, self.lb_SLErrVgap)
        lay.addRow(lb_SLErrPhs, self.lb_SLErrPhs)
        return wid

    def _setupRampStatusesWidget(self):
        # Ramp Ready
        lb_rmprdy = QLabel('Ramp Ready: ', self)
        self.led_RmpReady = SiriusLedAlert(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpReady-Mon')

        # Power Sensor
        self.graph_rmp = PyDMWaveformPlot(
            parent=self, background=QColor(255, 255, 255))
        self.graph_rmp.setObjectName('graph')
        self.graph_rmp.setStyleSheet('#graph{min-height:15em;min-width:20em;}')
        self.graph_rmp.maxRedrawRate = 2
        self.graph_rmp.mouseEnabledX = True
        self.graph_rmp.setShowXGrid(True)
        self.graph_rmp.setShowYGrid(True)
        self.graph_rmp.setShowLegend(False)
        self.graph_rmp.setAutoRangeX(True)
        self.graph_rmp.setAutoRangeY(True)
        self.graph_rmp.setAxisColor(QColor(0, 0, 0))
        self.graph_rmp.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        self.graph_rmp.plotItem.getAxis('left').setStyle(tickTextOffset=5)
        self.graph_rmp.addChannel(
            x_channel='RA-RF:PowerSensor1:TimeAxis-Mon',
            y_channel='RA-RF:PowerSensor1:TracData-Mon',
            redraw_mode=2, name='Power',
            color=QColor('blue'))
        self.graph_rmp.curveAtIndex(0).redrawCurve()

        # # Ramp Top
        lb_RmpTop = QLabel('Ramp Top', self)
        # Cavity Power
        lb_RmpPwrTop = QLabel('Cavity Power [W]: ', self)
        self.lb_RmpPwrTop = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:Cell3PwrTop-Mon')
        # Gap Voltage
        lb_RmpVCavTop = QLabel('Cavity Gap Voltage [kV]: ', self)
        self.lb_RmpVCavTopRB = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpVoltTop-RB')
        lbaux_RmpVCavTop = QLabel('/', self)
        self.lb_RmpVCavTopMon = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpVoltTop-Mon')
        hbox_RmpVCavTop = QHBoxLayout()
        hbox_RmpVCavTop.addWidget(self.lb_RmpVCavTopRB)
        hbox_RmpVCavTop.addWidget(lbaux_RmpVCavTop)
        hbox_RmpVCavTop.addWidget(self.lb_RmpVCavTopMon)
        # Phase
        lb_RmpPhsTop = QLabel('Phase [°]: ', self)
        self.lb_RmpPhsTop = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpPhsTop-RB')

        # # Ramp Bottom
        lb_RmpBot = QLabel('Ramp Bottom', self)
        # Cavity Power
        lb_RmpPwrBot = QLabel('Cavity Power [W]: ', self)
        self.lb_RmpPwrBot = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:Cell3PwrBot-Mon')
        # Gap Voltage
        lb_RmpVCavBot = QLabel('Cavity Gap Voltage [kV]: ', self)
        self.lb_RmpVCav = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpVoltBot-RB')
        # Phase
        lb_RmpPhsBot = QLabel('Phase [°]: ', self)
        self.lb_RmpPhsBot = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpPhsBot-RB')

        wid = QWidget()
        lay = QFormLayout(wid)
        lay.setFormAlignment(Qt.AlignHCenter)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(self.graph_rmp)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lb_rmprdy, self.led_RmpReady)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lb_RmpTop)
        lay.addRow(lb_RmpPwrTop, self.lb_RmpPwrTop)
        lay.addRow(lb_RmpVCavTop, hbox_RmpVCavTop)
        lay.addRow(lb_RmpPhsTop, self.lb_RmpPhsTop)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lb_RmpBot)
        lay.addRow(lb_RmpPwrBot, self.lb_RmpPwrBot)
        lay.addRow(lb_RmpVCavBot, self.lb_RmpVCav)
        lay.addRow(lb_RmpPhsBot, self.lb_RmpPhsBot)
        return wid

    def _toogleWidgets(self, index):
        self.wid_Stat.setVisible(index == 0)
        self.wid_Ramp.setVisible(index == 1)
        self.centralWidget().adjustSize()
        self.adjustSize()
