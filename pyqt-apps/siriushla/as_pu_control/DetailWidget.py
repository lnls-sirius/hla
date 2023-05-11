"""Detailed widget for controlling a pulsed mangnet."""
import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QLabel, QGroupBox, QFormLayout
from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriushla import util
from siriushla.widgets import SiriusLedState, SiriusLedAlert, PyDMLed, \
    PyDMStateButton, PyDMSpinboxScrollbar, SiriusLabel
from siriushla.as_ti_control.hl_trigger import HLTriggerSimple


class PUDetailWidget(QWidget):
    """Detailed widget for controlling a pulsed magnet."""

    def __init__(self, devname, parent=None):
        """Receive a parent and a pulsed mangnet name."""
        super().__init__(parent)
        self._devname = _PVName(devname)
        self._section = self._devname.sec
        self._prefix = _VACA_PREFIX
        self._pdev = self._devname.substitute(prefix=self._prefix)
        self.setObjectName(self._section+'App')
        self.setWindowIcon(qta.icon(
            'mdi.current-ac', color=util.get_appropriate_color(self._section)))

        self._create_pvs()
        self._setup_ui()
        self.setStyleSheet("""
            #pulses_box,
            #pwrstate_box {
                max-width: 8em;
            }
        """)
        self.setFocusPolicy(Qt.StrongFocus)

    def _create_pvs(self):
        """Create variables with pvs that'll be used."""
        self._voltage_sp_pv = self._pdev.substitute(propty='Voltage-SP')
        self._voltage_rb_pv = self._pdev.substitute(propty='Voltage-RB')
        self._voltage_mon_pv = self._pdev.substitute(propty='Voltage-Mon')
        self._kick_sp_pv = self._pdev.substitute(propty='Kick-SP')
        self._kick_rb_pv = self._pdev.substitute(propty='Kick-RB')
        self._kick_mon_pv = self._pdev.substitute(propty='Kick-Mon')
        self._pwrstate_sel_pv = self._pdev.substitute(propty='PwrState-Sel')
        self._pwrstate_sts_pv = self._pdev.substitute(propty='PwrState-Sts')
        self._enablepulses_sel_pv = self._pdev.substitute(propty='Pulse-Sel')
        self._enablepulses_sts_pv = self._pdev.substitute(propty='Pulse-Sts')
        self._reset_cmd_pv = self._pdev.substitute(propty='Reset-Cmd')
        self._intlk1_mon_pv = self._pdev.substitute(propty='Intlk1-Mon')
        self._intlk2_mon_pv = self._pdev.substitute(propty='Intlk2-Mon')
        self._intlk3_mon_pv = self._pdev.substitute(propty='Intlk3-Mon')
        self._intlk4_mon_pv = self._pdev.substitute(propty='Intlk4-Mon')
        self._intlk5_mon_pv = self._pdev.substitute(propty='Intlk5-Mon')
        self._intlk6_mon_pv = self._pdev.substitute(propty='Intlk6-Mon')
        self._intlk7_mon_pv = self._pdev.substitute(propty='Intlk7-Mon')
        self._intlk1_lbcte_pv = self._pdev.substitute(propty='Intlk1Label-Cte')
        self._intlk2_lbcte_pv = self._pdev.substitute(propty='Intlk2Label-Cte')
        self._intlk3_lbcte_pv = self._pdev.substitute(propty='Intlk3Label-Cte')
        self._intlk4_lbcte_pv = self._pdev.substitute(propty='Intlk4Label-Cte')
        self._intlk5_lbcte_pv = self._pdev.substitute(propty='Intlk5Label-Cte')
        self._intlk6_lbcte_pv = self._pdev.substitute(propty='Intlk6Label-Cte')
        self._intlk7_lbcte_pv = self._pdev.substitute(propty='Intlk7Label-Cte')
        if 'Sept' not in self._devname:
            self._intlk8_mon_pv = self._pdev.substitute(propty='Intlk8-Mon')
            self._intlk8_lbcte_pv = \
                self._pdev.substitute(propty='Intlk8Label-Cte')
        self._ctrlmode_pv = self._pdev.substitute(propty='CtrlMode-Mon')

        self._trigname = self._devname.substitute(dis='TI')

    def _setup_ui(self):
        self.header_label = QLabel('<h1>' + self._devname + '</h1>')
        self.header_label.setObjectName('header_label')
        interlock_box = QGroupBox('Interlock', self)
        interlock_box.setObjectName('interlock_box')
        interlock_box.setLayout(self._interlock_layout())
        pwrstate_box = QGroupBox('Power', self)
        pwrstate_box.setObjectName('pwrstate_box')
        pwrstate_box.setLayout(self._pwrstate_layout())
        pulses_box = QGroupBox('Pulses', self)
        pulses_box.setObjectName('pulses_box')
        pulses_box.setLayout(self._pulses_layout())
        voltage_box = QGroupBox('Voltage', self)
        voltage_box.setObjectName('voltage_box')
        voltage_box.setLayout(self._voltage_layout())
        kick_box = QGroupBox('Kick', self)
        kick_box.setObjectName('kick_box')
        kick_box.setLayout(self._kick_layout())
        if 'NLK' in self._devname:
            ccvh_box = QGroupBox('C.Coil H Voltage', self)
            ccvh_box.setLayout(self._voltage_layout(coil='CCoilH'))
            cckh_box = QGroupBox('C.Coil H Kick', self)
            cckh_box.setLayout(self._kick_layout(coil='CCoilH'))
            ccvv_box = QGroupBox('C.Coil V Voltage', self)
            ccvv_box.setLayout(self._voltage_layout(coil='CCoilV'))
            cckv_box = QGroupBox('C.Coil V Kick', self)
            cckv_box.setLayout(self._kick_layout(coil='CCoilV'))
        timing_box = QGroupBox('Trigger', self)
        timing_box.setObjectName('timing_box')
        hbl = QHBoxLayout(timing_box)
        hbl.setContentsMargins(0, 0, 0, 0)
        show_deltadelay = 'NLK' in self._devname
        hbl.addWidget(HLTriggerSimple(
            timing_box, self._trigname, self._prefix, delay=False,
            delayraw=True, src=True, deltadelay=show_deltadelay,
            deltadelayraw=show_deltadelay))

        vbl1 = QVBoxLayout()
        vbl1.addWidget(pwrstate_box)
        vbl1.addWidget(pulses_box)

        gbl2 = QGridLayout()
        gbl2.addWidget(voltage_box, 0, 0)
        gbl2.addWidget(kick_box, 1, 0)
        if 'NLK' in self._devname:
            gbl2.addWidget(ccvh_box, 0, 1)
            gbl2.addWidget(cckh_box, 1, 1)
            gbl2.addWidget(ccvv_box, 0, 2)
            gbl2.addWidget(cckv_box, 1, 2)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.header_label, 0, 0, 1, 3)
        self.layout.addWidget(interlock_box, 1, 0, 3, 1)
        self.layout.addLayout(vbl1, 1, 1, 2, 1)
        self.layout.addLayout(gbl2, 1, 2, 2, 3)
        self.layout.addWidget(timing_box, 3, 1, 1, 4)
        self.layout.addLayout(self._ctrlmode_layout(), 4, 1, 1, 4)

    def _interlock_layout(self):
        interlock_layout = QGridLayout()

        intlk_cnt = 8 if 'Sept' not in self._devname else 7
        for i in range(intlk_cnt):
            label = SiriusLabel(
                self, getattr(self, '_intlk' + str(i+1) + '_lbcte_pv'))
            led = PyDMLed(
                self, getattr(self, '_intlk' + str(i+1) + '_mon_pv'))
            led.onColor = led.LightGreen
            led.offColor = led.Red
            interlock_layout.addWidget(led, i, 0)
            interlock_layout.addWidget(label, i, 1)

        self.reset_bt = PyDMPushButton(
            parent=self, init_channel=self._reset_cmd_pv, pressValue=1)
        self.reset_bt.setIcon(qta.icon('fa5s.sync'))
        self.reset_bt.setObjectName('reset_bt')
        self.reset_bt.setStyleSheet(
            '#reset_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        interlock_layout.addWidget(
            self.reset_bt, i+1, 0, 1, 2, alignment=Qt.AlignHCenter)

        return interlock_layout

    def _pwrstate_layout(self):
        pwrstate_layout = QHBoxLayout()

        self.state_button = PyDMStateButton(
            parent=self, init_channel=self._pwrstate_sel_pv)
        self.state_led = SiriusLedState(self, self._pwrstate_sts_pv)

        pwrstate_layout.addWidget(self.state_button)
        pwrstate_layout.addWidget(self.state_led)

        return pwrstate_layout

    def _pulses_layout(self):
        pulses_layout = QHBoxLayout()

        self.pulses_state_button = PyDMStateButton(
            parent=self, init_channel=self._enablepulses_sel_pv)
        self.pulses_state_led = SiriusLedState(
            parent=self, init_channel=self._enablepulses_sts_pv)

        pulses_layout.addWidget(self.pulses_state_button)
        pulses_layout.addWidget(self.pulses_state_led)

        return pulses_layout

    def _voltage_layout(self, coil=''):
        sp_pv = self._voltage_sp_pv.substitute(propty_name=coil+'Voltage')
        rb_pv = self._voltage_rb_pv.substitute(propty_name=coil+'Voltage')
        mon_pv = self._voltage_mon_pv.substitute(propty_name=coil+'Voltage')

        sp_widget = PyDMSpinboxScrollbar(self, sp_pv)
        rb_label = SiriusLabel(self, rb_pv, keep_unit=True)
        rb_label.showUnits = True
        mon_label = SiriusLabel(self, mon_pv, keep_unit=True)
        mon_label.showUnits = True

        lay = QFormLayout()
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignHCenter)
        lay.addRow('SP:', sp_widget)
        lay.addRow('RB:', rb_label)
        lay.addRow('Mon:', mon_label)
        return lay

    def _kick_layout(self, coil=''):
        sp_pv = self._kick_sp_pv.substitute(propty_name=coil+'Kick')
        rb_pv = self._kick_rb_pv.substitute(propty_name=coil+'Kick')
        mon_pv = self._kick_mon_pv.substitute(propty_name=coil+'Kick')

        sp_widget = PyDMSpinboxScrollbar(self, sp_pv)
        rb_label = SiriusLabel(self, rb_pv, keep_unit=True)
        rb_label.showUnits = True
        mon_label = SiriusLabel(self, mon_pv, keep_unit=True)
        mon_label.showUnits = True

        lay = QFormLayout()
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setFormAlignment(Qt.AlignHCenter)
        lay.addRow('SP:', sp_widget)
        lay.addRow('RB:', rb_label)
        lay.addRow('Mon:', mon_label)
        return lay

    def _ctrlmode_layout(self):
        ctrlmode_layout = QHBoxLayout()

        self.ctrlmode_led = SiriusLedAlert(
            parent=self, init_channel=self._ctrlmode_pv)
        self.ctrlmode_label = SiriusLabel(
            parent=self, init_channel=self._ctrlmode_pv)

        ctrlmode_layout.addStretch()
        ctrlmode_layout.addWidget(self.ctrlmode_led)
        ctrlmode_layout.addWidget(self.ctrlmode_label)

        return ctrlmode_layout


if __name__ == "__main__":
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication(None, sys.argv)
    w = PUDetailWidget(devname="SI-01SA:PM-InjDpKckr")
    w.show()
    sys.exit(app.exec_())
