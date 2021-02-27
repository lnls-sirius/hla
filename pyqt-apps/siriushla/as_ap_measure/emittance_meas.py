#!/usr/bin/env python-sirius

import logging as _log
from threading import Thread, Event
import numpy as np
from scipy.optimize import curve_fit
from epics import PV

import matplotlib.pyplot as mplt
import matplotlib.gridspec as mgs
from matplotlib import rcParams

from qtpy.QtWidgets import QPushButton, QLabel, QGridLayout, QGroupBox, \
    QFormLayout, QMessageBox, QWidget, QComboBox, QSpinBox, QVBoxLayout, \
    QFileDialog, QHBoxLayout, QCheckBox
from qtpy.QtGui import QColor
from qtpy.QtCore import Qt, Slot

from pyqtgraph import PlotCurveItem, mkPen

from pydm.widgets import PyDMImageView
from pydm.widgets.logdisplay import PyDMLogDisplay

import mathphys.constants as _consts
from siriuspy.magnet.factory import NormalizerFactory as _NormFact

from siriushla.widgets import SiriusSpinbox, SiriusLabel, MatplotlibWidget, \
    QDoubleSpinBoxPlus
from siriushla.as_ti_control import HLTriggerSimple

rcParams.update({
    'font.size': 9, 'axes.grid': True, 'grid.linestyle': '--',
    'grid.alpha': 0.5})

DT = 0.001
SIMUL = False

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-6  # [MeV]

_log.basicConfig(format='%(levelname)7s ::: %(message)s')


