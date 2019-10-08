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
        lb_Pwr = QLabel('Power [W]: ', self)
        self.lb_Pwr = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:Cell3Pwr-Mon')

        # Reflected Power
        lb_ReflPwr = QLabel('Reflected Power [W]: ', self)
        self.lb_ReflPwr = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:PwrRev-Mon')

        # Gap Voltage
        lb_vgap = QLabel('Gap Voltage [kV]: ', self)
        self.lb_VGap = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:VCav')

        # Gap Voltage Ref
        lb_vgapCheck = QLabel('Gap Voltage (LL) [mV]: ', self)
        self.lb_VGapCheck = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:SL:INP:AMP')
        lb_auxvgapCheck = QLabel('/')
        lb_auxvgapCheck.setStyleSheet('max-width:1em;')
        self.lb_VGapRefCheck = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:SL:REF:AMP')
        self.lb_VGapRefCheck.setStyleSheet('max-width: 4em;')
        hlay_vgapCheck = QHBoxLayout()
        hlay_vgapCheck.addWidget(self.lb_VGapCheck)
        hlay_vgapCheck.addWidget(lb_auxvgapCheck)
        hlay_vgapCheck.addWidget(self.lb_VGapRefCheck)

        # Phase
        lb_phs = QLabel('Phase [°]: ', self)
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
        lay.addRow(lb_vgap, self.lb_VGap)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lb_vgapCheck, hlay_vgapCheck)
        lay.addRow(lb_phs, hlay_phs)
        lay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(lb_detune, self.lb_Detune)
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

        # Power
        lb_rmppwr = QLabel('Power [W]: ', self)
        self.lb_RmpPwr = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RAMP:TOP:W')

        # Reflected Power
        lb_rmpreflpwr = QLabel('Reflected Power [W]: ', self)
        self.lb_RmpRefPwr = PyDMLabel(
            parent=self, init_channel='BO-05D:RF-P5Cav:PwrRevTop-Mon')

        # Gap Voltage
        lb_rmpvcav = QLabel('Gap Voltage [kV]: ', self)
        self.lb_RmpVCav = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpVoltTop-Mon')

        lb_RmpPhsTop = QLabel('Phase Top [°]: ', self)
        self.lb_auxRmpPhsTop = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpPhsTop-SP')
        self.lb_auxRmpPhsTop.setStyleSheet('max-width: 4em;')
        lb_auxRmpPhsTop = QLabel('/')
        lb_auxRmpPhsTop.setStyleSheet('max-width:1em;')
        self.lb_auxRmpPhsTopRef = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpPhsTop-RB')
        self.lb_auxRmpPhsTopRef.setStyleSheet('max-width: 4em;')
        hlay_rmpphstop = QHBoxLayout()
        hlay_rmpphstop.addWidget(self.lb_auxRmpPhsTop)
        hlay_rmpphstop.addWidget(lb_auxRmpPhsTop)
        hlay_rmpphstop.addWidget(self.lb_auxRmpPhsTopRef)

        lb_RmpPhsBot = QLabel('Phase Bottom [°]: ', self)
        self.lb_auxRmpPhsTop = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpPhsBot-SP')
        self.lb_auxRmpPhsTop.setStyleSheet('max-width: 4em;')
        lb_auxRmpPhsTop = QLabel('/')
        lb_auxRmpPhsTop.setStyleSheet('max-width:1em;')
        self.lb_auxRmpPhsTopRef = PyDMLabel(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpPhsBot-RB')
        self.lb_auxRmpPhsTopRef.setStyleSheet('max-width: 4em;')
        hlay_rmpphsbot = QHBoxLayout()
        hlay_rmpphsbot.addWidget(self.lb_auxRmpPhsTop)
        hlay_rmpphsbot.addWidget(lb_auxRmpPhsTop)
        hlay_rmpphsbot.addWidget(self.lb_auxRmpPhsTopRef)

        wid = QWidget()
        lay = QFormLayout(wid)
        lay.setFormAlignment(Qt.AlignHCenter)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(lb_rmprdy, self.led_RmpReady)
        lay.addRow(self.graph_rmp)
        lay.addRow(lb_rmppwr, self.lb_RmpPwr)
        lay.addRow(lb_rmpreflpwr, self.lb_RmpRefPwr)
        lay.addRow(lb_rmpvcav, self.lb_RmpVCav)
        lay.addRow(lb_RmpPhsTop, hlay_rmpphstop)
        lay.addRow(lb_RmpPhsBot, hlay_rmpphsbot)
        return wid

    def _toogleWidgets(self, index):
        self.wid_Stat.setVisible(index == 0)
        self.wid_Ramp.setVisible(index == 1)
        self.centralWidget().adjustSize()
        self.adjustSize()
