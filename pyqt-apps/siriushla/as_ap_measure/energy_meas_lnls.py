#!/usr/bin/env python-sirius

import numpy as np
from epics import PV
from qtpy.QtWidgets import QLabel, QGridLayout, QGroupBox, QFormLayout, \
    QMessageBox, QWidget, QSpinBox, QVBoxLayout, QHBoxLayout, QPushButton,\
    QFileDialog
from qtpy.QtCore import QTimer

from matplotlib import rcParams

from .utils import MatplotlibWidget, ProcessImage, C, E0
from siriuspy.search import PSSearch as _PSS

rcParams['font.size'] = 9


class EnergyMeasure(QWidget):
    """."""

    DISP = 1.087
    B_ANG = np.pi/4
    MAX_SPREAD = 2

    def __init__(self, parent=None):
        """."""
        super().__init__(parent=parent)
        self.energylist = []
        self.spreadlist = []
        self.currentlist = []
        self.centroidlist = []
        self.sigmalist = []
        self.bend_curr = PV('LI-01:PS-Spect:seti')
        self.spect_excdata = _PSS.conv_psname_2_excdata('LI-01:PS-Spect')

        self._setupUi()

        self.t1 = QTimer()
        self.t1.timeout.connect(self.meas_energy)
        self.t1.start(500)

    def _setupUi(self):
        gl = QGridLayout(self)
        self.plt_energy = MatplotlibWidget(self)
        gl.addWidget(self.plt_energy, 0, 0, 1, 3)
        self.plt_spread = MatplotlibWidget(self)
        gl.addWidget(self.plt_spread, 1, 0, 1, 3)

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
        gb_data = QGroupBox('Data', self)
        gl.addWidget(gb_en, 2, 0)
        gl.addWidget(gb_sp, 2, 1)
        gl.addWidget(gb_data, 2, 2)
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

        vl = QVBoxLayout(gb_data)
        self.pb_save_data = QPushButton('Save Raw Data', gb_data)
        self.pb_save_data.clicked.connect(self.pb_save_data_clicked)
        vl.addWidget(self.pb_save_data)
        self.pb_load_data = QPushButton('Load Raw Data', gb_data)
        self.pb_load_data.clicked.connect(self.pb_load_data_clicked)
        vl.addWidget(self.pb_load_data)

        vl = QVBoxLayout()
        gl.addItem(vl, 0, 3, 3, 1)
        hl = QHBoxLayout()
        hl.setSpacing(10)
        self.spbox_npoints = QSpinBox(self)
        self.spbox_npoints.setKeyboardTracking(False)
        self.spbox_npoints.setMinimum(10)
        self.spbox_npoints.setMaximum(200000)
        self.spbox_npoints.setValue(100)
        hl.addWidget(QLabel('Number of Points:', self))
        hl.addWidget(self.spbox_npoints)
        self.pb_reset_data = QPushButton('Reset Data', self)
        self.pb_reset_data.clicked.connect(self.pb_reset_data_clicked)
        hl.addWidget(self.pb_reset_data)
        vl.addItem(hl)

        self.plt_image = ProcessImage(self)
        vl.addWidget(self.plt_image)

    def pb_reset_data_clicked(self):
        """."""
        self.energylist = [self.energylist[-1]]
        self.spreadlist = [self.spreadlist[-1]]
        self.plot_data()
        return

    def pb_save_data_clicked(self):
        """."""
        if not self.currentlist or not self.centroidlist or not self.sigmalist:
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
        header = '{0:15s} {1:17s} {2:17s}'.format(
                        'Current [A]', 'Beam Center [m]', 'Beam Size [m]')
        np.savetxt(
            fname, np.column_stack(
                    (self.currentlist, self.centroidlist, self.sigmalist)),
            header=header, fmt='%-17.9f %-17.10f %-17.10f')

    def pb_load_data_clicked(self):
        """."""
        fname = QFileDialog.getOpenFileName(
                    self, 'Open file',
                    '/home/fac_files/lnls-sirius/linac-opi/meas_codes', '')
        if fname[0]:
            self.load_from_file(fname[0])

    def load_from_file(self, fname):
        try:
            self.currentlist, self.centroidlist, self.sigmalist = \
                                    np.loadtxt(fname, skiprows=1, unpack=True)
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

        self.currentlist = self.currentlist.tolist()
        self.centroidlist = self.centroidlist.tolist()
        self.sigmalist = self.sigmalist.tolist()
        for i in range(len(self.currentlist)):
            energy, spread = self.convert_to_energy(
                self.currentlist[i], self.centroidlist[i], self.sigmalist[i])
            if spread >= self.MAX_SPREAD or spread <= 0:
                return
            self.energylist.append(energy)
            self.spreadlist.append(spread)
        self.plot_data()

    def convert_to_energy(self, bend_curr, cen_x, sigma_x):
        """."""
        multipoles = self.spect_excdata.interp_curr2mult(currents=bend_curr)
        BL = multipoles['normal'][0]

        nom_kin_en = BL / self.B_ANG * C*1e-6  # in MeV
        kin_en = nom_kin_en * (1 - cen_x / self.DISP)
        energy = np.sqrt(kin_en**2 + E0*E0)
        spread = sigma_x / self.DISP * 100  # in percent%
        return energy, spread

    def meas_energy(self):
        """."""
        cen_x, sigma_x, cen_y, sigma_y = self.plt_image.get_params()
        if cen_x is None:
            return

        bend_curr = self.bend_curr.value
        if bend_curr is None:
            return
        energy, spread = self.convert_to_energy(bend_curr, cen_x, sigma_x)

        if spread >= self.MAX_SPREAD or spread <= 0:
            return

        self.energylist.append(energy)
        self.spreadlist.append(spread)
        self.currentlist.append(bend_curr)
        self.centroidlist.append(cen_x)
        self.sigmalist.append(sigma_x)
        self.plot_data()

    def plot_data(self):
        DT = 0.001

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
