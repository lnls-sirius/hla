"""LI LLRF Motor Control Windows."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QWidget, QLabel
from pydm.widgets import PyDMLineEdit
from ..widgets import SiriusLabel, SiriusMainWindow, PyDMLedMultiChannel, \
    SiriusPushButton, PyDMStateButton, SiriusSpinbox
from .util import MOTOR_CONTROL


class MotorControlWindow(SiriusMainWindow):
    """Motor Control Window of the SHB and HPPS."""

    def __init__(self, parent=None, motor_type="SHB"):
        """Init."""
        super().__init__(parent)
        self.main_dev = 'LA-RF:LLRF:'
        self.motor_type = motor_type
        self.setObjectName('LIApp')
        self.setWindowTitle(motor_type + ' Control')
        self.setMaximumHeight(250)
        self.setMinimumHeight(175)

        self._setupUi()

    def buildLed(self, pv_name=''):
        """Build a led widget"""
        config = 0
        if "ST" in pv_name:
            config = 1
        ch2vals = {
            pv_name: config}
        led = PyDMLedMultiChannel(self)
        led.set_channels2values(ch2vals)
        return led

    def getWidget(self, wid_type='', pv_name=''):
        """Get the selected widget"""
        if wid_type == 'led':
            widget = self.buildLed(pv_name)
        elif wid_type == 'button':
            widget = SiriusPushButton(
                label="Enable",
                init_channel=pv_name,
                pressValue=1,
                releaseValue=0)
        elif wid_type == 'label':
            widget = SiriusLabel(
                init_channel=pv_name)
            widget.showUnits = True
        elif wid_type == 'spinBox':
            widget = SiriusSpinbox(
                init_channel=pv_name)
            widget.showStepExponent = False
        elif wid_type == 'state':
            widget = PyDMStateButton(
                init_channel=pv_name)
        else:
            widget = PyDMLineEdit(
                init_channel=pv_name)
        return widget

    def ledBox(self, main_title='', data=None, basename=''):
        """Show all the leds PVs of a dict"""
        lb_glay = QGridLayout()
        pos = [0, 0]
        lb_glay.addWidget(
            QLabel(main_title), pos[0], pos[1], 1, 2,
            alignment=Qt.AlignCenter)
        for title, name in data.items():
            pos[0] += 1
            lb_glay.addWidget(
                QLabel(title), pos[0], pos[1],
                alignment=Qt.AlignRight)
            lb_glay.addWidget(
                self.getWidget('led', basename + name),
                pos[0], pos[1] + 1,
                alignment=Qt.AlignLeft)
        return lb_glay, pos

    def infoBox(self, title='', pv_name=''):
        """Show general control information (Besides the leds)"""
        ib_hlay = QHBoxLayout()

        if title == "Up to Limit" and self.motor_type == "HPPS":
            title = "Up to Zero"

        ib_hlay.addWidget(
            QLabel(title), alignment=Qt.AlignRight)

        if "Up to" in title:
            wid_type = 'button'
        else:
            wid_type = 'label'

        ib_hlay.addWidget(
            self.getWidget(wid_type, pv_name),
            alignment=Qt.AlignLeft)
        return ib_hlay

    def rbvBox(self):
        """Show a RBV Widget"""
        rbv_hlay = QHBoxLayout()
        basename = self.main_dev + "KLY1"
        rbv_hlay.addWidget(
            QLabel("Phase"),
            alignment=Qt.AlignRight)
        for pv_name in MOTOR_CONTROL[self.motor_type]:
            wid_type = 'label'
            align = Qt.AlignLeft
            if 'SET' in pv_name:
                wid_type = 'spinBox'
                align = Qt.AlignCenter
            widget = self.getWidget(
                wid_type, basename + pv_name)
            rbv_hlay.addWidget(
                widget,
                alignment=align)
        return rbv_hlay

    def pidBox(self):
        """Show the PID control widgets"""
        pb_glay = QGridLayout()
        pos = [0, 0]
        for title, pv_name in MOTOR_CONTROL["SHB"].items():
            if pv_name == ":FL":
                basedev = "SHB"
            else:
                basedev = "BUN1"

            pb_glay.addWidget(
                QLabel(title), pos[0], pos[1],
                alignment=Qt.AlignRight)
            pos[1] += 1

            if "PID" in title:
                wid_type = 'state'
            elif "K" in title:
                wid_type = 'label'
            else:
                wid_type = 'edit'

            pb_glay.addWidget(
                self.getWidget(
                    wid_type, self.main_dev + basedev + pv_name),
                pos[0], pos[1],
                alignment=Qt.AlignLeft)
            pos[1] += 1

            if pos[1] >= 4:
                pos[1] = 0
                pos[0] += 1
        return pb_glay

    def basicData(self, pos=None, lay=None):
        """Show all the general control information"""
        basename = self.main_dev + self.motor_type
        max_row = pos[0] + 2
        for title, data in MOTOR_CONTROL["General"].items():
            if title in ["Status", "Limits"]:
                lb_glay, pos_temp = self.ledBox(title, data, basename)
                pos[0] += pos_temp[0]
                pos[1] += pos_temp[1]
                lay.addLayout(
                    lb_glay,
                    pos[0], pos[1], 1, 1,
                    alignment=Qt.AlignTop)
            else:
                lay.addLayout(
                    self.infoBox(title, basename + data),
                    pos[0], pos[1], 1, 1,
                    alignment=Qt.AlignCenter)
                pos[0] += 1
            if pos[0] >= max_row:
                pos[0] = 1
                pos[1] += 1
        return pos

    def _setupUi(self):
        """Show the selected Control Window"""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay = QGridLayout()
        wid.setLayout(lay)
        pos = [0, 0]

        if self.motor_type == 'HPPS':
            widget = self.rbvBox()
        if self.motor_type == 'SHB':
            widget = self.pidBox()

        lay.addLayout(
            widget, pos[0], pos[1], 1, 2)
        pos[0] += 1

        pos = self.basicData(pos, lay)
