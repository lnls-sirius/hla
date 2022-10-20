"""RF Main Control window."""

from functools import partial as _part
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QFormLayout, QHBoxLayout, QVBoxLayout,\
    QComboBox, QGroupBox, QTabWidget, QLabel, QCheckBox, QSpacerItem, QWidget,\
    QSizePolicy as QSzPlcy, QPushButton, QRadioButton
from qtpy.QtGui import QColor
import qtawesome as qta
from pyqtgraph import InfiniteLine, mkPen

from pydm.widgets import PyDMLineEdit, PyDMEnumComboBox

from ..widgets import SiriusMainWindow, PyDMStateButton, PyDMLed, \
    SiriusLedAlert, SiriusLedState, PyDMLedMultiChannel, SiriusTimePlot, \
    SiriusConnectionSignal, SiriusPushButton, SiriusLabel, \
    SiriusWaveformPlot, SiriusSpinbox
from ..util import connect_window, get_appropriate_color
from .details import TransmLineStatusDetails, CavityStatusDetails, \
    LLRFInterlockDetails, TempMonitor
from .custom_widgets import RFEnblDsblButton
from .util import SEC_2_CHANNELS


class RFMainControl(SiriusMainWindow):
    """RF Control Overview Window."""

    def __init__(self, parent=None, prefix='', section=''):
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section.upper()
        self.chs = SEC_2_CHANNELS[self.section]
        for group in ['Coupler', 'Cells']:
            key = group+' Limits PVs'
            for pvn in self.chs['Cav Sts']['Temp'][key]:
                channel = SiriusConnectionSignal(self.prefix+pvn)
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
        cwid = QWidget(self)
        self.setCentralWidget(cwid)

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
            wid_cw = QWidget(self)
            wid_cw.setLayout(self._powerMeterLayout())
            wid_pwrmon.addTab(wid_cw, 'CW')
            wid_rampmon = QWidget(self)
            wid_rampmon.setLayout(self._rampMonLayout())
            wid_pwrmon.addTab(wid_rampmon, 'Ramp')

        gbox_graphs = QGroupBox('Graphs', self)
        gbox_graphs.setLayout(self._graphsLayout())

        lay = QGridLayout(cwid)
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
            QSpinBox, QPushButton, PyDMEnumComboBox{
                min-width:5em; max-width:5em;
            }
            PyDMLineEdit, SiriusSpinbox{
                min-width:7em; max-width:7em;
            }
            PyDMStateButton{
                min-width: 2.58em;
            }
            SiriusLabel{
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
        self.led_emerg = SiriusLedAlert(
            self, self.prefix+self.chs['Emergency'])

        # # Sirius Interlock
        self.ld_siriusintlk = QLabel(
            'Sirius Interlock', self, alignment=Qt.AlignRight)
        self.led_siriusintlk = SiriusLedAlert(
            self, self.prefix+self.chs['Sirius Intlk'])

        # # LLRF Interlock
        self.ld_intlk = QLabel('LLRF Interlock', self, alignment=Qt.AlignRight)
        self.led_intlk = SiriusLedAlert(
            self, self.prefix+self.chs['LLRF Intlk'])
        self.pb_intlkdtls = QPushButton(qta.icon('fa5s.ellipsis-v'), '', self)
        self.pb_intlkdtls.setObjectName('dtls')
        self.pb_intlkdtls.setStyleSheet(
            '#dtls{min-width:18px;max-width:18px;icon-size:20px;}')
        connect_window(self.pb_intlkdtls, LLRFInterlockDetails, parent=self,
                       section=self.section, prefix=self.prefix)
        hlay_intlksts = QHBoxLayout()
        hlay_intlksts.addWidget(self.led_intlk)
        hlay_intlksts.addWidget(self.pb_intlkdtls)

        # Status
        self._ld_stats = QLabel(
            '<h4>Status</h4>', self, alignment=Qt.AlignLeft)

        # # Status Cavity
        self.ld_cavsts = QLabel('Cavity', self, alignment=Qt.AlignRight)
        self.led_cavsts = PyDMLedMultiChannel(
            self, {self.prefix+self.chs['Cav Sts']['Geral']: 1})
        self.pb_cavdtls = QPushButton(qta.icon('fa5s.ellipsis-v'), '', self)
        self.pb_cavdtls.setObjectName('dtls')
        self.pb_cavdtls.setStyleSheet(
            '#dtls{min-width:18px;max-width:18px;icon-size:20px;}')
        connect_window(self.pb_cavdtls, CavityStatusDetails, parent=self,
                       section=self.section, prefix=self.prefix)
        hlay_cavsts = QHBoxLayout()
        hlay_cavsts.addWidget(self.led_cavsts)
        hlay_cavsts.addWidget(self.pb_cavdtls)

        # # Status Transmission Line
        self.ld_tlsts = QLabel('Transm. Line', self, alignment=Qt.AlignRight)
        self.led_tlsts = PyDMLedMultiChannel(
            self, {self.prefix+self.chs['TL Sts']['Geral']: 1})
        self.pb_tldtls = QPushButton(qta.icon('fa5s.ellipsis-v'), '', self)
        self.pb_tldtls.setObjectName('dtls')
        self.pb_tldtls.setStyleSheet(
            '#dtls{min-width:18px;max-width:18px;icon-size:20px;}')
        connect_window(self.pb_tldtls, TransmLineStatusDetails, parent=self,
                       section=self.section, prefix=self.prefix)
        hlay_tlsts = QHBoxLayout()
        hlay_tlsts.addWidget(self.led_tlsts)
        hlay_tlsts.addWidget(self.pb_tldtls)

        # Reset
        self._ld_reset = QLabel('<h4>Reset</h4>', self, alignment=Qt.AlignLeft)

        # # Reset Global
        self.ld_globreset = QLabel(
            'Reset Global', self, alignment=Qt.AlignRight)
        self.pb_globreset = SiriusPushButton(
            label='', icon=qta.icon('fa5s.sync'), releaseValue=0,
            parent=self, init_channel=self.prefix+self.chs['Reset']['Global'])
        self.pb_globreset.setObjectName('pb_globreset')
        self.pb_globreset.setStyleSheet(
            '#pb_globreset{min-width:25px; max-width:25px; icon-size:20px;}')

        # # Reset LLRF
        self.ld_llrfreset = QLabel('Reset LLRF', self, alignment=Qt.AlignRight)
        self.pb_llrfreset = SiriusPushButton(
            label='', icon=qta.icon('fa5s.sync'), releaseValue=0,
            parent=self, init_channel=self.prefix+self.chs['Reset']['LLRF'])
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
        # self.bt_genenbl = PyDMStateButton(
        #    self, self.prefix+'RF-Gen:GeneralRF-Sel')
        self.lb_genenbl = SiriusLedState(
            self, self.prefix+'RF-Gen:GeneralRF-Sts')

        # Frequência
        self.ld_genfreq = QLabel(
            'Frequency [Hz]', self, alignment=Qt.AlignCenter)
        self.le_genfreq = PyDMLineEdit(
            self, self.prefix+'RF-Gen:GeneralFreq-SP')
        self.le_genfreq.setStyleSheet('min-width:7em; max-width:7em;')
        self.le_genfreq.precisionFromPV = False
        self.le_genfreq.precision = 2
        self.lb_genfreq = SiriusLabel(
            self, self.prefix+'RF-Gen:GeneralFreq-RB')
        self.lb_genfreq.setStyleSheet(
            'min-width:7em; max-width:7em; qproperty-alignment:AlignLeft;')
        self.lb_genfreq.precisionFromPV = False
        self.lb_genfreq.precision = 2

        # Phase Continuous State
        self.ld_genphscont = QLabel(
            'Phase Cont.', self, alignment=Qt.AlignCenter)
        # self.bt_genphscont = PyDMStateButton(
        #    self, self.prefix+'RF-Gen:FreqPhsCont-Sel')
        self.lb_genphscont = SiriusLedState(
            self, self.prefix+'RF-Gen:FreqPhsCont-Sts')

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
            for k, val in self.chs['SSA'].items():
                self._create_ssa_wid(lay_amp, int(k)+1, val)

        # LLRF
        # # Slow Loop Control
        self.lb_slmode = SiriusLabel(self, self.prefix+self.chs['SL']['Mode'])
        self.led_slmode = PyDMLedMultiChannel(
            self, {self.prefix+self.chs['SL']['Mode']: 0})
        self.bt_slenbl = PyDMStateButton(
            self, self.prefix+self.chs['SL']['Enbl']+':S')
        self.led_slenbl = SiriusLedState(
            self, self.prefix+self.chs['SL']['Enbl'])

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

        self.cb_amp = QComboBox()
        self.cb_amp.addItems(['[mV]', '[V]'])
        self.cb_amp.setStyleSheet(
            'QComboBox{max-width: 3.8em; font-weight: bold;}')
        self.cb_amp.currentTextChanged.connect(
            self._handle_ampl_unit_visibility)
        self.sb_amp1 = SiriusSpinbox(
            self, self.prefix+self.chs['SL']['ASet'][0]+'-SP')
        self.sb_amp1.showStepExponent = False
        self.lb_amp1 = SiriusLabel(
            self, self.prefix+self.chs['SL']['ASet'][0]+'-RB')
        self.sb_amp2 = SiriusSpinbox(
            self, self.prefix+self.chs['SL']['ASet'][1]+'-SP')
        self.sb_amp2.showStepExponent = False
        self.sb_amp2.setVisible(False)
        self.lb_amp2 = SiriusLabel(
            self, self.prefix+self.chs['SL']['ASet'][1]+'-RB')
        self.lb_amp2.setVisible(False)
        self.cb_ampincrate = PyDMEnumComboBox(
            self, self.prefix+self.chs['SL']['AInc']+':S')
        self.lb_ampincrate = SiriusLabel(
            self, self.prefix+self.chs['SL']['AInc'])
        self.sb_phs = SiriusSpinbox(
            self, self.prefix+self.chs['SL']['PSet']+':S')
        self.sb_phs.showStepExponent = False
        self.lb_phs = SiriusLabel(
            self, self.prefix+self.chs['SL']['PSet'])
        self.cb_phsincrate = PyDMEnumComboBox(
            self, self.prefix+self.chs['SL']['PInc']+':S')
        self.lb_phsincrate = SiriusLabel(
            self, self.prefix+self.chs['SL']['PInc'])
        lay_slctrl = QGridLayout()
        lay_slctrl.setHorizontalSpacing(9)
        lay_slctrl.setVerticalSpacing(9)
        lay_slctrl.addWidget(QLabel('<h4>SP/RB</h4>', self,
                                    alignment=Qt.AlignCenter), 0, 2, 1, 2)
        lay_slctrl.addWidget(QLabel('<h4>Inc. Rate SP/RB</h4>', self,
                                    alignment=Qt.AlignCenter), 0, 4, 1, 2)
        lay_slctrl.addWidget(QLabel('<h4>Amplitude</h4>', self,
                                    alignment=Qt.AlignCenter), 1, 0)
        lay_slctrl.addWidget(self.cb_amp, 1, 1)
        lay_slctrl.addWidget(QLabel('<h4>Phase [DEG]</h4>', self,
                                    alignment=Qt.AlignCenter), 2, 0, 1, 2)
        lay_slctrl.addWidget(self.sb_amp1, 1, 2, alignment=Qt.AlignRight)
        lay_slctrl.addWidget(self.sb_amp2, 1, 2, alignment=Qt.AlignRight)
        lay_slctrl.addWidget(self.lb_amp1, 1, 3, alignment=Qt.AlignLeft)
        lay_slctrl.addWidget(self.lb_amp2, 1, 3, alignment=Qt.AlignLeft)
        lay_slctrl.addWidget(self.cb_ampincrate, 1, 4, alignment=Qt.AlignRight)
        lay_slctrl.addWidget(self.lb_ampincrate, 1, 5, alignment=Qt.AlignLeft)
        lay_slctrl.addWidget(self.sb_phs, 2, 2, alignment=Qt.AlignRight)
        lay_slctrl.addWidget(self.lb_phs, 2, 3, alignment=Qt.AlignLeft)
        lay_slctrl.addWidget(self.cb_phsincrate, 2, 4, alignment=Qt.AlignRight)
        lay_slctrl.addWidget(self.lb_phsincrate, 2, 5, alignment=Qt.AlignLeft)

        self.lb_iref = SiriusLabel(self, self.prefix+self.chs['SL']['IRef'])
        self.lb_iref.showUnits = True
        self.lb_iinp = SiriusLabel(self, self.prefix+self.chs['SL']['IInp'])
        self.lb_iinp.showUnits = True
        self.lb_ierr = SiriusLabel(self, self.prefix+self.chs['SL']['IErr'])
        self.lb_ierr.showUnits = True
        self.lb_qref = SiriusLabel(self, self.prefix+self.chs['SL']['QRef'])
        self.lb_qref.showUnits = True
        self.lb_qinp = SiriusLabel(self, self.prefix+self.chs['SL']['QInp'])
        self.lb_qinp.showUnits = True
        self.lb_qerr = SiriusLabel(self, self.prefix+self.chs['SL']['QErr'])
        self.lb_qerr.showUnits = True
        self.lb_ampref = SiriusLabel(self, self.prefix+self.chs['SL']['ARef'])
        self.lb_ampref.showUnits = True
        self.lb_ampinp = SiriusLabel(self, self.prefix+self.chs['SL']['AInp'])
        self.lb_ampinp.showUnits = True
        self.lb_amperr = SiriusLabel(self, self.prefix+self.chs['SL']['AErr'])
        self.lb_amperr.showUnits = True
        self.lb_phsref = SiriusLabel(self, self.prefix+self.chs['SL']['PRef'])
        self.lb_phsref.showUnits = True
        self.lb_phsinp = SiriusLabel(self, self.prefix+self.chs['SL']['PInp'])
        self.lb_phsinp.showUnits = True
        self.lb_phserr = SiriusLabel(self, self.prefix+self.chs['SL']['PErr'])
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
        self.bt_autotun = PyDMStateButton(
            self, self.prefix+self.chs['Tun']['Auto']+':S')
        self.lb_autotun = SiriusLedState(
            self, self.prefix+self.chs['Tun']['Auto'])
        lb_dtune = QLabel('DTune: ', self, alignment=Qt.AlignRight)
        self.sb_dtune = SiriusSpinbox(
            self, self.prefix+self.chs['Tun']['DTune'].replace('RB', 'SP'))
        self.sb_dtune.showStepExponent = False
        self.lb_dtune = SiriusLabel(
            self, self.prefix+self.chs['Tun']['DTune'])
        self.lb_dtune.showUnits = True
        lb_dphase = QLabel('Dephase: ', self, alignment=Qt.AlignRight)
        self.lb_dphase = SiriusLabel(
            self, self.prefix+self.chs['Tun']['DPhase'])
        self.lb_dphase.showUnits = True
        lb_tunact = QLabel(
            'Acting: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.led_tunact = SiriusLedState(
            self, self.prefix+self.chs['Tun']['Acting'])
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
        lay_tunset.addWidget(lb_tunact, 4, 1)
        lay_tunset.addWidget(self.led_tunact, 4, 2, alignment=Qt.AlignCenter)
        lay_tunset.addItem(
            QSpacerItem(10, 0, QSzPlcy.Expanding, QSzPlcy.Ignored), 1, 4)

        # # # Plungers motors
        lb_plg1 = QLabel('Plunger 1')
        lb_plg2 = QLabel('Plunger 2')
        lb_down = QLabel('Down')
        lb_up = QLabel('Up')
        self.led_plg1_dn = PyDMLed(
            self, self.prefix+self.chs['Tun']['Pl1Down'])
        self.led_plg1_dn.offColor = QColor(64, 64, 64)
        self.led_plg1_dn.onColor = QColor('blue')
        self.led_plg1_dn.shape = PyDMLed.ShapeMap.Square
        self.led_plg1_up = PyDMLed(
            self, self.prefix+self.chs['Tun']['Pl1Up'])
        self.led_plg1_up.offColor = QColor(64, 64, 64)
        self.led_plg1_up.onColor = QColor('blue')
        self.led_plg1_up.shape = PyDMLed.ShapeMap.Square
        self.led_plg2_dn = PyDMLed(
            self, self.prefix+self.chs['Tun']['Pl2Down'])
        self.led_plg2_dn.offColor = QColor(64, 64, 64)
        self.led_plg2_dn.onColor = QColor('blue')
        self.led_plg2_dn.shape = PyDMLed.ShapeMap.Square
        self.led_plg2_up = PyDMLed(
            self, self.prefix+self.chs['Tun']['Pl2Up'])
        self.led_plg2_up.offColor = QColor(64, 64, 64)
        self.led_plg2_up.onColor = QColor('blue')
        self.led_plg2_up.shape = PyDMLed.ShapeMap.Square
        lay_plunmon = QGridLayout()
        lay_plunmon.addItem(
            QSpacerItem(10, 10, QSzPlcy.Expanding, QSzPlcy.Expanding), 0, 0)
        lay_plunmon.addWidget(lb_down, 1, 2)
        lay_plunmon.addWidget(lb_up, 1, 3)
        lay_plunmon.addWidget(lb_plg1, 2, 1)
        lay_plunmon.addWidget(lb_plg2, 3, 1)
        lay_plunmon.addWidget(self.led_plg1_dn, 2, 2)
        lay_plunmon.addWidget(self.led_plg1_up, 2, 3)
        lay_plunmon.addWidget(self.led_plg2_dn, 3, 2)
        lay_plunmon.addWidget(self.led_plg2_up, 3, 3)
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
            y_channel=self.prefix+self.chs['Tun']['PlM1Curr'], color='blue',
            name='Motor 1', lineStyle=Qt.SolidLine, lineWidth=1)
        self.graph_plunmotors.addYChannel(
            y_channel=self.prefix+self.chs['Tun']['PlM2Curr'], color='red',
            name='Motor 2', lineStyle=Qt.SolidLine, lineWidth=1)
        self.graph_plunmotors.setLabel('left', '')

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

        # # FieldFlatness settings
        pvs = self.chs['FFlat']
        lb2 = '6' if self.section == 'SI' else '4'
        lb_fflat = QLabel(
            '<h3> • Field Flatness</h3>', self, alignment=Qt.AlignLeft)
        lb_ffsts = QLabel('Acting: ', self, alignment=Qt.AlignRight)
        self.lb_ffsts = SiriusLedState(self, self.prefix+pvs['Sts'])
        lb_ffen = QLabel('Enable: ', self, alignment=Qt.AlignRight)
        self.bt_ffen = PyDMStateButton(self, self.prefix+pvs['Auto']+':S')
        self.lb_ffen = SiriusLedState(self, self.prefix+pvs['Auto'])
        lb_ffpos = QLabel('Position: ', self, alignment=Qt.AlignRight)
        self.bt_ffpos = PyDMStateButton(self, self.prefix+pvs['Pos']+':S')
        self.lb_ffpos = SiriusLedState(self, self.prefix+pvs['Pos'])
        lb_ffg1 = QLabel('Gain Cell 2: ', self, alignment=Qt.AlignRight)
        lb_ffg2 = QLabel(f'Gain Cell {lb2:s}: ', self, alignment=Qt.AlignRight)
        self.sb_ffg1 = SiriusSpinbox(self, self.prefix+pvs['Gain1']+':S')
        self.sb_ffg2 = SiriusSpinbox(self, self.prefix+pvs['Gain2']+':S')
        self.sb_ffg1.showStepExponent = False
        self.sb_ffg2.showStepExponent = False
        self.lb_ffg1 = SiriusLabel(self, self.prefix+pvs['Gain1'])
        self.lb_ffg2 = SiriusLabel(self, self.prefix+pvs['Gain2'])
        self.lb_ffg1.showUnits = True
        self.lb_ffg2.showUnits = True
        lb_ffdb = QLabel('DeadBand: ', self, alignment=Qt.AlignRight)
        self.sb_ffdb = SiriusSpinbox(self, self.prefix+pvs['Deadband']+':S')
        self.sb_ffdb.showStepExponent = False
        self.lb_ffdb = SiriusLabel(self, self.prefix+pvs['Deadband'])
        self.lb_ffdb.showUnits = True
        lb_ffcell1 = QLabel('Cell 2: ', self, alignment=Qt.AlignRight)
        self.lb_ffcell1 = SiriusLabel(self, self.prefix+pvs['Cell1'])
        self.lb_ffcell1.showUnits = True
        lb_ffcell2 = QLabel(f'Cell {lb2:s}: ', self, alignment=Qt.AlignRight)
        self.lb_ffcell2 = SiriusLabel(self, self.prefix+pvs['Cell2'])
        self.lb_ffcell2.showUnits = True
        lb_fferr = QLabel('Error: ', self, alignment=Qt.AlignRight)
        self.lb_fferr = SiriusLabel(self, self.prefix+pvs['Err'])
        self.lb_fferr.showUnits = True
        lay_fflat = QGridLayout()
        lay_fflat.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        lay_fflat.setVerticalSpacing(12)
        lay_fflat.addWidget(lb_fflat, 0, 0)
        lay_fflat.addWidget(lb_ffen, 1, 0)
        lay_fflat.addWidget(self.bt_ffen, 1, 1)
        lay_fflat.addWidget(self.lb_ffen, 1, 2)
        lay_fflat.addWidget(lb_ffpos, 2, 0)
        lay_fflat.addWidget(self.bt_ffpos, 2, 1)
        lay_fflat.addWidget(self.lb_ffpos, 2, 2)
        lay_fflat.addWidget(lb_ffg1, 3, 0)
        lay_fflat.addWidget(self.sb_ffg1, 3, 1)
        lay_fflat.addWidget(self.lb_ffg1, 3, 2)
        lay_fflat.addWidget(lb_ffg2, 4, 0)
        lay_fflat.addWidget(self.sb_ffg2, 4, 1)
        lay_fflat.addWidget(self.lb_ffg2, 4, 2)
        lay_fflat.addWidget(lb_ffdb, 5, 0)
        lay_fflat.addWidget(self.sb_ffdb, 5, 1)
        lay_fflat.addWidget(self.lb_ffdb, 5, 2)
        lay_fflat.addWidget(lb_ffcell1, 6, 0)
        lay_fflat.addWidget(self.lb_ffcell1, 6, 1)
        lay_fflat.addWidget(lb_ffcell2, 7, 0)
        lay_fflat.addWidget(self.lb_ffcell2, 7, 1)
        lay_fflat.addWidget(lb_fferr, 8, 0)
        lay_fflat.addWidget(self.lb_fferr, 8, 1)
        lay_fflat.addWidget(lb_ffsts, 9, 0)
        lay_fflat.addWidget(self.lb_ffsts, 9, 1, alignment=Qt.AlignCenter)
        wid_fflat = QWidget()
        wid_fflat.setLayout(lay_fflat)

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
        wid_llrf.addTab(wid_fflat, 'Field Flatness')

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
        self.bt_rmpenbl = PyDMStateButton(
            self, self.prefix+'BR-RF-DLLRF-01:RmpEnbl-Sel')
        self.lb_rmpenbl = SiriusLedState(
            self, self.prefix+'BR-RF-DLLRF-01:RmpEnbl-Sts')

        self.led_rmpready = PyDMLed(
            self, self.prefix+'BR-RF-DLLRF-01:RmpReady-Mon')
        self.led_rmpready.onColor = PyDMLed.LightGreen
        self.led_rmpready.offColor = PyDMLed.Red

        self.led_rmptrig = PyDMLed(
            self, self.prefix+'BR-RF-DLLRF-01:5HZTRIG')
        self.led_rmptrig.onColor = PyDMLed.LightGreen
        self.led_rmptrig.offColor = PyDMLed.Red

        self.cb_rmpincts = SiriusSpinbox(
            self, self.prefix+'BR-RF-DLLRF-01:RmpIncTs-SP')
        self.cb_rmpincts.showStepExponent = False
        self.lb_rmpincts = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:RmpIncTs-RB')
        self.lb_rmpincts.showUnits = True

        self.sb_rmpts1 = SiriusSpinbox(
            self, self.prefix+'BR-RF-DLLRF-01:RmpTs1-SP')
        self.sb_rmpts1.showStepExponent = False
        self.lb_rmpts1 = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:RmpTs1-RB')
        self.lb_rmpts1.showUnits = True
        self.sb_rmpts2 = SiriusSpinbox(
            self, self.prefix+'BR-RF-DLLRF-01:RmpTs2-SP')
        self.sb_rmpts2.showStepExponent = False
        self.lb_rmpts2 = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:RmpTs2-RB')
        self.lb_rmpts2.showUnits = True
        self.sb_rmpts3 = SiriusSpinbox(
            self, self.prefix+'BR-RF-DLLRF-01:RmpTs3-SP')
        self.sb_rmpts3.showStepExponent = False
        self.lb_rmpts3 = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:RmpTs3-RB')
        self.lb_rmpts3.showUnits = True
        self.sb_rmpts4 = SiriusSpinbox(
            self, self.prefix+'BR-RF-DLLRF-01:RmpTs4-SP')
        self.sb_rmpts4.showStepExponent = False
        self.lb_rmpts4 = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:RmpTs4-RB')
        self.lb_rmpts4.showUnits = True

        self.sb_rmpphstop = SiriusSpinbox(
            self, self.prefix+'BR-RF-DLLRF-01:RmpPhsTop-SP')
        self.sb_rmpphstop.showStepExponent = False
        self.lb_rmpphstop = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:RmpPhsTop-RB')
        self.lb_rmpphstop.showUnits = True
        self.ld_rmpphstop = QLabel('Amplitude', self, alignment=Qt.AlignRight)
        self.cb_rmpphstop = QComboBox()
        self.cb_rmpphstop.addItems(['[mV]', '[V]'])
        self.cb_rmpphstop.setStyleSheet('QComboBox{max-width: 3.5em;}')
        self.cb_rmpphstop.currentTextChanged.connect(
            self._handle_rmpampl_unit_visibility)
        lay_rmpphstopdesc = QHBoxLayout()
        lay_rmpphstopdesc.addWidget(self.ld_rmpphstop)
        lay_rmpphstopdesc.addWidget(self.cb_rmpphstop)
        lay_rmpphstopdesc.setAlignment(Qt.AlignRight)
        self.le_rmpvolttop1 = PyDMLineEdit(
            self, self.prefix+'BR-RF-DLLRF-01:mV:RAMP:AMP:TOP-SP')
        self.lb_rmpvolttop1 = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:mV:RAMP:AMP:TOP-RB')
        self.lb_rmpvolttop1.showUnits = True
        self.le_rmpvolttop2 = PyDMLineEdit(
            self, self.prefix+'RA-RaBO01:RF-LLRF:RmpAmpVCavTop-SP')
        self.le_rmpvolttop2.setVisible(False)
        self.lb_rmpvolttop2 = SiriusLabel(
            self, self.prefix+'RA-RaBO01:RF-LLRF:RmpAmpVCavTop-RB')
        self.lb_rmpvolttop2.setVisible(False)
        self.lb_rmpvolttop2.showUnits = True

        self.sb_rmpphsbot = SiriusSpinbox(
            self, self.prefix+'BR-RF-DLLRF-01:RmpPhsBot-SP')
        self.sb_rmpphsbot.showStepExponent = False
        self.lb_rmpphsbot = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:RmpPhsBot-RB')
        self.lb_rmpphsbot.showUnits = True
        self.ld_rmpphsbot = QLabel('Amplitude', self, alignment=Qt.AlignRight)
        self.cb_rmpphsbot = QComboBox()
        self.cb_rmpphsbot.addItems(['[mV]', '[V]'])
        self.cb_rmpphsbot.setStyleSheet('QComboBox{max-width: 3.5em;}')
        self.cb_rmpphsbot.currentTextChanged.connect(
            self._handle_rmpampl_unit_visibility)
        lay_rmpphsbotdesc = QHBoxLayout()
        lay_rmpphsbotdesc.addWidget(self.ld_rmpphsbot)
        lay_rmpphsbotdesc.addWidget(self.cb_rmpphsbot)
        lay_rmpphsbotdesc.setAlignment(Qt.AlignRight)
        self.le_rmpvoltbot1 = PyDMLineEdit(
            self, self.prefix+'BR-RF-DLLRF-01:mV:RAMP:AMP:BOT-SP')
        self.lb_rmpvoltbot1 = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:mV:RAMP:AMP:BOT-RB')
        self.lb_rmpvoltbot1.showUnits = True
        self.le_rmpvoltbot2 = PyDMLineEdit(
            self, self.prefix+'RA-RaBO01:RF-LLRF:RmpAmpVCavBot-SP')
        self.le_rmpvoltbot2.setVisible(False)
        self.lb_rmpvoltbot2 = SiriusLabel(
            self, self.prefix+'RA-RaBO01:RF-LLRF:RmpAmpVCavBot-RB')
        self.lb_rmpvoltbot2.setVisible(False)
        self.lb_rmpvoltbot2.showUnits = True

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(ctrls_label, 0, 0)
        lay.addItem(
            QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay.addWidget(QLabel('Enable: ', self,
                             alignment=Qt.AlignRight), 2, 0)
        lay.addWidget(self.bt_rmpenbl, 2, 1)
        lay.addWidget(self.lb_rmpenbl, 2, 2, alignment=Qt.AlignLeft)
        lay.addWidget(QLabel('Ramp Ready: ', self,
                             alignment=Qt.AlignRight), 3, 0)
        lay.addWidget(self.led_rmpready, 3, 1, alignment=Qt.AlignLeft)
        lay.addWidget(QLabel('Receiving trigger: ', self,
                             alignment=Qt.AlignRight), 4, 0)
        lay.addWidget(self.led_rmptrig, 4, 1, alignment=Qt.AlignLeft)
        lay.addItem(
            QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 5, 0)
        lay.addWidget(QLabel('<h4>Durations</h4>', self), 6, 0, 1, 3)
        lay.addWidget(QLabel('Bottom: ', self,
                             alignment=Qt.AlignRight), 7, 0)
        lay.addWidget(self.sb_rmpts1, 7, 1)
        lay.addWidget(self.lb_rmpts1, 7, 2)
        lay.addWidget(QLabel('Rampup: ', self,
                             alignment=Qt.AlignRight), 8, 0)
        lay.addWidget(self.sb_rmpts2, 8, 1)
        lay.addWidget(self.lb_rmpts2, 8, 2)
        lay.addWidget(QLabel('Top: ', self,
                             alignment=Qt.AlignRight), 9, 0)
        lay.addWidget(self.sb_rmpts3, 9, 1)
        lay.addWidget(self.lb_rmpts3, 9, 2)
        lay.addWidget(QLabel('Rampdown:', self,
                             alignment=Qt.AlignRight), 10, 0)
        lay.addWidget(self.sb_rmpts4, 10, 1)
        lay.addWidget(self.lb_rmpts4, 10, 2)
        lay.addWidget(QLabel('Ramp Inc. Rate: ', self,
                             alignment=Qt.AlignRight), 11, 0)
        lay.addWidget(self.cb_rmpincts, 11, 1)
        lay.addWidget(self.lb_rmpincts, 11, 2)
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 12, 0)
        lay.addWidget(QLabel('<h4>Bottom</h4>', self), 13, 0, 1, 3)
        lay.addWidget(QLabel('Phase', self,
                             alignment=Qt.AlignRight), 14, 0)
        lay.addWidget(self.sb_rmpphsbot, 14, 1)
        lay.addWidget(self.lb_rmpphsbot, 14, 2)
        lay.addLayout(lay_rmpphsbotdesc, 15, 0)
        lay.addWidget(self.le_rmpvoltbot1, 15, 1)
        lay.addWidget(self.le_rmpvoltbot2, 15, 1)
        lay.addWidget(self.lb_rmpvoltbot1, 15, 2)
        lay.addWidget(self.lb_rmpvoltbot2, 15, 2)
        lay.addWidget(QLabel('<h4>Top</h4>', self), 16, 0, 1, 3)
        lay.addWidget(QLabel('Phase', self,
                             alignment=Qt.AlignRight), 17, 0)
        lay.addWidget(self.sb_rmpphstop, 17, 1)
        lay.addWidget(self.lb_rmpphstop, 17, 2)
        lay.addLayout(lay_rmpphstopdesc, 18, 0)
        lay.addWidget(self.le_rmpvolttop1, 18, 1)
        lay.addWidget(self.le_rmpvolttop2, 18, 1)
        lay.addWidget(self.lb_rmpvolttop1, 18, 2)
        lay.addWidget(self.lb_rmpvolttop2, 18, 2)
        lay.addItem(QSpacerItem(
            200, 10, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding), 19, 3)
        return lay

    def _rampMonLayout(self):
        self.ramp_graph = SiriusWaveformPlot(
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
        self.ramp_graph.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        self.ramp_graph.plotItem.getAxis('left').setStyle(tickTextOffset=5)
        self.ramp_graph.addChannel(
            y_channel=self.prefix+'RA-RF:PowerSensor1:TracData-Mon',
            x_channel=self.prefix+'RA-RF:PowerSensor1:TimeAxis-Mon',
            redraw_mode=2, name='Power [W]', color=QColor('blue'))
        self.curve_pwrmtr = self.ramp_graph.curveAtIndex(0)
        self.rb_pwrmtr = QRadioButton('Power Meter Signal', self)
        self.rb_pwrmtr.setChecked(True)
        self.rb_pwrmtr.toggled.connect(
            _part(self._handle_rmpwfm_visibility, 0))
        self.ramp_graph.addChannel(
            y_channel=self.prefix+'BR-RF-DLLRF-01:VCavRampWf.AVAL',
            x_channel=self.prefix+'BR-RF-DLLRF-01:DiagWf32Scale.AVAL',
            redraw_mode=2, name='VGav kV', color=QColor('blue'))
        self.curve_vgav = self.ramp_graph.curveAtIndex(1)
        self.rb_vgav = QRadioButton('VGav [kV]', self)
        self.rb_vgav.toggled.connect(_part(self._handle_rmpwfm_visibility, 1))
        self.ramp_graph.addChannel(
            y_channel=self.prefix+'BR-RF-DLLRF-01:VCavRampWf:W.AVAL',
            x_channel=self.prefix+'BR-RF-DLLRF-01:DiagWf32Scale.AVAL',
            redraw_mode=2, name='Power [W]', color=QColor('blue'))
        self.curve_pwr = self.ramp_graph.curveAtIndex(2)
        self.ramp_graph.setLabel('left', '')
        self.rb_pwr = QRadioButton('Power [W]', self)
        self.rb_pwr.toggled.connect(_part(self._handle_rmpwfm_visibility, 2))
        hbox_rb = QHBoxLayout()
        hbox_rb.addWidget(self.rb_pwrmtr)
        hbox_rb.addWidget(self.rb_vgav)
        hbox_rb.addWidget(self.rb_pwr)

        self.curve_vgav.setVisible(False)
        self.curve_pwr.setVisible(False)

        self.lb_vgapdesc = QLabel(
            '<h4>Gap Voltage:</h4>', self, alignment=Qt.AlignCenter)

        self.lb_c3pwrbot = SiriusLabel(
            self, self.prefix+'BO-05D:RF-P5Cav:Cell3PwrBot-Mon')
        self.lb_c3pwrbot.showUnits = True
        self.lb_pwrfwdbot = SiriusLabel(
            self, self.prefix+'BO-05D:RF-P5Cav:PwrFwdBot-Mon')
        self.lb_pwrfwdbot.showUnits = True
        self.lb_pwrrevbot = SiriusLabel(
            self, self.prefix+'BO-05D:RF-P5Cav:PwrRevBot-Mon')
        self.lb_pwrrevbot.showUnits = True
        self.lb_c3phsbot = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:BOT:CELL3:PHS')
        self.lb_c3phsbot.showUnits = True
        self.lb_cavvgapbot = SiriusLabel(
            self, self.prefix+'BO-05D:RF-P5Cav:RmpAmpVCavBot-Mon')
        self.lb_cavvgapbot.showUnits = True

        self.lb_c3pwrtop = SiriusLabel(
            self, self.prefix+'BO-05D:RF-P5Cav:Cell3PwrTop-Mon')
        self.lb_c3pwrtop.showUnits = True
        self.lb_pwrfwdtop = SiriusLabel(
            self, self.prefix+'BO-05D:RF-P5Cav:PwrFwdTop-Mon')
        self.lb_pwrfwdtop.showUnits = True
        self.lb_pwrrevtop = SiriusLabel(
            self, self.prefix+'BO-05D:RF-P5Cav:PwrRevTop-Mon')
        self.lb_pwrrevtop.showUnits = True
        self.lb_c3phstop = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:TOP:CELL3:PHS')
        self.lb_c3phstop.showUnits = True
        self.lb_cavvgaptop = SiriusLabel(
            self, self.prefix+'BO-05D:RF-P5Cav:RmpAmpVCavTop-Mon')
        self.lb_cavvgaptop.showUnits = True

        lay = QGridLayout()
        lay.setVerticalSpacing(15)
        lay.addWidget(QLabel(
            '<h4>Bottom</h4>', self, alignment=Qt.AlignCenter), 1, 1)
        lay.addWidget(QLabel(
            '<h4>Top</h4>', self, alignment=Qt.AlignCenter), 1, 2)
        lay.addWidget(QLabel(
            '<h4>Cavity Power</h4>', self, alignment=Qt.AlignCenter), 2, 0)
        lay.addWidget(QLabel(
            '<h4>Power Fwd.</h4>', self, alignment=Qt.AlignCenter), 3, 0)
        lay.addWidget(QLabel(
            '<h4>Power Rev.</h4>', self, alignment=Qt.AlignCenter), 4, 0)
        lay.addWidget(QLabel(
            '<h4>Phase</h4>', self, alignment=Qt.AlignCenter), 5, 0)
        lay.addWidget(self.lb_vgapdesc, 6, 0)
        lay.addWidget(self.lb_c3pwrbot, 2, 1)
        lay.addWidget(self.lb_pwrfwdbot, 3, 1)
        lay.addWidget(self.lb_pwrrevbot, 4, 1)
        lay.addWidget(self.lb_c3phsbot, 5, 1)
        lay.addWidget(self.lb_cavvgapbot, 6, 1, alignment=Qt.AlignCenter)
        lay.addWidget(self.lb_c3pwrtop, 2, 2)
        lay.addWidget(self.lb_pwrfwdtop, 3, 2)
        lay.addWidget(self.lb_pwrrevtop, 4, 2)
        lay.addWidget(self.lb_c3phstop, 5, 2)
        lay.addWidget(self.lb_cavvgaptop, 6, 2, alignment=Qt.AlignCenter)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed), 7, 0)
        lay.addWidget(self.ramp_graph, 8, 0, 1, 3)
        lay.addLayout(hbox_rb, 9, 0, 1, 3)
        lay.addItem(
            QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Expanding), 10, 0)
        return lay

    def _autoStartLayout(self):
        self.bt_autostart = PyDMStateButton(
            self, self.prefix+'BR-RF-DLLRF-01:AUTOSTART:S')
        self.led_autostart = SiriusLedState(
            self, self.prefix+'BR-RF-DLLRF-01:AUTOSTART')
        hl_autostart = QHBoxLayout()
        hl_autostart.setAlignment(Qt.AlignLeft)
        hl_autostart.addWidget(self.bt_autostart)
        hl_autostart.addWidget(self.led_autostart)

        self.cb_comstart = PyDMEnumComboBox(
            self, self.prefix+'BR-RF-DLLRF-01:COMMSTART:S')
        self.cb_comstart.setStyleSheet('min-width: 15em; max-width: 15em;')

        self.lb_statestart = SiriusLabel(
            self, self.prefix+'BR-RF-DLLRF-01:STATESTART')
        self.lb_statestart.setStyleSheet(
            'qproperty-alignment: AlignLeft; min-width:15em; max-width:15em;')

        self.led_startok = PyDMLedMultiChannel(
            self, {self.prefix+'BR-RF-DLLRF-01:EPS': 0,
                   self.prefix+'BR-RF-DLLRF-01:FIM': 0,
                   self.prefix+'BR-RF-DLLRF-01:TXREADY': 1,
                   self.prefix+'BR-RF-DLLRF-01:FASTILK': 0})

        self.led_tuneok = PyDMLedMultiChannel(
            self, {self.prefix+'BR-RF-DLLRF-01:TUNE:FWDMIN': 1})

        self.led_closeloopok = PyDMLedMultiChannel(
            self, {self.prefix+'BR-RF-DLLRF-01:SL:FWDMIN': 1,
                   self.prefix+'BR-RF-DLLRF-01:FL:FWDMIN': 1,
                   self.prefix+'BR-RF-DLLRF-01:AL:FWDMIN': 1,
                   self.prefix+'BR-RF-DLLRF-01:PL:FWDMIN': 1})

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
        self.cb_units.addItems(['W', 'dBm', 'mV'])
        self.cb_units.setStyleSheet(
            'QComboBox{max-width: 3.5em; font-weight: bold;}')
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

        self._pm_labels = dict()
        self._pm_labels['dBm'] = list()
        self._pm_labels['W'] = list()
        self._pm_labels['mV'] = list()
        idx = 0
        for name, dic in data.items():
            wch, dbch, mvch = dic['W'], dic['dBm'], dic['mV']
            color = dic['color']
            row = idx+1

            # Table
            cbx = QCheckBox(self)
            cond = True if self.section == 'BO' else 'Coup' in name
            cbx.setChecked(cond)
            cbx.setObjectName(name)
            cbx.setStyleSheet('color:'+color+'; max-width: 1.2em;')
            cbx.stateChanged.connect(self._handle_curves_visibility)

            lb_desc = QLabel(name, self)
            lb_desc.setStyleSheet(
                'min-height: 1.5em; color:'+color+'; max-width: 8em;'
                'qproperty-alignment: AlignCenter;')

            lb_dbmpwr = SiriusLabel(self, self.prefix+dbch)
            lb_dbmpwr.showUnits = True
            lb_dbmpwr.setVisible(False)
            self._pm_labels['dBm'].append(lb_dbmpwr)

            lb_wpwr = SiriusLabel(self, self.prefix+wch)
            lb_wpwr.showUnits = True
            self._pm_labels['W'].append(lb_wpwr)

            lb_mvpwr = SiriusLabel(self, self.prefix+mvch)
            lb_mvpwr.showUnits = True
            lb_mvpwr.setVisible(False)
            self._pm_labels['mV'].append(lb_mvpwr)

            lay_vals.addWidget(cbx, row, 0)
            lay_vals.addWidget(lb_desc, row, 1)
            lay_vals.addWidget(lb_dbmpwr, row, 2)
            lay_vals.addWidget(lb_wpwr, row, 2)
            lay_vals.addWidget(lb_mvpwr, row, 2)

            # Graph
            self.pwr_mon_graph.addYChannel(
                y_channel=self.prefix+dbch, name=name+' dBm', color=color,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves[name+' dBm'] = self.pwr_mon_graph.curveAtIndex(3*idx)
            self.pwr_mon_graph.addYChannel(
                y_channel=self.prefix+wch, name=name+' W', color=color,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves[name+' W'] = self.pwr_mon_graph.curveAtIndex(3*idx+1)
            self.pwr_mon_graph.addYChannel(
                y_channel=self.prefix+mvch, name=name+' mV', color=color,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves[name+' mV'] = self.pwr_mon_graph.curveAtIndex(3*idx+2)

            idx += 1
        self.pwr_mon_graph.setLabel('left', '')

        if self.section == 'BO':
            for name in data:
                self.curves[name+' dBm'].setVisible(False)
                self.curves[name+' mV'].setVisible(False)

            lb_cavphs = QLabel('Phase', self, alignment=Qt.AlignCenter)
            self.lb_cavphs = SiriusLabel(
                self, self.prefix+'BR-RF-DLLRF-01:CAV:PHS')
            self.lb_cavphs.showUnits = True
            lay_vals.addWidget(lb_cavphs, 5, 1, alignment=Qt.AlignCenter)
            lay_vals.addWidget(self.lb_cavphs, 5, 2)
        else:
            for name in data:
                self.curves[name+' W'].setVisible('Coup' in name)
                self.curves[name+' dBm'].setVisible(False)
                self.curves[name+' mV'].setVisible(False)

        self.ld_cavvgap = QLabel(
            'Gap Voltage:', self, alignment=Qt.AlignCenter)
        self.ld_cavvgap.setStyleSheet('QLabel{font-size: 15pt;}')
        self.lb_cavvgap = SiriusLabel(self, self.prefix+self.chs['CavVGap'])
        self.lb_cavvgap.setStyleSheet('QLabel{font-size: 20pt;}')
        self.lb_cavvgap.showUnits = True
        lay_cavvgap = QHBoxLayout()
        lay_cavvgap.addWidget(self.ld_cavvgap)
        lay_cavvgap.addWidget(self.lb_cavvgap)

        lay = QGridLayout()
        lay.setHorizontalSpacing(25)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay.addLayout(lay_vals, 2, 0)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed), 3, 0)
        lay.addWidget(self.pwr_mon_graph, 4, 0)
        lay.addItem(QSpacerItem(
            0, 50, QSzPlcy.Ignored, QSzPlcy.Minimum), 5, 0)
        lay.addLayout(lay_cavvgap, 6, 0)
        lay.addItem(QSpacerItem(
            0, 10, QSzPlcy.Ignored, QSzPlcy.MinimumExpanding), 7, 0)
        return lay

    def _graphsLayout(self):
        # Temperatures
        self.temp_wid = QWidget()
        self.temp_wid.setStyleSheet("""
            #tempcell_graph, #tempcoup_graph, #tempcirc_graph{
                min-width: 26em; min-height: 10.5em; max-height: 10.5em;}
            QTabWidget::pane{
                border-bottom: 2px solid gray;}
            QPushButton{
                min-width: 6em;}
        """)

        lb_temp = QLabel('<h3>Temperatures [°C]</h3>', self)
        self.pb_wattemp = QPushButton('Temp. Monitor', self)
        connect_window(
            self.pb_wattemp, TempMonitor, parent=self,
            prefix=self.prefix, section=self.section)
        self.temp_tab = QTabWidget(self)
        self.temp_tab.setObjectName(self.section+'Tab')
        self.temp_tab.setContentsMargins(0, 0, 0, 0)

        lay_temp = QGridLayout(self.temp_wid)
        lay_temp.setSpacing(4)
        lay_temp.addWidget(lb_temp, 0, 0)
        lay_temp.addWidget(self.pb_wattemp, 0, 1)
        lay_temp.addWidget(self.temp_tab, 1, 0, 1, 2)
        lay_temp.setRowStretch(0, 1)
        lay_temp.setRowStretch(1, 10)

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
            chn = self.prefix+self.chs['Cav Sts']['Temp']['Cells'][idx][0]
            color = self.chs['Cav Sts']['Temp']['Cells'][idx][1]

            self.tempcell_graph.addYChannel(
                y_channel=chn, name=cid, color=color,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves[cid] = self.tempcell_graph.curveAtIndex(idx)

            cbx = QCheckBox(cid, self)
            cbx.setChecked(True)
            cbx.setObjectName(cid)
            cbx.setStyleSheet('color:'+color+';')
            cbx.stateChanged.connect(self._handle_curves_visibility)
            hbox_cbs.addWidget(cbx)

        self.tempcell_graph.setLabel('left', '')

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
            y_channel=self.prefix+self.chs['Cav Sts']['Temp']['Coupler'][0],
            color=self.chs['Cav Sts']['Temp']['Coupler'][1],
            name='Coupler', lineStyle=Qt.SolidLine, lineWidth=1)
        self.curves['Coupler'] = self.tempcoup_graph.curveAtIndex(0)
        self.tempcoup_graph.setLabel('left', '')
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
        ch2vals = {
            self.prefix+self.chs['TL Sts']['Circ TIn']: {
                'comp': 'wt', 'value': lims_circ},
            self.prefix+self.chs['TL Sts']['Circ TOut']: {
                'comp': 'wt', 'value': lims_circ}
        }
        self.led_tempcircok = PyDMLedMultiChannel(self, ch2vals)
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
            y_channel=self.prefix+self.chs['TL Sts']['Circ TIn'],
            name='CTIn', color='magenta',
            lineStyle=Qt.SolidLine, lineWidth=1)
        self.tempcirc_graph.addYChannel(
            y_channel=self.prefix+self.chs['TL Sts']['Circ TOut'],
            name='CTOut', color='darkRed',
            lineStyle=Qt.SolidLine, lineWidth=1)
        self.tempcirc_graph.setLabel('left', '')

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
        self.led_condrun.channel = self.prefix + \
            self.chs['Cav Sts']['Vac']['Cond']
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
            y_channel=self.prefix+self.chs['Cav Sts']['Vac']['Cells'],
            name='Vacuum', color='black', lineStyle=Qt.SolidLine, lineWidth=1)
        self.vacuum_graph.setLabel('left', '')

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
        led_sts = SiriusLedState(self, self.prefix+chs_dict['Status'])
        lay_amp.addWidget(led_sts, row, 1)

        lb_name = QLabel('<h4>'+chs_dict['Name']+'</h4>', self,
                         alignment=Qt.AlignLeft)
        lb_name.setStyleSheet('max-height: 1.29em;')
        lay_amp.addWidget(lb_name, row, 2)

        lb_pwr = SiriusLabel(self, self.prefix+chs_dict['Power'])
        lb_pwr.showUnits = True
        lb_pwr.setStyleSheet('min-width: 6em; max-width: 6em;')
        lay_amp.addWidget(lb_pwr, row, 3)

        bt_src1 = RFEnblDsblButton(
            parent=self,
            channels={
                'on': self.prefix+chs_dict['SRC 1']['PV'].replace(
                    '-Sts', 'Enbl-Sel'),
                'off': self.prefix+chs_dict['SRC 1']['PV'].replace(
                    '-Sts', 'Dsbl-Sel')})
        if self.section == 'BO':
            ch2vals = {
                self.prefix+'BO-ToBO:RF-ACDCPanel:300Vdc-Mon': {
                    'comp': 'gt', 'value': 280.0},
                self.prefix+chs_dict['SRC 1']['PV']: 1}
            led_src1 = PyDMLedMultiChannel(self, ch2vals)
        else:
            led_src1 = SiriusLedState(
                self, self.prefix+chs_dict['SRC 1']['PV'])
        lay_amp.addLayout(self._create_vlay(bt_src1, led_src1), row, 4)

        bt_src2 = RFEnblDsblButton(
            parent=self,
            channels={
                'on': self.prefix+chs_dict['SRC 2']['PV'].replace(
                    '-Sts', 'Enbl-Sel'),
                'off': self.prefix+chs_dict['SRC 2']['PV'].replace(
                    '-Sts', 'Dsbl-Sel')})
        led_src2 = SiriusLedState(self, self.prefix+chs_dict['SRC 2']['PV'])
        lay_amp.addLayout(self._create_vlay(bt_src2, led_src2), row, 5)

        bt_pinsw = RFEnblDsblButton(
            parent=self,
            channels={
                'on': self.prefix+chs_dict['PinSw'].replace(
                    '-Mon', 'Enbl-Cmd'),
                'off': self.prefix+chs_dict['PinSw'].replace(
                    '-Mon', 'Dsbl-Cmd')})
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "ch[0] < 3.0", "channels": [' +
            '{"channel": "'+self.prefix+chs_dict['PreDrive'] +
            '", "trigger": true}]}]')
        bt_pinsw.pb_on.rules = rules
        led_pinsw = SiriusLedState(self, self.prefix+chs_dict['PinSw'])
        lay_amp.addLayout(self._create_vlay(bt_pinsw, led_pinsw), row, 6)

        lb_drive = SiriusLabel(self, self.prefix+chs_dict['PreDrive'])
        lb_drive.showUnits = True
        led_drive = PyDMLedMultiChannel(
            parent=self, channels2values={
                self.prefix+chs_dict['PreDrive']: {'comp': 'lt', 'value': 3}})
        lay_amp.addLayout(self._create_vlay(lb_drive, led_drive), row, 7)

        ch_pinsw = SiriusConnectionSignal(self.prefix+chs_dict['PinSw'])
        ch_pinsw.new_value_signal[int].connect(
            _part(self._handle_predrive_led_channels, led_drive, chs_dict))

    def _handle_pwrdata_visibility(self, text):
        for group, labels in self._pm_labels.items():
            for lbl in labels:
                lbl.setVisible(text == group)

        for name in self.chs['PwrMtr']:
            cbx = self.findChild(QCheckBox, name)
            visi = cbx.isChecked()
            curvew = self.curves[name + ' W']
            curvew.setVisible(text == 'W' and visi)
            curvedbm = self.curves[name + ' dBm']
            curvedbm.setVisible(text == 'dBm' and visi)
            curvemv = self.curves[name + ' mV']
            curvemv.setVisible(text == 'mV' and visi)

    def _handle_curves_visibility(self, state):
        name = self.sender().objectName()
        if name in self.chs['PwrMtr']:
            name += ' ' + self.cb_units.currentText()
        curve = self.curves[name]
        curve.setVisible(state)

    def _handle_predrive_led_channels(self, led_drive, chs_dict, value):
        val = 100 if value == 1 else 3
        ch2vals = {
            self.prefix+chs_dict['PreDrive']: {
                'comp': 'lt', 'value': val}
            }
        led_drive.set_channels2values(ch2vals)

    def _handle_rmpwfm_visibility(self, index):
        self.curve_pwrmtr.setVisible(index == 0)
        self.curve_vgav.setVisible(index == 1)
        self.curve_pwr.setVisible(index == 2)

    def _update_temp_limits(self, value):
        address = self.sender().address
        if 'Coup' in address:
            if 'Lower' in address:
                self.chs['Cav Sts']['Temp']['Coupler Limits'][0] = value
            else:
                self.chs['Cav Sts']['Temp']['Coupler Limits'][1] = value

            lims = self.chs['Cav Sts']['Temp']['Coupler Limits']
            ch2vals = {
                self.prefix+self.chs['Cav Sts']['Temp']['Coupler'][0]: {
                    'comp': 'wt', 'value': lims}
                }
            self.led_tempcellok.set_channels2values(ch2vals)
            self.line_coup_minlim.setPos(lims[0])
            self.line_coup_maxlim.setPos(lims[1])
        else:
            if 'Lower' in address:
                self.chs['Cav Sts']['Temp']['Cells Limits'][0] = value
            else:
                self.chs['Cav Sts']['Temp']['Cells Limits'][1] = value

            lims = self.chs['Cav Sts']['Temp']['Cells Limits']
            ch2vals = {self.prefix+c[0]: {'comp': 'wt', 'value': lims}
                       for c in self.chs['Cav Sts']['Temp']['Cells']}
            self.led_tempcoupok.set_channels2values(ch2vals)
            self.line_cell_minlim.setPos(lims[0])
            self.line_cell_maxlim.setPos(lims[1])

    def _handle_ampl_unit_visibility(self, text):
        self.sb_amp1.setVisible(text == '[mV]')
        self.lb_amp1.setVisible(text == '[mV]')
        self.sb_amp2.setVisible(text == '[V]')
        self.lb_amp2.setVisible(text == '[V]')

    def _handle_rmpampl_unit_visibility(self, text):
        self.blockSignals(True)
        self.cb_rmpphsbot.setCurrentText(text)
        self.cb_rmpphstop.setCurrentText(text)
        self.le_rmpvolttop1.setVisible(text == '[mV]')
        self.lb_rmpvolttop1.setVisible(text == '[mV]')
        self.le_rmpvoltbot1.setVisible(text == '[mV]')
        self.lb_rmpvoltbot1.setVisible(text == '[mV]')
        self.le_rmpvolttop2.setVisible(text == '[V]')
        self.lb_rmpvolttop2.setVisible(text == '[V]')
        self.le_rmpvoltbot2.setVisible(text == '[V]')
        self.lb_rmpvoltbot2.setVisible(text == '[V]')
        self.blockSignals(False)
