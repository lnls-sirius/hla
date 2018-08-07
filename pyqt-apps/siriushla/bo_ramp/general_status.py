"""Booster Ramp Control HLA: General Status Module."""

from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, \
                            QSizePolicy as QSzPlcy, QSpacerItem
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSlot
from siriushla.widgets import QLed
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, \
                               ConnTiming as _ConnTiming


DarkGreen = QColor(20, 80, 10)


class GeneralStatus(QGroupBox):
    """Widget to show general Booster timing and magnets status."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__('General Status', parent)
        self.prefix = _PVName(prefix)
        self._conn_magnets = None
        self._conn_timing = None
        self._setupUi()

    def _setupUi(self):
        label_timing = QLabel('<h4>Timing</h4>', self)
        label_timing.setAlignment(Qt.AlignCenter)
        label_conntiming = QLabel('Connection', self)
        self.led_conntiming = QLed(self)
        self.led_conntiming.setOffColor(DarkGreen)
        self.led_conntiming.state = False
        self.led_conntiming.setFixedSize(40, 40)

        label_ti_cycling = QLabel('Configured to Cycle', self)
        self.led_ti_cycling = QLed(self)
        self.led_ti_cycling.setOffColor(DarkGreen)
        self.led_ti_cycling.state = False
        self.led_ti_cycling.setFixedSize(40, 40)

        label_ti_ramping = QLabel('Configured to Ramp', self)
        self.led_ti_ramping = QLed(self)
        self.led_ti_ramping.setOffColor(DarkGreen)
        self.led_ti_ramping.state = False
        self.led_ti_ramping.setFixedSize(40, 40)

        label_magnets = QLabel('<h4>Magnets</h4>', self)
        label_magnets.setAlignment(Qt.AlignCenter)
        label_conntmagnets = QLabel('Connection', self)
        self.led_connmagnets = QLed(self)
        self.led_connmagnets.setOffColor(DarkGreen)
        self.led_connmagnets.state = False
        self.led_connmagnets.setFixedSize(40, 40)

        label_ma_cycling = QLabel('OpMode Cycle', self)
        self.led_ma_cycling = QLed(self)
        self.led_ma_cycling.setOffColor(DarkGreen)
        self.led_ma_cycling.state = False
        self.led_ma_cycling.setFixedSize(40, 40)

        label_ma_ramping = QLabel('OpMode RampWfm', self)
        self.led_ma_ramping = QLed(self)
        self.led_ma_ramping.setOffColor(DarkGreen)
        self.led_ma_ramping.state = False
        self.led_ma_ramping.setFixedSize(40, 40)

        lay = QGridLayout()
        lay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 0, 0)
        lay.addWidget(label_timing, 1, 0, 1, 2)
        lay.addWidget(label_conntiming, 2, 0)
        lay.addWidget(self.led_conntiming, 2, 1)
        lay.addWidget(label_ti_cycling, 3, 0)
        lay.addWidget(self.led_ti_cycling, 3, 1)
        lay.addWidget(label_ti_ramping, 4, 0)
        lay.addWidget(self.led_ti_ramping, 4, 1)
        lay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 5, 0)
        lay.addWidget(label_magnets, 6, 0, 1, 2)
        lay.addWidget(label_conntmagnets, 7, 0)
        lay.addWidget(self.led_connmagnets, 7, 1)
        lay.addWidget(label_ma_cycling, 8, 0)
        lay.addWidget(self.led_ma_cycling, 8, 1)
        lay.addWidget(label_ma_ramping, 9, 0)
        lay.addWidget(self.led_ma_ramping, 9, 1)
        lay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 10, 0)

        self.setLayout(lay)
        self.setMaximumHeight(450)

    def updateMagnetsConnState(self):
        """Update magnets connection state led."""
        self.led_connmagnets.state = self._conn_magnets.connected

    def updateTimingConnState(self):
        """Update timing connection state led."""
        self.led_conntiming.state = self._conn_timing.connected

    def updateMagnetsOpModeState(self):
        """Update magnets operational mode state led."""
        self.led_ma_cycling.state = self._conn_magnets.check_opmode_cycle()
        self.led_ma_ramping.state = self._conn_magnets.check_opmode_rmpwfm()

    def updateTimingOpModeState(self):
        """Update timing operational mode state led."""
        self.led_ti_cycling.state = self._conn_timing.check_cycle()
        self.label_ti_ramping.state = self._conn_timing.check_ramp()

    @pyqtSlot(_ConnMagnets, _ConnTiming)
    def getConnectors(self, conn_magnet, conn_timing):
        """Receive connectors."""
        self._conn_magnets = conn_magnet
        self._conn_timing = conn_timing
