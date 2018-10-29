"""Creates the Contextes Menus for the Register."""

import numpy as _np
from functools import partial as _part
from datetime import datetime as _datetime
from qtpy.QtWidgets import QMenu, QFileDialog, QWidget, QMessageBox, \
    QScrollArea, QLabel, QPushButton, QSizePolicy, \
    QGridLayout, QVBoxLayout, QHBoxLayout
from qtpy.QtCore import Signal, Qt, QRect
from siriuspy.csdevice.orbitcorr import OrbitCorrDev
from siriuspy.servconf.srvconfig import ConnConfigService
from siriushla.as_ap_servconf import LoadConfiguration, SaveConfiguration
from siriushla.widgets import SiriusConnectionSignal


class OrbitRegisters(QWidget):

    def __init__(self, parent, prefix, acc=None, nr_registers=9):
        super(OrbitRegisters, self).__init__(parent)
        self._nr_registers = nr_registers
        self.prefix = prefix
        self.acc = acc
        pre = self.prefix
        self._orbits = {
            'ref': [
                SiriusConnectionSignal(pre + 'OrbitRefX-RB'),
                SiriusConnectionSignal(pre + 'OrbitRefY-RB')],
            'mti': [
                SiriusConnectionSignal(pre + 'OrbitMultiTurnX-Mon'),
                SiriusConnectionSignal(pre + 'OrbitMultiTurnY-Mon')],
            'sp': [
                SiriusConnectionSignal(pre + 'OrbitSmoothSinglePassX-Mon'),
                SiriusConnectionSignal(pre + 'OrbitSmoothSinglePassY-Mon')],
            'orb': [
                SiriusConnectionSignal(pre + 'OrbitSmoothX-Mon'),
                SiriusConnectionSignal(pre + 'OrbitSmoothY-Mon')],
            'off': [
                SiriusConnectionSignal(pre + 'OrbitOfflineX-SP'),
                SiriusConnectionSignal(pre + 'OrbitOfflineY-SP')],
            }
        self.setupui()

    def channels(self):
        chans = []
        for v in self._orbits.values():
            chans.extend(v)
        return chans

    def setupui(self):
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
            reg = OrbitRegister(
                self, self.prefix, self._orbits, i+1, acc=self.acc)
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

    new_orbx_signal = Signal(_np.ndarray)
    new_orby_signal = Signal(_np.ndarray)
    new_string_signal = Signal(str)

    def __init__(self, parent, prefix, orbits, idx, acc='SI'):
        """Initialize the Context Menu."""
        super(OrbitRegister, self).__init__(parent)
        self.idx = idx
        self.prefix = prefix
        text = acc.lower() + 'orb'
        self.EXT = '.' + text
        self.EXT_FLT = 'Sirius Orbit Files (*.{})'.format(text)
        self._config_type = acc.lower() + '_orbit'
        self._servconf = ConnConfigService(self._config_type)
        self._csorb = OrbitCorrDev(acc.upper())
        self.string_status = 'Empty'
        self.name = 'Register {0:d}'.format(self.idx)
        self.setup_ui()

        self._orbits = orbits
        self.last_dir = self.DEFAULT_DIR
        self.filename = ''
        self._orbx = _np.zeros(self._csorb.NR_BPMS)
        self._orby = _np.zeros(self._csorb.NR_BPMS)

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
        self.setMinimumWidth(350)
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

        act = menu.addAction('Load From &File')
        act.triggered.connect(self._load_orbit_from_file)
        act = menu.addAction('Load From &ServConf')
        act.triggered.connect(self._load_orbit_from_servconf)
        menu2 = menu.addMenu('Load from &PV')
        act = menu2.addAction('&Smooth Orbit')
        act.triggered.connect(_part(self._register_orbit, 'orb'))
        act = menu2.addAction('&MultiTurn Orbit')
        act.triggered.connect(_part(self._register_orbit, 'mti'))
        act = menu2.addAction('Single&Pass Orbit')
        act.triggered.connect(_part(self._register_orbit, 'sp'))
        act = menu2.addAction('&Reference Orbit')
        act.triggered.connect(_part(self._register_orbit, 'ref'))
        act = menu2.addAction('&Offline Orbit')
        act.triggered.connect(_part(self._register_orbit, 'off'))
        act = menu.addAction('&Clear Register')
        act.triggered.connect(self._reset_orbit)
        act = menu.addAction('Save To File')
        act.triggered.connect(self._save_orbit_to_file)
        act = menu.addAction('Save To ServConf')
        act.triggered.connect(self._save_orbit_to_servconf)

    def _reset_orbit(self):
        zer = _np.zeros(self._orbx.shape)
        self._update_and_emit('Empty', zer, zer.copy(), '')

    def _register_orbit(self, flag, _):
        pvx, pvy = self._orbits.get(flag, (None, None))
        if not pvx or not pvy:
            self._update_and_emit('Error: wrong specification.')
            return
        if not pvx.connected or not pvy.connected:
            self._update_and_emit(
                'Error: PV {0:s} not connected.'.format(pvx.pvname))
            return
        self._update_and_emit(
            'Orbit Registered.', pvx.getvalue(), pvy.getvalue())

    def _save_orbit_to_file(self, _):
        header = '# ' + _datetime.now().strftime('%Y/%M/%d-%H:%M:%S') + '\n'
        header += '# ' + 'BPMX [um]       BPMY [um]' + '\n'
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

    def _load_orbit_from_file(self):
        filename = QFileDialog.getOpenFileName(caption='Select an Orbit File.',
                                               directory=self.last_dir,
                                               filter=self.EXT_FLT)
        if not filename[0]:
            return
        orbx, orby = _np.loadtxt(filename[0], unpack=True)
        self._update_and_emit('Orbit Loaded: ', orbx, orby, filename[0])

    def _load_orbit_from_servconf(self):
        win = LoadConfiguration(self._config_type, self)
        win.configname.connect(self._set_orbit)
        win.show()

    def _set_orbit(self, confname):
        data, _ = self._servconf.config_get(confname)
        self._update_and_emit(
            'Orbit Loaded: '+confname,
            _np.array(data['x']), _np.array(data['y']))

    def _save_orbit_to_servconf(self):
        win = SaveConfiguration(self._config_type, self)
        win.configname.connect(self._save_orbit)
        win.show()

    def _save_orbit(self, confname):
        data = {'x': self._orbx.tolist(), 'y': self.orby.tolist()}
        try:
            self._servconf.config_insert(confname, data)
        except TypeError as e:
            QMessageBox.warning(self, 'Warning', str(e), QMessageBox.Ok)

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
    wid = OrbitRegisters(win, pref + 'SI-Glob:AP-SOFB:', 9)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys

    _main()
