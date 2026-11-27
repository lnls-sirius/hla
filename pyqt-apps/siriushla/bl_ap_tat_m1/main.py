"""BL AP TAT M1"""

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QWidget, QGroupBox, \
    QHBoxLayout, QVBoxLayout, QFrame, QLabel

from pydm.widgets import PyDMLabel

import qtawesome as qta

from ..widgets import SiriusLedState, SiriusPushButton, \
    SiriusSpinbox, PyDMLedMultiChannel
    
from .util import Mirror, DIRECTIONS


class BLTATMirror(QWidget):
    """TATU Mirror Control Window."""

    def __init__(self, mirror, parent=None):
        """."""
        super().__init__(parent=parent)
        self.device = mirror
        self.mirror = Mirror(self.device)
        self.setWindowTitle('TATU Mirror Control')
        self.setObjectName('IDApp')

        self.setMaximumSize(640, 340)
        self.setMinimumSize(640, 340)

        self._setupUi()

    def _setupUi(self):
        window_lay = QVBoxLayout()
        window_lay.setContentsMargins(0,0,0,0)
        main_lay = QVBoxLayout()
        main_lay.setContentsMargins(16,16,16,8)

        main_frame = QFrame()
        main_frame.setLayout(main_lay)

        title = QLabel("TATU M1 Control")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-weight: bold; font-size: 12pt;")
        title.setMaximumHeight(30)
        
        main_lay.addWidget(title)
        main_lay.addWidget(self._setupControl())

        window_lay.addWidget(main_frame)
        self.setLayout(window_lay)

    def _setupControl(self):
        control_lay = QVBoxLayout()

        control_frame = QFrame()
        control_frame.setLayout(control_lay)
        
        control_lay.addWidget(self._setupMirrorState())
        control_lay.addWidget(self._setupMotor())

        return control_frame

    def _setupMirrorState(self):
        mirror_state_lay = QHBoxLayout()

        mirror_state_frame = QGroupBox("Mirror state")
        mirror_state_frame.setLayout(mirror_state_lay)

        up_frame = self.set_elevate_bundle(DIRECTIONS['Up'])
        down_frame = self.set_elevate_bundle(DIRECTIONS['Down'])

        mirror_state_lay.addWidget(up_frame)
        mirror_state_lay.addWidget(down_frame)

        return mirror_state_frame

    def set_elevate_bundle(self, direction):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignCenter)

        frame.setToolTip(
            f"{direction['Name']} mirror motor position, sending to {direction['Value']} mm\n"
            f"Light Green Led -> Motor sensor activated\n"
             "Dark Green Led -> Motor out of desired position")

        limits = direction.get('Limits', {})
        ch2val = dict()
        for key, pv in limits.items():
            ch2val[pv] = {'value': True, 'comp': 'eq'}
        
        led = PyDMLedMultiChannel(self, channels2values=ch2val)
        led.setOffColor(SiriusLedState.DarkGreen)

        button = SiriusPushButton(
            init_channel=self.mirror.set)
        button.pressValue = direction['Value']
        button.setText(f" {direction['Name']}")
        button.setIcon(qta.icon(direction['Icon']))
        button.setIconSize(QSize(24,24))
        button.setMaximumSize(240, 30)
        button.setMinimumSize(240, 30)

        layout.addWidget(led)
        layout.addWidget(button)

        return frame

    def _setupMotor(self):
        motor_lay = QHBoxLayout()
        motor_frame = QGroupBox("Motor settings")
        motor_frame.setLayout(motor_lay)

        motor_lay.setContentsMargins(8,16,8,16)

        motor_lay.addWidget(self.set_setpoint_motor())
        motor_lay.addWidget(self.set_readback_motor())
        motor_lay.addWidget(self.set_enbl_status())
        motor_lay.addWidget(self.set_stop_motor())

        return motor_frame

    def set_setpoint_motor(self):
        motor_setpoint_lay = QVBoxLayout()
        motor_setpoint_frame = QFrame()
        motor_setpoint_frame.setLayout(motor_setpoint_lay)
        motor_setpoint_frame.setToolTip("Mirror motor setpoint")

        motor_setpoint_label = QLabel("Setpoint")
        motor_setpoint_label.setStyleSheet("font-weight: bold;")
        motor_setpoint_label.setAlignment(Qt.AlignHCenter)
        motor_setpoint_lay.addWidget(motor_setpoint_label)

        motor_spin = SiriusSpinbox(init_channel=self.mirror.set)
        motor_setpoint_lay.addWidget(motor_spin)

        return motor_setpoint_frame

    def set_readback_motor(self):
        motor_pos_lay = QVBoxLayout()
        motor_pos_frame = QFrame()
        motor_pos_frame.setLayout(motor_pos_lay)
        motor_pos_frame.setToolTip("Mirror motor position (RBV)")

        motor_pos_label = QLabel("Current Pos")
        motor_pos_label.setStyleSheet("font-weight: bold;")
        motor_pos_label.setAlignment(Qt.AlignHCenter)
        motor_pos_lay.addWidget(motor_pos_label)

        motor_pos = PyDMLabel(init_channel=self.mirror.rbv)
        motor_pos.setAlignment(Qt.AlignCenter)
        motor_pos.showUnits = True
        motor_pos_lay.addWidget(motor_pos)

        return motor_pos_frame

    def set_enbl_status(self):
        motor_enbl_lay = QVBoxLayout()
        motor_enbl_lay.setContentsMargins(9,9,9,12)
        motor_enbl_frame = QFrame()
        motor_enbl_frame.setLayout(motor_enbl_lay)
        motor_enbl_frame.setToolTip('Mirror motor enabled status')

        motor_enbl_label = QLabel("Motor Enabled")
        motor_enbl_label.setStyleSheet("font-weight: bold;")
        motor_enbl_label.setAlignment(Qt.AlignHCenter)
        motor_enbl_lay.addWidget(motor_enbl_label)

        motor_enbl_led = SiriusLedState(init_channel=self.mirror.enbl)
        motor_enbl_lay.addWidget(motor_enbl_led)

        return motor_enbl_frame

    def set_stop_motor(self):
        stop_motor_lay = QHBoxLayout()
        stop_motor_frame = QFrame()
        stop_motor_frame.setLayout(stop_motor_lay)

        stop_motor_btn = SiriusPushButton(
            init_channel=self.mirror.stop)
        stop_motor_btn.pressValue = 1
        stop_motor_btn.setText(" STOP")
        stop_motor_btn.setIcon(qta.icon('fa5.stop-circle'))
        stop_motor_btn.setIconSize(QSize(22,22))
        stop_motor_btn.setMaximumSize(80, 30)
        stop_motor_lay.addWidget(stop_motor_btn)

        return stop_motor_frame
