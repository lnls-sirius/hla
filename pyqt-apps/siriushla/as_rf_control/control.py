from functools import partial as _part
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QFormLayout, QHBoxLayout, QVBoxLayout,\
    QComboBox, QGroupBox, QTabWidget, QLabel, QCheckBox, QSpacerItem, QWidget,\
    QSizePolicy as QSzPlcy, QPushButton, QRadioButton
from qtpy.QtGui import QColor
import qtawesome as qta
from pydm.widgets import PyDMLineEdit, PyDMEnumComboBox, PyDMWaveformPlot, \
    PyDMLabel, PyDMSpinbox
from siriushla.widgets import SiriusMainWindow, PyDMStateButton, PyDMLed, \
    SiriusLedAlert, SiriusLedState, PyDMLedMultiChannel, SiriusTimePlot, \
    SiriusConnectionSignal, SiriusPushButton
from siriushla.util import connect_window, get_appropriate_color
from pyqtgraph import InfiniteLine, mkPen
from .details import TransmLineStatusDetails, CavityStatusDetails, \
    LLRFInterlockDetails
from .custom_widgets import RFEnblDsblButton
from .util import SEC_2_CHANNELS


class RFMainControl(SiriusMainWindow):
    """RF Control Overview Window."""

    def __init__(self, parent=None, prefix='', section=''):
        super().__init__(parent)
        self.section = section.upper()
        self.chs = SEC_2_CHANNELS[self.section]
        for group in ['Coupler', 'Cells']:
            key = group+' Limits PVs'
            for pv in self.chs['Cav Sts']['Temp'][key]:
                channel = SiriusConnectionSignal(pv)
                channel.new_value_signal[float].connect(
                    self._update_temp_limits)

        self.setObjectName(self.section + 'App')
        self.setWindowTitle(self.section + ' RF Control Overview Window')
        self.setWindowIcon(
            qta.icon('mdi.waves', color=get_appropriate_color(self.section)))
        self.curves = dict()

        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)

        label = QLabel('<h2>'+self.section+' RF Controls - Overview</h2>',
                       self, alignment=Qt.AlignCenter)

        gbox_intlks = QGroupBox('Status', self)
        gbox_intlks.setLayout(self._statusLayout())

        gbox_rfgen = QGroupBox('RF Generator', self)
        gbox_rfgen.setObjectName('RFGen')
        gbox_rfgen.setStyleSheet('#RFGen{background-color: #d7ccc8;}')
        gbox_rfgen.setLayout(self._rfGenLayout())

        if self.section == 'SI':
            wid_startctrl = QGroupBox('Start Controls', self)
            wid_startctrl.setLayout(self._startControlLayout())
        else:
            wid_startctrl = QTabWidget(self)
            wid_startctrl.setObjectName(self.section+'Tab')
            wid_startctrl.setStyleSheet(
                "#"+self.section+'Tab'+"::pane {"
                "    border-left: 2px solid gray;"
                "    border-bottom: 2px solid gray;"
                "    border-right: 2px solid gray;}")
            wid_control = QWidget(self)
            wid_control.setLayout(self._startControlLayout())
            wid_startctrl.addTab(wid_control, 'Start Controls')
            wid_rampctrl = QWidget(self)
            wid_rampctrl.setLayout(self._rampControlLayout())
            wid_startctrl.addTab(wid_rampctrl, 'Ramp Controls')
            wid_autostart = QWidget(self)
            wid_autostart.setLayout(self._autoStartLayout())
            wid_startctrl.addTab(wid_autostart, 'Auto Start')

        if self.section == 'SI':
            wid_pwrmon = QGroupBox('Power Meter', self)
            wid_pwrmon.setLayout(self._powerMeterLayout())
        else:
            wid_pwrmon = QTabWidget(self)
            wid_pwrmon.setObjectName(self.section+'Tab')
            wid_pwrmon.setStyleSheet(
                "#"+self.section+'Tab'+"::pane {"
                "    border-left: 2px solid gray;"
                "    border-bottom: 2px solid gray;"
                "    border-right: 2px solid gray;}")
            wid_rampmon = QWidget(self)
            wid_rampmon.setLayout(self._rampMonLayout())
            wid_pwrmon.addTab(wid_rampmon, 'Ramp')
            wid_cw = QWidget(self)
            wid_cw.setLayout(self._powerMeterLayout())
            wid_pwrmon.addTab(wid_cw, 'CW')

        gbox_graphs = QGroupBox('Graphs', self)
        gbox_graphs.setLayout(self._graphsLayout())

        lay = QGridLayout(cw)
        lay.addWidget(label, 0, 0, 1, 4)
        lay.addWidget(gbox_intlks, 1, 0, 1, 1)
        lay.addWidget(gbox_rfgen, 2, 0, 1, 1)
        lay.addWidget(wid_startctrl, 1, 1, 2, 1)
        lay.addWidget(wid_pwrmon, 1, 2, 2, 1)
        lay.addWidget(gbox_graphs, 1, 3, 2, 1)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 5)
        lay.setColumnStretch(2, 3)
        lay.setColumnStretch(3, 4)

        self.setStyleSheet("""
            QSpinBox, QComboBox, QPushButton, PyDMLineEdit,
            PyDMSpinbox, PyDMEnumComboBox{
                min-width:5em; max-width:5em;
            }
            PyDMStateButton{
                min-width: 2.58em;
            }
            PyDMLabel{
                qproperty-alignment: AlignCenter;
            }
            QLed{
                max-width: 1.29em;
            }
            QLabel{
                max-height:1.5em; min-width:4em;
            }""")

    def _statusLayout(self):
        # Interlocks
        self._ld_intlks = QLabel(
            '<h4>Interlocks</h4>', self, alignment=Qt.AlignLeft)

        # # Emergency
        self.ld_emerg = QLabel('Emergency Stop', self, alignment=Qt.AlignRight)
        self.ld_emerg.setStyleSheet('min-width: 6.8em;')
        self.led_emerg = SiriusLedAlert(self, self.chs['Emergency'])

        # # Sirius Interlock
        self.ld_siriusintlk = QLabel(
            'Sirius Interlock', self, alignment=Qt.AlignRight)
        self.led_siriusintlk = SiriusLedAlert(self, self.chs['Sirius Intlk'])

        # # LLRF Interlock
        self.ld_intlk = QLabel('LLRF Interlock', self, alignment=Qt.AlignRight)
        self.led_intlk = SiriusLedAlert(self, self.chs['LLRF Intlk'])
        self.pb_intlkdtls = QPushButton(qta.icon('fa5s.ellipsis-v'), '', self)
        self.pb_intlkdtls.setObjectName('dtls')
        self.pb_intlkdtls.setStyleSheet(
            '#dtls{min-width:18px;max-width:18px;icon-size:20px;}')
        connect_window(self.pb_intlkdtls, LLRFInterlockDetails, parent=self,
                       section=self.section)
        hlay_intlksts = QHBoxLayout()
        hlay_intlksts.addWidget(self.led_intlk)
        hlay_intlksts.addWidget(self.pb_intlkdtls)

        # Status
        self._ld_stats = QLabel(
            '<h4>Status</h4>', self, alignment=Qt.AlignLeft)

        # # Status Cavity
        self.ld_cavsts = QLabel('Cavity', self, alignment=Qt.AlignRight)
        self.led_cavsts = PyDMLedMultiChannel(
            self, {self.chs['Cav Sts']['Geral']: 1})
        self.pb_cavdtls = QPushButton(qta.icon('fa5s.ellipsis-v'), '', self)
        self.pb_cavdtls.setObjectName('dtls')
        self.pb_cavdtls.setStyleSheet(
            '#dtls{min-width:18px;max-width:18px;icon-size:20px;}')
        connect_window(self.pb_cavdtls, CavityStatusDetails, parent=self,
                       section=self.section)
        hlay_cavsts = QHBoxLayout()
        hlay_cavsts.addWidget(self.led_cavsts)
        hlay_cavsts.addWidget(self.pb_cavdtls)

        # # Status Transmission Line
        self.ld_tlsts = QLabel('Transm. Line', self, alignment=Qt.AlignRight)
        self.led_tlsts = PyDMLedMultiChannel(
            self, {self.chs['TL Sts']['Geral']: 1})
        self.pb_tldtls = QPushButton(qta.icon('fa5s.ellipsis-v'), '', self)
        self.pb_tldtls.setObjectName('dtls')
        self.pb_tldtls.setStyleSheet(
            '#dtls{min-width:18px;max-width:18px;icon-size:20px;}')
        connect_window(self.pb_tldtls, TransmLineStatusDetails, parent=self,
                       section=self.section)
        hlay_tlsts = QHBoxLayout()
        hlay_tlsts.addWidget(self.led_tlsts)
        hlay_tlsts.addWidget(self.pb_tldtls)

        # Reset
        self._ld_reset = QLabel('<h4>Reset</h4>', self, alignment=Qt.AlignLeft)

        # # Reset Global
        self.ld_globreset = QLabel(
            'Reset Global', self, alignment=Qt.AlignRight)
        self.pb_globreset = SiriusPushButton(
            label='', icon=qta.icon('fa5s.sync'),
            parent=self, init_channel=self.chs['Reset']['Global'])
        self.pb_globreset.setObjectName('pb_globreset')
        self.pb_globreset.setStyleSheet(
            '#pb_globreset{min-width:25px; max-width:25px; icon-size:20px;}')

        # # Reset LLRF
        self.ld_llrfreset = QLabel('Reset LLRF', self, alignment=Qt.AlignRight)
        self.pb_llrfreset = SiriusPushButton(
            label='', icon=qta.icon('fa5s.sync'),
            parent=self, init_channel=self.chs['Reset']['LLRF'])
        self.pb_llrfreset.setObjectName('pb_llrfreset')
        self.pb_llrfreset.setStyleSheet(
            '#pb_llrfreset{min-width:25px; max-width:25px; icon-size:20px;}')

        lay = QGridLayout()
        lay.addWidget(self._ld_intlks, 0, 0, 1, 2)
        lay.addWidget(self.ld_emerg, 1, 0)
        lay.addWidget(self.led_emerg, 1, 1)
        lay.addWidget(self.ld_siriusintlk, 2, 0)
        lay.addWidget(self.led_siriusintlk, 2, 1)
        lay.addWidget(self.ld_intlk, 3, 0)
        lay.addLayout(hlay_intlksts, 3, 1)
        lay.addWidget(self._ld_stats, 4, 0, 1, 2)
        lay.addWidget(self.ld_cavsts, 5, 0)
        lay.addLayout(hlay_cavsts, 5, 1)
        lay.addWidget(self.ld_tlsts, 6, 0)
        lay.addLayout(hlay_tlsts, 6, 1)
        lay.addWidget(self._ld_reset, 7, 0, 1, 2)
        lay.addWidget(self.ld_globreset, 8, 0)
        lay.addWidget(self.pb_globreset, 8, 1)
        lay.addWidget(self.ld_llrfreset, 9, 0)
        lay.addWidget(self.pb_llrfreset, 9, 1)
        return lay

    def _rfGenLayout(self):
        # On/Off
        self.ld_genenbl = QLabel('Enable', self, alignment=Qt.AlignCenter)
        # self.bt_genenbl = PyDMStateButton(self, 'RF-Gen:GeneralRF-Sel')
        self.lb_genenbl = SiriusLedState(self, 'RF-Gen:GeneralRF-Sts')

        # Frequência
        self.ld_genfreq = QLabel('Frequency', self, alignment=Qt.AlignCenter)
        self.le_genfreq = PyDMLineEdit(self, 'RF-Gen:GeneralFreq-SP')
        self.le_genfreq.setStyleSheet('min-width:7em; max-width:7em;')
        self.le_genfreq.precisionFromPV = False
        self.le_genfreq.precision = 2
        self.lb_genfreq = PyDMLabel(self, 'RF-Gen:GeneralFreq-RB')
        self.lb_genfreq.setStyleSheet(
            'min-width:7em; max-width:7em; qproperty-alignment:AlignLeft;')
        self.lb_genfreq.precisionFromPV = False
        self.lb_genfreq.precision = 2

        # Phase Continuous State
        self.ld_genphscont = QLabel(
            'Phase Cont.', self, alignment=Qt.AlignCenter)
        # self.bt_genphscont = PyDMStateButton(self, 'RF-Gen:FreqPhsCont-Sel')
        self.lb_genphscont = SiriusLedState(self, 'RF-Gen:FreqPhsCont-Sts')

        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.ld_genenbl)
        # lay.addWidget(self.bt_genenbl)
        lay.addWidget(self.lb_genenbl, alignment=Qt.AlignCenter)
        lay.addStretch()
        lay.addWidget(self.ld_genfreq)
        lay.addWidget(self.le_genfreq)
        lay.addWidget(self.lb_genfreq)
        lay.addStretch()
        lay.addWidget(self.ld_genphscont)
        # lay.addWidget(self.bt_genphscont)
        lay.addWidget(self.lb_genphscont, alignment=Qt.AlignCenter)
        lay.addStretch()
        return lay

    def _startControlLayout(self):
        # SSA
        dic = self.chs['SSA'] if self.section == 'BO' else self.chs['SSA']['1']
        lay_amp = QGridLayout()
        lay_amp.setHorizontalSpacing(8)
        lay_amp.setVerticalSpacing(20)
        lay_amp.addItem(QSpacerItem(
            10, 0, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 0)
        lay_amp.addWidget(QLabel('<h4>Power</h4>', self,
                                 alignment=Qt.AlignCenter), 1, 3)
        lay_amp.addWidget(QLabel('<h4>'+dic['SRC 1']['Label']+'</h4>', self,
                                 alignment=Qt.AlignCenter), 1, 4)
        lay_amp.addWidget(QLabel('<h4>'+dic['SRC 2']['Label']+'</h4>', self,
                                 alignment=Qt.AlignCenter), 1, 5)
        lay_amp.addWidget(QLabel('<h4>Pin Sw</h4>', self,
                                 alignment=Qt.AlignCenter), 1, 6)
        lay_amp.addWidget(QLabel('<h4>Pre Drive</h4>', self,
                                 alignment=Qt.AlignCenter), 1, 7)
        lay_amp.addItem(QSpacerItem(
            10, 0, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 8)

        if self.section == 'BO':
            self._create_ssa_wid(lay_amp, 2, self.chs['SSA'])
        else:
            for k, v in self.chs['SSA'].items():
                self._create_ssa_wid(lay_amp, int(k)+1, v)

        # LLRF
        # # Slow Loop Control
        self.lb_slmode = PyDMLabel(self, self.chs['SL']['Mode'])
        self.led_slmode = PyDMLedMultiChannel(
            self, {self.chs['SL']['Mode']: 0})
        self.bt_slenbl = PyDMStateButton(self, self.chs['SL']['Enbl']+':S')
        self.led_slenbl = SiriusLedState(self, self.chs['SL']['Enbl'])

        lay_over = QGridLayout()
        lay_over.setAlignment(Qt.AlignCenter)
        lay_over.addWidget(QLabel('<h4>Mode</h4>', self,
                                  alignment=Qt.AlignCenter), 0, 0)
        lay_over.addWidget(self.lb_slmode, 0, 1)
        lay_over.addWidget(self.led_slmode, 0, 2, alignment=Qt.AlignLeft)
        lay_over.addWidget(QLabel('<h4>Enable</h4>', self,
                                  alignment=Qt.AlignCenter), 1, 0)
        lay_over.addWidget(self.bt_slenbl, 1, 1)
        lay_over.addWidget(self.led_slenbl, 1, 2, alignment=Qt.AlignLeft)

        self.sb_amp = PyDMSpinbox(self, self.chs['SL']['ASet']+':S')
        self.sb_amp.showStepExponent = False
        self.lb_amp = PyDMLabel(self, self.chs['SL']['ASet'])
        self.cb_ampincrate = PyDMEnumComboBox(
            self, self.chs['SL']['AInc']+':S')
        self.lb_ampincrate = PyDMLabel(self, self.chs['SL']['AInc'])
        self.sb_phs = PyDMSpinbox(self, self.chs['SL']['PSet']+':S')
        self.sb_phs.showStepExponent = False
        self.lb_phs = PyDMLabel(self, self.chs['SL']['PSet'])
        self.cb_phsincrate = PyDMEnumComboBox(
            self, self.chs['SL']['PInc']+':S')
        self.lb_phsincrate = PyDMLabel(self, self.chs['SL']['PInc'])
        lay_slctrl = QGridLayout()
        lay_slctrl.setHorizontalSpacing(9)
        lay_slctrl.setVerticalSpacing(9)
        lay_slctrl.addWidget(QLabel('<h4>SP/RB</h4>', self,
                                    alignment=Qt.AlignCenter), 0, 1, 1, 2)
        lay_slctrl.addWidget(QLabel('<h4>Inc. Rate SP/RB</h4>', self,
                                    alignment=Qt.AlignCenter), 0, 3, 1, 2)
        lay_slctrl.addWidget(QLabel('<h4>Amplitude [mV]</h4>', self,
                                    alignment=Qt.AlignCenter), 1, 0)
        lay_slctrl.addWidget(QLabel('<h4>Phase [DEG]</h4>', self,
                                    alignment=Qt.AlignCenter), 2, 0)
        lay_slctrl.addWidget(self.sb_amp, 1, 1, alignment=Qt.AlignRight)
        lay_slctrl.addWidget(self.lb_amp, 1, 2, alignment=Qt.AlignLeft)
        lay_slctrl.addWidget(self.cb_ampincrate, 1, 3, alignment=Qt.AlignRight)
        lay_slctrl.addWidget(self.lb_ampincrate, 1, 4, alignment=Qt.AlignLeft)
        lay_slctrl.addWidget(self.sb_phs, 2, 1, alignment=Qt.AlignRight)
        lay_slctrl.addWidget(self.lb_phs, 2, 2, alignment=Qt.AlignLeft)
        lay_slctrl.addWidget(self.cb_phsincrate, 2, 3, alignment=Qt.AlignRight)
        lay_slctrl.addWidget(self.lb_phsincrate, 2, 4, alignment=Qt.AlignLeft)

        self.lb_iref = PyDMLabel(self, self.chs['SL']['IRef'])
        self.lb_iref.showUnits = True
        self.lb_iinp = PyDMLabel(self, self.chs['SL']['IInp'])
        self.lb_iinp.showUnits = True
        self.lb_ierr = PyDMLabel(self, self.chs['SL']['IErr'])
        self.lb_ierr.showUnits = True
        self.lb_qref = PyDMLabel(self, self.chs['SL']['QRef'])
        self.lb_qref.showUnits = True
        self.lb_qinp = PyDMLabel(self, self.chs['SL']['QInp'])
        self.lb_qinp.showUnits = True
        self.lb_qerr = PyDMLabel(self, self.chs['SL']['QErr'])
        self.lb_qerr.showUnits = True
        self.lb_ampref = PyDMLabel(self, self.chs['SL']['ARef'])
        self.lb_ampref.showUnits = True
        self.lb_ampinp = PyDMLabel(self, self.chs['SL']['AInp'])
        self.lb_ampinp.showUnits = True
        self.lb_amperr = PyDMLabel(self, self.chs['SL']['AErr'])
        self.lb_amperr.showUnits = True
        self.lb_phsref = PyDMLabel(self, self.chs['SL']['PRef'])
        self.lb_phsref.showUnits = True
        self.lb_phsinp = PyDMLabel(self, self.chs['SL']['PInp'])
        self.lb_phsinp.showUnits = True
        self.lb_phserr = PyDMLabel(self, self.chs['SL']['PErr'])
        self.lb_phserr.showUnits = True
        lay_slmon = QGridLayout()
        lay_slmon.setHorizontalSpacing(9)
        lay_slmon.setVerticalSpacing(9)
        lay_slmon.addWidget(
            QLabel('<h4>Reference</h4>', self, alignment=Qt.AlignCenter), 1, 0)
        lay_slmon.addWidget(
            QLabel('<h4>Input</h4>', self, alignment=Qt.AlignCenter), 2, 0)
        lay_slmon.addWidget(
            QLabel('<h4>Error</h4>', self, alignment=Qt.AlignCenter), 3, 0)
        lay_slmon.addWidget(
            QLabel('<h4>I</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        lay_slmon.addWidget(self.lb_iref, 1, 1)
        lay_slmon.addWidget(self.lb_iinp, 2, 1)
        lay_slmon.addWidget(self.lb_ierr, 3, 1)
        lay_slmon.addWidget(
            QLabel('<h4>Q</h4>', self, alignment=Qt.AlignCenter), 0, 2)
        lay_slmon.addWidget(self.lb_qref, 1, 2)
        lay_slmon.addWidget(self.lb_qinp, 2, 2)
        lay_slmon.addWidget(self.lb_qerr, 3, 2)
        lay_slmon.addWidget(
            QLabel('<h4>Amp.</h4>', self, alignment=Qt.AlignCenter), 0, 3)
        lay_slmon.addWidget(self.lb_ampref, 1, 3)
        lay_slmon.addWidget(self.lb_ampinp, 2, 3)
        lay_slmon.addWidget(self.lb_amperr, 3, 3)
        lay_slmon.addWidget(
            QLabel('<h4>Phase</h4>', self, alignment=Qt.AlignCenter), 0, 4)
        lay_slmon.addWidget(self.lb_phsref, 1, 4)
        lay_slmon.addWidget(self.lb_phsinp, 2, 4)
        lay_slmon.addWidget(self.lb_phserr, 3, 4)
        lay_slmon.addItem(
            QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Expanding), 4, 0)

        wid_sl = QWidget()
        lay_sl = QGridLayout(wid_sl)
        lay_sl.setAlignment(Qt.AlignTop)
        lay_sl.setSpacing(20)
        lay_sl.addItem(
            QSpacerItem(10, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 1, 0)
        lay_sl.addLayout(lay_over, 1, 1)
        lay_sl.addItem(
            QSpacerItem(0, 25, QSzPlcy.Ignored, QSzPlcy.Fixed), 2, 1)
        lay_sl.addLayout(lay_slctrl, 3, 1)
        lay_sl.addItem(
            QSpacerItem(0, 25, QSzPlcy.Ignored, QSzPlcy.Fixed), 4, 1)
        lay_sl.addLayout(lay_slmon, 5, 1)
        lay_sl.addItem(
            QSpacerItem(10, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 1, 3)

        # # Tuning
        # # # Tuning settings
        lb_autotun = QLabel('Auto Tuning: ', self, alignment=Qt.AlignRight)
        self.bt_autotun = PyDMStateButton(self, self.chs['Tun']['Auto']+':S')
        self.lb_autotun = SiriusLedState(self, self.chs['Tun']['Auto'])
        lb_dtune = QLabel('DTune: ', self, alignment=Qt.AlignRight)
        self.sb_dtune = PyDMSpinbox(
            self, self.chs['Tun']['DTune'].replace('RB', 'SP'))
        self.sb_dtune.showStepExponent = False
        self.lb_dtune = PyDMLabel(self, self.chs['Tun']['DTune'])
        self.lb_dtune.showUnits = True
        lb_dphase = QLabel('Dephase: ', self, alignment=Qt.AlignRight)
        self.lb_dphase = PyDMLabel(self, self.chs['Tun']['DPhase'])
        self.lb_dphase.showUnits = True
        lay_tunset = QGridLayout()
        lay_tunset.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        lay_tunset.setVerticalSpacing(12)
        lay_tunset.addItem(
            QSpacerItem(10, 0, QSzPlcy.Expanding, QSzPlcy.Ignored), 1, 0)
        lay_tunset.addWidget(lb_autotun, 1, 1)
        lay_tunset.addWidget(self.bt_autotun, 1, 2)
        lay_tunset.addWidget(self.lb_autotun, 1, 3)
        lay_tunset.addWidget(lb_dtune, 2, 1)
        lay_tunset.addWidget(self.sb_dtune, 2, 2)
        lay_tunset.addWidget(self.lb_dtune, 2, 3)
        lay_tunset.addWidget(lb_dphase, 3, 1)
        lay_tunset.addWidget(self.lb_dphase, 3, 2)
        lay_tunset.addItem(
            QSpacerItem(10, 0, QSzPlcy.Expanding, QSzPlcy.Ignored), 1, 4)

        # # # Plungers motors
        lb_plg1 = QLabel('Plunger 1')
        lb_plg2 = QLabel('Plunger 2')
        lb_down = QLabel('Down')
        lb_up = QLabel('Up')
        self.led_Plg1_Dn = PyDMLed(self, self.chs['Tun']['Pl1Down'])
        self.led_Plg1_Dn.offColor = QColor(64, 64, 64)
        self.led_Plg1_Dn.onColor = QColor('blue')
        self.led_Plg1_Dn.shape = PyDMLed.ShapeMap.Square
        self.led_Plg1_Up = PyDMLed(self, self.chs['Tun']['Pl1Up'])
        self.led_Plg1_Up.offColor = QColor(64, 64, 64)
        self.led_Plg1_Up.onColor = QColor('blue')
        self.led_Plg1_Up.shape = PyDMLed.ShapeMap.Square
        self.led_Plg2_Dn = PyDMLed(self, self.chs['Tun']['Pl2Down'])
        self.led_Plg2_Dn.offColor = QColor(64, 64, 64)
        self.led_Plg2_Dn.onColor = QColor('blue')
        self.led_Plg2_Dn.shape = PyDMLed.ShapeMap.Square
        self.led_Plg2_Up = PyDMLed(self, self.chs['Tun']['Pl2Up'])
        self.led_Plg2_Up.offColor = QColor(64, 64, 64)
        self.led_Plg2_Up.onColor = QColor('blue')
        self.led_Plg2_Up.shape = PyDMLed.ShapeMap.Square
        lay_plunmon = QGridLayout()
        lay_plunmon.addItem(
            QSpacerItem(10, 10, QSzPlcy.Expanding, QSzPlcy.Expanding), 0, 0)
        lay_plunmon.addWidget(lb_down, 1, 2)
        lay_plunmon.addWidget(lb_up, 1, 3)
        lay_plunmon.addWidget(lb_plg1, 2, 1)
        lay_plunmon.addWidget(lb_plg2, 3, 1)
        lay_plunmon.addWidget(self.led_Plg1_Dn, 2, 2)
        lay_plunmon.addWidget(self.led_Plg1_Up, 2, 3)
        lay_plunmon.addWidget(self.led_Plg2_Dn, 3, 2)
        lay_plunmon.addWidget(self.led_Plg2_Up, 3, 3)
        lay_plunmon.addItem(
            QSpacerItem(10, 10, QSzPlcy.Expanding, QSzPlcy.Expanding), 4, 4)

        self.graph_plunmotors = SiriusTimePlot(self)
        self.graph_plunmotors.setObjectName('graph')
        self.graph_plunmotors.setStyleSheet(
            '#graph{min-height:15em;min-width:20em;max-height:15em;}')
        self.graph_plunmotors.autoRangeX = True
        self.graph_plunmotors.autoRangeY = True
        self.graph_plunmotors.backgroundColor = QColor(255, 255, 255)
        self.graph_plunmotors.showXGrid = True
        self.graph_plunmotors.showYGrid = True
        self.graph_plunmotors.showLegend = True
        self.graph_plunmotors.timeSpan = 1800
        self.graph_plunmotors.maxRedrawRate = 2
        self.graph_plunmotors.addYChannel(
            y_channel=self.chs['Tun']['PlM1Curr'], color='blue',
            name='Motor 1', lineStyle=Qt.SolidLine, lineWidth=1)
        self.graph_plunmotors.addYChannel(
            y_channel=self.chs['Tun']['PlM2Curr'], color='red',
            name='Motor 2', lineStyle=Qt.SolidLine, lineWidth=1)

        wid_tun = QWidget()
        lay_plun = QGridLayout(wid_tun)
        lay_plun.addWidget(QLabel('<h3> • Settings</h3>', self,
                                  alignment=Qt.AlignLeft), 0, 0, 1, 3)
        lay_plun.addLayout(lay_tunset, 1, 0, 1, 3)
        lay_plun.addItem(
            QSpacerItem(0, 25, QSzPlcy.Ignored, QSzPlcy.Fixed), 2, 0)
        lay_plun.addWidget(QLabel('<h3> • Plungers</h3>', self,
                                  alignment=Qt.AlignLeft), 3, 0)
        lay_plun.addLayout(lay_plunmon, 4, 0)
        lay_plun.addWidget(self.graph_plunmotors, 4, 1, 1, 2)

        wid_llrf = QTabWidget(self)
        color = 'green' if self.section == 'BO' else 'blue'
        wid_llrf.setStyleSheet("""
            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: """+color+""";
                color: white;
                border: 0.1em solid white;
            }""")
        wid_llrf.addTab(wid_sl, 'Slow Loop Control')
        wid_llrf.addTab(wid_tun, 'Tuning')

        # Layout
        vlay = QVBoxLayout()
        vlay.addWidget(QLabel('<h3> • Solid State Amplifiers</h3>', self,
                              alignment=Qt.AlignLeft))
        vlay.addLayout(lay_amp)
        vlay.addItem(QSpacerItem(0, 50, QSzPlcy.Ignored, QSzPlcy.Fixed))
        vlay.addWidget(QLabel('<h3> • LLRF</h3>', self,
                              alignment=Qt.AlignLeft))
        vlay.addWidget(wid_llrf)
        vlay.addStretch()
        return vlay

    def _rampControlLayout(self):
        ctrls_label = QLabel('<h3> • Controls</h3>', self,
                             alignment=Qt.AlignLeft)
        self.bt_RmpEnbl = PyDMStateButton(self, 'BR-RF-DLLRF-01:RmpEnbl-Sel')
        self.lb_RmpEnbl = SiriusLedState(self, 'BR-RF-DLLRF-01:RmpEnbl-Sts')

        self.led_RmpReady = PyDMLed(
            parent=self, init_channel='BR-RF-DLLRF-01:RmpReady-Mon')
        self.led_RmpReady.onColor = PyDMLed.LightGreen
        self.led_RmpReady.offColor = PyDMLed.Red

        self.cb_RmpIncTs = PyDMSpinbox(self, 'BR-RF-DLLRF-01:RmpIncTs-SP')
        self.cb_RmpIncTs.showStepExponent = False
        self.lb_RmpIncTs = PyDMLabel(self, 'BR-RF-DLLRF-01:RmpIncTs-RB')
        self.lb_RmpIncTs.showUnits = True

        self.sb_RmpTs1 = PyDMSpinbox(self, 'BR-RF-DLLRF-01:RmpTs1-SP')
        self.sb_RmpTs1.showStepExponent = False
        self.lb_RmpTs1 = PyDMLabel(self, 'BR-RF-DLLRF-01:RmpTs1-RB')
        self.lb_RmpTs1.showUnits = True
        self.sb_RmpTs2 = PyDMSpinbox(self, 'BR-RF-DLLRF-01:RmpTs2-SP')
        self.sb_RmpTs2.showStepExponent = False
        self.lb_RmpTs2 = PyDMLabel(self, 'BR-RF-DLLRF-01:RmpTs2-RB')
        self.lb_RmpTs2.showUnits = True
        self.sb_RmpTs3 = PyDMSpinbox(self, 'BR-RF-DLLRF-01:RmpTs3-SP')
        self.sb_RmpTs3.showStepExponent = False
        self.lb_RmpTs3 = PyDMLabel(self, 'BR-RF-DLLRF-01:RmpTs3-RB')
        self.lb_RmpTs3.showUnits = True
        self.sb_RmpTs4 = PyDMSpinbox(self, 'BR-RF-DLLRF-01:RmpTs4-SP')
        self.sb_RmpTs4.showStepExponent = False
        self.lb_RmpTs4 = PyDMLabel(self, 'BR-RF-DLLRF-01:RmpTs4-RB')
        self.lb_RmpTs4.showUnits = True

        self.sb_RmpPhsTop = PyDMSpinbox(self, 'BR-RF-DLLRF-01:RmpPhsTop-SP')
        self.sb_RmpPhsTop.showStepExponent = False
        self.lb_RmpPhsTop = PyDMLabel(self, 'BR-RF-DLLRF-01:RmpPhsTop-RB')
        self.lb_RmpPhsTop.showUnits = True
        self.sb_RmpVoltTop = PyDMLineEdit(
            self, 'BR-RF-DLLRF-01:mV:RAMP:AMP:TOP-SP')
        self.lb_RmpVoltTop = PyDMLabel(
            self, 'BR-RF-DLLRF-01:mV:RAMP:AMP:TOP-RB')
        self.lb_RmpVoltTop.showUnits = True

        self.sb_RmpPhsBot = PyDMSpinbox(self, 'BR-RF-DLLRF-01:RmpPhsBot-SP')
        self.sb_RmpPhsBot.showStepExponent = False
        self.lb_RmpPhsBot = PyDMLabel(self, 'BR-RF-DLLRF-01:RmpPhsBot-RB')
        self.lb_RmpPhsBot.showUnits = True
        self.sb_RmpVoltBot = PyDMLineEdit(
            self, 'BR-RF-DLLRF-01:mV:RAMP:AMP:BOT-SP')
        self.lb_RmpVoltBot = PyDMLabel(
            self, 'BR-RF-DLLRF-01:mV:RAMP:AMP:BOT-RB')
        self.lb_RmpVoltBot.showUnits = True

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(ctrls_label, 0, 0)
        lay.addItem(
            QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay.addWidget(QLabel('Enable: ', self,
                             alignment=Qt.AlignRight), 2, 0)
        lay.addWidget(self.bt_RmpEnbl, 2, 1)
        lay.addWidget(self.lb_RmpEnbl, 2, 2, alignment=Qt.AlignLeft)
        lay.addWidget(QLabel('Ramp Ready: ', self,
                             alignment=Qt.AlignRight), 3, 0)
        lay.addWidget(self.led_RmpReady, 3, 1, alignment=Qt.AlignLeft)
        lay.addItem(
            QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 4, 0)
        lay.addWidget(QLabel('<h4>Durations</h4>', self), 5, 0, 1, 3)
        lay.addWidget(QLabel('Bottom: ', self,
                             alignment=Qt.AlignRight), 6, 0)
        lay.addWidget(self.sb_RmpTs1, 6, 1)
        lay.addWidget(self.lb_RmpTs1, 6, 2)
        lay.addWidget(QLabel('Rampup: ', self,
                             alignment=Qt.AlignRight), 7, 0)
        lay.addWidget(self.sb_RmpTs2, 7, 1)
        lay.addWidget(self.lb_RmpTs2, 7, 2)
        lay.addWidget(QLabel('Top: ', self,
                             alignment=Qt.AlignRight), 8, 0)
        lay.addWidget(self.sb_RmpTs3, 8, 1)
        lay.addWidget(self.lb_RmpTs3, 8, 2)
        lay.addWidget(QLabel('Rampdown:', self,
                             alignment=Qt.AlignRight), 9, 0)
        lay.addWidget(self.sb_RmpTs4, 9, 1)
        lay.addWidget(self.lb_RmpTs4, 9, 2)
        lay.addWidget(QLabel('Ramp Inc. Rate: ', self,
                             alignment=Qt.AlignRight), 10, 0)
        lay.addWidget(self.cb_RmpIncTs, 10, 1)
        lay.addWidget(self.lb_RmpIncTs, 10, 2, alignment=Qt.AlignLeft)
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 11, 0)
        lay.addWidget(QLabel('<h4>Top</h4>', self), 12, 0, 1, 3)
        lay.addWidget(QLabel('Phase:', self,
                             alignment=Qt.AlignRight), 13, 0)
        lay.addWidget(self.sb_RmpPhsTop, 13, 1)
        lay.addWidget(self.lb_RmpPhsTop, 13, 2)
        lay.addWidget(QLabel('Amplitude:', self,
                             alignment=Qt.AlignRight), 14, 0)
        lay.addWidget(self.sb_RmpVoltTop, 14, 1)
        lay.addWidget(self.lb_RmpVoltTop, 14, 2)
        lay.addWidget(QLabel('<h4>Bottom</h4>', self), 15, 0, 1, 3)
        lay.addWidget(QLabel('Phase:', self,
                             alignment=Qt.AlignRight), 16, 0)
        lay.addWidget(self.sb_RmpPhsBot, 16, 1)
        lay.addWidget(self.lb_RmpPhsBot, 16, 2)
        lay.addWidget(QLabel('Amplitude:', self,
                             alignment=Qt.AlignRight), 17, 0)
        lay.addWidget(self.sb_RmpVoltBot, 17, 1)
        lay.addWidget(self.lb_RmpVoltBot, 17, 2)
        lay.addItem(QSpacerItem(
            10, 10, QSzPlcy.MinimumExpanding, QSzPlcy.MinimumExpanding), 18, 3)
        return lay

    def _rampMonLayout(self):
        self.ramp_graph = PyDMWaveformPlot(
            parent=self, background=QColor(255, 255, 255))
        self.ramp_graph.setObjectName('graph')
        self.ramp_graph.setStyleSheet(
            '#graph{min-height:15em;min-width:21em;max-height:15em;}')
        self.ramp_graph.maxRedrawRate = 2
        self.ramp_graph.mouseEnabledX = True
        self.ramp_graph.setShowXGrid(True)
        self.ramp_graph.setShowYGrid(True)
        self.ramp_graph.setShowLegend(False)
        self.ramp_graph.setAutoRangeX(True)
        self.ramp_graph.setAutoRangeY(True)
        self.ramp_graph.setAxisColor(QColor(0, 0, 0))
        self.ramp_graph.plotItem.showButtons()
        self.ramp_graph.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        self.ramp_graph.plotItem.getAxis('left').setStyle(tickTextOffset=5)
        self.ramp_graph.addChannel(
            y_channel='RA-RF:PowerSensor1:TracData-Mon',
            x_channel='RA-RF:PowerSensor1:TimeAxis-Mon',
            redraw_mode=2, name='Power [W]', color=QColor('blue'))
        self.curve_PwrMtr = self.ramp_graph.curveAtIndex(0)
        self.rb_PwrMtr = QRadioButton('Power Meter Signal', self)
        self.rb_PwrMtr.setChecked(True)
        self.rb_PwrMtr.toggled.connect(
            _part(self._handle_rmpwfm_visibility, 0))
        self.ramp_graph.addChannel(
            y_channel='BR-RF-DLLRF-01:VCavRampWf.AVAL',
            x_channel='BR-RF-DLLRF-01:DiagWf32Scale.AVAL',
            redraw_mode=2, name='VGav kV', color=QColor('blue'))
        self.curve_VGav = self.ramp_graph.curveAtIndex(1)
        self.rb_VGav = QRadioButton('VGav [kV]', self)
        self.rb_VGav.toggled.connect(_part(self._handle_rmpwfm_visibility, 1))
        self.ramp_graph.addChannel(
            y_channel='BR-RF-DLLRF-01:VCavRampWf:W.AVAL',
            x_channel='BR-RF-DLLRF-01:DiagWf32Scale.AVAL',
            redraw_mode=2, name='Power [W]', color=QColor('blue'))
        self.curve_Pwr = self.ramp_graph.curveAtIndex(2)
        self.rb_Pwr = QRadioButton('Power [W]', self)
        self.rb_Pwr.toggled.connect(_part(self._handle_rmpwfm_visibility, 2))
        hbox_rb = QHBoxLayout()
        hbox_rb.addWidget(self.rb_PwrMtr)
        hbox_rb.addWidget(self.rb_VGav)
        hbox_rb.addWidget(self.rb_Pwr)

        self.curve_VGav.setVisible(False)
        self.curve_Pwr.setVisible(False)

        self.lb_PwrFwdBot = PyDMLabel(self, 'BO-05D:RF-P5Cav:PwrFwdBot-Mon')
        self.lb_PwrFwdBot.showUnits = True
        self.lb_PwrRevBot = PyDMLabel(self, 'BO-05D:RF-P5Cav:PwrRevBot-Mon')
        self.lb_PwrRevBot.showUnits = True
        self.lb_C3PwrBot = PyDMLabel(self, 'BO-05D:RF-P5Cav:Cell3PwrBot-Mon')
        self.lb_C3PwrBot.showUnits = True
        self.lb_C3PhsBot = PyDMLabel(self, 'BR-RF-DLLRF-01:BOT:CELL3:PHS')
        self.lb_C3PhsBot.showUnits = True
        self.lb_PwrFwdTop = PyDMLabel(self, 'BO-05D:RF-P5Cav:PwrFwdTop-Mon')
        self.lb_PwrFwdTop.showUnits = True
        self.lb_PwrRevTop = PyDMLabel(self, 'BO-05D:RF-P5Cav:PwrRevTop-Mon')
        self.lb_PwrRevTop.showUnits = True
        self.lb_C3PwrTop = PyDMLabel(self, 'BO-05D:RF-P5Cav:Cell3PwrTop-Mon')
        self.lb_C3PwrTop.showUnits = True
        self.lb_C3PhsTop = PyDMLabel(self, 'BR-RF-DLLRF-01:TOP:CELL3:PHS')
        self.lb_C3PhsTop.showUnits = True

        lay = QGridLayout()
        lay.setVerticalSpacing(15)
        lay.addWidget(QLabel('<h4>Bottom</h4>', self,
                             alignment=Qt.AlignCenter), 1, 1)
        lay.addWidget(QLabel('<h4>Top</h4>', self,
                             alignment=Qt.AlignCenter), 1, 2)
        lay.addWidget(QLabel('<h4>Power Fwd.</h4>', self,
                             alignment=Qt.AlignCenter), 2, 0)
        lay.addWidget(QLabel('<h4>Power Rev.</h4>', self,
                             alignment=Qt.AlignCenter), 3, 0)
        lay.addWidget(QLabel('<h4>Cavity Power</h4>', self,
                             alignment=Qt.AlignCenter), 4, 0)
        lay.addWidget(QLabel('<h4>Phase</h4>', self,
                             alignment=Qt.AlignCenter), 5, 0)
        lay.addWidget(self.lb_PwrFwdBot, 2, 1)
        lay.addWidget(self.lb_PwrRevBot, 3, 1)
        lay.addWidget(self.lb_C3PwrBot, 4, 1)
        lay.addWidget(self.lb_C3PhsBot, 5, 1)
        lay.addWidget(self.lb_PwrFwdTop, 2, 2)
        lay.addWidget(self.lb_PwrRevTop, 3, 2)
        lay.addWidget(self.lb_C3PwrTop, 4, 2)
        lay.addWidget(self.lb_C3PhsTop, 5, 2)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed), 6, 0)
        lay.addWidget(self.ramp_graph, 7, 0, 1, 3)
        lay.addLayout(hbox_rb, 8, 0, 1, 3)
        lay.addItem(
            QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Expanding), 9, 0)
        return lay

    def _autoStartLayout(self):
        self.bt_autostart = PyDMStateButton(self, 'BR-RF-DLLRF-01:AUTOSTART:S')
        self.led_autostart = SiriusLedState(self, 'BR-RF-DLLRF-01:AUTOSTART')
        hl_autostart = QHBoxLayout()
        hl_autostart.setAlignment(Qt.AlignLeft)
        hl_autostart.addWidget(self.bt_autostart)
        hl_autostart.addWidget(self.led_autostart)

        self.cb_comstart = PyDMEnumComboBox(self, 'BR-RF-DLLRF-01:COMMSTART:S')
        self.cb_comstart.setStyleSheet('min-width: 15em; max-width: 15em;')

        self.lb_statestart = PyDMLabel(self, 'BR-RF-DLLRF-01:STATESTART')
        self.lb_statestart.setStyleSheet(
            'qproperty-alignment: AlignLeft; min-width:15em; max-width:15em;')

        self.led_startok = PyDMLedMultiChannel(
            self, {'BR-RF-DLLRF-01:EPS': 0,
                   'BR-RF-DLLRF-01:FIM': 0,
                   'BR-RF-DLLRF-01:TXREADY': 1,
                   'BR-RF-DLLRF-01:FASTILK': 0})

        self.led_tuneok = PyDMLedMultiChannel(
            self, {'BR-RF-DLLRF-01:TUNE:FWDMIN': 1})

        self.led_closeloopok = PyDMLedMultiChannel(
            self, {'BR-RF-DLLRF-01:SL:FWDMIN': 1,
                   'BR-RF-DLLRF-01:FL:FWDMIN': 1,
                   'BR-RF-DLLRF-01:AL:FWDMIN': 1,
                   'BR-RF-DLLRF-01:PL:FWDMIN': 1})

        lay = QFormLayout()
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignLeft)
        lay.addRow(QLabel('<h3> • Commands</h3>', self))
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow('Enable: ', hl_autostart)
        lay.addRow('Command: ', self.cb_comstart)
        lay.addRow('Current State:', self.lb_statestart)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow(QLabel('<h3> • Statuses</h3>', self))
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow('Auto Start Beginning Ok: ', self.led_startok)
        lay.addRow('Auto Tuning Ok: ', self.led_tuneok)
        lay.addRow('Auto Close Loops Ok: ', self.led_closeloopok)
        return lay

    def _powerMeterLayout(self):
        lay_vals = QGridLayout()
        lay_vals.setAlignment(Qt.AlignTop)
        lay_vals.setHorizontalSpacing(15)
        lay_vals.setVerticalSpacing(6)
        lay_vals.addWidget(
            QLabel('<h4>Channel</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        self.cb_units = QComboBox(self)
        self.cb_units.setStyleSheet('font-weight: bold;')
        self.cb_units.addItems(['W', 'dBm'])
        self.cb_units.currentTextChanged.connect(
            self._handle_pwrdata_visibility)
        lay_vals.addWidget(self.cb_units, 0, 2)

        self.pwr_mon_graph = SiriusTimePlot(self)
        self.pwr_mon_graph.autoRangeX = True
        self.pwr_mon_graph.autoRangeY = True
        self.pwr_mon_graph.backgroundColor = QColor(255, 255, 255)
        self.pwr_mon_graph.showXGrid = True
        self.pwr_mon_graph.showYGrid = True
        self.pwr_mon_graph.timeSpan = 1800
        self.pwr_mon_graph.maxRedrawRate = 1
        self.pwr_mon_graph.setObjectName('pwrmon_graph')
        self.pwr_mon_graph.setStyleSheet(
            '#pwrmon_graph{min-width: 21em; min-height: 18em;}')

        data = self.chs['PwrMtr']

        self._pm_dBm_labels = set()
        self._pm_W_labels = set()
        for idx, curve_data in enumerate(data):
            name, wch, dbch, color = curve_data
            row = idx+1

            # Table
            cb = QCheckBox(self)
            cond = True if self.section == 'BO' else 'Coup' in name
            cb.setChecked(cond)
            cb.setObjectName(name)
            cb.setStyleSheet('color:'+color+'; max-width: 1.2em;')
            cb.stateChanged.connect(self._handle_curves_visibility)

            lb_desc = QLabel(name, self)
            lb_desc.setStyleSheet(
                'min-height: 1.5em; color:'+color+'; max-width: 8em;'
                'qproperty-alignment: AlignCenter;')

            lb_dbmpwr = PyDMLabel(self, dbch)
            lb_dbmpwr.showUnits = True
            lb_dbmpwr.setVisible(False)
            self._pm_dBm_labels.add(lb_dbmpwr)

            lb_wpwr = PyDMLabel(self, wch)
            lb_wpwr.showUnits = True
            self._pm_W_labels.add(lb_wpwr)

            lay_vals.addWidget(cb, row, 0)
            lay_vals.addWidget(lb_desc, row, 1)
            lay_vals.addWidget(lb_dbmpwr, row, 2)
            lay_vals.addWidget(lb_wpwr, row, 2)

            # Graph
            self.pwr_mon_graph.addYChannel(
                y_channel=dbch, name=name+' dBm', color=color,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves[name+' dBm'] = self.pwr_mon_graph.curveAtIndex(2*idx)
            self.pwr_mon_graph.addYChannel(
                y_channel=wch, name=name+' W', color=color,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves[name+' W'] = \
                self.pwr_mon_graph.curveAtIndex(2*idx+1)

        if self.section == 'BO':
            for name, _, _, _ in data:
                self.curves[name+' dBm'].setVisible(False)

            lb_CavPhs = QLabel('Phase', self, alignment=Qt.AlignCenter)
            self.lb_CavPhs = PyDMLabel(self, 'BR-RF-DLLRF-01:CAV:PHS')
            self.lb_CavPhs.showUnits = True
            lay_vals.addWidget(lb_CavPhs, 5, 1, alignment=Qt.AlignCenter)
            lay_vals.addWidget(self.lb_CavPhs, 5, 2)
        else:
            for name, _, _, _ in data:
                if 'Coup' not in name:
                    self.curves[name+' dBm'].setVisible(False)
                    self.curves[name+' W'].setVisible(False)
                else:
                    self.curves[name+' dBm'].setVisible(False)

        lay = QGridLayout()
        lay.setHorizontalSpacing(25)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay.addLayout(lay_vals, 2, 0)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed), 3, 0)
        lay.addWidget(self.pwr_mon_graph, 4, 0)
        lay.addItem(QSpacerItem(
            0, 10, QSzPlcy.Ignored, QSzPlcy.MinimumExpanding), 5, 0)
        return lay

    def _graphsLayout(self):
        # Temperatures
        self.temp_wid = QWidget()
        self.temp_wid.setStyleSheet("""
            #tempcell_graph, #tempcoup_graph, #tempcirc_graph{
                min-width: 26em; min-height: 10.5em; max-height: 10.5em;}
            QTabWidget::pane{
                border-bottom: 2px solid gray;}
        """)

        lb_temp = QLabel('<h3>Temperatures [°C]</h3>', self)
        self.temp_tab = QTabWidget(self)
        self.temp_tab.setObjectName(self.section+'Tab')
        self.temp_tab.setContentsMargins(0, 0, 0, 0)

        lay_temp = QVBoxLayout(self.temp_wid)
        lay_temp.setSpacing(4)
        lay_temp.addWidget(lb_temp)
        lay_temp.addWidget(self.temp_tab)
        lay_temp.setStretch(0, 1)
        lay_temp.setStretch(0, 10)

        # Cavity
        # # Cells
        lb_tempcell = QLabel('<h3> • Cell</h3>', self)
        self.led_tempcellok = PyDMLedMultiChannel(self)
        hbox_tempcell_state = QHBoxLayout()
        hbox_tempcell_state.addWidget(lb_tempcell, alignment=Qt.AlignLeft)
        hbox_tempcell_state.addWidget(
            self.led_tempcellok, alignment=Qt.AlignRight)

        self.tempcell_graph = SiriusTimePlot(self)
        self.tempcell_graph.setObjectName('tempcell_graph')
        self.tempcell_graph.autoRangeX = True
        self.tempcell_graph.autoRangeY = True
        self.tempcell_graph.backgroundColor = QColor(255, 255, 255)
        self.tempcell_graph.showXGrid = True
        self.tempcell_graph.showYGrid = True
        self.tempcell_graph.timeSpan = 1800
        self.tempcell_graph.maxRedrawRate = 2
        hbox_cbs = QHBoxLayout()

        for idx in range(len(self.chs['Cav Sts']['Temp']['Cells'])):
            cid = 'Cell ' + str(idx + 1)
            ch = self.chs['Cav Sts']['Temp']['Cells'][idx][0]
            color = self.chs['Cav Sts']['Temp']['Cells'][idx][1]

            self.tempcell_graph.addYChannel(
                y_channel=ch, name=cid, color=color,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves[cid] = self.tempcell_graph.curveAtIndex(idx)

            cb = QCheckBox(cid, self)
            cb.setChecked(True)
            cb.setObjectName(cid)
            cb.setStyleSheet('color:'+color+';')
            cb.stateChanged.connect(self._handle_curves_visibility)
            hbox_cbs.addWidget(cb)

        pen = mkPen(color='k', width=2, style=Qt.DashLine)
        self.line_cell_maxlim = InfiniteLine(angle=0, pen=pen)
        self.line_cell_minlim = InfiniteLine(angle=0, pen=pen)
        self.tempcell_graph.addItem(self.line_cell_maxlim)
        self.tempcell_graph.addItem(self.line_cell_minlim)

        # # Coupler
        lb_tempcoup = QLabel('<h3> • Coupler</h3>', self)
        self.led_tempcoupok = PyDMLedMultiChannel(self)
        hbox_tempcoup_state = QHBoxLayout()
        hbox_tempcoup_state.addWidget(lb_tempcoup, alignment=Qt.AlignLeft)
        hbox_tempcoup_state.addWidget(
            self.led_tempcoupok, alignment=Qt.AlignRight)

        self.tempcoup_graph = SiriusTimePlot(self)
        self.tempcoup_graph.setObjectName('tempcoup_graph')
        self.tempcoup_graph.autoRangeX = True
        self.tempcoup_graph.autoRangeY = True
        self.tempcoup_graph.backgroundColor = QColor(255, 255, 255)
        self.tempcoup_graph.showXGrid = True
        self.tempcoup_graph.showYGrid = True
        self.tempcoup_graph.timeSpan = 1800
        self.tempcoup_graph.maxRedrawRate = 2

        self.tempcoup_graph.addYChannel(
            y_channel=self.chs['Cav Sts']['Temp']['Coupler'][0],
            color=self.chs['Cav Sts']['Temp']['Coupler'][1],
            name='Coupler', lineStyle=Qt.SolidLine, lineWidth=1)
        self.curves['Coupler'] = self.tempcoup_graph.curveAtIndex(0)
        self.line_coup_maxlim = InfiniteLine(angle=0, pen=pen)
        self.line_coup_minlim = InfiniteLine(angle=0, pen=pen)
        self.tempcoup_graph.addItem(self.line_coup_maxlim)
        self.tempcoup_graph.addItem(self.line_coup_minlim)

        self.cavtemp_wid = QWidget()
        lay_cavtemp = QVBoxLayout(self.cavtemp_wid)
        lay_cavtemp.setAlignment(Qt.AlignTop)
        lay_cavtemp.setContentsMargins(0, 0, 0, 9)
        lay_cavtemp.addLayout(hbox_tempcell_state)
        lay_cavtemp.addWidget(self.tempcell_graph)
        lay_cavtemp.addLayout(hbox_cbs)
        lay_cavtemp.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay_cavtemp.addLayout(hbox_tempcoup_state)
        lay_cavtemp.addWidget(self.tempcoup_graph)

        self.temp_tab.addTab(self.cavtemp_wid, 'Cavity')

        # Transm.Line Temperatures
        lb_tempcirc = QLabel('<h3> • Circulator</h3>', self)
        lims_circ = self.chs['TL Sts']['Circ Limits']
        self.led_tempcircok = PyDMLedMultiChannel(
            self, {self.chs['TL Sts']['Circ TIn']: {
                    'comp': 'wt', 'value': lims_circ},
                   self.chs['TL Sts']['Circ TOut']: {
                    'comp': 'wt', 'value': lims_circ}})
        hbox_tempcirc_state = QHBoxLayout()
        hbox_tempcirc_state.addWidget(lb_tempcirc, alignment=Qt.AlignLeft)
        hbox_tempcirc_state.addWidget(
            self.led_tempcircok, alignment=Qt.AlignRight)

        self.tempcirc_graph = SiriusTimePlot(self)
        self.tempcirc_graph.setObjectName('tempcirc_graph')
        self.tempcirc_graph.autoRangeX = True
        self.tempcirc_graph.autoRangeY = True
        self.tempcirc_graph.backgroundColor = QColor(255, 255, 255)
        self.tempcirc_graph.showXGrid = True
        self.tempcirc_graph.showYGrid = True
        self.tempcirc_graph.timeSpan = 1800
        self.tempcirc_graph.maxRedrawRate = 1
        self.tempcirc_graph.addYChannel(
            y_channel=self.chs['TL Sts']['Circ TIn'], name='CTIn',
            color='magenta', lineStyle=Qt.SolidLine, lineWidth=1)
        self.tempcirc_graph.addYChannel(
            y_channel=self.chs['TL Sts']['Circ TOut'], name='CTOut',
            color='darkRed', lineStyle=Qt.SolidLine, lineWidth=1)

        self.line_circ_maxlim = InfiniteLine(
            pos=lims_circ[1], angle=0, pen=pen)
        self.line_circ_minlim = InfiniteLine(
            pos=lims_circ[0], angle=0, pen=pen)
        self.tempcirc_graph.addItem(self.line_circ_maxlim)
        self.tempcirc_graph.addItem(self.line_circ_minlim)

        self.trltemp_wid = QWidget()
        lay_trltemp = QVBoxLayout(self.trltemp_wid)
        lay_trltemp.setAlignment(Qt.AlignTop)
        lay_trltemp.setContentsMargins(0, 0, 0, 9)
        lay_trltemp.addLayout(hbox_tempcirc_state)
        lay_trltemp.addWidget(self.tempcirc_graph)

        self.temp_tab.addTab(self.trltemp_wid, 'Transm. Line')

        # Vacuum
        lb_vacuum = QLabel('<h3>Vacuum: Pressure [mBar]</h3>', self)
        self.led_condrun = PyDMLed(self)
        self.led_condrun.setToolTip('Conditioning acting')
        self.led_condrun.channel = (self.chs['Cav Sts']['Vac']['Cond'])
        self.led_condrun.offColor = QColor(128, 77, 0)
        self.led_condrun.onColor = PyDMLed.Yellow
        hbox_vacuum_state = QHBoxLayout()
        hbox_vacuum_state.addWidget(lb_vacuum, alignment=Qt.AlignLeft)
        hbox_vacuum_state.addWidget(self.led_condrun, alignment=Qt.AlignRight)

        self.vacuum_graph = SiriusTimePlot(self)
        self.vacuum_graph.setObjectName('vacuum_graph')
        self.vacuum_graph.autoRangeX = True
        self.vacuum_graph.autoRangeY = True
        self.vacuum_graph.backgroundColor = QColor(255, 255, 255)
        self.vacuum_graph.showXGrid = True
        self.vacuum_graph.showYGrid = True
        self.vacuum_graph.timeSpan = 1800
        self.vacuum_graph.maxRedrawRate = 1
        self.vacuum_graph.addYChannel(
            y_channel=self.chs['Cav Sts']['Vac']['Cells'], name='Vacuum',
            color='black', lineStyle=Qt.SolidLine, lineWidth=1)

        self.vac_wid = QWidget()
        self.vac_wid.setStyleSheet("""
            #vacuum_graph{
                min-width: 30em; min-height: 10.5em; max-height: 10.5em;}
        """)
        lay_vac = QVBoxLayout(self.vac_wid)
        lay_vac.setAlignment(Qt.AlignTop)
        lay_vac.addLayout(hbox_vacuum_state)
        lay_vac.addWidget(self.vacuum_graph)

        lay = QGridLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.temp_wid, 0, 0)
        lay.addWidget(self.vac_wid, 1, 0)
        lay.setRowStretch(0, 7)
        lay.setRowStretch(1, 3)
        return lay

    def _create_vlay(self, widget1, widget2):
        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        lay.addWidget(widget1)
        lay.addWidget(widget2, alignment=Qt.AlignCenter)
        return lay

    def _create_ssa_wid(self, lay_amp, row, chs_dict):
        led_sts = SiriusLedState(self, chs_dict['Status'])
        lay_amp.addWidget(led_sts, row, 1)

        lb_name = QLabel('<h4>'+chs_dict['Name']+'</h4>', self,
                         alignment=Qt.AlignLeft)
        lay_amp.addWidget(lb_name, row, 2)

        lb_pwr = PyDMLabel(self, chs_dict['Power'])
        lb_pwr.showUnits = True
        lb_pwr.setStyleSheet('min-width: 6em; max-width: 6em;')
        lay_amp.addWidget(lb_pwr, row, 3)

        bt_src1 = RFEnblDsblButton(
            parent=self,
            channels={
                'on': chs_dict['SRC 1']['PV'].replace('-Sts', 'Enbl-Sel'),
                'off': chs_dict['SRC 1']['PV'].replace('-Sts', 'Dsbl-Sel')})
        if self.section == 'BO':
            ch2vals = {
                'BO-ToBO:RF-ACDCPanel:300Vdc-Mon': {'comp': 'gt',
                                                    'value': 280.0},
                chs_dict['SRC 1']['PV']: 1}
            led_src1 = PyDMLedMultiChannel(self, ch2vals)
        else:
            led_src1 = SiriusLedState(self, chs_dict['SRC 1']['PV'])
        lay_amp.addLayout(self._create_vlay(bt_src1, led_src1), row, 4)

        bt_src2 = RFEnblDsblButton(
            parent=self,
            channels={
                'on': chs_dict['SRC 2']['PV'].replace('-Sts', 'Enbl-Sel'),
                'off': chs_dict['SRC 2']['PV'].replace('-Sts', 'Dsbl-Sel')})
        led_src2 = SiriusLedState(self, chs_dict['SRC 2']['PV'])
        lay_amp.addLayout(self._create_vlay(bt_src2, led_src2), row, 5)

        bt_pinsw = RFEnblDsblButton(
            parent=self,
            channels={
                'on': chs_dict['PinSw'].replace('-Mon', 'Enbl-Cmd'),
                'off': chs_dict['PinSw'].replace('-Mon', 'Dsbl-Cmd')})
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "ch[0] < 3.0", "channels": [' +
            '{"channel": "'+chs_dict['PreDrive']+'", "trigger": true}]}]')
        bt_pinsw.pb_on.rules = rules
        led_pinsw = SiriusLedState(self, chs_dict['PinSw'])
        lay_amp.addLayout(self._create_vlay(bt_pinsw, led_pinsw), row, 6)

        lb_drive = PyDMLabel(self, chs_dict['PreDrive'])
        lb_drive.showUnits = True
        led_drive = PyDMLedMultiChannel(
            parent=self, channels2values={
                chs_dict['PreDrive']: {'comp': 'lt', 'value': 3}})
        lay_amp.addLayout(self._create_vlay(lb_drive, led_drive), row, 7)

        ch_pinsw = SiriusConnectionSignal(chs_dict['PinSw'])
        ch_pinsw.new_value_signal[int].connect(
            _part(self._handle_predrive_led_channels, led_drive, chs_dict))

    def _handle_pwrdata_visibility(self, text):
        for lb in self._pm_dBm_labels:
            lb.setVisible(text == 'dBm')
        for lb in self._pm_W_labels:
            lb.setVisible(text == 'W')

        pwr_names = [data[0] for data in self.chs['PwrMtr']]
        for name in pwr_names:
            cb = self.findChild(QCheckBox, name)
            visi = cb.isChecked()
            curvedBm = self.curves[name + ' dBm']
            curveW = self.curves[name + ' W']
            if text == 'dBm':
                curvedBm.setVisible(visi)
                curveW.setVisible(False)
            else:
                curvedBm.setVisible(False)
                curveW.setVisible(visi)

    def _handle_curves_visibility(self, state):
        name = self.sender().objectName()
        pwr_names = [data[0] for data in self.chs['PwrMtr']]
        if name in pwr_names:
            name += (' W' if self.cb_units.currentText() == 'W' else ' dBm')
        curve = self.curves[name]
        curve.setVisible(state)

    def _handle_predrive_led_channels(self, led_drive, chs_dict, value):
        val = 100 if value == 1 else 3
        ch2vals = {chs_dict['PreDrive']: {'comp': 'lt', 'value': val}}
        led_drive.set_channels2values(ch2vals)

    def _handle_rmpwfm_visibility(self, index):
        self.curve_PwrMtr.setVisible(index == 0)
        self.curve_VGav.setVisible(index == 1)
        self.curve_Pwr.setVisible(index == 2)

    def _update_temp_limits(self, value):
        address = self.sender().address
        if 'Coup' in address:
            if 'Lower' in address:
                self.chs['Cav Sts']['Temp']['Coupler Limits'][0] = value
            else:
                self.chs['Cav Sts']['Temp']['Coupler Limits'][1] = value

            lims = self.chs['Cav Sts']['Temp']['Coupler Limits']
            ch2vals = {self.chs['Cav Sts']['Temp']['Coupler'][0]: {
                       'comp': 'wt', 'value': lims}}
            self.led_tempcellok.set_channels2values(ch2vals)
            self.line_coup_minlim.setPos(lims[0])
            self.line_coup_maxlim.setPos(lims[1])
        else:
            if 'Lower' in address:
                self.chs['Cav Sts']['Temp']['Cells Limits'][0] = value
            else:
                self.chs['Cav Sts']['Temp']['Cells Limits'][1] = value

            lims = self.chs['Cav Sts']['Temp']['Cells Limits']
            ch2vals = {c[0]: {'comp': 'wt', 'value': lims}
                       for c in self.chs['Cav Sts']['Temp']['Cells']}
            self.led_tempcoupok.set_channels2values(ch2vals)
            self.line_cell_minlim.setPos(lims[0])
            self.line_cell_maxlim.setPos(lims[1])
