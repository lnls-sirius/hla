#!/usr/bin/env python-sirius

import os
import sys
import numpy as np
import time
from threading import Thread, Event
from epics import PV
from PyQt5.QtWidgets import (QPushButton, QLabel, QGridLayout, QGroupBox,
                             QFormLayout, QMessageBox, QApplication,
                             QSizePolicy, QWidget, QComboBox, QSpinBox,
                             QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QFileDialog)
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
SIMUL = False


class EmittanceMeasure(QWidget):
    I2K1 = [0.0089, -2.1891, -0.0493]
    QUAD = 'H1FQPS-3'
    DIST = 2.8775
    QUAD_L = 0.112

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
        self.measurement = None
        self.I_meas = None
        self.sigma = None
        self.plane_meas = None

        self._setupUi()

    def meas_emittance(self):
        self._acquire_data()
        self._perform_analysis()

    def _acquire_data(self):
        samples = self.spbox_samples.value()
        nsteps = self.spbox_steps.value()
        I_ini = self.spbox_I_ini.value()
        I_end = self.spbox_I_end.value()

        self.line_sigmax.set_xdata([])
        self.line_sigmax.set_ydata([])
        self.line_sigmay.set_xdata([])
        self.line_sigmay.set_ydata([])
        self.line_fit.set_xdata([])
        self.line_fit.set_ydata([])
        self.plt_sigma.figure.canvas.draw()

        pl = 'y' if self.cbbox_plane.currentIndex() else 'x'
        curr_list = np.linspace(I_ini, I_end, nsteps)
        sigma = []
        I_meas = []
        for i, I in enumerate(curr_list):
            print('setting Quadrupole to ', I)
            if not SIMUL:
                self.quad_I_sp.put(I, wait=True)
            self._measuring.wait(5 if i else 15)
            j = 0
            I_tmp = []
            sig_tmp = []
            while j < samples:
                if self._measuring.is_set():
                    self.pb_stop.setEnabled(False)
                    self.pb_start.setEnabled(True)
                    print('Stopped')
                    return
                print('measuring sample', j)
                I_now = self.quad_I_rb.value
                cen_x, sigma_x, cen_y, sigma_y = self.plt_image.get_params()
                mu, sig = (cen_x, sigma_x) if pl == 'x' else (cen_y, sigma_y)
                max_size = self.spbox_threshold.value()*1e-3
                if sig > max_size:
                    self._measuring.wait(1)
                    continue
                I_tmp.append(I_now)
                sig_tmp.append(abs(sig))
                self._measuring.wait(0.5)
                j += 1
            ind = np.argsort(sig_tmp)
            I_tmp = np.array(I_tmp)[ind]
            sig_tmp = np.array(sig_tmp)[ind]
            I_meas.extend(I_tmp[6:-6])
            sigma.extend(sig_tmp[6:-6])
            if pl=='x':
                self.line_sigmax.set_xdata(I_meas)
                self.line_sigmax.set_ydata(np.array(sigma)*1e3)
            else:
                self.line_sigmay.set_xdata(I_meas)
                self.line_sigmay.set_ydata(np.array(sigma)*1e3)
            self.plt_sigma.axes.set_xlim(
                    [min(I_meas)*(1-DT*10), max(I_meas)*(1+DT*10)])
            self.plt_sigma.axes.set_ylim(
                    [min(sigma)*(1-DT)*1e3, max(sigma)*(1+DT)*1e3])
            self.plt_sigma.figure.canvas.draw()
        self._measuring.set()
        self.pb_stop.setEnabled(False)
        self.pb_start.setEnabled(True)
        print('Finished!')
        self.I_meas = I_meas
        self.sigma = sigma
        self.plane_meas = pl

    def _perform_analysis(self):
        sigma = np.array(self.sigma)
        I_meas = np.array(self.I_meas)
        pl = self.plane_meas

        if pl=='x':
            # Method 1: Transfer Matrix
            nemitx, betax, alphax = self._trans_matrix_method(
                                            I_meas, sigma, pl='x')
            self.nemitx_tm.append(nemitx)
            self.betax_tm.append(betax)
            self.alphax_tm.append(alphax)
            # Method 2: Parabola Fitting
            nemitx, betax, alphax = self._thin_lens_method(
                                            I_meas, sigma, pl='x')
            self.nemitx_parf.append(nemitx)
            self.betax_parf.append(betax)
            self.alphax_parf.append(alphax)
        else:
            # Method 1: Transfer Matrix
            nemity, betay, alphay = self._trans_matrix_method(
                                            I_meas, sigma, pl='y')
            self.nemity_tm.append(nemity)
            self.betay_tm.append(betay)
            self.alphay_tm.append(alphay)
            # Method 2: Parabola Fitting
            nemity, betay, alphay = self._thin_lens_method(
                                            I_meas, sigma, pl='y')
            self.nemity_parf.append(nemity)
            self.betay_parf.append(betay)
            self.alphay_parf.append(alphay)

        for pref in ('nemit', 'beta', 'alpha'):
            for var in ('_tm', '_parf'):
                tp = pref + pl + var
                yd = np.array(getattr(self, tp))
                line = getattr(self, 'line_'+tp)
                line.set_xdata(np.arange(yd.shape[0]))
                line.set_ydata(yd)
                lb = getattr(self, 'lb_'+tp)
                lb.setText('{0:.3f}'.format(yd.mean()))
            all = []
            for var in ('x_tm', 'y_tm', 'x_parf', 'y_parf'):
                all.extend(getattr(self, pref + var))
            all = np.array(all)
            plt = getattr(self, 'plt_' + pref)
            plt.axes.set_xlim([-0.1, all.shape[0]+0.1])
            plt.axes.set_ylim([all.min()*(1-DT), all.max()*(1+DT)])
            plt.figure.canvas.draw()

    def _get_K1_from_I(self, I_meas):
        energy = self.spbox_energy.value()
        kin_en = np.sqrt(energy*energy - electron_rest_en*electron_rest_en)
        return np.polyval(self.I2K1, I_meas)*light_speed/kin_en/1e6

    def _trans_matrix_method(self, I_meas, sigma, pl='x'):
        K1 = self._get_K1_from_I(I_meas)
        energy = self.spbox_energy.value()

        Rx, Ry = self._get_resp_mat(K1, energy)
        R = Rx if pl=='x' else Ry
        a, b, c = np.linalg.lstsq(R, sigma*sigma, rcond=None)[0]
        emit = np.sqrt(abs(a*c - b*b))
        beta = a/emit
        alpha = -b/emit
        nemit = emit * energy / electron_rest_en * 1e6  # in mm.mrad
        return nemit, beta, alpha

    def _thin_lens_method(self, I_meas, sigma, pl='x'):
        I_meas2 = I_meas if pl=='x' else -I_meas

        K1 = self._get_K1_from_I(I_meas2)
        energy = self.spbox_energy.value()

        al, bl, cl = np.polyfit(K1*self.QUAD_L, sigma*sigma, 2)
        yd = np.sqrt(np.polyval([al, bl, cl], K1*self.QUAD_L))
        self.line_fit.set_xdata(I_meas)
        self.line_fit.set_ydata(yd*1e3)
        self.plt_sigma.figure.canvas.draw()
        a = al
        b = -bl/2/al
        c = cl - bl**2/4/al
        ld = self.DIST + self.QUAD_L/2
        emit = np.sqrt(abs(a*c))/ld**2
        beta = np.sqrt(abs(a/c))
        alpha = (1/ld - b)*beta
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

        vl = QVBoxLayout()
        gl.addItem(vl, 0, 1, 3, 1)
        gb = QGroupBox('Data Acquisition Configs.', self)
        fl = QFormLayout(gb)
        vl.addWidget(gb)
        self.pb_start = QPushButton('Start', gb)
        self.pb_start.clicked.connect(self.pb_start_clicked)
        self.pb_stop = QPushButton('Stop', gb)
        self.pb_stop.clicked.connect(self.pb_stop_clicked)
        self.pb_stop.setEnabled(False)
        fl.addRow(self.pb_start, self.pb_stop)
        self.cbbox_plane = QComboBox(gb)
        self.cbbox_plane.addItem('Horizontal')
        self.cbbox_plane.addItem('Vertical')
        fl.addRow(QLabel('Plane', gb), self.cbbox_plane)
        self.spbox_steps = QSpinBox(gb)
        self.spbox_steps.setValue(11)
        fl.addRow(QLabel('Nr Steps', gb), self.spbox_steps)
        self.spbox_samples = QSpinBox(gb)
        self.spbox_samples.setMinimum(12)
        self.spbox_samples.setValue(16)
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

        gb = QGroupBox('Analysis Configs.', self)
        fl = QFormLayout(gb)
        vl.addWidget(gb)
        self.spbox_energy = QDoubleSpinBox(gb)
        self.spbox_energy.setMinimum(0.511)
        self.spbox_energy.setMaximum(200)
        self.spbox_energy.setValue(150)
        self.spbox_energy.setDecimals(2)
        fl.addRow(QLabel('Energy [MeV]', gb), self.spbox_energy)
        self.pb_save_data = QPushButton('Save Raw', gb)
        self.pb_save_data.clicked.connect(self.pb_save_data_clicked)
        self.pb_load_data = QPushButton('Load Raw', gb)
        self.pb_load_data.clicked.connect(self.pb_load_data_clicked)
        fl.addRow(self.pb_save_data, self.pb_load_data)
        self.pb_analyse_data = QPushButton('Analyse', gb)
        self.pb_analyse_data.clicked.connect(self.pb_analyse_data_clicked)
        fl.addRow(self.pb_analyse_data)

        gb = QGroupBox('Results', self)
        vl.addWidget(gb)
        gl2 = QGridLayout(gb)
        gl2.addWidget(QLabel('Trans. Matrix', gb), 0, 1, 1, 2)
        gl2.addWidget(QLabel('Parabola Fit', gb), 0, 3, 1, 2)
        gl2.addWidget(QLabel('Hor.', gb), 1, 1)
        gl2.addWidget(QLabel('Vert.', gb), 1, 2)
        gl2.addWidget(QLabel('Hor.', gb), 1, 3)
        gl2.addWidget(QLabel('Vert.', gb), 1, 4)
        gl2.addWidget(QLabel('Norm. emitt. [mm.mrad]', gb), 2, 0)
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
        self.line_fit = wid.axes.plot([], '-k', lw=1)[0]
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
        Rx = np.column_stack((R11*R11, 2*R11*R12, R12*R12))
        Ry = np.column_stack((R33*R33, 2*R33*R34, R34*R34))
        return Rx, Ry

    def pb_save_data_clicked(self):
        if self.I_meas is None or self.sigma is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Could not Save")
            msg.setInformativeText(
                "There are no data saved in Memory. Make a measurement First.")
            msg.setWindowTitle("Warning")
            msg.resize(900, 300)
            msg.exec_()
            return
        fname = QFileDialog.getSaveFileName(
                    self, 'Save file',
                    '/home/fac_files/lnls-sirius/linac-opi/meas_codes',
                    "Text Files (*.txt *.dat)")
        if fname[0]:
            self.save_to_file(fname[0])

    def save_to_file(self, fname):
        header = 'Plane = {0:s}\n'.format(self.plane_meas)
        header += '{0:15s} {1:15s}'.format('Current [A]', 'Beam Size [m]')
        np.savetxt(fname, np.column_stack(
            (self.I_meas, self.sigma)), header=header, fmt='%-15.9f %-15.10f')

    def pb_load_data_clicked(self):
        fname = QFileDialog.getOpenFileName(
                    self, 'Open file',
                    '/home/fac_files/lnls-sirius/linac-opi/meas_codes', '')
        if fname[0]:
            self.load_from_file(fname[0])

    def load_from_file(self, fname):
        try:
            self.I_meas, self.sigma = np.loadtxt(fname, skiprows=2, unpack=True)
        except (ValueError, TypeError):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Could not Load File")
            msg.setInformativeText(
                "The chosen file does not match the formatting.")
            msg.setWindowTitle("Warning")
            msg.resize(900, 300)
            msg.exec_()
            return
        with open(fname, 'r') as f:
            self.plane_meas = f.readline().split()[-1]

        if self.plane_meas=='x':
            self.line_sigmax.set_xdata(self.I_meas)
            self.line_sigmax.set_ydata(np.array(self.sigma)*1e3)
        else:
            self.line_sigmay.set_xdata(self.I_meas)
            self.line_sigmay.set_ydata(np.array(self.sigma)*1e3)
        self.plt_sigma.axes.set_xlim(
                [min(self.I_meas)*(1-DT*10), max(self.I_meas)*(1+DT*10)])
        self.plt_sigma.axes.set_ylim(
                [min(self.sigma)*(1-DT)*1e3, max(self.sigma)*(1+DT)*1e3])
        self.plt_sigma.figure.canvas.draw()

    def pb_analyse_data_clicked(self):
        if self.I_meas is None or self.sigma is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Could Perform Analysis")
            msg.setInformativeText(
                "No data in memory. Please make a measurement or load the data.")
            msg.setWindowTitle("Warning")
            msg.resize(900, 300)
            msg.exec_()
            return
        self._perform_analysis()

    def pb_start_clicked(self):
        """
        Slot documentation goes here.
        """
        print('Starting...')
        if self.measurement is not None and self.measurement.isAlive():
            return
        self.pb_stop.setEnabled(True)
        self.pb_start.setEnabled(False)
        self._measuring = Event()
        self.measurement = Thread(target=self.meas_emittance, daemon=True)
        self.measurement.start()

    def pb_stop_clicked(self):
        """
        Slot documentation goes here.
        """
        print('Stopping...')
        self._measuring.set()

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
