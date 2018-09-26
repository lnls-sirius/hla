"""Booster Ramp Control HLA: Ramp Statistics Module."""

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGroupBox, QLabel, QPushButton,\
                            QGridLayout, QSpacerItem, QSizePolicy as QSzPlcy
from pydm.widgets import PyDMWaveformPlot
from siriuspy.envars import vaca_prefix as _vaca_prefix


class Statistics(QGroupBox):
    """Widget to ramp status monitoring."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Statistics', parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._wavEff = []
        self._wavXStack = []
        self._wavYStack = []
        self._injcurr_idx = 0
        self._ejecurr_idx = -1
        self._setupUi()

    def _setupUi(self):
        l_boocurr = QLabel('<h4>Booster Current (mA)</h4>', self,
                           alignment=Qt.AlignCenter)
        l_injcurr = QLabel('Injected:', self, alignment=Qt.AlignRight)
        self.label_injcurr = QLabel(self)
        l_ejecurr = QLabel('Ejected:', self, alignment=Qt.AlignRight)
        self.label_ejecurr = QLabel(self)

        self.graph_boocurr = PyDMWaveformPlot(
            parent=self, init_y_channels=[
                'ca://'+_vaca_prefix+'BO-35D:DI-DCCT:CurrHstr-Mon'])
        self.graph_boocurr.autoRangeX = True
        self.graph_boocurr.autoRangeY = True
        self.graph_boocurr.backgroundColor = QColor(255, 255, 255)
        self.graph_boocurr.showLegend = False
        self.graph_boocurr.showXGrid = True
        self.graph_boocurr.showYGrid = True
        self.graph_boocurr.setLabels(left='<h3>Current</h3>',
                                     bottom='<h3>Ramp Index</h3>')
        self.graph_boocurr.setMinimumSize(600, 400)
        leftAxis = self.graph_boocurr.getAxis('left')
        leftAxis.setStyle(autoExpandTextSpace=False, tickTextWidth=25)
        self.curveCurrHstr = self.graph_boocurr.curveAtIndex(0)
        self.curveCurrHstr.data_changed.connect(self._updateRampEffGraph)

        l_rampeff = QLabel('<h4>Ramp Efficiency (%):</h4>', self,
                           alignment=Qt.AlignRight)
        self.label_rampeff = QLabel(self)

        self.graph_rampeff = PyDMWaveformPlot(self)
        self.graph_rampeff.autoRangeX = True
        self.graph_rampeff.autoRangeY = True
        self.graph_rampeff.backgroundColor = QColor(255, 255, 255)
        self.graph_rampeff.showLegend = False
        self.graph_rampeff.showXGrid = True
        self.graph_rampeff.showYGrid = True
        self.graph_rampeff.setLabels(left='<h3>Ramp Efficiency</h3>',
                                     bottom='<h3>Number of cycles</h3>')
        self.graph_rampeff.setMinimumSize(600, 400)
        self.graph_rampeff.addChannel(
            y_channel='ca://FAKE:RampEff-Mon', name='Efficiency',
            color='blue', lineWidth=2, lineStyle=Qt.SolidLine)
        self.graph_rampeff.addChannel(
            y_channel='ca://FAKE:Stacks-Mon', name='Stacks',
            color='red', lineStyle=Qt.NoPen, symbol='o', symbolSize=10)
        leftAxis = self.graph_rampeff.getAxis('left')
        leftAxis.setStyle(autoExpandTextSpace=False, tickTextWidth=25)
        self.curveEff = self.graph_rampeff.curveAtIndex(0)
        self.curveStacks = self.graph_rampeff.curveAtIndex(1)

        self.pb_addStack = QPushButton('Add to stack', self)
        self.pb_addStack.clicked.connect(self._addStack)
        self.pb_addStack.setFixedWidth(300)
        self.pb_addStack.setVisible(False)  # temporary, TODO
        self.pb_resetGraph = QPushButton('Reset graph', self)
        self.pb_resetGraph.clicked.connect(self._resetGraph)
        self.pb_resetGraph.setFixedWidth(300)

        glay = QGridLayout()
        glay.setAlignment(Qt.AlignHCenter)
        glay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 0)
        glay.addWidget(l_boocurr, 1, 1, 1, 2)
        glay.addWidget(l_injcurr, 2, 1)
        glay.addWidget(self.label_injcurr, 2, 2)
        glay.addWidget(l_ejecurr, 3, 1)
        glay.addWidget(self.label_ejecurr, 3, 2)
        glay.addWidget(self.graph_boocurr, 4, 1, 1, 2)
        glay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 5, 0)
        glay.addWidget(l_rampeff, 6, 1)
        glay.addWidget(self.label_rampeff, 6, 2)
        glay.addWidget(self.graph_rampeff, 7, 1, 1, 2)
        glay.addWidget(self.pb_addStack, 8, 1)
        glay.addWidget(self.pb_resetGraph, 8, 2)
        glay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 9, 3)
        self.setLayout(glay)

    def _updateRampEffGraph(self):
        if self.curveCurrHstr.yData is not None:
            curr_hstr = self.curveCurrHstr.yData
            # TODO: on settings: choose current waveform indices to calc eff
            inj_curr = curr_hstr[self._injcurr_idx]
            eje_curr = curr_hstr[self._ejecurr_idx]
            self._wavEff.append(eje_curr/inj_curr)
            self.label_injcurr.setText(inj_curr)
            self.label_ejecurr.setText(eje_curr)
            self.label_rampeff.setText(eje_curr/inj_curr)
            self.curveEff.receiveYWaveform(np.array(self._wavEff))
            self.curveEff.redrawCurve()

    def _addStack(self):
        if len(self._wavEff):
            self._wavXStack.append(len(self._wavEff)-1)
            self._wavYStack.append(self._wavEff[-1])
            self.curveStacks.receiveXWaveform(np.array(self._wavXStack))
            self.curveStacks.receiveYWaveform(np.array(self._wavYStack))
            self.curveStacks.redrawCurve()
        # TODO: generate signal to save current BoosterRamp config in a stack

    def _resetGraph(self):
        self._wavXStack.clear()
        self._wavYStack.clear()
        self._wavEff.clear()
        self.curveEff.receiveYWaveform(np.array(self._wavEff))
        self.curveStacks.receiveXWaveform(np.array(self._wavXStack))
        self.curveStacks.receiveYWaveform(np.array(self._wavYStack))
        self.graph_rampeff.redrawPlot()

    def handleUpdateSettings(self, settings):
        """Handle update indeces to calculate ramp efficiency."""
        self._injcurr_idx = settings[0]
        self._ejecurr_idx = settings[1]
