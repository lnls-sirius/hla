#!/usr/bin/env python-sirius

import os
import sys
import numpy as np
import time
from threading import Thread
from epics import PV
from PyQt5.QtWidgets import (QPushButton, QLabel, QGridLayout, QGroupBox,
                             QFormLayout, QMessageBox, QApplication,
                             QSizePolicy, QWidget, QComboBox, QSpinBox,
                             QVBoxLayout, QHBoxLayout, QDoubleSpinBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer, QSize, Qt
from pydm.application import PyDMApplication
from pydm.widgets import PyDMImageView, PyDMLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

from matplotlib import rcParams
from pyqtgraph import PlotCurveItem, mkPen
from scipy.optimize import curve_fit
from scipy.stats import norm

from utils import set_environ, MatplotlibWidget, ProcessImage, gettransmat

rcParams['font.size'] = 9

light_speed = 299792458
electron_rest_en = 0.5109989461  # in MeV
DT = 0.001


class EmittanceMeasure(QWidget):
    I2K1 = [-0.0089, 2.1891, 0.0493]
    QUAD = 'H1FQPS-3'
    DIST = 2.8775
    QUAD_L = 0.05

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.quad_I_sp = PV('LA-CN:' + self.QUAD + ':seti')
        self.quad_I_rb = PV('LA-CN:' + self.QUAD + ':rdi')
        self.nemitx_tm = []
        self.nemity_tm = []
        self.nemitx_parf = []
        self.nemity_parf = []
        self.betax_tm = []
        self.betay_tm = []
        self.betax_parf = []
        self.betay_parf = []
        self.alphax_tm = []
        self.alphay_tm = []
        self.alphax_parf = []
        self.alphay_parf = []

        self._setupUi()

    def meas_emittance(self):
        energy = self.spbox_energy.value()
        samples = self.spbox_samples.value()
        nsteps = self.spbox_steps.value()
        I_ini = self.spbox_I_ini.value()
        I_end = self.spbox_I_end.value()

        curr_list = np.linspace(I_ini, I_end, nsteps)
        sigmax = []
        sigmay = []
        I_meas = []
        for I in curr_list:
            print('setting Quadrupole to ', I)
            self.quad_I_sp.put(I, wait=True)
            time.sleep(5)
            j = 0
            while j < samples:
                print('measuring sample', j)
                if not self._measuring:
                    return
                I_now = self.quad_I_rb.value
                cen_x, sigma_x, cen_y, sigma_y = self.plt_image.get_params()
                max_size = self.spbox_threshold.value()*1e-3
                if sigma_x > max_size or sigma_y > max_size:
                    time.sleep(1)
                    continue
                I_meas.append(I_now)
                sigmax.append(sigma_x)
                sigmay.append(sigma_y)
                all = sigmax + sigmay
                self.line_sigmax.set_xdata(I_meas)
                self.line_sigmax.set_ydata(np.array(sigmax)*1e3)
                self.line_sigmay.set_xdata(I_meas)
                self.line_sigmay.set_ydata(np.array(sigmay)*1e3)
                self.plt_sigma.axes.set_xlim(
                        [min(I_meas)*(1-DT), max(I_meas)*(1+DT)])
                self.plt_sigma.axes.set_ylim(
                        [min(all)*(1-DT), max(all)*(1+DT)])
                self.plt_sigma.figure.canvas.draw()
                time.sleep(0.5)
                j += 1

        kin_en = np.sqrt(energy*energy - electron_rest_en*electron_rest_en)
        K1 = np.polyval(self.I2K1, I_meas)*light_speed/kin_en/1e6
        sigmax = np.array(sigmax)
        sigmay = np.array(sigmay)

        # Method 1: Transfer Matrix
        nemitx, betax, alphax = self._trans_matrix_method(K1, sigmax, energy)
        nemity, betay, alphay = self._trans_matrix_method(K1, sigmay, energy)
        self.nemitx_tm.append(nemitx)
        self.nemity_tm.append(nemity)
        self.betax_tm.append(betax)
        self.betay_tm.append(betay)
        self.alphax_tm.append(alphax)
        self.alphay_tm.append(alphay)
        # Method 2: Parabola Fitting
        nemitx, betax, alphax = self._thin_lens_method(K1, sigmax, energy)
        nemity, betay, alphay = self._thin_lens_method(K1, sigmay, energy)
        self.nemitx_parf.append(nemitx)
        self.nemity_parf.append(nemity)
        self.betax_parf.append(betax)
        self.betay_parf.append(betay)
        self.alphax_parf.append(alphax)
        self.alphay_parf.append(alphay)

        for pref in ('nemit', 'beta', 'alpha'):
            all = []
            for var in ('x_tm', 'y_tm', 'x_parf', 'y_parf'):
                tp = pref + var
                all.extend(getattr(self, tp))
                yd = np.array(getattr(self, tp))
                line = getattr(self, 'line_'+tp)
                line.set_xdata(np.arange(yd.shape[0]))
                line.set_ydata(yd)
                lb = getattr(self, 'lb_'+tp)
                lb.setText('{0:.3f}'.format(yd.mean()))
            all = np.array(all)
            plt = getattr(self, 'plt_' + pref)
            plt.axes.set_xlim([0, all.shape[0]+0.1])
            plt.axes.set_ylim([all.min()*(1-DT), all.max()*(1+DT)])
            plt.figure.canvas.draw()

        self._measuring = False
        self.pb_stop.setEnabled(False)
        self.pb_start.setEnabled(True)

    def _trans_matrix_method(self, K1, sigma, energy):
        Rx, Ry = self._get_resp_mat(K1, energy)
        a, b, c = np.linalg.lstsq(self.Rx, sigma*sigma)[0]
        emit = np.sqrt(abs(a*c - b*b/4.0))
        beta = a/emit
        alpha = -b/2.0/emit
        nemit = emit * energy / electron_rest_en * 1e6  # in mm.mrad
        return nemit, beta, alpha

    def _thin_lens_method(self, K1, sigma, energy):
        al, bl, cl = np.polyfit(K1*self.QUAD_L, sigma*sigma, 2)
        a = al
        b = -bl/2/al
        c = cl - bl**2/4/al
        ld = self.DIST + self.QUAD_L/2
        emit = np.sqrt(abs(a*c))/ld**2
        beta = np.sqrt(abs(a/c))
        alpha = (1/ld-b)*np.sqrt(abs(a/c))
        nemit = emit * energy / electron_rest_en * 1e6  # in mm.mrad
        return nemit, beta, alpha

    def _setupUi(self):
        gl = QGridLayout(self)
        wid = MatplotlibWidget(self)
        gl.addWidget(wid, 0, 0)
        wid.axes.set_xlabel('Index')
        wid.axes.set_ylabel('Normalized Emittance [mm.mrad]')
        wid.axes.grid(True)
        wid.axes.set_aspect('auto')
        wid.figure.set_tight_layout(True)
        self.line_nemitx_tm = wid.axes.plot(
            self.nemitx_tm, '-bo', lw=1, label='Hor. Trans. Mat.')[0]
        self.line_nemitx_parf = wid.axes.plot(
            self.nemitx_parf, '--bd', lw=1, label='Hor. Parab. Fit')[0]
        self.line_nemity_tm = wid.axes.plot(
            self.nemity_tm, '--ro', lw=1, label='Vert. Trans. Mat.')[0]
        self.line_nemity_parf = wid.axes.plot(
            self.nemity_parf, '--rd', lw=1, label='Vert. Parab. Fit')[0]
        wid.axes.legend(loc='best')
        self.plt_nemit = wid

        wid = MatplotlibWidget(self)
        gl.addWidget(wid, 1, 0)
        wid.axes.set_xlabel('Index')
        wid.axes.set_ylabel(r'$\beta$ [m]')
        wid.axes.grid(True)
        wid.axes.set_aspect('auto')
        wid.figure.set_tight_layout(True)
        self.line_betax_tm = wid.axes.plot(
            self.betax_tm, '-bo', lw=1, label='Hor. Trans. Mat.')[0]
        self.line_betax_parf = wid.axes.plot(
            self.betax_parf, '--bd', lw=1, label='Hor. Parab. Fit')[0]
        self.line_betay_tm = wid.axes.plot(
            self.betay_tm, '--ro', lw=1, label='Vert. Trans. Mat.')[0]
        self.line_betay_parf = wid.axes.plot(
            self.betay_parf, '--rd', lw=1, label='Vert. Parab. Fit')[0]
        self.plt_beta = wid

        wid = MatplotlibWidget(self)
        gl.addWidget(wid, 2, 0)
        wid.axes.set_xlabel('Index')
        wid.axes.set_ylabel(r'$\alpha$')
        wid.axes.grid(True)
        wid.axes.set_aspect('auto')
        wid.figure.set_tight_layout(True)
        self.line_alphax_tm = wid.axes.plot(
            self.alphax_tm, '-bo', lw=1, label='Hor. Trans. Mat.')[0]
        self.line_alphax_parf = wid.axes.plot(
            self.alphax_parf, '--bd', lw=1, label='Hor. Parab. Fit')[0]
        self.line_alphay_tm = wid.axes.plot(
            self.alphay_tm, '--ro', lw=1, label='Vert. Trans. Mat.')[0]
        self.line_alphay_parf = wid.axes.plot(
            self.alphay_parf, '--rd', lw=1, label='Vert. Parab. Fit')[0]
        self.plt_alpha = wid

        gb = QGroupBox('Configurations', self)
        fl = QFormLayout(gb)
        gl.addWidget(gb, 0, 1)
        self.pb_start = QPushButton('Start', gb)
        self.pb_start.clicked.connect(self.pb_start_clicked)
        self.pb_stop = QPushButton('Stop', gb)
        self.pb_stop.clicked.connect(self.pb_stop_clicked)
        fl.addRow(self.pb_start, self.pb_stop)
        self.spbox_energy = QDoubleSpinBox(gb)
        self.spbox_energy.setMinimum(0.511)
        self.spbox_energy.setMaximum(200)
        self.spbox_energy.setValue(150)
        self.spbox_energy.setDecimals(2)
        fl.addRow(QLabel('Energy [MeV]', gb), self.spbox_energy)
        self.spbox_steps = QSpinBox(gb)
        self.spbox_steps.setValue(7)
        fl.addRow(QLabel('Nr Steps', gb), self.spbox_steps)
        self.spbox_samples = QSpinBox(gb)
        self.spbox_samples.setValue(10)
        fl.addRow(QLabel('Nr Samples per step', gb), self.spbox_samples)
        self.spbox_I_ini = QDoubleSpinBox(gb)
        self.spbox_I_ini.setMinimum(-4)
        self.spbox_I_ini.setMaximum(4)
        self.spbox_I_ini.setValue(-0.7)
        self.spbox_I_ini.setDecimals(3)
        fl.addRow(QLabel('Initial Current [A]', gb), self.spbox_I_ini)
        self.spbox_I_end = QDoubleSpinBox(gb)
        self.spbox_I_end.setMinimum(-4)
        self.spbox_I_end.setMaximum(4)
        self.spbox_I_end.setValue(0.7)
        self.spbox_I_end.setDecimals(3)
        fl.addRow(QLabel('Final Current [A]', gb), self.spbox_I_end)
        self.spbox_threshold = QDoubleSpinBox(gb)
        self.spbox_threshold.setMinimum(0)
        self.spbox_threshold.setMaximum(20)
        self.spbox_threshold.setValue(4)
        self.spbox_threshold.setDecimals(2)
        fl.addRow(QLabel('Max. Size Accpbl. [mm]', gb), self.spbox_threshold)

        gb = QGroupBox('Results', self)
        gl.addWidget(gb, 1, 1, 2, 1)
        gl2 = QGridLayout(gb)
        gl2.addWidget(QLabel('Trans. Matrix', gb), 0, 1, 1, 2)
        gl2.addWidget(QLabel('Parabola Fit', gb), 0, 3, 1, 2)
        gl2.addWidget(QLabel('Hor.', gb), 1, 1)
        gl2.addWidget(QLabel('Vert.', gb), 1, 2)
        gl2.addWidget(QLabel('Hor.', gb), 1, 3)
        gl2.addWidget(QLabel('Vert.', gb), 1, 4)
        gl2.addWidget(QLabel('Norm. emitt. [mm.rad]', gb), 2, 0)
        gl2.addWidget(QLabel('beta [m]', gb), 3, 0)
        gl2.addWidget(QLabel('alpha', gb), 4, 0)
        for i, pref in enumerate(('nemit', 'beta', 'alpha')):
            for j, tp in enumerate(('x_tm', 'y_tm', 'x_parf', 'y_parf')):
                name = pref + tp
                lb = QLabel('----', gb)
                setattr(self, 'lb_' + name, lb)
                gl2.addWidget(lb, i+2, j+1)

        wid = MatplotlibWidget(self)
        gl.addWidget(wid, 0, 2)
        wid.axes.set_xlabel('Quad. Current [A]')
        wid.axes.set_ylabel('Beam Size [mm]')
        wid.axes.grid(True)
        wid.axes.set_aspect('auto')
        wid.figure.set_tight_layout(True)
        self.line_sigmax = wid.axes.plot([], 'bo', lw=1, label='Horizontal')[0]
        self.line_sigmay = wid.axes.plot([], 'ro', lw=1, label='Vertical')[0]
        self.plt_sigma = wid

        self.plt_image = ProcessImage(self, prof='PRF5')
        gl.addWidget(self.plt_image, 1, 2, 2, 1)

    def _get_resp_mat(self, K1, energy):
        gamma = energy/electron_rest_en
        R = np.zeros((len(K1), 6, 6))
        Rd = gettransmat('drift', L=self.DIST, gamma=gamma)
        for i, k1 in enumerate(K1):
            Rq = gettransmat('quad', L=self.QUAD_L, gamma=gamma, K1=k1)
            R[i] = np.dot(Rd, Rq)
        R11 = R[:, 0, 0].reshape(-1, 1)
        R12 = R[:, 0, 1].reshape(-1, 1)
        R33 = R[:, 2, 2].reshape(-1, 1)
        R34 = R[:, 2, 3].reshape(-1, 1)
        Rx = np.column_stack((R11*R11, R11*R12, R12*R12))
        Ry = np.column_stack((R33*R33, R33*R34, R34*R34))
        return Rx, Ry

    def pb_start_clicked(self):
        """
        Slot documentation goes here.
        """
        self.pb_stop.setEnabled(True)
        self.pb_start.setEnabled(False)
        self._measuring = True
        self.measurement = Thread(target=self.meas_emittance, daemon=True)
        self.measurement.start()

    def pb_stop_clicked(self):
        """
        Slot documentation goes here.
        """
        self._measuring = False
        self.pb_stop.setEnabled(False)
        self.pb_start.setEnabled(True)

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
    win = EmittanceMeasure()
    win.show()
    sys.exit(app.exec_())
