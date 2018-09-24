"""Booster Ramp Control HLA: General Status Module."""

from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, \
                            QSizePolicy as QSzPlcy, QSpacerItem
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSlot
from siriushla.widgets import QLed
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, \
                               ConnTiming as _ConnTiming, \
                               ConnRF as _ConnRF


DarkGreen = QColor(20, 80, 10)


class GeneralStatus(QGroupBox):
    """Widget to show general Booster timing and magnets status."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__('General Status', parent)
        self.prefix = _PVName(prefix)
        self._conn_magnets = None
        self._conn_timing = None
        self._conn_rf = None
        self._setupUi()

    def _setupUi(self):
        label_timing = QLabel('<h4>TI</h4>', self, alignment=Qt.AlignCenter)
        label_magnets = QLabel('<h4>MA</h4>', self, alignment=Qt.AlignCenter)
        label_rf = QLabel('<h4>RF</h4>', self, alignment=Qt.AlignCenter)
        label_conn = QLabel('Connection', self)
        label_ramping = QLabel('Configured to Ramp', self)

        for led_name in ['led_conntiming', 'led_ti_ramping',
                         'led_connmagnets', 'led_ma_ramping',
                         'led_connrf', 'led_rf_ramping']:
            setattr(self, led_name, QLed(self))
            led = getattr(self, led_name)
            led.setOffColor(DarkGreen)
            led.state = False
            led.setFixedSize(40, 40)

        glay = QGridLayout()
        glay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 0)
        glay.addWidget(label_conn, 2, 1)
        glay.addWidget(label_ramping, 3, 1)
        glay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 2)
        glay.addWidget(label_timing, 1, 3)
        glay.addWidget(self.led_conntiming, 2, 3)
        glay.addWidget(self.led_ti_ramping, 3, 3)
        glay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 4)
        glay.addWidget(label_magnets, 1, 5)
        glay.addWidget(self.led_connmagnets, 2, 5)
        glay.addWidget(self.led_ma_ramping, 3, 5)
        glay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 6)
        glay.addWidget(label_rf, 1, 7)
        glay.addWidget(self.led_connrf, 2, 7)
        glay.addWidget(self.led_rf_ramping, 3, 7)
        glay.addItem(QSpacerItem(40, 40, QSzPlcy.Fixed, QSzPlcy.Fixed), 5, 8)
        self.setLayout(glay)

    def updateMagnetsConnState(self):
        """Update magnets connection state led."""
        self.led_connmagnets.state = self._conn_magnets.connected

    def updateTimingConnState(self):
        """Update timing connection state led."""
        self.led_conntiming.state = self._conn_timing.connected

    def updateRFConnState(self):
        """Update RF connection state led."""
        self.led_connrf.state = self._conn_rf.connected

    def updateMagnetsOpModeState(self):
        """Update magnets operational mode state led."""
        self.led_ma_ramping.state = self._conn_magnets.check_opmode_rmpwfm()

    def updateTimingOpModeState(self):
        """Update timing operational mode state led."""
        self.label_ti_ramping.state = self._conn_timing.check_ramp()

    def updateRFOpModeState(self):
        """Update RF operational mode state led."""
        self.label_rf_ramping.state = self._conn_rf.check_ramp()

    @pyqtSlot(_ConnMagnets, _ConnTiming, _ConnRF)
    def getConnectors(self, conn_magnet, conn_timing, conn_rf):
        """Receive connectors."""
        self._conn_magnets = conn_magnet
        self._conn_timing = conn_timing
        self._conn_rf = conn_rf
