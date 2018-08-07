"""Booster Ramp Control HLA: Ramp Statistics Module."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGroupBox, QLabel, QPushButton, \
                            QVBoxLayout, QGridLayout, \
                            QSpacerItem, QSizePolicy as QSzPlcy
from pydm.widgets import PyDMLabel, PyDMWaveformPlot
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName


class RampStatistics(QGroupBox):
    """Widget to ramp status monitoring."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Statistics', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        glay_nrcycles = QGridLayout()
        l_nrcycles = QLabel('# of cycles:', self, alignment=Qt.AlignRight)
        self.pydmlabel_nrcycles = PyDMLabel(
            parent=self,
            init_channel='ca://'+_vaca_prefix+'BO-35D:DI-DCCT:NrCycles-Mon')
        self.pb_resetcycles = QPushButton('Reset', self)
        self.pb_resetcycles.clicked.connect(self._handleResetNrCycles)
        glay_nrcycles.addWidget(l_nrcycles, 0, 0)
        glay_nrcycles.addWidget(self.pydmlabel_nrcycles, 0, 1)
        glay_nrcycles.addWidget(self.pb_resetcycles, 1, 1)

        l_boocurr = QLabel('<h4>Booster Current</h4>',
                           alignment=Qt.AlignCenter)
        l_injcurr = QLabel('Injected [mA]:', self, alignment=Qt.AlignRight)
        self.pydmlabel_injcurr = PyDMLabel(
            parent=self,
            init_channel='ca://'+_vaca_prefix+'BO-35D:DI-DCCT:InjCurr-Mon')
        l_ejecurr = QLabel('Ejected [mA]:', self, alignment=Qt.AlignRight)
        self.pydmlabel_ejecurr = PyDMLabel(
            parent=self,
            init_channel='ca://'+_vaca_prefix+'BO-35D:DI-DCCT:EjeCurr-Mon')
        l_rampeff = QLabel('Efficiency [%]:', self, alignment=Qt.AlignRight)
        self.pydmlabel_rampeff = PyDMLabel(
            parent=self,
            init_channel='ca://'+_vaca_prefix+'BO-35D:DI-DCCT:RampEff-Mon')
        glay_boocurr = QGridLayout()
        glay_boocurr.addWidget(l_boocurr, 0, 0, 1, 2)
        glay_boocurr.addWidget(l_injcurr, 1, 0)
        glay_boocurr.addWidget(self.pydmlabel_injcurr, 1, 1)
        glay_boocurr.addWidget(l_ejecurr, 2, 0)
        glay_boocurr.addWidget(self.pydmlabel_ejecurr, 2, 1)
        glay_boocurr.addWidget(l_rampeff, 3, 0)
        glay_boocurr.addWidget(self.pydmlabel_rampeff, 3, 1)

        self.graph = PyDMWaveformPlot(self)
        self.graph.autoRangeX = True
        self.graph.autoRangeY = True
        self.graph.backgroundColor = QColor(255, 255, 255)
        self.graph.showLegend = False
        self.graph.showXGrid = True
        self.graph.showYGrid = True
        self.graph.title = 'Ramp efficiency per number of cycles'
        self.graph.setMinimumSize(500, 300)
        self.graph.addChannel(
            y_channel='ca://' + _vaca_prefix + 'BO-35D:DI-DCCT:RampEff-Mon',
            name='Efficiency', color='blue', lineWidth=2)

        vlay = QVBoxLayout(self)
        vlay.setAlignment(Qt.AlignCenter)
        vlay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        vlay.addLayout(glay_nrcycles)
        vlay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        vlay.addLayout(glay_boocurr)
        vlay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        vlay.addWidget(self.graph)
        vlay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))

    def _handleResetNrCycles(self):
        # TODO
        pass
