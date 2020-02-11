"""Creates the Contextes Menus for the Register."""

from functools import partial as _part
from datetime import datetime as _datetime
import numpy as _np
from qtpy.QtWidgets import QMenu, QFileDialog, QWidget, QMessageBox, \
    QScrollArea, QLabel, QPushButton, QSizePolicy, QGridLayout, QVBoxLayout, \
    QHBoxLayout, QDialog, QComboBox, QLineEdit
from qtpy.QtCore import Signal, Qt
from qtpy.QtGui import QDoubleValidator
import qtawesome as qta

from siriuspy.csdevice.orbitcorr import SOFBFactory
from siriuspy.clientconfigdb import ConfigDBClient, ConfigDBException
from siriushla.as_ap_configdb import LoadConfigDialog, SaveConfigDialog
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
                SiriusConnectionSignal(pre + 'RefOrbX-RB'),
                SiriusConnectionSignal(pre + 'RefOrbY-RB')],
            'mti': [
                SiriusConnectionSignal(pre + 'MTurnIdxOrbX-Mon'),
                SiriusConnectionSignal(pre + 'MTurnIdxOrbY-Mon')],
            'sp': [
                SiriusConnectionSignal(pre + 'SPassOrbX-Mon'),
                SiriusConnectionSignal(pre + 'SPassOrbY-Mon')],
            'orb': [
                SiriusConnectionSignal(pre + 'SlowOrbX-Mon'),
                SiriusConnectionSignal(pre + 'SlowOrbY-Mon')],
            'off': [
                SiriusConnectionSignal(pre + 'OfflineOrbX-SP'),
                SiriusConnectionSignal(pre + 'OfflineOrbY-SP')],
            'bpm': [
                SiriusConnectionSignal(pre + 'BPMOffsetX-Mon'),
                SiriusConnectionSignal(pre + 'BPMOffsetY-Mon')],
            'mat': SiriusConnectionSignal(pre + 'RespMat-RB'),
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
        scr_ar_wid.setObjectName('scr_ar_wid')
        scr_ar_wid.setStyleSheet("""
            #scr_ar_wid{
                min-width:40em; min-height:10em;
                background-color: transparent;
            }""")
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
        self.setObjectName(text+str(idx))
        self.EXT = '.' + text
        self.EXT_FLT = 'Sirius Orbit Files (*.{})'.format(text)
        self._config_type = acc.lower() + '_orbit'
        self._client = ConfigDBClient(config_type=self._config_type)
        self._csorb = SOFBFactory.create(acc.upper())
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
        self.setStyleSheet("""
            #{}{{
                min-width:11.29em;
            }}""".format(self.objectName()))
        hbl = QHBoxLayout(self)

        btn = QPushButton(self.name, self)
        hbl.addWidget(btn)
        btn.setEnabled(True)
        btn.setAutoDefault(False)

        lbl = QLabel(self)
        hbl.addWidget(lbl)
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setHorizontalStretch(1)
        lbl.setSizePolicy(sz_pol)
        lbl.setMouseTracking(True)
        lbl.setAcceptDrops(True)
        lbl.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.new_string_signal.connect(lbl.setText)

        menu = QMenu(btn)
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.setMenu(menu)
        btn.clicked.connect(btn.showMenu)

        act = menu.addAction('Get From &File')
        act.setIcon(qta.icon('mdi.file-upload-outline'))
        act.triggered.connect(self._load_orbit_from_file)
        act = menu.addAction('Get From &ServConf')
        act.setIcon(qta.icon('mdi.cloud-download-outline'))
        act.triggered.connect(self._load_orbit_from_servconf)
        menu2 = menu.addMenu('Get from &PV')
        menu2.setIcon(qta.icon('mdi.download-network-outline'))
        if self._csorb.isring:
            act = menu2.addAction('&SlowOrb')
            act.setIcon(qta.icon('mdi.turtle'))
            act.triggered.connect(_part(self._register_orbit, 'orb'))
            act = menu2.addAction('&MTurnOrb')
            act.setIcon(qta.icon('mdi.alarm-multiple'))
            act.triggered.connect(_part(self._register_orbit, 'mti'))
        act = menu2.addAction('S&PassOrb')
        act.setIcon(qta.icon('mdi.clock-fast'))
        act.triggered.connect(_part(self._register_orbit, 'sp'))
        act = menu2.addAction('&RefOrb')
        act.triggered.connect(_part(self._register_orbit, 'ref'))
        act = menu2.addAction('&OfflineOrb')
        act.setIcon(qta.icon('mdi.signal-off'))
        act.triggered.connect(_part(self._register_orbit, 'off'))
        act = menu2.addAction('&BPM Offsets')
        act.setIcon(qta.icon('mdi.currency-sign'))
        act.triggered.connect(_part(self._register_orbit, 'bpm'))
        act = menu2.addAction('RespMat')
        act.setIcon(qta.icon('mdi.matrix'))
        act.triggered.connect(self._open_matrix_sel)
        act = menu.addAction('&Edit Orbit')
        act.setIcon(qta.icon('mdi.table-edit'))
        act.triggered.connect(self._edit_orbit)
        act = menu.addAction('&Clear')
        act.setIcon(qta.icon('mdi.delete-empty'))
        act.triggered.connect(self._reset_orbit)
        act = menu.addAction('Save To File')
        act.setIcon(qta.icon('mdi.file-download-outline'))
        act.triggered.connect(self._save_orbit_to_file)
        act = menu.addAction('Save To ServConf')
        act.setIcon(qta.icon('mdi.cloud-upload-outline'))
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
                'Error: PV {0:s} not connected.'.format(pvx.address))
            return
        self._update_and_emit(
            'Orbit Registered.', pvx.getvalue(), pvy.getvalue())

    def _open_matrix_sel(self):
        wid = QDialog(self)
        wid.setObjectName(self._csorb.acc+'App')
        wid.setLayout(QVBoxLayout())

        cbbox = QComboBox(wid)
        cbbox.setEditable(True)
        cbbox.setMaxVisibleItems(10)
        corrnames = self._csorb.CH_NAMES + self._csorb.CV_NAMES
        if self._csorb.acc == 'SI':
            corrnames.append('RF')
        cbbox.addItems(corrnames)
        wid.layout().addWidget(QLabel('Choose the corrector:', wid))
        wid.layout().addWidget(cbbox)

        ledit = QLineEdit(wid)
        ledit.setValidator(QDoubleValidator())
        ledit.setText('1.0')
        wid.layout().addWidget(QLabel('Choose the Kick [urad]:', wid))
        wid.layout().addWidget(ledit)
        ledit.textChanged.connect(_part(self._accept_mat_sel, ledit, cbbox))
        cbbox.currentIndexChanged.connect(
            _part(self._accept_mat_sel, ledit, cbbox))

        hlay = QHBoxLayout()
        cancel = QPushButton('Cancel', wid)
        confirm = QPushButton('Ok', wid)
        cancel.clicked.connect(wid.reject)
        confirm.clicked.connect(wid.accept)
        confirm.setDefault(True)
        hlay.addStretch()
        hlay.addWidget(cancel)
        hlay.addStretch()
        hlay.addWidget(confirm)
        hlay.addStretch()
        wid.layout().addItem(hlay)
        res = wid.exec_()

        if res != QDialog.Accepted:
            self._reset_orbit()

    def _accept_mat_sel(self, ledit, cbbox, _):
        idx = cbbox.currentIndex()
        corr = cbbox.currentText()
        if not ledit.text():
            return
        kick = float(ledit.text())
        pvm = self._orbits.get('mat')
        if pvm is None or not pvm.connected:
            self._update_and_emit(
                'Error: PV {0:s} not connected.'.format(pvm.pvname))
        val = pvm.getvalue()
        orbs = val.reshape(-1, self._csorb.NR_CORRS)[:, idx]
        orbx = orbs[:len(orbs)//2] * kick
        orby = orbs[len(orbs)//2:] * kick
        self._update_and_emit(
            'RespMat: {0:s}'.format(corr), orbx, orby)

    def _edit_orbit(self):
        orbx = self.orbx
        orby = self.orby

        wid = QDialog(self)
        wid.setObjectName(self._csorb.acc+'App')
        wid.setLayout(QVBoxLayout())

        hbl = QHBoxLayout()
        wid.layout().addItem(hbl)
        hbl.addWidget(QLabel('X = ', wid))
        multx = QLineEdit(wid)
        multx.setValidator(QDoubleValidator())
        multx.setText('1.0')
        # multx.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        multx.setAlignment(Qt.AlignCenter)
        multx.setStyleSheet('max-width:5em;')
        hbl.addWidget(multx)
        hbl.addWidget(QLabel('*X   +   ', wid))
        addx = QLineEdit(wid)
        addx.setValidator(QDoubleValidator())
        addx.setText('0.0')
        addx.setAlignment(Qt.AlignCenter)
        addx.setStyleSheet('max-width:5em;')
        hbl.addWidget(addx)
        hbl.addWidget(QLabel(' [um]', wid))

        hbl = QHBoxLayout()
        wid.layout().addItem(hbl)
        hbl.addWidget(QLabel('Y = ', wid))
        multy = QLineEdit(wid)
        multy.setValidator(QDoubleValidator())
        multy.setText('1.0')
        # multy.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        multy.setAlignment(Qt.AlignCenter)
        multy.setStyleSheet('max-width:5em;')
        hbl.addWidget(multy)
        hbl.addWidget(QLabel('*Y   +   ', wid))
        addy = QLineEdit(wid)
        addy.setValidator(QDoubleValidator())
        addy.setText('0.0')
        addy.setAlignment(Qt.AlignCenter)
        addy.setStyleSheet('max-width:5em;')
        hbl.addWidget(addy)
        hbl.addWidget(QLabel(' [um]', wid))

        hlay = QHBoxLayout()
        cancel = QPushButton('Cancel', wid)
        confirm = QPushButton('Ok', wid)
        cancel.clicked.connect(wid.reject)
        confirm.clicked.connect(wid.accept)
        hlay.addStretch()
        hlay.addWidget(cancel)
        hlay.addStretch()
        hlay.addWidget(confirm)
        hlay.addStretch()
        wid.layout().addItem(hlay)
        res = wid.exec_()

        if res == QDialog.Accepted:
            mltx = float(multx.text())
            mlty = float(multy.text())
            plusx = float(addx.text())
            plusy = float(addy.text())
            orbx = mltx * orbx + plusx
            orby = mlty * orby + plusy
            self._update_and_emit('Orbit Edited', orbx, orby)

    def _save_orbit_to_file(self, _):
        header = '# ' + _datetime.now().strftime('%Y/%m/%d-%H:%M:%S') + '\n'
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
        win = LoadConfigDialog(self._config_type, self)
        win.configname.connect(self._set_orbit)
        win.show()

    def _set_orbit(self, confname):
        data = self._client.get_config_value(confname)
        self._update_and_emit(
            'Orbit Loaded: '+confname,
            _np.array(data['x']), _np.array(data['y']))

    def _save_orbit_to_servconf(self):
        win = SaveConfigDialog(self._config_type, self)
        win.configname.connect(self._save_orbit)
        win.show()

    def _save_orbit(self, confname):
        data = {'x': self._orbx.tolist(), 'y': self.orby.tolist()}
        try:
            self._client.insert_config(confname, data)
        except (ConfigDBException, TypeError) as err:
            QMessageBox.warning(self, 'Warning', str(err), QMessageBox.Ok)

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
    wid = OrbitRegisters(win, pref + 'SI-Glob:AP-SOFB:', 'SI')
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import VACA_PREFIX as pref
    import sys

    _main()
