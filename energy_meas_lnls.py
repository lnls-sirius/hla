#!/usr/bin/env python-sirius

import os
import sys
import numpy as np
from epics import PV
from PyQt5.QtWidgets import (QMainWindow, QLabel, QGridLayout, QGroupBox,
                             QFormLayout, QMessageBox, QApplication,
                             QSizePolicy, QWidget, QComboBox, QSpinBox,
                             QVBoxLayout, QHBoxLayout, QCheckBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer, QSize, Qt, pyqtSlot
from pydm.application import PyDMApplication
from pydm.widgets import PyDMImageView, PyDMLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

from matplotlib import rcParams
from pyqtgraph import PlotCurveItem, mkPen
from scipy.optimize import curve_fit
from scipy.stats import norm

from utils import set_environ, MatplotlibWidget, ProcessImage

rcParams['font.size'] = 9

light_speed = 299792458
electron_rest_en = 0.5109989461  # in MeV
DT = 0.001


class EnergyMeasure(QWidget):
    DISP = 1.087
    I2BL = [-0.00015394, 0.02964633, -0.00354184]
    B_ANG = np.pi/4
    MAX_SPREAD = 2

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.energylist = []
        self.spreadlist = []
        self.bend_curr = PV('LA-CN:H1DPPS-1:seti')

        self._setupUi()

        self.t1 = QTimer()
        self.t1.timeout.connect(self.meas_energy)
        self.t1.start(500)

    def _setupUi(self):
        gl = QGridLayout(self)
        self.plt_energy = MatplotlibWidget(self)
        gl.addWidget(self.plt_energy, 0, 0, 1, 2)
        self.plt_spread = MatplotlibWidget(self)
        gl.addWidget(self.plt_spread, 1, 0, 1, 2)

        self.line_energy = self.plt_energy.axes.plot(
            self.energylist, '--bo', lw=1, label='Energy')[0]
        self.line_spread = self.plt_spread.axes.plot(
            self.spreadlist, '--ro', lw=1, label='Spread')[0]

        self.plt_energy.axes.set_xlabel('Index')
        self.plt_energy.axes.set_ylabel('Energy [MeV]')
        self.plt_energy.axes.grid(True)
        self.plt_energy.axes.set_aspect('auto')
        self.plt_energy.figure.set_tight_layout(True)

        self.plt_spread.axes.set_xlabel('Index')
        self.plt_spread.axes.set_ylabel('Spread [%]')
        self.plt_spread.axes.grid(True)
        self.plt_spread.axes.set_aspect('auto')
        self.plt_spread.figure.set_tight_layout(True)

        gb_en = QGroupBox('Energy [MeV]', self)
        gb_sp = QGroupBox('Spread [%]', self)
        gl.addWidget(gb_en, 2, 0)
        gl.addWidget(gb_sp, 2, 1)
        fl_en = QFormLayout(gb_en)
        fl_sp = QFormLayout(gb_sp)

        self.lb_ave_en = QLabel('0.000', gb_en)
        self.lb_std_en = QLabel('0.000', gb_en)
        fl_en.addRow('Average', self.lb_ave_en)
        fl_en.addRow('Deviation', self.lb_std_en)
        self.lb_ave_sp = QLabel('0.000', gb_sp)
        self.lb_std_sp = QLabel('0.000', gb_sp)
        fl_sp.addRow('Average', self.lb_ave_sp)
        fl_sp.addRow('Deviation', self.lb_std_sp)

        vl = QVBoxLayout()
        gl.addItem(vl, 0, 2, 3, 1)
        hl = QHBoxLayout()
        self.spbox_npoints = QSpinBox(self)
        self.spbox_npoints.setKeyboardTracking(False)
        self.spbox_npoints.setMinimum(10)
        self.spbox_npoints.setMaximum(200000)
        self.spbox_npoints.setValue(100)
        hl.addWidget(QLabel('Number of Points:', self))
        hl.addWidget(self.spbox_npoints)
        vl.addItem(hl)

        self.plt_image = ProcessImage(self)
        vl.addWidget(self.plt_image)

    def meas_energy(self):
        cen_x, sigma_x, cen_y, sigma_y = self.plt_image.get_params()
        if cen_x is None:
            return

        bend_curr = self.bend_curr.value
        if bend_curr is None:
            return
        BL = np.polyval(self.I2BL, abs(bend_curr))  # Must take abs of current
        nom_kin_en = BL/self.B_ANG*light_speed*1e-6  # in MeV
        kin_en = nom_kin_en * (1 - cen_x / self.DISP)
        energy = np.sqrt(kin_en**2 + electron_rest_en**2)

        spread = sigma_x / self.DISP * 100  # in percent%

        if spread >= self.MAX_SPREAD or spread <= 0:
            return

        self.energylist.append(energy)
        self.spreadlist.append(spread)
        npnts = self.spbox_npoints.value()
        if len(self.energylist) > npnts:
            self.energylist = self.energylist[-npnts-1:]
            self.spreadlist = self.spreadlist[-npnts-1:]

        yd = np.array(self.energylist)
        self.line_energy.set_xdata(np.arange(yd.shape[0]))
        self.line_energy.set_ydata(yd)
        self.plt_energy.axes.set_xlim([0, yd.shape[0]+0.1])
        self.plt_energy.axes.set_ylim([yd.min()*(1-DT), yd.max()*(1+DT)])
        self.plt_energy.figure.canvas.draw()
        self.lb_ave_en.setText('{0:.3f}'.format(yd.mean()))
        self.lb_std_en.setText(
            r'{0:.3f} ({1:.3f}%)'.format(yd.std(), yd.std()/yd.mean()*100))

        yd = np.array(self.spreadlist)
        self.line_spread.set_xdata(np.arange(yd.shape[0]))
        self.line_spread.set_ydata(yd)
        self.plt_spread.axes.set_xlim([0, yd.shape[0]+0.1])
        self.plt_spread.axes.set_ylim([yd.min()*(1-DT), yd.max()*(1+DT)])
        self.plt_spread.figure.canvas.draw()
        self.lb_ave_sp.setText('{0:.3f}'.format(yd.mean()))
        self.lb_std_sp.setText('{0:.3f}'.format(yd.std()))


    # def closeEvent(self, event):
    #     reply = QMessageBox.question(
    #         self, 'Message', u"Are you sure to quit?",
    #         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    #
    #     if reply == QMessageBox.Yes:
    #         event.accept()
    #         try:
    #             self.t1.stop()
    #         except Exception:
    #             pass
    #     else:
    #         event.ignore()


if __name__ == "__main__":
    set_environ()
    app = PyDMApplication(use_main_window=False)
    win = EnergyMeasure()
    win.show()
    sys.exit(app.exec_())
