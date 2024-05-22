"""LI Egun control."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QGroupBox, \
    QSpacerItem, QSizePolicy as QSzPlcy, QPushButton
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX

from ..widgets import SiriusMainWindow, SiriusLedState, \
    SiriusSpinbox, PyDMStateButton, SiriusLabel
from ..util import get_appropriate_color, connect_window
from .custom_widgets import LIEGTrigEnblDetail


class LIEgunWindow(SiriusMainWindow):
    """Egun Control Window."""

    def __init__(self, parent=None, prefix=VACA_PREFIX, is_it=False):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.dev_pref = 'IT-EGH' if is_it else 'LI-01'
        self.dev_desc = 'Injector Test' if is_it else 'Linac'
        self.setWindowTitle(self.dev_desc+' E-gun Control Window')
        self.sec = self.dev_pref[0:2]
        color = get_appropriate_color(self.sec)
        self.setWindowIcon(qta.icon('mdi.spotlight-beam', color=color))
        self.setObjectName(self.sec+'App')
        self._setupUi()

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)

        self.title = QLabel('<h2>'+self.dev_desc+' E-gun</h2>', self)

        wid_sysstatus = self._setupSysStatusWidget()
        wid_hvps = self._setupHVPSWidget()
        if self.sec == 'IT':
            wid_timing = ITTIWidget(self, self.prefix)
        wid_trigger = self._setupTriggerWidget()
        wid_filaps = self._setupFilaPSWidget()
        wid_biasps = self._setupBiasPSWidget()
        wid_pulseps = self._setupPulsePSWidget()
        wid_multipulseps = self._setupMultiPulsePSWidget()

        layout = QGridLayout(cw)
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(12)
        layout.addWidget(self.title, 0, 0, 1, 6)
        if self.sec == 'IT':
            layout.addWidget(wid_sysstatus, 1, 0, 2, 1)
            layout.addWidget(wid_hvps, 1, 1, 2, 4)
            layout.addWidget(wid_timing, 1, 5)
            layout.addWidget(wid_trigger, 2, 5)
            layout.addWidget(wid_filaps, 3, 0, 1, 6)
            layout.addWidget(wid_biasps, 4, 0, 1, 6)
            layout.addWidget(wid_pulseps, 5, 0, 1, 3)
            layout.addWidget(wid_multipulseps, 5, 3, 1, 3)
            layout.setRowStretch(1, 1)
            layout.setRowStretch(2, 3)
        else:
            layout.addWidget(wid_sysstatus, 1, 0, 1, 1)
            layout.addWidget(wid_hvps, 1, 1, 1, 4)
            layout.addWidget(wid_trigger, 1, 5)
            layout.addWidget(wid_filaps, 2, 0, 1, 6)
            layout.addWidget(wid_biasps, 3, 0, 1, 6)
            layout.addWidget(wid_pulseps, 4, 0, 1, 3)
            layout.addWidget(wid_multipulseps, 4, 3, 1, 3)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 2)
        layout.setColumnStretch(3, 2)
        layout.setColumnStretch(4, 2)
        layout.setColumnStretch(5, 3)

        self.setStyleSheet("""
            QLabel{
                max-height: 2em;
                qproperty-alignment: AlignCenter;
            }""")

    def _setupSysStatusWidget(self):
        self._ld_sysexternal = QLabel('Ext. Intlk', self)
        self._led_sysexternal = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-External:status')
        self._led_sysexternal.offColor = SiriusLedState.Red

        self._ld_sysvalve = QLabel('Valve', self)
        self._led_sysvalve = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-Valve:status')
        self._led_sysvalve.offColor = SiriusLedState.Red

        self._ld_sysgate = QLabel('Gate', self)
        self._led_sysgate = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-Gate:status')
        self._led_sysgate.offColor = SiriusLedState.Red

        self._ld_sysvac = QLabel('Vacuum', self)
        self._led_sysvac = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-Vacuum:status')
        self._led_sysvac.offColor = SiriusLedState.Red

        self._ld_sysplc = QLabel('PLC', self)
        self._led_sysplc = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-PLC:status')
        self._led_sysplc.offColor = SiriusLedState.Yellow

        self._ld_syssysstart = QLabel('System\nStart', self)
        self._bt_syssysstart = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-System:start')

        wid = QGroupBox('System Status', self)
        lay = QGridLayout(wid)
        lay.addWidget(self._ld_sysexternal, 0, 0)
        lay.addWidget(self._led_sysexternal, 0, 1)
        lay.addWidget(self._ld_sysvalve, 1, 0)
        lay.addWidget(self._led_sysvalve, 1, 1)
        lay.addWidget(self._ld_sysgate, 2, 0)
        lay.addWidget(self._led_sysgate, 2, 1)
        lay.addWidget(self._ld_sysvac, 3, 0)
        lay.addWidget(self._led_sysvac, 3, 1)
        lay.addWidget(self._ld_sysplc, 4, 0)
        lay.addWidget(self._led_sysplc, 4, 1)
        lay.addWidget(self._ld_syssysstart, 5, 0)
        lay.addWidget(self._bt_syssysstart, 5, 1)
        return wid

    def _setupHVPSWidget(self):
        self._ld_hvpsswtsel = QLabel('Switch', self)
        self._bt_hvpsswtsel = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-HVPS:switch')

        self._led_hvpsswtsts = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-HVPS:swstatus')

        self._ld_hvpsvoltsp = QLabel('Voltage SP [kV]', self)
        self._sb_hvpsvoltsp = SiriusSpinbox(
            self, self.prefix+self.dev_pref+':EG-HVPS:voltoutsoft')

        self._ld_hvpsvoltrb = QLabel('Voltage RB [kV]', self)
        self._lb_hvpsvoltrb = SiriusLabel(
            self, self.prefix+self.dev_pref+':EG-HVPS:voltinsoft')

        self._ld_hvpsenblsel = QLabel('Enable')
        self._bt_hvpsenblsel = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-HVPS:enable')

        self._led_hvpsenblsts = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-HVPS:enstatus')

        self._ld_hvpscurrsp = QLabel('Current SP [mA]')
        self._sb_hvpscurrsp = SiriusSpinbox(
            self, self.prefix+self.dev_pref+':EG-HVPS:currentoutsoft')

        self._ld_hvpscurrrb = QLabel('Current RB [mA]')
        self._lb_hvpscurrrb = SiriusLabel(
            self, self.prefix+self.dev_pref+':EG-HVPS:currentinsoft')

        wid = QGroupBox('High Voltage Power Supply', self)
        lay = QGridLayout(wid)
        lay.addWidget(self._ld_hvpsswtsel, 0, 0, 1, 2)
        lay.addWidget(self._bt_hvpsswtsel, 1, 0, alignment=Qt.AlignRight)
        lay.addWidget(self._led_hvpsswtsts, 1, 1, alignment=Qt.AlignLeft)
        lay.addWidget(self._ld_hvpsvoltsp, 0, 2)
        lay.addWidget(self._sb_hvpsvoltsp, 1, 2)
        lay.addWidget(self._ld_hvpsvoltrb, 0, 3)
        lay.addWidget(self._lb_hvpsvoltrb, 1, 3)
        lay.addItem(QSpacerItem(1, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), 2, 0)
        lay.addWidget(self._ld_hvpsenblsel, 3, 0, 1, 2)
        lay.addWidget(self._bt_hvpsenblsel, 4, 0, alignment=Qt.AlignRight)
        lay.addWidget(self._led_hvpsenblsts, 4, 1, alignment=Qt.AlignLeft)
        lay.addWidget(self._ld_hvpscurrsp, 3, 2)
        lay.addWidget(self._sb_hvpscurrsp, 4, 2)
        lay.addWidget(self._ld_hvpscurrrb, 3, 3)
        lay.addWidget(self._lb_hvpscurrrb, 4, 3)
        return wid

    def _setupTriggerWidget(self):
        self._ld_trigsts = QLabel('Status', self)
        self._led_trigsts = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-TriggerPS:status')

        self._ld_trigall = QLabel('Trigger Allow', self)
        self._led_trigall = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-TriggerPS:allow')

        self._ld_trigenbl = QLabel('Trigger', self)
        self._bt_trigenblsel = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-TriggerPS:enable')
        self._led_trigenblsts = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-TriggerPS:enablereal')

        wid = QGroupBox('Trigger', self)
        lay = QGridLayout(wid)
        lay.addWidget(self._ld_trigsts, 0, 0, 1, 3)
        lay.addWidget(self._led_trigsts, 1, 0, 1, 3)
        lay.addWidget(self._ld_trigall, 2, 0, 1, 3)
        lay.addWidget(self._led_trigall, 3, 0, 1, 3)
        lay.addWidget(self._ld_trigenbl, 4, 0, 1, 3)
        lay.addWidget(self._bt_trigenblsel, 5, 0, alignment=Qt.AlignRight)
        lay.addWidget(self._led_trigenblsts, 5, 1, alignment=Qt.AlignLeft)

        if 'LI' in self.dev_pref:
            self._pb_trigenbl_dtl = QPushButton(self)
            self._pb_trigenbl_dtl.setObjectName('dtl')
            self._pb_trigenbl_dtl.setStyleSheet(
                "#dtl{min-width:18px; max-width:18px; icon-size:20px;}")
            self._pb_trigenbl_dtl.setIcon(qta.icon('fa5s.ellipsis-v'))
            connect_window(
                self._pb_trigenbl_dtl, LIEGTrigEnblDetail, self,
                prefix=self.prefix, device=self.dev_pref+':EG-TriggerPS')
            lay.addWidget(self._pb_trigenbl_dtl, 5, 2, alignment=Qt.AlignLeft)
        return wid

    def _setupFilaPSWidget(self):
        self._ld_filaswtsel = QLabel('Switch', self)
        self._bt_filaswtsel = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-FilaPS:switch')

        self._led_filasswtsts = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-FilaPS:swstatus')

        self._ld_filacurrsp = QLabel('Current SP [A]', self)
        self._sb_filacurrsp = SiriusSpinbox(
            self, self.prefix+self.dev_pref+':EG-FilaPS:currentoutsoft')

        self._ld_filacurrrb = QLabel('Current RB [A]', self)
        self._lb_filacurrrb = SiriusLabel(
            self, self.prefix+self.dev_pref+':EG-FilaPS:currentinsoft')

        self._ld_filavoltrb = QLabel('Voltage RB [V]', self)
        self._lb_filavoltrb = SiriusLabel(
            self, self.prefix+self.dev_pref+':EG-FilaPS:voltinsoft')

        wid = QGroupBox('Filament Power Supply', self)
        lay = QGridLayout(wid)
        lay.addWidget(self._ld_filaswtsel, 0, 0, 1, 2)
        lay.addWidget(self._bt_filaswtsel, 1, 0, alignment=Qt.AlignRight)
        lay.addWidget(self._led_filasswtsts, 1, 1, alignment=Qt.AlignLeft)
        lay.addWidget(self._ld_filacurrsp, 0, 2)
        lay.addWidget(self._sb_filacurrsp, 1, 2)
        lay.addWidget(self._ld_filacurrrb, 0, 3)
        lay.addWidget(self._lb_filacurrrb, 1, 3)
        lay.addWidget(self._ld_filavoltrb, 0, 4)
        lay.addWidget(self._lb_filavoltrb, 1, 4)
        return wid

    def _setupBiasPSWidget(self):
        self._ld_biasswtsel = QLabel('Switch', self)
        self._bt_biasswtsel = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-BiasPS:switch')

        self._led_biassswtsts = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-BiasPS:swstatus')

        self._ld_biasvoltsp = QLabel('Voltage SP [V]', self)
        self._sb_biasvoltsp = SiriusSpinbox(
            self, self.prefix+self.dev_pref+':EG-BiasPS:voltoutsoft')

        self._ld_biasvoltrb = QLabel('Voltage RB [V]', self)
        self._lb_biasvoltrb = SiriusLabel(
            self, self.prefix+self.dev_pref+':EG-BiasPS:voltinsoft')

        self._ld_biascurrrb = QLabel('Current RB [A]', self)
        self._lb_biascurrrb = SiriusLabel(
            self, self.prefix+self.dev_pref+':EG-BiasPS:currentinsoft')

        wid = QGroupBox('Bias Power Supply', self)
        lay = QGridLayout(wid)
        lay.addWidget(self._ld_biasswtsel, 0, 0, 1, 2)
        lay.addWidget(self._bt_biasswtsel, 1, 0, alignment=Qt.AlignRight)
        lay.addWidget(self._led_biassswtsts, 1, 1, alignment=Qt.AlignLeft)
        lay.addWidget(self._ld_biasvoltsp, 0, 2)
        lay.addWidget(self._sb_biasvoltsp, 1, 2)
        lay.addWidget(self._ld_biasvoltrb, 0, 3)
        lay.addWidget(self._lb_biasvoltrb, 1, 3)
        lay.addWidget(self._ld_biascurrrb, 0, 4)
        lay.addWidget(self._lb_biascurrrb, 1, 4)
        return wid

    def _setupPulsePSWidget(self):
        self._ld_pulsemodsel = QLabel('Mode', self)
        self._ld_pulseswtsel = QLabel('Switch', self)
        self._ld_pulsesing = QLabel('Single', self)
        self._ld_pulsemult = QLabel('Multi', self)

        self._bt_pulsesingmod = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-PulsePS:singleselect')
        self._led_pulsesingmod = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-PulsePS:singleselstatus')
        self._bt_pulsesingswt = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-PulsePS:singleswitch')
        self._led_pulsesingswt = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-PulsePS:singleswstatus')

        self._bt_pulsemultmod = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-PulsePS:multiselect')
        self._led_pulsemultmod = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-PulsePS:multiselstatus')
        self._bt_pulsemultswt = PyDMStateButton(
            self, self.prefix+self.dev_pref+':EG-PulsePS:multiswitch')
        self._led_pulsemultswt = SiriusLedState(
            self, self.prefix+self.dev_pref+':EG-PulsePS:multiswstatus')

        wid = QGroupBox('Pulse Power Supply', self)
        lay = QGridLayout(wid)
        lay.addWidget(self._ld_pulsemodsel, 0, 1, 1, 2)
        lay.addWidget(self._ld_pulseswtsel, 0, 3, 1, 2)
        lay.addWidget(self._ld_pulsesing, 1, 0)
        lay.addWidget(self._ld_pulsemult, 2, 0)
        lay.addWidget(self._bt_pulsesingmod, 1, 1, alignment=Qt.AlignRight)
        lay.addWidget(self._led_pulsesingmod, 1, 2, alignment=Qt.AlignLeft)
        lay.addWidget(self._bt_pulsesingswt, 1, 3, alignment=Qt.AlignRight)
        lay.addWidget(self._led_pulsesingswt, 1, 4, alignment=Qt.AlignLeft)
        lay.addWidget(self._bt_pulsemultmod, 2, 1, alignment=Qt.AlignRight)
        lay.addWidget(self._led_pulsemultmod, 2, 2, alignment=Qt.AlignLeft)
        lay.addWidget(self._bt_pulsemultswt, 2, 3, alignment=Qt.AlignRight)
        lay.addWidget(self._led_pulsemultswt, 2, 4, alignment=Qt.AlignLeft)
        return wid

    def _setupMultiPulsePSWidget(self):
        self._ld_mpulspwrsp = QLabel('Power SP [V]', self)
        self._sb_mpulspwrsp = SiriusSpinbox(
            self, self.prefix+self.dev_pref+':EG-PulsePS:poweroutsoft')
        self._sb_mpulspwrsp.limitsFromChannel = False
        self._sb_mpulspwrsp.setMinimum(0)
        self._sb_mpulspwrsp.setMaximum(300)
        self._ld_mpulspwrrb = QLabel('Power RB [V]', self)
        self._lb_mpulspwrrb = SiriusLabel(
            self, self.prefix+self.dev_pref+':EG-PulsePS:powerinsoft')

        wid = QGroupBox('Multi Pulse Power Supply', self)
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignVCenter)
        lay.addWidget(self._ld_mpulspwrsp, 0, 0)
        lay.addWidget(self._sb_mpulspwrsp, 1, 0)
        lay.addWidget(self._ld_mpulspwrrb, 0, 1)
        lay.addWidget(self._lb_mpulspwrrb, 1, 1)
        return wid


class ITTIWidget(QWidget):
    """IT Timing control widget."""

    def __init__(self, parent=None, prefix='', is_main=False):
        """Init."""
        super().__init__(parent)
        self.setObjectName('ITApp')

        ld_tienbl = QLabel('Enable Pulses', self, alignment=Qt.AlignCenter)
        bt_tienblsel = PyDMStateButton(
            self, prefix+'IT-EGH:TI-TrigGen:ChanOut-Sel')
        led_tienblsts = SiriusLedState(
            self, prefix+'IT-EGH:TI-TrigGen:ChanOut-Sts')

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setContentsMargins(0, 0, 0, 0)

        glay = QGridLayout()
        glay.addWidget(ld_tienbl, 0, 0, 1, 2)
        glay.addWidget(bt_tienblsel, 1, 0)
        glay.addWidget(led_tienblsts, 1, 1)
        if not is_main:
            gbox = QGroupBox('Timing', self)
            gbox.setLayout(glay)
            lay.addWidget(gbox)
        else:
            lb_title = QLabel(
                '<h3>IT - Timing</h3>', self, alignment=Qt.AlignCenter)
            lay.setHorizontalSpacing(15)
            lay.setVerticalSpacing(15)
            lay.addWidget(lb_title, 0, 0)
            lay.addLayout(glay, 1, 0)
