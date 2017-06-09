import numpy as _np
import datetime as _datetime
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog
from PyQt5.QtCore import pyqtSignal
from selection_matrix import NR_BPMs

class RegisterMenu(QMenu):
    DEFAULT_DIR = '/home/fernando'
    EXTENSION = 'Sirius Orbit Files (*.siorb)'

    new_orbitx_signal = pyqtSignal(_np.ndarray)
    new_orbity_signal = pyqtSignal(_np.ndarray)
    new_filename_signal = pyqtSignal(str)

    def __init__(self,main_win,register,parent=None):
        super().__init__(parent)
        self.main_window = main_win
        self.register = register
        self.last_dir = self.DEFAULT_DIR
        self.filename = ''
        self._orbx = _np.zeros(NR_BPMs)
        self._orby = _np.zeros(NR_BPMs)
        self.setupUi()

    @property
    def orbx(self): return self._orbx.copy()

    @property
    def orbx(self): return self._orbx.copy()

    def setupUi(self):
        act = self.addAction('&Load Orbit')
        act.triggered.connect(self._load_orbit)
        menu = self.addMenu('&Save Orbit')
        act = menu.addAction('Absolute')
        act.triggered.connect(self._save_orbit(0))
        for i in range(1,10):
            act = menu.addAction('as diff to Reg. &'+str(i))
            act.triggered.connect(self._save_orbit(i))
            regLb = getattr(self.main_window,'LB_Register'+str(i))
            self.new_filename_signal.connect(regLb.setText)
        act = self.addAction('&Reset Orbit')
        act.triggered.connect(self._reset_orbit)

    def _reset_orbit(self):
        ze = _np.zeros(self._orbx.shape)
        self._update_and_emit(ze, ze.copy(),'')

    def _save_orbit(self,register):
        def save():
            sub_orbx = _np.zeros(self._orbx.shape)
            sub_orby = _np.zeros(self._orby.shape)
            ref_file = None
            if register:
                regWid = getattr(self.main_window,'CM_Register'+str(register))
                sub_orbx = regWid.orbx
                sub_orby = regWid.orby
            orbx = self.main_window.SOFB_orbitx - sub_orbx
            orby = self.main_window.SOFB_orbity - sub_orby
            header = '# ' + _datetime.datetime.now().strftime('%Y/%M/%d-%H:%M:%S') + '\n'
            filename = QFileDialog.getSaveFileName(caption='Define a File Name to Save the Orbit',
                                        directory=self.last_dir,
                                        filter='Text files (*.txt)')
            fname = filename[0]
            fname += '' if fname.endswith(self.EXTENSION) else self.EXTENSION
            _np.savetxt(fname,_np.vstack([orbx,orby]).T)
            self._update_and_emit(orbx,orby,fname)
        return save

    def _load_orbit(self):
        filename = QFileDialog.getOpenFileName(caption='Select an Orbit File.',
                                               directory= self.last_dir,
                                               filter= self.EXTENSION)
        if not filename[0]: return
        orbx, orby = _np.loadtxt(filename,unpack=True)
        self._update_and_emit(orbx,orby,filename[0])

    def _update_and_emit(self,orbx,orby,fname):
        self._orbx = orbx
        self._orby = orby
        self.new_orbitx_signal.emit(orbx)
        self.new_orbity_signal.emit(orby)
        self.new_filename_signal.emit(fname)
        self.filename = fname
        self.last_dir = fname.rsplit('/',1)[0]
