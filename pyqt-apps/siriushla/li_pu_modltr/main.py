"""LI Modulators Control."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, \
    QHBoxLayout, QPushButton, QFrame

import qtawesome as qta

from pydm.widgets import PyDMPushButton

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName

from ..util import connect_window, get_appropriate_color
from ..widgets import SiriusMainWindow, SiriusLedState, SiriusSpinbox, \
    PyDMStateButton, SiriusLabel
from .auxiliary_dialogs import ModIntlkDetailDialog, ModEmerStopDialog


class LIModltrWindow(SiriusMainWindow):
    """LI Modulators Control."""

    def __init__(self, prefix=VACA_PREFIX, parent=None):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.setWindowTitle('Linac Modulators Window')
        self.setObjectName('LIApp')
        self.setWindowIcon(
            qta.icon('mdi.current-ac', color=get_appropriate_color('LI')))

        self._setupUi()

        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        lay = QHBoxLayout(cw)
        for dev in ['LI-01:PU-Modltr-1', 'LI-01:PU-Modltr-2']:
            dev = _PVName(dev).substitute(prefix=self.prefix)
            lay.addWidget(self._setupModltrWidget(dev))

        self.setStyleSheet("""
            QLed{
                min-width: 1.29em; max-width: 1.29em;
            }""")

    def _setupModltrWidget(self, dev):
        title = QLabel(
            '<h2>'+_PVName(dev).device_name+'</h2>', self,
            alignment=Qt.AlignCenter)

        wid_intlk = self._setupInterlockWidget(dev)

        wid_ctrls = self._setupMainControlsWidget(dev)

        wid_sps = self._setupSetpointsWidget(dev)

        wid_emer = self._setupEmerStopWidget(dev)

        wid_auxmon = self._setupAuxMonitorWidget(dev)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.setHorizontalSpacing(20)
        lay.setVerticalSpacing(20)
        lay.addWidget(title, 0, 0, 1, 2)
        lay.addWidget(wid_intlk, 1, 0, 1, 2)
        lay.addWidget(wid_ctrls, 2, 0, 1, 2)
        lay.addWidget(wid_sps, 3, 0)
        lay.addWidget(wid_emer, 3, 1)
        lay.addWidget(wid_auxmon, 4, 0, 1, 2)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 1)
        return wid

    def _setupInterlockWidget(self, dev):
        # Remote/Local
        ld_ctrlmode = QLabel('<h3>Remote/Local</h3>')
        led_ctrlmode = SiriusLedState(self, dev+':Remote')
        led_ctrlmode.offColor = SiriusLedState.Red

        # Output_Status
        ld_output = QLabel('<h3>Output_Status</h3>')
        led_output = SiriusLedState(self, dev+':OutPut_Status')

        # Reset
        pb_reset = PyDMPushButton(
            self, label='Reset', icon=qta.icon('fa5s.sync'),
            pressValue=1, releaseValue=0, init_channel=dev+':RESET')
        pb_reset.writeWhenRelease = True
        pb_reset.setObjectName('reset')
        pb_reset.setStyleSheet("""
            #reset{
                min-width: 5em; max-width: 5em;
                min-height: 1.5em; max-height: 1.5em;
            }""")

        # Interlocks
        lay_ilks = QGridLayout()

        lay_ilks.setVerticalSpacing(9)
        interlocks = [
         'Run/Stop', 'PreHeat', 'Charge_Allowed', 'TrigOut_Allowed',
         'Emer_Stop', 'CPS_ALL', 'Thy_Heat', 'Kly_Heat', 'LV_Rdy_OK',
         'HV_Rdy_OK', 'TRIG_Rdy_OK', 'MOD_Self_Fault', 'MOD_Sys_Ready',
         'TRIG_Norm', 'Pulse_Current']
        for idx, ilk in enumerate(interlocks):
            row = idx % 8
            col = int(idx > 7)
            led = SiriusLedState(self, dev+':'+ilk)
            led.offColor = led.Red
            lbl = QLabel(ilk)
            hbox = QHBoxLayout()
            hbox.setAlignment(Qt.AlignLeft)
            hbox.addWidget(led)
            hbox.addWidget(lbl)
            lay_ilks.addLayout(hbox, row, col)

        pb_check = QPushButton('Check', self)
        pb_check.setObjectName('check')
        pb_check.setStyleSheet("""
            #check{
                min-width: 5em; max-width: 5em;
                min-height: 1.5em; max-height: 1.5em;
            }""")
        connect_window(
            pb_check, ModIntlkDetailDialog, self,
            device=dev, prefix=self.prefix)
        lay_ilks.addWidget(pb_check, 7, 1, alignment=Qt.AlignCenter)

        wid = QFrame(self)
        wid.setStyleSheet(
            '.QFrame{border: 2px solid gray;}')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.setHorizontalSpacing(10)
        lay.addWidget(led_ctrlmode, 0, 0, alignment=Qt.AlignCenter)
        lay.addWidget(ld_ctrlmode, 0, 1, alignment=Qt.AlignLeft)
        lay.addWidget(led_output, 1, 0, alignment=Qt.AlignCenter)
        lay.addWidget(ld_output, 1, 1, alignment=Qt.AlignLeft)
        lay.addWidget(pb_reset, 2, 0, 1, 2, alignment=Qt.AlignCenter)
        lay.addLayout(lay_ilks, 0, 2, 3, 1)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 4)
        lay.setColumnStretch(2, 8)
        lay.setRowStretch(0, 2)
        lay.setRowStretch(1, 2)
        lay.setRowStretch(2, 1)
        return wid

    def _setupMainControlsWidget(self, dev):
        lb_RUN_STOP = QLabel(
            '<h4>RUN_STOP</h4>', self, alignment=Qt.AlignCenter)
        led_RUN_STOP = SiriusLedState(self, dev + ':RUN_STOP')
        led_RUN_STOP.offColor = SiriusLedState.Red
        btn_STOP = PyDMPushButton(
            parent=self, init_channel=dev + ':RUN_STOP', pressValue=0,
            icon=qta.icon('mdi.power-off'))
        btn_STOP.setToolTip(
            'Turn Off: Only press if you know what you are doing')
        btn_STOP.showConfirmDialog = True
        btn_STOP.confirmMessage = (
            "This Action will Turn off the Klystron and Thyratron."
            "<h4>After this operation the system will enter in a 1h long "
            "ramping process when turned on again.</h4>\n"
            "Are you sure you want to proceed?")
        btn_RUN = PyDMPushButton(
            parent=self, init_channel=dev + ':RUN_STOP', pressValue=1,
            icon=qta.icon('mdi.power-on'))
        btn_RUN.setToolTip('Turn On')
        gdl_RUN_STOP = QGridLayout()
        gdl_RUN_STOP.addWidget(btn_STOP, 0, 0)
        gdl_RUN_STOP.addWidget(btn_RUN, 0, 1)
        gdl_RUN_STOP.addWidget(
            led_RUN_STOP, 1, 0, 1, 2, alignment=Qt.AlignCenter)

        lb_PREHEAT = QLabel(
            '<h4>PREHEAT</h4>', self, alignment=Qt.AlignCenter)
        led_PREHEAT = SiriusLedState(self, dev + ':PREHEAT')
        led_PREHEAT.offColor = SiriusLedState.Red
        btn_PREHEAT_OFF = PyDMPushButton(
            parent=self, init_channel=dev + ':PREHEAT', pressValue=0,
            icon=qta.icon('mdi.power-off'))
        btn_PREHEAT_OFF.setToolTip(
            'Turn Off: Only press if you know what you are doing')
        btn_PREHEAT_OFF.showConfirmDialog = True
        btn_PREHEAT_OFF.confirmMessage = (
            "This Action will Turn off the Klystron and Thyratron."
            "<h4>After this operation the system will enter in a 1h long "
            "ramping process when turned on again.</h4>\n"
            "Are you sure you want to proceed?")
        btn_PREHEAT_ON = PyDMPushButton(
            parent=self, init_channel=dev + ':PREHEAT', pressValue=1,
            icon=qta.icon('mdi.power-on'))
        btn_PREHEAT_ON.showConfirmDialog = True
        btn_PREHEAT_ON.confirmMessage = (
            "If PREHEAT is disabled, this action will <h4>start the 1h long "
            "ramping process of the Klystron and Thyratron.</h4>\n"
            "Are you sure you want to proceed?")
        gdl_PREHEAT = QGridLayout()
        gdl_PREHEAT.addWidget(btn_PREHEAT_OFF, 0, 0)
        gdl_PREHEAT.addWidget(btn_PREHEAT_ON, 0, 1)
        gdl_PREHEAT.addWidget(
            led_PREHEAT, 1, 0, 1, 2, alignment=Qt.AlignCenter)

        lb_Charge = QLabel(
            '<h4>Charge</h4>', self, alignment=Qt.AlignCenter)
        pb_Charge = PyDMStateButton(
            self, dev + ':CHARGE')

        lb_TrigOut = QLabel(
            '<h4>TrigOut</h4>', self, alignment=Qt.AlignCenter)
        pb_TrigOut = PyDMStateButton(
            self, dev + ':TRIGOUT')

        wid = QFrame()
        wid.setStyleSheet(
            '.QFrame{border: 2px solid gray;}')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.setHorizontalSpacing(30)
        lay.addWidget(lb_RUN_STOP, 0, 0)
        lay.addLayout(gdl_RUN_STOP, 1, 0, alignment=Qt.AlignCenter)
        lay.addWidget(lb_PREHEAT, 0, 1)
        lay.addLayout(gdl_PREHEAT, 1, 1, alignment=Qt.AlignCenter)
        lay.addWidget(lb_Charge, 0, 2)
        lay.addWidget(pb_Charge, 1, 2)
        lay.addWidget(lb_TrigOut, 0, 3)
        lay.addWidget(pb_TrigOut, 1, 3)
        return wid

    def _setupSetpointsWidget(self, dev):
        lbl_sp = QLabel('<h4>Setpoint</h4>', self, alignment=Qt.AlignCenter)
        lbl_rb = QLabel('<h4>Readback</h4>', self, alignment=Qt.AlignCenter)
        lbl_kv = QLabel('kV', self, alignment=Qt.AlignCenter)
        lbl_ma = QLabel('mA', self, alignment=Qt.AlignCenter)

        sb_volt = SiriusSpinbox(self, dev+':WRITE_V')
        sb_volt.showStepExponent = False
        lb_volt = SiriusLabel(self, dev+':READV')
        lb_volt.setAlignment(Qt.AlignCenter)

        sb_curr = SiriusSpinbox(self, dev+':WRITE_I')
        sb_curr.showStepExponent = False
        lb_curr = SiriusLabel(self, dev+':READI')
        lb_curr.setAlignment(Qt.AlignCenter)

        wid = QFrame()
        wid.setStyleSheet(
            '.QFrame{border: 2px solid gray;}')
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_sp, 0, 0)
        lay.addWidget(lbl_rb, 0, 1)
        lay.addWidget(sb_volt, 1, 0)
        lay.addWidget(lb_volt, 1, 1)
        lay.addWidget(lbl_kv, 1, 2)
        lay.addWidget(sb_curr, 2, 0)
        lay.addWidget(lb_curr, 2, 1)
        lay.addWidget(lbl_ma, 2, 2)
        return wid

    def _setupEmerStopWidget(self, dev):
        pb_emerstop = QPushButton('EMER\nSTOP', self)
        pb_emerstop.setObjectName('emerstop')
        pb_emerstop.setStyleSheet("""
            #emerstop {
                background-color: red;
                min-width: 3em; max-width: 3em;
                min-height: 3em; max-height: 3em;
                font-weight: bold;
            }""")
        connect_window(
            pb_emerstop, ModEmerStopDialog, self,
            device=dev, prefix=self.prefix)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(pb_emerstop)
        return wid

    def _setupAuxMonitorWidget(self, dev):
        lb_klymin = SiriusLabel(self, dev+':K_W_T1')
        lb_klymin.setStyleSheet(
            'QLabel{min-width: 2em; max-width: 2em;}')
        lb_klysec = SiriusLabel(self, dev+':K_W_T2')
        lb_klysec.setStyleSheet(
            'QLabel{min-width: 2em; max-width: 2em;}')
        lb_thymin = SiriusLabel(self, dev+':TH_W_T01')
        lb_thymin.setStyleSheet(
            'QLabel{min-width: 2em; max-width: 2em;}')
        lb_thysec = SiriusLabel(self, dev+':TH_W_T02')
        lb_thysec.setStyleSheet(
            'QLabel{min-width: 2em; max-width: 2em;}')

        wid = QFrame(self)
        wid.setStyleSheet(
            '.QFrame{border: 2px solid gray;}')
        lay = QHBoxLayout(wid)
        lay.addStretch()
        lay.addWidget(QLabel('<h4>Klystron</h4>'))
        lay.addWidget(lb_klymin)
        lay.addWidget(QLabel('Min'))
        lay.addWidget(lb_klysec)
        lay.addWidget(QLabel('Sec'))
        lay.addStretch()
        lay.addWidget(QLabel('<h4>THyratron</h4>'))
        lay.addWidget(lb_thymin)
        lay.addWidget(QLabel('Min'))
        lay.addWidget(lb_thysec)
        lay.addWidget(QLabel('Sec'))
        lay.addStretch()
        return wid
