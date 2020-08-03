#!/usr/bin/env python-sirius

import numpy as np

from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QGridLayout, QGroupBox, QFormLayout, \
    QWidget, QSpinBox, QVBoxLayout, QHBoxLayout, QPushButton

from pydm.widgets import PyDMTimePlot

from siriushla.widgets import SiriusSpinbox, PyDMStateButton, SiriusLabel, \
    SiriusLedState, SiriusProcessImage
from siriushla.as_ti_control import HLTriggerSimple


class EnergyMeasure(QWidget):
    """."""

    def __init__(self, parent=None):
        """."""
        super().__init__(parent=parent)
        self._setupUi()
        self.setObjectName('LIApp')

    def _setupUi(self):
        pref = 'LI-Glob:AP-MeasEnergy'
        gl = QGridLayout(self)
        self.plt_energy = PyDMTimePlot(
            self, init_y_channels=[pref+':Energy-Mon'],
            background=QColor('white'))
        gl.addWidget(self.plt_energy, 1, 0, 1, 2)
        self.plt_spread = PyDMTimePlot(
            self, init_y_channels=[pref+':Spread-Mon'],
            background=QColor('white'))
        gl.addWidget(self.plt_spread, 2, 0, 1, 2)

        self.plt_energy.setLabel('left', text='Energy [MeV]')
        self.plt_energy.setShowXGrid(True)
        self.plt_energy.setShowYGrid(True)
        c = self.plt_energy.curveAtIndex(0)
        c.color = QColor('blue')
        c.symbol = c.symbols['Circle']
        c.symbolSize = 10
        c.lineWidth = 3
        c.data_changed.connect(self._update_energy_stats)
        self.plt_energy.setTimeSpan(100)

        self.plt_spread.setLabel('left', text='Spread [%]')
        self.plt_spread.setShowXGrid(True)
        self.plt_spread.setShowYGrid(True)
        c = self.plt_spread.curveAtIndex(0)
        c.color = QColor('red')
        c.symbol = c.symbols['Circle']
        c.symbolSize = 10
        c.lineWidth = 3
        c.data_changed.connect(self._update_spread_stats)
        self.plt_spread.setTimeSpan(100)

        gb_ctrl = QGroupBox('Control', self)
        gb_ener = QGroupBox('Properties', self)
        gl.addWidget(gb_ctrl, 3, 0)
        gl.addWidget(gb_ener, 3, 1)
        hl_ctrl = QHBoxLayout(gb_ctrl)
        fl_ener = QFormLayout(gb_ener)

        vl = QVBoxLayout()
        wid = QWidget(gb_ctrl)
        wid.setLayout(QHBoxLayout())
        btn = PyDMStateButton(gb_ctrl, init_channel=pref+':MeasureCtrl-Sel')
        led = SiriusLedState(gb_ctrl, init_channel=pref+':MeasureCtrl-Sts')
        wid.layout().addWidget(btn)
        wid.layout().addWidget(led)
        vl.addWidget(QLabel('Start/Stop Acq.', gb_ctrl))
        vl.addWidget(wid)
        hl_ctrl.addItem(vl)

        vl = QVBoxLayout()
        wid = QWidget(gb_ctrl)
        wid.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(wid, init_channel='LI-01:PS-Spect:Current-SP')
        lbl = SiriusLabel(wid, init_channel='LI-01:PS-Spect:Current-Mon')
        spnbox.showStepExponent = False
        wid.layout().addWidget(spnbox)
        wid.layout().addWidget(lbl)
        vl.addWidget(QLabel('Spectrometer Current [A]', gb_ctrl))
        vl.addWidget(wid)
        hl_ctrl.addItem(vl)

        wid = QWidget(gb_ener)
        wid.setLayout(QHBoxLayout())
        self.lb_ave_en = QLabel('0.000', wid)
        self.lb_std_en = QLabel('0.000', wid)
        wid.layout().addWidget(self.lb_ave_en)
        wid.layout().addWidget(QLabel(
            '<html><head/><body><p>&#177;</p></body></html>', wid))
        wid.layout().addWidget(self.lb_std_en)
        fl_ener.addRow('Energy [MeV]', wid)

        wid = QWidget(gb_ener)
        wid.setLayout(QHBoxLayout())
        self.lb_ave_sp = QLabel('0.000', wid)
        self.lb_std_sp = QLabel('0.000', wid)
        wid.layout().addWidget(self.lb_ave_sp)
        wid.layout().addWidget(QLabel(
            '<html><head/><body><p>&#177;</p></body></html>', wid))
        wid.layout().addWidget(self.lb_std_sp)
        fl_ener.addRow('Spread [%]', wid)

        vl = QVBoxLayout()
        gl.addItem(vl, 0, 0, 1, 2)
        hl = QHBoxLayout()
        hl.setSpacing(0)
        self.spbox_npoints = QSpinBox(self)
        self.spbox_npoints.setKeyboardTracking(False)
        self.spbox_npoints.setMinimum(10)
        self.spbox_npoints.setMaximum(200000)
        self.spbox_npoints.setValue(100)
        self.spbox_npoints.editingFinished.connect(self.nrpoints_edited)
        hl.addWidget(QLabel('Choose TimeSpan [s]:', self))
        hl.addWidget(self.spbox_npoints)
        self.pb_reset_data = QPushButton('Reset Data', self)
        self.pb_reset_data.clicked.connect(self.pb_reset_data_clicked)
        hl.addWidget(self.pb_reset_data)
        vl.addItem(hl)

        self.plt_image = SiriusProcessImage(self, device=pref)
        gl.addWidget(self.plt_image, 0, 2, 3, 1)

        gb_trig = QGroupBox('Trigger', self)
        hbl = QHBoxLayout(gb_trig)
        hbl.addWidget(HLTriggerSimple(parent=self, prefix='LI-Fam:TI-Scrn'))
        gb_trig.setLayout(hbl)
        gl.addWidget(gb_trig, 3, 2)

    def _update_energy_stats(self):
        c = self.plt_energy.curveAtIndex(0)
        if c.points_accumulated:
            ener = np.array(c.data_buffer[1, -c.points_accumulated:])
            self.lb_ave_en.setText('{:.3f}'.format(np.mean(ener)))
            self.lb_std_en.setText('{:.3f}'.format(np.std(ener)))

    def _update_spread_stats(self):
        c = self.plt_spread.curveAtIndex(0)
        if c.points_accumulated:
            sprd = np.array(c.data_buffer[1, -c.points_accumulated:])
            self.lb_ave_sp.setText('{:.3f}'.format(np.mean(sprd)))
            self.lb_std_sp.setText('{:.3f}'.format(np.std(sprd)))

    def nrpoints_edited(self):
        val = self.spbox_npoints.value()
        self.plt_energy.setTimeSpan(val)
        self.plt_spread.setTimeSpan(val)

    def pb_reset_data_clicked(self):
        """."""
        c = self.plt_energy.curveAtIndex(0)
        c.points_accumulated = 0
        c = self.plt_spread.curveAtIndex(0)
        c.points_accumulated = 0
