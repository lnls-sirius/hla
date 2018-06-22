"""Booster Ramp Control HLA: Optics Adjust Module."""

from PyQt5.QtWidgets import QGroupBox, QGridLayout, QPushButton
from siriuspy.namesys import SiriusPVName as _PVName


class OpticsAdjust(QGroupBox):
    """Widget to perform optics adjust in normalized configurations."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Optics Configuration Adjustment', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout(self)
        self.bt_load = QPushButton('Load', self)
        self.bt_save = QPushButton('Save', self)
        self.bt_load.clicked.connect(self._load)
        self.bt_save.clicked.connect(self._save)
        glay.addWidget(self.bt_load, 0, 0)
        glay.addWidget(self.bt_save, 0, 1)

    def _load(self):
        print('Do stuff')

    def _save(self):
        print('Do stuff')
