"""Main module of the Application Interface."""
import os as _os
import sys as _sys
import logging as _log
from threading import Thread
import pathlib as _pathlib

import matplotlib.pyplot as mplt

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QPushButton, QGridLayout, QSpinBox, \
    QLabel, QGroupBox, QDoubleSpinBox, QComboBox, QFileDialog, QVBoxLayout, \
    QMessageBox

import qtawesome as qta

from mathphys.functions import save_pickle, load_pickle
from siriuspy.devices import EqualizeBPMs
from siriuspy.clientconfigdb import ConfigDBException
from siriushla import util
from siriushla.widgets import SiriusMainWindow, SiriusLogDisplay, \
    MatplotlibWidget
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ap_configdb import LoadConfigDialog, SaveConfigDialog


class BPMsEqualizeSwitching(SiriusMainWindow):
    """."""

    EXT = 'pickle'
    EXT_FLT = f'Pickle Files (*.{EXT:s})'
    DEFAULT_DIR = _pathlib.Path.home().as_posix()
    DEFAULT_DIR += _os.path.sep + _os.path.join(
        'shared', 'screens-iocs', 'data_by_day')

    def __init__(self, parent=None):
        """."""
        super().__init__(parent=parent)

        root = _log.getLogger()
        handler = _log.StreamHandler(_sys.stdout)
        root.setLevel(_log.INFO)
        handler.setLevel(_log.INFO)
        formatter = _log.Formatter('%(levelname)7s ::: %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)

        self.bpms_eq = EqualizeBPMs(logger=root)
        self._last_dir = self.DEFAULT_DIR
        self._thread = Thread()
        self._orbits = None
        self.setupui()
        self.setObjectName('SIApp')
        color = util.get_appropriate_color('SI')
        icon = qta.icon(
            'mdi.approximately-equal-box', options=[dict(color=color)])
        self.setWindowIcon(icon)

    def setupui(self):
        """."""
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("SI - BPMs - Equalize Switching")
        self.setDocumentMode(False)
        self.setDockNestingEnabled(True)

        mwid = self._create_central_widget()
        self.setCentralWidget(mwid)

    def _create_central_widget(self):
        wid = QWidget(self)
        lay = QGridLayout()
        wid.setLayout(lay)

        wid.layout().addWidget(
            QLabel(f'<h1>Equalize Switching </h1>', wid),
            0, 0, 1, 2, alignment=Qt.AlignCenter)

        ctrls = self.get_acq_control_widget(wid)
        anly = self.get_analysis_control_widget(wid)
        status = self.get_status_widget(wid)
        apply = self.get_application_widget(wid)
        saveload = self.get_saveload_widget(wid)
        plots = self.get_plots_widget(wid)
        updt_orb = self.get_update_reforb_widget(wid)

        lay.addWidget(ctrls, 1, 0)
        lay.addWidget(saveload, 2, 0)
        lay.addWidget(anly, 3, 0)
        lay.addWidget(plots, 4, 0)
        lay.addWidget(apply, 5, 0)
        lay.addWidget(updt_orb, 6, 0)
        lay.addWidget(status, 1, 1, 6, 1)
        return wid

    def get_acq_control_widget(self, parent):
        """."""
        wid = QGroupBox('Measurement Control', parent)
        lay = QGridLayout()
        wid.setLayout(lay)

        self.cb_acqstrat = QComboBox(wid)
        self.cb_acqstrat.addItems(self.bpms_eq.AcqStrategies._fields)
        self.cb_acqstrat.setCurrentIndex(self.bpms_eq.acq_strategy)

        self.sp_invredgain = QDoubleSpinBox(self)
        self.sp_invredgain.setRange(0, 1)
        self.sp_invredgain.setSingleStep(0.01)
        self.sp_invredgain.setValue(self.bpms_eq.acq_inverse_reduced_gain)

        self.sp_acqtimeout = QDoubleSpinBox(self)
        self.sp_acqtimeout.setRange(0, 120)
        self.sp_acqtimeout.setSingleStep(1)
        self.sp_acqtimeout.setValue(self.bpms_eq.acq_timeout)

        self.sp_nrpoints = QSpinBox(self)
        self.sp_nrpoints.setRange(100, 100000)
        self.sp_nrpoints.setSingleStep(1)
        self.sp_nrpoints.setValue(self.bpms_eq.acq_nrpoints)

        pusb_start = QPushButton(qta.icon('mdi.play'), 'Acquire Data', wid)
        pusb_start.clicked.connect(self._start_activity)
        pusb_start.setObjectName('meas')

        lb_acqstrat = QLabel('Acquisition Strategy', wid)
        lb_invredgain = QLabel('Inverse Reduced Gain', wid)
        lb_acqtimeout = QLabel('Timeout [s]', wid)
        lb_nrpoints = QLabel('Number of Points', wid)

        lay.addWidget(lb_acqstrat, 0, 1, alignment=Qt.AlignRight)
        lay.addWidget(self.cb_acqstrat, 0, 2)
        lay.addWidget(lb_invredgain, 1, 1, alignment=Qt.AlignRight)
        lay.addWidget(self.sp_invredgain, 1, 2)
        lay.addWidget(lb_acqtimeout, 2, 1, alignment=Qt.AlignRight)
        lay.addWidget(self.sp_acqtimeout, 2, 2)
        lay.addWidget(lb_nrpoints, 3, 1, alignment=Qt.AlignRight)
        lay.addWidget(self.sp_nrpoints, 3, 2)
        lay.addWidget(pusb_start, 5, 1, 1, 2, alignment=Qt.AlignCenter)
        lay.setRowMinimumHeight(4, 20)
        lay.setColumnStretch(3, 2)
        lay.setColumnStretch(0, 2)
        return wid

    def get_analysis_control_widget(self, parent):
        """."""
        wid = QGroupBox('Analysis Control', parent)
        lay = QGridLayout()
        wid.setLayout(lay)
        self.cb_procmeth = QComboBox(wid)
        self.cb_procmeth.addItems(self.bpms_eq.ProcMethods._fields)
        self.cb_procmeth.setCurrentIndex(self.bpms_eq.proc_method)

        pusb_proc = QPushButton(qta.icon('mdi.chart-line'), 'Process', wid)
        pusb_proc.clicked.connect(self._start_activity)
        pusb_proc.setObjectName('proc')

        lay.addWidget(QLabel('Process Method:', wid), 0, 0)
        lay.addWidget(self.cb_procmeth, 0, 1)
        lay.addWidget(pusb_proc, 0, 3)
        lay.setColumnStretch(2, 2)
        lay.setColumnStretch(4, 2)
        return wid

    def _start_activity(self):
        """."""
        if self._thread.is_alive():
            _log.error('There is another measurement happening.')
            return
        if self.sender().objectName().startswith('meas'):
            self._thread = Thread(target=self._do_meas, daemon=True)
        else:
            self._thread = Thread(target=self._process_data, daemon=True)
        self._thread.start()

    def _do_meas(self):
        self.bpms_eq.acq_strategy = int(self.cb_acqstrat.currentIndex())
        self.bpms_eq.acq_nrpoints = int(self.sp_nrpoints.value())
        self.bpms_eq.acq_inverse_reduced_gain = float(
            self.sp_invredgain.value())
        self.bpms_eq.acq_timeout = float(self.sp_acqtimeout.value())

        try:
            self.bpms_eq.acquire_bpm_data()
        except Exception as err:
            _log.error(str(err))
            return
        self._process_data()

    def _process_data(self):
        _log.info('Processing data')
        self.bpms_eq.proc_method = int(self.cb_procmeth.currentIndex())
        try:
            self.bpms_eq.process_data()
        except Exception as err:
            _log.error('Problem processing data.')
            _log.error(str(err))
        _log.info('Processing Done!')

    def get_status_widget(self, parent):
        """."""
        wid = QGroupBox('Status', parent)
        lay = QGridLayout()
        wid.setLayout(lay)

        self.log_label = SiriusLogDisplay(wid, level=_log.INFO)
        self.log_label.logFormat = '%(message)s'
        lay.addWidget(self.log_label, 0, 0)
        return wid

    def get_application_widget(self, parent):
        wid = QGroupBox('Apply to BPMs', parent)
        lay = QGridLayout()
        wid.setLayout(lay)
        pusb_appnew = QPushButton(
            qta.icon('ei.arrow-down'), 'Apply New Gains', wid)
        pusb_appnew.clicked.connect(self._apply_new)
        pusb_appold = QPushButton(
            qta.icon('ei.arrow-down'), 'Restore Initial Gains', wid)
        pusb_appold.clicked.connect(self._apply_old)
        lay.addWidget(pusb_appnew, 0, 1)
        lay.addWidget(pusb_appold, 0, 3)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(2, 2)
        lay.setColumnStretch(4, 2)
        return wid

    def _apply_new(self):
        gains = self.bpms_eq.data.get('gains_new')
        if gains is None:
            _log.error('New gains not found.')
            return
        try:
            self.bpms_eq.set_gains(gains)
        except Exception as err:
            _log.error(str(err))

    def _apply_old(self):
        gains = self.bpms_eq.data.get('gains_init')
        if gains is None:
            _log.error('Initial gains not found.')
            return
        try:
            self.bpms_eq.set_gains(gains)
        except Exception as err:
            _log.error(str(err))

    def get_saveload_widget(self, parent):
        """."""
        svld_wid = QGroupBox('Save and Load Data', parent)
        svld_lay = QGridLayout(svld_wid)

        pbld = QPushButton('Load', svld_wid)
        pbld.setIcon(qta.icon('mdi.file-upload-outline'))
        pbld.setToolTip('Load data from file')
        pbld.clicked.connect(self._load_data_from_file)

        pbsv = QPushButton('Save', svld_wid)
        pbsv.setIcon(qta.icon('mdi.file-download-outline'))
        pbsv.setToolTip('Save data to file')
        pbsv.clicked.connect(self._save_data_to_file)

        svld_lay.addWidget(pbsv, 0, 1)
        svld_lay.addWidget(pbld, 0, 3)
        svld_lay.setColumnStretch(0, 2)
        svld_lay.setColumnStretch(2, 2)
        svld_lay.setColumnStretch(4, 2)
        return svld_wid

    def _save_data_to_file(self, _):
        filename = QFileDialog.getSaveFileName(
            caption='Define a File Name to Save Data',
            directory=self._last_dir,
            filter=self.EXT_FLT)
        fname = filename[0]
        if not fname:
            return
        self._last_dir, _ = _os.path.split(fname)
        fname += '' if fname.endswith(self.EXT) else ('.' + self.EXT)
        save_pickle(self.bpms_eq.data, fname, overwrite=True)
        _log.info(f'File Saved ... {fname.split("/")[-1]}')

    def _load_data_from_file(self):
        filename = QFileDialog.getOpenFileName(
            caption='Select a Data File.', directory=self._last_dir,
            filter=self.EXT_FLT)
        fname = filename[0]
        if not fname:
            return
        self._last_dir, _ = _os.path.split(fname)

        self.bpms_eq.data = load_pickle(fname)

        _log.info(f'File Loaded ... {fname.split("/")[-1]}')
        self.cb_acqstrat.setCurrentIndex(self.bpms_eq.acq_strategy)
        self.sp_nrpoints.setValue(self.bpms_eq.acq_nrpoints)
        self.sp_invredgain.setValue(self.bpms_eq.acq_inverse_reduced_gain)
        self.sp_acqtimeout.setValue(self.bpms_eq.acq_timeout)
        self.cb_procmeth.setCurrentIndex(self.bpms_eq.proc_method)

    def get_plots_widget(self, parent):
        wid = QGroupBox('Make Some Plots', parent)
        lay = QGridLayout(wid)
        wid.setLayout(lay)

        pusb_mean = QPushButton('Antennas Mean', wid)
        pusb_mean.clicked.connect(self._plot)
        pusb_mean.setObjectName('mean')
        pusb_gains = QPushButton('Antennas Gains', wid)
        pusb_gains.clicked.connect(self._plot)
        pusb_gains.setObjectName('gains')
        pusb_dorb = QPushButton('Orbit Variation', wid)
        pusb_dorb.setObjectName('dorb')
        pusb_dorb.clicked.connect(self._plot)
        pusb_idcs = QPushButton('Cycle Indices', wid)
        pusb_idcs.setObjectName('idcs')
        pusb_idcs.clicked.connect(self._plot)
        lay.addWidget(pusb_mean, 1, 1)
        lay.addWidget(pusb_gains, 1, 3)
        lay.addWidget(pusb_dorb, 2, 1)
        lay.addWidget(pusb_idcs, 2, 3)
        lay.setRowStretch(0, 2)
        lay.setRowStretch(3, 2)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(2, 2)
        lay.setColumnStretch(4, 2)
        return wid

    def _plot(self):
        name = self.sender().objectName()
        fig = None
        if name.startswith('dorb'):
            fig, axs = self.bpms_eq.plot_orbit_distortion()
            winname = 'Orbit Variation'
        elif name.startswith('gains'):
            fig, axs = self.bpms_eq.plot_gains()
            winname = 'Gains'
        elif name.startswith('mean'):
            fig, axs = self.bpms_eq.plot_antennas_mean()
            winname = 'Antennas Mean'
        elif name.startswith('idcs'):
            fig, axs = self.bpms_eq.plot_semicycle_indices()
            winname = 'Cycle Indices'
        if fig is None:
            _log.error('Error with plot.')
            return
        height = fig.get_figheight()
        width = fig.get_figwidth()
        wind = create_window_from_widget(MatplotlibWidget, winname)
        obj = wind(self, figure=fig)
        obj.resize(width*100, height*100)
        obj.show()

    def get_update_reforb_widget(self, parent):
        wid = QGroupBox('Update Orbits', parent)
        lay = QGridLayout(wid)
        wid.setLayout(lay)

        self.cb_orb = QComboBox(wid)
        self.cb_orb.addItems(['bba_orb', 'ref_orb', 'servconf'])
        self.cb_orb.currentTextChanged.connect(self._load_orbit)
        pb_orb = QPushButton(
            qta.icon('ei.arrow-down'), 'Save New Orbit', wid)
        pb_orb.clicked.connect(self._save_orbit)

        lay.addWidget(
            QLabel('Config to change: '), 0, 0, alignment=Qt.AlignCenter)
        lay.addWidget(self.cb_orb, 0, 1)
        lay.addWidget(pb_orb, 0, 3)
        lay.setColumnStretch(2, 2)
        lay.setRowStretch(1, 2)
        return wid

    def _load_orbit(self, confname=None):
        if confname is None:
            confname = self.sender().currentText()
        win = LoadConfigDialog('si_orbit', self)
        if confname.startswith('servconf'):
            confname, status = win.exec_()
            if not status:
                _log.warning('Loading aborted by user.')
                return
        self._orbits = win.client.get_config_value(
            confname, config_type='si_orbit')
        _log.info(f'Orbit configuration named {confname} was loaded.')

    def _save_orbit(self):
        if self._orbits is None:
            self._load_orbit(self.cb_orb.currentText())
        dorbx = self.bpms_eq.data.get('dorbx')
        dorby = self.bpms_eq.data.get('dorby')
        if dorbx is None:
            _log.error('Must Acquire and process data first.')
            return
        data = dict()
        data['x'] = self._orbits['x'] + dorbx
        data['y'] = self._orbits['y'] + dorby

        win = SaveConfigDialog('si_orbit', self)
        def _save(confname):
            try:
                win.client.insert_config(
                    confname, data, config_type='si_orbit')
            except (ConfigDBException, TypeError) as err:
                _log.warning(str(err))
                QMessageBox.warning(self, 'Warning', str(err), QMessageBox.Ok)
        # win.configname.connect(_save)
        confname, status = win.exec_()
        if not status:
            _log.warning('Saving aborted by user.')
            return
        _save(confname)
        _log.info('Configuration saved.')
