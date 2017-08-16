"""Creates the Contextes Menus for the Register."""

import numpy as _np
from datetime import datetime as _datetime
from PyQt5.QtWidgets import QMenu, QFileDialog
from PyQt5.QtCore import pyqtSignal
from selection_matrix import NR_BPMs


class RegisterMenu(QMenu):
    """Create the Context Menu for the Registers."""

    DEFAULT_DIR = '/home/fac/sirius-iocs/si-ap-sofb'
    EXT = '.siorb'
    EXT_FLT = 'Sirius Orbit Files (*.siorb)'

    new_orbitx_signal = pyqtSignal(_np.ndarray)
    new_orbity_signal = pyqtSignal(_np.ndarray)
    new_string_signal = pyqtSignal(str)

    def __init__(self, main_win, register, parent=None):
        """Initialize the Context Menu."""
        super().__init__(parent)
        self.main_window = main_win
        self.register = register
        self.string_status = 'Empty'
        regLB = getattr(self.main_window, 'LB_Register' + str(register))
        self.new_string_signal.connect(regLB.setText)
        self.new_string_signal.emit(self.string_status)

        self.last_dir = self.DEFAULT_DIR
        self.filename = ''
        self._orbx = _np.zeros(NR_BPMs)
        self._orby = _np.zeros(NR_BPMs)

        self.setupUi()

    @property
    def orbx(self):
        """Return the horizontal orbit."""
        return self._orbx.copy()

    @property
    def orby(self):
        """Return the Vertical orbit."""
        return self._orby.copy()

    def setupUi(self):
        """Setup Ui of Context Menu."""
        act = self.addAction('&Load Orbit')
        act.triggered.connect(self._load_orbit)
        # act = self.addAction('Register &Current Orbit')
        # act.triggered.connect(self._register_orbit)
        menu = self.addMenu('Register &Orbit')
        act = menu.addAction('Last &Measured Orbit')
        act.triggered.connect(self._register_orbit('orb'))
        act = menu.addAction('Re&ference Orbit')
        act.triggered.connect(self._register_orbit('ref'))
        act = menu.addAction('&Golden Orbit')
        act.triggered.connect(self._register_orbit('gol'))
        act = menu.addAction('&Offline Orbit')
        act.triggered.connect(self._register_orbit('off'))
        act = self.addAction('&Reset Orbit')
        act.triggered.connect(self._reset_orbit)
        act = self.addAction('&Save Registered Orbit')
        act.triggered.connect(self._save_orbit)

    def _reset_orbit(self):
        ze = _np.zeros(self._orbx.shape)
        self._update_and_emit(ze, ze.copy(), '', 'Empty')

    def _register_orbit(self, flag):
        def register(trig):
            if flag == 'orb':
                orbx = self.main_window.PV_SOFBOnlineOrbitXMon.value
                orby = self.main_window.PV_SOFBOnlineOrbitYMon.value
            elif flag == 'ref':
                orbx = self.main_window.PV_SOFBOrbitRefXRB.value
                orby = self.main_window.PV_SOFBOrbitRefYRB.value
            elif flag == 'off':
                orbx = self.main_window.PV_SOFBOfflineOrbitXRB.value
                orby = self.main_window.PV_SOFBOfflineOrbitYRB.value
            elif flag == 'gol':
                orbx = self.main_window.PV_SOFBGoldenOrbitXRB.value
                orby = self.main_window.PV_SOFBGoldenOrbitYRB.value
            else:
                return
            if orbx is not None and orby is not None:
                self._update_and_emit(orbx, orby, '', 'Orbit Registered.')
        return register

    def _save_orbit(self, trig):
        header = '# ' + _datetime.now().strftime('%Y/%M/%d-%H:%M:%S') + '\n'
        filename = QFileDialog.getSaveFileName(
            caption='Define a File Name to Save the Orbit',
            directory=self.last_dir,
            filter=self.EXT_FLT)
        fname = filename[0]
        fname += '' if fname.endswith(self.EXT) else self.EXT
        _np.savetxt(fname, _np.vstack([self.orbx, self.orby]).T, header=header)
        self._update_and_emit(self.orbx, self.orby, fname, 'Orbit Saved: ')

    def _load_orbit(self):
        filename = QFileDialog.getOpenFileName(caption='Select an Orbit File.',
                                               directory=self.last_dir,
                                               filter=self.EXT_FLT)
        if not filename[0]:
            return
        orbx, orby = _np.loadtxt(filename[0], unpack=True)
        self._update_and_emit(orbx, orby, filename[0], 'Orbit Loaded: ')

    def _update_and_emit(self, orbx, orby, fname, string):
        self._orbx = orbx
        self._orby = orby
        pure_name = ''
        path = self.last_dir
        if fname:
            path, pure_name = fname.rsplit('/', 1)
        self.string_status = string + pure_name
        self.filename = fname
        self.last_dir = path
        self.new_orbitx_signal.emit(orbx)
        self.new_orbity_signal.emit(orby)
        self.new_string_signal.emit(self.string_status)
