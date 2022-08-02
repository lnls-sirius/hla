"""LI LLRF Motor Control Windows."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QWidget, QLabel
from pydm.widgets import PyDMSpinbox
from ..widgets import SiriusLabel, SiriusMainWindow, PyDMLedMultiChannel, SiriusPushButton
from .util import MOTOR_CONTROL

class MotorControlWindow(SiriusMainWindow):
    """Motor Control Window."""

    def __init__(self, parent=None, motor_type="SHB"):
        """Init."""
        super().__init__(parent)
        self.prefix = 'LA-RF:LLRF:'
        self.motor_type = motor_type
        self.setObjectName('LIApp')
        self.setWindowTitle(motor_type + ' Control')

        self._setupUi()

    def buildLed(self, pv_name=''):
        config = 0
        if "ST" in pv_name:
            config = 1

        ch2vals = {
            pv_name: config}
        led = PyDMLedMultiChannel(self)
        led.set_channels2values(ch2vals)
        return led

    def ledBox(self, data=None, pos=None, basename='', lay=None):
        for title, name in data.items():
            lay.addWidget(
                QLabel(title), pos[0], pos[1], 1, 1,
                alignment=Qt.AlignCenter)
            lay.addWidget(
                self.buildLed(basename + name), pos[0], pos[1]+1, 1, 1,
                alignment=Qt.AlignCenter)
            pos[0] += 1
        return pos

    def infoBox(self, title='', pv_name='', pos=[0, 0], lay=None):
        lay.addWidget(
            QLabel(title), pos[0], pos[1], 1, 1,
            alignment=Qt.AlignCenter)
        if title == "Absolute Position":
            widget = SiriusLabel(
                init_channel=pv_name)
            widget.showUnits = True
        else:
            widget = SiriusPushButton(
                label="Enable",
                init_channel=pv_name,
                pressValue=1,
                releaseValue=0)

        lay.addWidget(
            widget, pos[0], pos[1]+1, 1, 1,
            alignment=Qt.AlignCenter)

    def rbvBox(self, pos=None, lay=None):
        basename = self.prefix + "KLY1"
        lay.addWidget(
            QLabel("Phase"), pos[0], pos[1], 1, 2,
            alignment=Qt.AlignCenter)
        widget = PyDMSpinbox(
                init_channel=basename+MOTOR_CONTROL[self.motor_type][0])
        widget.showStepExponent = False
        lay.addWidget(
            widget,
            pos[0], pos[1]+2, 1, 1,
            alignment=Qt.AlignCenter)
        lay.addWidget(
            SiriusLabel(
                init_channel=basename+MOTOR_CONTROL[self.motor_type][1]),
            pos[0], pos[1]+3, 1, 1,
            alignment=Qt.AlignCenter)

    def basicData(self, pos=None, lay=None):
        basename = self.prefix + self.motor_type
        for title, data in MOTOR_CONTROL["General"].items():
            print(pos)
            if title in ["Status", "Limits"]:
                lay.addWidget(
                    QLabel(title), pos[0], pos[1], 1, 2,
                    alignment=Qt.AlignCenter)
                pos[0] += 1
                pos = self.ledBox(data, pos, basename, lay)
            else:
                self.infoBox(title, basename+data, pos, lay)

                pos[0] += 1
            if pos[0] >= 3:
                pos[0] = 1
                pos[1] += 2


    def _setupUi(self):
        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay = QGridLayout()
        wid.setLayout(lay)

        pos = [0, 0]
        if self.motor_type == 'HPPS':
            self.rbvBox(pos, lay)

        pos[0] += 1
        self.basicData(pos, lay)
