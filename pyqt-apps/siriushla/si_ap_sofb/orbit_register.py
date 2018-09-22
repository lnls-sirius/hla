"""Creates the Contextes Menus for the Register."""

import numpy as _np
from functools import partial as _part
from datetime import datetime as _datetime
from epics import PV as _PV
from qtpy.QtWidgets import (
    QMenu, QFileDialog, QWidget, QScrollArea, QLabel, QPushButton,
    QSizePolicy, QGridLayout, QVBoxLayout, QHBoxLayout)
from qtpy.QtCore import Signal, QRect, Qt
from siriushla.si_ap_sofb.selection_matrix import NR_BPMs


class OrbitRegisters(QWidget):

    def __init__(self, parent, prefix, nr_registers):
        super(OrbitRegisters, self).__init__(parent)
        self._nr_registers = nr_registers
        self.prefix = prefix
        self._setup_ui()

    def _setup_ui(self):
        gdl = QGridLayout(self)
        gdl.setContentsMargins(0, 0, 0, 0)

        scr_ar = QScrollArea(self)
        gdl.addWidget(scr_ar, 0, 0, 1, 1)
        scr_ar.setSizeAdjustPolicy(QScrollArea.AdjustToContentsOnFirstShow)
        scr_ar.setWidgetResizable(True)

        scr_ar_wid = QWidget()
        scr_ar.setWidget(scr_ar_wid)
        scr_ar_wid.setGeometry(QRect(0, 0, 730, 284))
        hbl = QHBoxLayout(scr_ar_wid)
        hbl.setContentsMargins(0, 0, 0, 0)

        vbl = QVBoxLayout()

        hbl.addLayout(vbl)

        self.registers = []
        for i in range(self._nr_registers):
            reg = OrbitRegister(self, self.prefix, i+1)
            vbl.addWidget(reg)
            self.registers.append(reg)

    def get_registers_control(self):
        ctrls = dict()
        for reg in self.registers:
            ctrls[reg.name] = dict()
            ctrls[reg.name]['x'] = dict()
            ctrls[reg.name]['x']['signal'] = reg.new_orbx_signal
            ctrls[reg.name]['x']['getvalue'] = reg.getorbx
            ctrls[reg.name]['y'] = dict()
            ctrls[reg.name]['y']['signal'] = reg.new_orby_signal
            ctrls[reg.name]['y']['getvalue'] = reg.getorby
        return ctrls