class EmittanceMeasure(QWidget):

    def __init__(self, parent=None, place='LI'):
        super().__init__(parent=parent)
        self._place = place or 'LI'
        self.setObjectName(self._place[0:2] + 'App')
        self._select_experimental_setup()
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

    def _select_experimental_setup(self):
        if self._place.lower().startswith('li'):
            self.plt_image = ProcessImage(self, place='LI-Emittance')
            self.conv2kl = _NormFact.create('LI-01:MA-QF3')
            self.quad_I_sp = PV('LI-01:PS-QF3:Current-SP')
            self.quad_I_rb = PV('LI-01:PS-QF3:Current-Mon')
            self.DIST = 2.8775
            self.QUAD_L = 0.112
        if self._place.lower().startswith('tb-qd2a'):
            self.plt_image = ProcessImage(self, place='TB-Emittance')
            self.conv2kl = _NormFact.create('TB-02:MA-QD2A')
            self.quad_I_sp = PV('TB-02:PS-QD2A:Current-SP')
            self.quad_I_rb = PV('TB-02:PS-QD2A:Current-RB')
            self.DIST = 6.904
            self.QUAD_L = 0.1
        if self._place.lower().startswith('tb-qf2a'):
            self.plt_image = ProcessImage(self, place='TB-Emittance')
            self.conv2kl = _NormFact.create('TB-02:MA-QF2A')
            self.quad_I_sp = PV('TB-02:PS-QF2A:Current-SP')
            self.quad_I_rb = PV('TB-02:PS-QF2A:Current-RB')
            self.DIST = 6.534
            self.QUAD_L = 0.1

    def _acquire_data(self):
        samples = self.spbox_samples.value()
        outlier = self.spbox_outliers.value()
        if samples <= outlier:
            _log.warning(
                'Number of samples must be larger than number o outliers.')
            _log.warning('Acquisition aborted.')
            return
        nsteps = self.spbox_steps.value()
        I_ini = self.spbox_I_ini.value()
        I_end = self.spbox_I_end.value()

        outs = outlier // 2    # outliers below median
        outg = outlier - outs  # outliers above median

        self.line_sigmax.set_xdata([])
        self.line_sigmax.set_ydata([])
        self.line_sigmay.set_xdata([])
        self.line_sigmay.set_ydata([])
        self.line_fit.set_xdata([])
        self.line_fit.set_ydata([])
        self.fig_sigma.figure.canvas.draw()

        pl = 'y' if self.cbbox_plane.currentIndex() else 'x'
        curr_list = np.linspace(I_ini, I_end, nsteps)
        init_curr = self.quad_I_sp.value
        sigma = []
        I_meas = []
        for i, I in enumerate(curr_list):
            _log.info('setting quadrupole to {0:8.3f} A'.format(I))
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
                    _log.info('Stopped')
                    return
                _log.info('    sample {0:02d}'.format(j))
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
            I_meas.extend(I_tmp[outs:-outg])
            sigma.extend(sig_tmp[outs:-outg])
            if pl == 'x':
                self.line_sigmax.set_xdata(I_meas)
                self.line_sigmax.set_ydata(np.array(sigma)*1e3)
            else:
                self.line_sigmay.set_xdata(I_meas)
                self.line_sigmay.set_ydata(np.array(sigma)*1e3)
            self.fig_sigma.figure.axes[0].set_xlim(
                    [min(I_meas)*(1-DT*10), max(I_meas)*(1+DT*10)])
            self.fig_sigma.figure.axes[0].set_ylim(
                    [min(sigma)*(1-DT)*1e3, max(sigma)*(1+DT)*1e3])
            self.fig_sigma.figure.canvas.draw()
        self._measuring.set()
        _log.info('Returning Quad to Initial Current')
        self.quad_I_sp.put(init_curr, wait=True)

        self.pb_stop.setEnabled(False)
        self.pb_start.setEnabled(True)
        _log.info('Finished!')
        self.I_meas = I_meas
        self.sigma = sigma
        self.plane_meas = pl

    def _perform_analysis(self):
        sigma = np.array(self.sigma)
        I_meas = np.array(self.I_meas)
        pl = self.plane_meas
        K1 = self._get_K1_from_I(I_meas)

        # Transfer Matrix
        nem, bet, alp = self._trans_matrix_analysis(K1, sigma, pl=pl)
        getattr(self, 'nemit' + pl + '_tm').append(nem)
        getattr(self, 'beta' + pl + '_tm').append(bet)
        getattr(self, 'alpha' + pl + '_tm').append(alp)

        # Parabola Fitting
        nem, bet, alp = self._thin_lens_approx(K1, sigma, pl=pl)
        getattr(self, 'nemit' + pl + '_parf').append(nem)
        getattr(self, 'beta' + pl + '_parf').append(bet)
        getattr(self, 'alpha' + pl + '_parf').append(alp)

        for pref in ('nemit', 'beta', 'alpha'):
            for var in ('_tm', '_parf'):
                tp = pref + pl + var
                yd = np.array(getattr(self, tp))
                line = getattr(self, 'line_'+tp)
                line.set_xdata(np.arange(yd.shape[0]))
                line.set_ydata(yd)
                lb = getattr(self, 'lb_'+tp)
                lb.setText('{0:.3f}'.format(yd.mean()))
            params = []
            for var in ('x_tm', 'y_tm', 'x_parf', 'y_parf'):
                params.extend(getattr(self, pref + var))
            params = np.array(params)
            axes = getattr(self, 'line_' + pref + 'x_parf').axes
            axes.set_xlim([-0.1, params.shape[0]+0.1])
            axes.set_ylim([params.min()*(1-DT), params.max()*(1+DT)])
            self.fig_res.figure.canvas.draw()

    def _get_K1_from_I(self, I_meas):
        energy = self.spbox_energy.value() * 1e-3  # energy in GeV
        KL = self.conv2kl.conv_current_2_strength(
            I_meas, strengths_dipole=energy)
        return KL/self.QUAD_L

    def _trans_matrix_analysis(self, K1, sigma, pl='x'):
        Rx, Ry = self._get_trans_mat(K1)
        R = Rx if pl == 'x' else Ry
        pseudo_inv = (np.linalg.inv(np.transpose(R) @ R) @ np.transpose(R))
        [s_11, s_12, s_22] = pseudo_inv @ (sigma*sigma)
        # s_11, s_12, s_22 = np.linalg.lstsq(R, sigma * sigma)[0]
        nemit, beta, alpha, gamma = self._twiss(s_11, s_12, s_22)
        return nemit, beta, alpha

    def _thin_lens_approx(self, K1, sigma, pl='x'):
        K1 = K1 if pl == 'x' else -K1
        a, b, c = np.polyfit(K1, sigma*sigma, 2)
        yd = np.sqrt(np.polyval([a, b, c], K1))
        self.line_fit.set_xdata(self.I_meas)
        self.line_fit.set_ydata(yd*1e3)
        self.fig_sigma.figure.canvas.draw()

        d = self.DIST + self.QUAD_L/2
        l = self.QUAD_L
        s_11 = a/(d*l)**2
        s_12 = (-b-2*d*l*s_11)/(2*l*d*d)
        s_22 = (c-s_11-2*d*s_12)/d**2
        nemit, beta, alpha, gamma = self._twiss(s_11, s_12, s_22)
        return nemit, beta, alpha

    def _twiss(self, s_11, s_12, s_22):
        energy = self.spbox_energy.value()  # energy in MeV
        emit = np.sqrt(abs(s_11 * s_22 - s_12 * s_12))
        beta = s_11 / emit
        alpha = -s_12 / emit
        gamma = s_22 / emit
        nemit = emit * energy / E0 * 1e6  # in mm.mrad
        return nemit, beta, alpha, gamma

    def _get_trans_mat(self, K1):
        R = np.zeros((len(K1), 4, 4))
        Rd = gettransmat('drift', L=self.DIST)
        for i, k1 in enumerate(K1):
            Rq = gettransmat('quad', L=self.QUAD_L, K1=k1)
            R[i] = np.dot(Rd, Rq)
        R11 = R[:, 0, 0].reshape(-1, 1)
        R12 = R[:, 0, 1].reshape(-1, 1)
        R33 = R[:, 2, 2].reshape(-1, 1)
        R34 = R[:, 2, 3].reshape(-1, 1)
        Rx = np.column_stack((R11*R11, 2*R11*R12, R12*R12))
        Ry = np.column_stack((R33*R33, 2*R33*R34, R34*R34))
        return Rx, Ry

    def _setupUi(self):
        gl = QGridLayout(self)
        fig = mplt.figure()
        wid = MatplotlibWidget(fig, parent=self)
        wid.setObjectName('fig_result')
        wid.setStyleSheet('#fig_result{min-width: 25em;}')
        self.fig_res = wid

        gs = mgs.GridSpec(3, 1)
        gs.update(left=0.18, right=0.98, top=0.97, bottom=0.08, hspace=0.25)

        axes = wid.figure.add_subplot(gs[0, 0])
        axes.set_xlabel('Index')
        axes.set_ylabel('Normalized Emit. [mm.mrad]')
        axes.grid(True)
        axes.set_aspect('auto')
        self.line_nemitx_tm = axes.plot(
            self.nemitx_tm, '-bo', lw=1, label='Hor. Trans. Mat.')[0]
        self.line_nemitx_parf = axes.plot(
            self.nemitx_parf, '--bd', lw=1, label='Hor. Parab. Fit')[0]
        self.line_nemity_tm = axes.plot(
            self.nemity_tm, '--ro', lw=1, label='Vert. Trans. Mat.')[0]
        self.line_nemity_parf = axes.plot(
            self.nemity_parf, '--rd', lw=1, label='Vert. Parab. Fit')[0]
        axes.legend(loc='best')

        axes = wid.figure.add_subplot(gs[1, 0])
        axes.set_xlabel('Index')
        axes.set_ylabel(r'$\beta$ [m]')
        self.line_betax_tm = axes.plot(
            self.betax_tm, '-bo', lw=1, label='Hor. Trans. Mat.')[0]
        self.line_betax_parf = axes.plot(
            self.betax_parf, '--bd', lw=1, label='Hor. Parab. Fit')[0]
        self.line_betay_tm = axes.plot(
            self.betay_tm, '--ro', lw=1, label='Vert. Trans. Mat.')[0]
        self.line_betay_parf = axes.plot(
            self.betay_parf, '--rd', lw=1, label='Vert. Parab. Fit')[0]

        axes = wid.figure.add_subplot(gs[2, 0])
        axes.set_xlabel('Index')
        axes.set_ylabel(r'$\alpha$')
        self.line_alphax_tm = axes.plot(
            self.alphax_tm, '-bo', lw=1, label='Hor. Trans. Mat.')[0]
        self.line_alphax_parf = axes.plot(
            self.alphax_parf, '--bd', lw=1, label='Hor. Parab. Fit')[0]
        self.line_alphay_tm = axes.plot(
            self.alphay_tm, '--ro', lw=1, label='Vert. Trans. Mat.')[0]
        self.line_alphay_parf = axes.plot(
            self.alphay_parf, '--rd', lw=1, label='Vert. Parab. Fit')[0]

        measlay = QVBoxLayout()

        gb = QGroupBox('QF3 Current [A]', self)
        measlay.addWidget(gb)
        gb.setLayout(QHBoxLayout())
        spnbox = SiriusSpinbox(gb, init_channel='LI-01:PS-QF3:Current-SP')
        lbl = SiriusLabel(gb, init_channel='LI-01:PS-QF3:Current-Mon')
        spnbox.showStepExponent = False
        gb.layout().addWidget(spnbox)
        gb.layout().addWidget(lbl)
        gb.layout().setAlignment(Qt.AlignTop)

        gb = QGroupBox('Data Acquisition Configs.', self)
        fl = QFormLayout(gb)
        measlay.addWidget(gb)
        self.pb_start = QPushButton('Start', gb)
        self.pb_start.clicked.connect(self.pb_start_clicked)
        self.pb_stop = QPushButton('Stop', gb)
        self.pb_stop.clicked.connect(self.pb_stop_clicked)
        self.pb_stop.setEnabled(False)
        hbox_bts = QHBoxLayout()
        hbox_bts.addWidget(self.pb_start)
        hbox_bts.addWidget(self.pb_stop)
        fl.addRow(hbox_bts)
        self.cbbox_plane = QComboBox(gb)
        self.cbbox_plane.addItem('Horizontal')
        self.cbbox_plane.addItem('Vertical')
        fl.addRow(QLabel('Plane', gb), self.cbbox_plane)
        self.spbox_steps = QSpinBox(gb)
        self.spbox_steps.setValue(11)
        fl.addRow(QLabel('Nr Steps', gb), self.spbox_steps)
        self.spbox_samples = QSpinBox(gb)
        self.spbox_samples.setMinimum(1)
        self.spbox_samples.setValue(16)
        fl.addRow(QLabel('Nr Samples per step', gb), self.spbox_samples)
        self.spbox_outliers = QSpinBox(gb)
        self.spbox_outliers.setMinimum(0)
        self.spbox_outliers.setValue(12)
        fl.addRow(QLabel('Nr Outliers', gb), self.spbox_outliers)
        self.spbox_I_ini = QDoubleSpinBoxPlus(gb)
        self.spbox_I_ini.setMinimum(-4)
        self.spbox_I_ini.setMaximum(4)
        self.spbox_I_ini.setValue(-0.7)
        self.spbox_I_ini.setDecimals(3)
        fl.addRow(QLabel('Initial Current [A]', gb), self.spbox_I_ini)
        self.spbox_I_end = QDoubleSpinBoxPlus(gb)
        self.spbox_I_end.setMinimum(-4)
        self.spbox_I_end.setMaximum(4)
        self.spbox_I_end.setValue(0.7)
        self.spbox_I_end.setDecimals(3)
        fl.addRow(QLabel('Final Current [A]', gb), self.spbox_I_end)
        self.spbox_threshold = QDoubleSpinBoxPlus(gb)
        self.spbox_threshold.setMinimum(0)
        self.spbox_threshold.setMaximum(20)
        self.spbox_threshold.setValue(4)
        self.spbox_threshold.setDecimals(2)
        fl.addRow(QLabel('Max. Size Accpbl. [mm]', gb), self.spbox_threshold)

        measlay.setStretch(0, 2)
        measlay.setStretch(1, 8)

        anllay = QVBoxLayout()

        gb = QGroupBox('Analysis Configs.', self)
        vl = QVBoxLayout(gb)
        anllay.addWidget(gb)
        self.spbox_energy = QDoubleSpinBoxPlus(gb)
        self.spbox_energy.setMinimum(0.511)
        self.spbox_energy.setMaximum(200)
        self.spbox_energy.setValue(150)
        self.spbox_energy.setDecimals(2)
        self.pb_analyse_data = QPushButton('Analyse', gb)
        self.pb_analyse_data.clicked.connect(self.pb_analyse_data_clicked)
        hl = QHBoxLayout()
        hl.addWidget(QLabel('Energy [MeV]', gb))
        hl.addWidget(self.spbox_energy)
        hl.addWidget(self.pb_analyse_data)
        vl.addLayout(hl)
        self.pb_save_data = QPushButton('Save Raw', gb)
        self.pb_save_data.clicked.connect(self.pb_save_data_clicked)
        self.pb_load_data = QPushButton('Load Raw', gb)
        self.pb_load_data.clicked.connect(self.pb_load_data_clicked)
        hl = QHBoxLayout()
        hl.addWidget(self.pb_save_data)
        hl.addWidget(self.pb_load_data)
        vl.addLayout(hl)
        self.logdisplay = PyDMLogDisplay(self, level=_log.INFO)
        vl.addWidget(self.logdisplay)

        resultsgb = QGroupBox('Results', self)
        gl2 = QGridLayout(resultsgb)
        gl2.addWidget(QLabel('Trans. Matrix', resultsgb), 0, 1, 1, 2)
        gl2.addWidget(QLabel('Parabola Fit', resultsgb), 0, 3, 1, 2)
        gl2.addWidget(QLabel('Hor.', resultsgb), 1, 1)
        gl2.addWidget(QLabel('Vert.', resultsgb), 1, 2)
        gl2.addWidget(QLabel('Hor.', resultsgb), 1, 3)
        gl2.addWidget(QLabel('Vert.', resultsgb), 1, 4)
        gl2.addWidget(QLabel('Norm. emitt.\n[mm.mrad]', resultsgb), 2, 0)
        gl2.addWidget(QLabel('beta [m]', resultsgb), 3, 0)
        gl2.addWidget(QLabel('alpha', resultsgb), 4, 0)
        for i, pref in enumerate(('nemit', 'beta', 'alpha')):
            for j, tp in enumerate(('x_tm', 'y_tm', 'x_parf', 'y_parf')):
                name = pref + tp
                lb = QLabel('----', resultsgb)
                setattr(self, 'lb_' + name, lb)
                gl2.addWidget(lb, i+2, j+1)

        wid = MatplotlibWidget(parent=self)
        axes = wid.figure.add_subplot(111)
        axes.set_xlabel('Quad. Current [A]')
        axes.set_ylabel('Beam Size [mm]')
        wid.figure.set_tight_layout(True)
        self.line_sigmax = axes.plot([], 'bo', lw=1, label='Horizontal')[0]
        self.line_sigmay = axes.plot([], 'ro', lw=1, label='Vertical')[0]
        self.line_fit = axes.plot([], '-k', lw=1)[0]
        wid.setObjectName('fig_sigma')
        wid.setStyleSheet('#fig_sigma{min-width: 25em;}')
        self.fig_sigma = wid

        gl.addWidget(self.plt_image, 0, 0, 2, 1)
        gl.addItem(measlay, 0, 1)
        gl.addWidget(self.fig_sigma, 1, 1)
        gl.addItem(anllay, 0, 2)
        gl.addWidget(resultsgb, 1, 2)
        gl.addWidget(self.fig_res, 0, 3, 2, 1)

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
                self, 'Save file', '', 'Text Files (*.txt *.dat)')
        if fname[0]:
            self.save_to_file(fname[0])

    def save_to_file(self, fname):
        header = 'Plane = {0:s}\n'.format(self.plane_meas)
        header += '{0:15s} {1:15s}'.format('Current [A]', 'Beam Size [m]')
        np.savetxt(fname, np.column_stack(
            (self.I_meas, self.sigma)), header=header, fmt='%-15.9f %-15.10f')

    def pb_load_data_clicked(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', '', 'Text Files (*.txt *.dat)')
        if fname[0]:
            self.load_from_file(fname[0])

    def load_from_file(self, fname):
        try:
            self.I_meas, self.sigma = np.loadtxt(
                                        fname, skiprows=2, unpack=True)
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

        if self.plane_meas == 'x':
            self.line_sigmax.set_xdata(self.I_meas)
            self.line_sigmax.set_ydata(np.array(self.sigma)*1e3)
        else:
            self.line_sigmay.set_xdata(self.I_meas)
            self.line_sigmay.set_ydata(np.array(self.sigma)*1e3)
        self.fig_sigma.figure.axes[0].set_xlim(
                [min(self.I_meas)*(1-DT*10), max(self.I_meas)*(1+DT*10)])
        self.fig_sigma.figure.axes[0].set_ylim(
                [min(self.sigma)*(1-DT)*1e3, max(self.sigma)*(1+DT)*1e3])
        self.fig_sigma.figure.canvas.draw()

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
        _log.info('Starting...')
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
        _log.info('Stopping...')
        self._measuring.set()


def gettransmat(elem, L, K1=None, B=None):
    R = np.eye(4)

    if elem.lower().startswith('qu') and K1 is not None and K1 == 0:
        elem = 'drift'
    if elem.lower().startswith('dr'):
        R = np.array([
            [1, L, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, L],
            [0, 0, 0, 1],
        ])
    elif elem.lower().startswith('qu') and K1 is not None:
        kq = np.sqrt(abs(K1))
        c = np.cos(kq*L)
        s = np.sin(kq*L)
        ch = np.cosh(kq*L)
        sh = np.sinh(kq*L)
        if K1 > 0:
            x11, x12, x21 = c,  1/kq*s, -kq*s
            y11, y12, y21 = ch, 1/kq*sh, kq*sh
        else:
            x11, x12, x21 = ch, 1/kq*sh, kq*sh
            y11, y12, y21 = c,  1/kq*s, -kq*s
        R = np.array([
            [x11, x12, 0,   0],
            [x21, x11, 0,   0],
            [0,   0,   y11, y12],
            [0,   0,   y21, y11],
        ])
    return R


def _calc_moments(axis, proj):
    dx = axis[1]-axis[0]
    Norm = np.trapz(proj, dx=dx)
    cen = np.trapz(proj*axis, dx=dx)/Norm
    sec = np.trapz(proj*axis*axis, dx=dx)/Norm
    std = np.sqrt(sec - cen*cen)
    return cen, std


def _gaussian(x, amp, mu, sigma, y0):
    return amp*np.exp(-(x-mu)**2.0/(2.0*sigma**2.0))+y0


def _fit_gaussian(x, y, amp=None, mu=None, sigma=None, y0=None):
    amp = amp or np.amax(y)
    par = _calc_moments(x, y)
    mu = mu or par[0]
    sigma = sigma or par[1]
    y0 = y0 or np.mean(y)
    try:
        p_opt, p_cov = curve_fit(_gaussian, x, y, (amp, mu, sigma, y0))
    except Exception:
        p_opt = (amp, mu, sigma, y0)
        print('Fitting Problem')
    return p_opt


class ImageView(PyDMImageView):

    def __init__(self, callback, **kwargs):
        self.callback = callback
        super().__init__(**kwargs)
        self.colorMap = self.Jet

    @Slot(np.ndarray)
    def image_value_changed(self, image):
        image = self.callback(image, self._image_width)
        super().image_value_changed(image)


class ProcessImage(QWidget):
    def __init__(self, parent=None, place='LI-Energy'):
        super().__init__(parent)
        self._place = place or 'LI-Energy'
        self._select_experimental_setup()
        self.cen_x = None
        self.cen_y = None
        self.sigma_x = None
        self.sigma_y = None
        self.bg_ready = False
        self.bg = None
        self.nbg = 0
        self._setupUi()

    def _select_experimental_setup(self):
        if self._place.lower().startswith('li-ene'):
            prof = 'LA-BI:PRF4'
            self.conv_coefx = PV(prof + ':X:Gauss:Coef')
            self.conv_coefy = PV(prof + ':Y:Gauss:Coef')
            self.image_channel = prof + ':RAW:ArrayData'
            self.width_channel = prof + ':ROI:MaxSizeX_RBV'
            self.trig_name = 'LI-Fam:TI-Scrn'
        elif self._place.lower().startswith('li-emit'):
            prof = 'LA-BI:PRF5'
            self.conv_coefx = PV(prof + ':X:Gauss:Coef')
            self.conv_coefy = PV(prof + ':Y:Gauss:Coef')
            self.image_channel = prof + ':RAW:ArrayData'
            self.width_channel = prof + ':ROI:MaxSizeX_RBV'
            self.trig_name = 'LI-Fam:TI-Scrn'
        elif self._place.lower().startswith('tb-emit'):
            prof = 'TB-02:DI-ScrnCam-2'
            self.conv_coefx = PV(prof + ':ImgScaleFactorX-RB')
            self.conv_coefy = PV(prof + ':ImgScaleFactorY-RB')
            prof = 'TB-02:DI-Scrn-2'
            self.image_channel = prof + ':ImgData-Mon'
            self.width_channel = prof + ':ImgROIWidth-RB'
            self.trig_name = 'TB-Fam:TI-Scrn'
        else:
            raise Exception('Wrong value for "place".')

    def _setupUi(self):
        vl = QVBoxLayout(self)
        self.image_view = ImageView(
            self.process_image,
            parent=self,
            image_channel=self.image_channel,
            width_channel=self.width_channel)
        self.image_view.maxRedrawRate = 5
        self.image_view.readingOrder = self.image_view.Clike
        self.plt_roi = PlotCurveItem([0, 0, 400, 400, 0], [0, 400, 400, 0, 0])
        pen = mkPen()
        pen.setColor(QColor('red'))
        pen.setWidth(1)
        self.plt_roi.setPen(pen)
        self.image_view.addItem(self.plt_roi)
        self.plt_fit_x = PlotCurveItem([0, 0], [0, 400])
        self.plt_fit_y = PlotCurveItem([0, 0], [0, 400])
        self.plt_his_x = PlotCurveItem([0, 0], [0, 400])
        self.plt_his_y = PlotCurveItem([0, 0], [0, 400])
        pen = mkPen()
        pen.setColor(QColor('yellow'))
        self.plt_his_x.setPen(pen)
        self.plt_his_y.setPen(pen)
        self.image_view.addItem(self.plt_fit_x)
        self.image_view.addItem(self.plt_fit_y)
        self.image_view.addItem(self.plt_his_x)
        self.image_view.addItem(self.plt_his_y)
        vl.addWidget(self.image_view)

        gb_trig = QGroupBox('Trigger', self)
        vl.addWidget(gb_trig)
        gb_trig.setLayout(QVBoxLayout())
        gb_trig.layout().addWidget(HLTriggerSimple(gb_trig, self.trig_name))

        gb_pos = QGroupBox('Position [mm]', self)
        vl.addWidget(gb_pos)
        hl = QHBoxLayout(gb_pos)
        fl = QFormLayout()
        hl.addLayout(fl)
        self.cbox_method = QComboBox(gb_pos)
        self.cbox_method.addItem('Gauss Fit')
        self.cbox_method.addItem('Moments')
        fl.addRow(QLabel('Method', gb_pos), self.cbox_method)
        self.spbox_roi_size_x = QSpinBox(gb_pos)
        self.spbox_roi_size_y = QSpinBox(gb_pos)
        self.spbox_roi_center_x = QSpinBox(gb_pos)
        self.spbox_roi_center_y = QSpinBox(gb_pos)
        self.spbox_roi_size_x.setKeyboardTracking(False)
        self.spbox_roi_size_y.setKeyboardTracking(False)
        self.spbox_roi_center_x.setKeyboardTracking(False)
        self.spbox_roi_center_y.setKeyboardTracking(False)
        self.spbox_roi_size_x.setMaximum(2448)
        self.spbox_roi_size_y.setMaximum(2050)
        self.spbox_roi_center_x.setMaximum(2448)
        self.spbox_roi_center_y.setMaximum(2050)
        self.spbox_roi_size_x.setValue(300)
        self.spbox_roi_size_y.setValue(400)
        self.spbox_roi_center_x.setValue(500)
        self.spbox_roi_center_y.setValue(500)
        fl.addRow(QLabel('ROI Size X', gb_pos), self.spbox_roi_size_x)
        fl.addRow(QLabel('ROI Size Y', gb_pos), self.spbox_roi_size_y)
        self.cbbox_auto_center = QCheckBox('Automatic Centering', gb_pos)
        self.cbbox_auto_center.clicked.connect(self.cbbox_auto_center_clicked)
        self.cbbox_auto_center.setChecked(True)
        fl.addRow(self.cbbox_auto_center)
        fl.addRow(QLabel('ROI Center X', gb_pos), self.spbox_roi_center_x)
        fl.addRow(QLabel('ROI Center Y', gb_pos), self.spbox_roi_center_y)
        self.spbox_img_max = QSpinBox(gb_pos)
        self.spbox_img_max.setKeyboardTracking(False)
        self.spbox_img_max.setMinimum(0)
        self.spbox_img_max.setMaximum(2448)
        self.spbox_img_max.setValue(0)
        fl.addRow(QLabel('Max. Pixel Val.', gb_pos), self.spbox_img_max)
        self.cbbox_acq_bg = QCheckBox('Acquire Background', gb_pos)
        self.cbbox_acq_bg.clicked.connect(self.cbbox_acq_bg_checked)
        fl.addRow(self.cbbox_acq_bg)
        self.pb_reset_bg = QPushButton('Reset BG', gb_pos)
        self.pb_reset_bg.clicked.connect(self.pb_reset_bg_clicked)
        fl.addRow(self.pb_reset_bg)
        fl = QFormLayout()
        hl.addLayout(fl)
        self.lb_xave = QLabel('0', gb_pos)
        self.lb_yave = QLabel('0', gb_pos)
        self.lb_xstd = QLabel('0', gb_pos)
        self.lb_ystd = QLabel('0', gb_pos)
        fl.addRow(QLabel('Average Position', gb_pos))
        fl.addRow(QLabel('x = ', gb_pos), self.lb_xave)
        fl.addRow(QLabel('y = ', gb_pos), self.lb_yave)
        fl.addRow(QLabel('Beam Size', gb_pos))
        fl.addRow(QLabel('x = ', gb_pos), self.lb_xstd)
        fl.addRow(QLabel('y = ', gb_pos), self.lb_ystd)

        hl.setSpacing(12)
        hl.setStretch(0, 1)
        hl.setStretch(1, 1)

    def cbbox_auto_center_clicked(self, clicked):
        self.spbox_roi_center_x.setEnabled(not clicked)
        self.spbox_roi_center_y.setEnabled(not clicked)

    def pb_reset_bg_clicked(self, clicked=False):
        self.bg_ready = False
        self.bg = None
        self.nbg = 0

    def cbbox_acq_bg_checked(self, check):
        if check:
            self.pb_reset_bg_clicked()
        else:
            if self.bg is not None:
                self.bg /= self.nbg
                self.bg_ready = True

    def calc_roi(self, image):
        proj_x = image.sum(axis=0)
        proj_y = image.sum(axis=1)
        axis_x = np.arange(image.shape[1])
        axis_y = np.arange(image.shape[0])

        if self.cbbox_auto_center.isChecked():
            cen_x, _ = _calc_moments(axis_x, proj_x)
            cen_y, _ = _calc_moments(axis_y, proj_y)
        else:
            cen_x = self.spbox_roi_center_x.value()
            cen_y = self.spbox_roi_center_y.value()

        roi_size_x = self.spbox_roi_size_x.value()
        roi_size_y = self.spbox_roi_size_y.value()
        strt_x, end_x = np.array([-1, 1])*roi_size_x + int(cen_x)
        strt_y, end_y = np.array([-1, 1])*roi_size_y + int(cen_y)
        strt_x = max(strt_x, 0)
        strt_y = max(strt_y, 0)
        end_x = min(end_x, image.shape[1])
        end_y = min(end_y, image.shape[0])
        self.plt_roi.setData(
            np.array([strt_x, strt_x, end_x, end_x, strt_x]),
            np.array([strt_y, end_y, end_y, strt_y, strt_y]))

        image = image[strt_y:end_y, strt_x:end_x]
        proj_x = image.sum(axis=0)
        proj_y = image.sum(axis=1)
        axis_x = axis_x[strt_x:end_x]
        axis_y = axis_y[strt_y:end_y]
        return proj_x, proj_y, axis_x, axis_y

    def process_image(self, image, wid):
        if wid <= 0:
            return image
        try:
            image = image.reshape((-1, wid))
        except (TypeError, ValueError, AttributeError):
            return image
        if self.cbbox_acq_bg.isChecked():
            if self.bg is None:
                self.bg = np.array(image, dtype=float)
            else:
                self.bg += np.array(image, dtype=float)
            self.nbg += 1
            return image
        if self.bg_ready:
            image -= np.array(self.bg, dtype=image.dtype)
            b = np.where(image < 0)
            image[b] = 0

        maxi = self.spbox_img_max.value()
        if maxi > 0:
            b = np.where(image > maxi)
            self.image_view.colorMapMax = maxi
            image[b] = maxi

        proj_x, proj_y, axis_x, axis_y = self.calc_roi(image)
        x_max = max(proj_x)
        y_max = max(proj_y)
        if self.cbox_method.currentIndex():
            cen_x, std_x = _calc_moments(axis_x, proj_x)
            cen_y, std_y = _calc_moments(axis_y, proj_y)
            amp_x = x_max
            amp_y = y_max
            off_x = 0
            off_y = 0
        else:
            amp_x, cen_x, std_x, off_x = _fit_gaussian(axis_x, proj_x)
            amp_y, cen_y, std_y, off_y = _fit_gaussian(axis_y, proj_y)
        std_x = abs(std_x)
        std_y = abs(std_y)
        yd = _gaussian(axis_x, amp_x, cen_x, std_x, off_x)/x_max*400
        self.plt_fit_x.setData(axis_x, yd + axis_y[0])
        self.plt_his_x.setData(axis_x, proj_x/x_max*400 + axis_y[0])

        yd = _gaussian(axis_y, amp_y, cen_y, std_y, off_y)/y_max*400
        self.plt_fit_y.setData(yd + axis_x[0], axis_y)
        self.plt_his_y.setData(proj_y/y_max*400 + axis_x[0], axis_y)

        offset_x = image.shape[1]/2
        offset_y = image.shape[0]/2
        self.lb_xave.setText('{0:4d}'.format(int(cen_x or 0)))
        self.lb_yave.setText('{0:4d}'.format(int(cen_y or 0)))
        self.lb_xstd.setText('{0:4d}'.format(int(std_x or 0)))
        self.lb_ystd.setText('{0:4d}'.format(int(std_y or 0)))

        coefx = self.conv_coefx.value
        coefy = self.conv_coefy.value
        if coefx is None or coefy is None:
            return

        cen_x -= offset_x
        cen_y -= offset_y
        self.cen_x = cen_x * coefx*1e-3  # transform to meter
        self.cen_y = cen_y * coefy*1e-3
        self.sigma_x = std_x * coefx*1e-3
        self.sigma_y = std_y * coefy*1e-3

        return image

    def get_params(self):
        return self.cen_x, self.sigma_x, self.cen_y, self.sigma_y