class OrbitRegister(QWidget):
    """Create the Context Menu for the Registers."""

    DEFAULT_DIR = '/home/fac/sirius-iocs/si-ap-sofb'
    EXT = '.siorb'
    EXT_FLT = 'Sirius Orbit Files (*.siorb)'

    new_orbx_signal = Signal(_np.ndarray)
    new_orby_signal = Signal(_np.ndarray)
    new_string_signal = Signal(str)

    def __init__(self, parent, prefix, idx):
        """Initialize the Context Menu."""
        super(OrbitRegister, self).__init__(parent)
        self.idx = idx
        self.prefix = prefix
        self.string_status = 'Empty'
        self.name = 'Register {0:d}'.format(self.idx)
        self.setup_ui()

        pre = prefix[5:]  # remove ca://
        self._orbits = {
            'ref': [
                _PV(pre + 'OrbitRefX-RB'),
                _PV(pre + 'OrbitRefY-RB')],
            'orb': [
                _PV(pre + 'OrbitSmoothX-Mon'),
                _PV(pre + 'OrbitSmoothX-Mon')],
            'off': [
                _PV(pre + 'OrbitOfflineX-SP'),
                _PV(pre + 'OrbitOfflineY-SP')],
            }
        self.last_dir = self.DEFAULT_DIR
        self.filename = ''
        self._orbx = _np.zeros(NR_BPMs)
        self._orby = _np.zeros(NR_BPMs)

        self.new_string_signal.emit(self.string_status)

    def getorbx(self):
        """Return the horizontal orbit."""
        return self._orbx.copy()

    orbx = property(fget=getorbx)

    def getorby(self):
        """Return the Vertical orbit."""
        return self._orby.copy()

    orby = property(fget=getorby)

    def setup_ui(self):
        """Setup Ui of Context Menu."""
        hbl = QHBoxLayout(self)

        btn = QPushButton(self.name, self)
        hbl.addWidget(btn)
        btn.setEnabled(True)
        btn.setAutoDefault(False)

        lbl = QLabel(self)
        hbl.addWidget(lbl)
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setHorizontalStretch(1)
        sz_pol.setVerticalStretch(0)
        sz_pol.setHeightForWidth(lbl.sizePolicy().hasHeightForWidth())
        lbl.setSizePolicy(sz_pol)
        lbl.setMouseTracking(True)
        lbl.setAcceptDrops(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.new_string_signal.connect(lbl.setText)

        menu = QMenu(btn)
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.setMenu(menu)
        btn.clicked.connect(btn.showMenu)

        act = menu.addAction('&Load Orbit')
        act.triggered.connect(self._load_orbit)
        menu2 = menu.addMenu('Register &Orbit')
        act = menu2.addAction('Last &Measured Orbit')
        act.triggered.connect(_part(self._register_orbit, 'orb'))
        act = menu2.addAction('Re&ference Orbit')
        act.triggered.connect(_part(self._register_orbit, 'ref'))
        act = menu2.addAction('&Offline Orbit')
        act.triggered.connect(_part(self._register_orbit, 'off'))
        act = menu.addAction('&Reset Orbit')
        act.triggered.connect(self._reset_orbit)
        act = menu.addAction('&Save Registered Orbit')
        act.triggered.connect(self._save_orbit)

    def _reset_orbit(self):
        zer = _np.zeros(self._orbx.shape)
        self._update_and_emit('Empty', zer, zer.copy(), '')

    def _register_orbit(self, flag, trig):
        pvx, pvy = self._orbits.get(flag, (None, None))
        if not pvx or not pvy:
            self._update_and_emit('Error: wrong specification.')
            return
        if not pvx.connected or not pvy.connected:
            self._update_and_emit(
                'Error: PV {0:s} not connected.'.format(pvx.pvname))
            return
        self._update_and_emit('Orbit Registered.', pvx.value, pvy.value)

    def _save_orbit(self, trig):
        header = '# ' + _datetime.now().strftime('%Y/%M/%d-%H:%M:%S') + '\n'
        filename = QFileDialog.getSaveFileName(
            caption='Define a File Name to Save the Orbit',
            directory=self.last_dir,
            filter=self.EXT_FLT)
        fname = filename[0]
        if not fname:
            return
        fname += '' if fname.endswith(self.EXT) else self.EXT
        _np.savetxt(fname, _np.vstack([self.orbx, self.orby]).T, header=header)
        self._update_and_emit('Orbit Saved: ', self.orbx, self.orby, fname)

    def _load_orbit(self):
        filename = QFileDialog.getOpenFileName(caption='Select an Orbit File.',
                                               directory=self.last_dir,
                                               filter=self.EXT_FLT)
        if not filename[0]:
            return
        orbx, orby = _np.loadtxt(filename[0], unpack=True)
        self._update_and_emit('Orbit Loaded: ', orbx, orby, filename[0])

    def _update_and_emit(self, string, orbx=None, orby=None, fname=''):
        if orbx is None or orby is None:
            self.string_status = string
            self.new_string_signal.emit(self.string_status)
            return
        self._orbx = orbx
        self._orby = orby
        pure_name = ''
        path = self.last_dir
        if fname:
            path, pure_name = fname.rsplit('/', 1)
        self.string_status = string + pure_name
        self.filename = fname
        self.last_dir = path
        self.new_orbx_signal.emit(orbx)
        self.new_orby_signal.emit(orby)
        self.new_string_signal.emit(self.string_status)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    wid = OrbitRegisters(win, 'ca://' + pref+'SI-Glob:AP-SOFB:', 9)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys

    _main()
