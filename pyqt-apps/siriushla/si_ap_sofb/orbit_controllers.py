"""Define Controllers for the orbits displayed in the graphic."""

from functools import partial as _part
import numpy as _np
from qtpy.QtWidgets import QComboBox, QHBoxLayout, QSizePolicy
from pydm.widgets.base import PyDMPrimitiveWidget
from siriushla.widgets import SiriusConnectionSignal
import siriuspy.csdevice.orbitcorr as _csorb

CONST = _csorb.get_consts('SI')


class _BaseController(QComboBox, PyDMPrimitiveWidget):
    def __init__(self, parent, ctrls, setpoint, readback):
        QComboBox.__init__(self, parent)
        PyDMPrimitiveWidget.__init__(self)
        self.setpoint = setpoint
        self.readback = readback
        self.ctrls = ctrls
        self.orbits = {
            'x': _np.zeros(CONST.NR_BPMS, dtype=float),
            'y': _np.zeros(CONST.NR_BPMS, dtype=float)}
        self.signals_to_watch = tuple()
        self.slots = {
            'x': _part(self._watch_if_changed, 'x'),
            'y': _part(self._watch_if_changed, 'y')}

        self.setup_ui()

    def channels(self):
        chans = list(self.readback.values())
        chans += list(self.setpoint.values())
        return chans

    def connect_signals(self):
        for pln in ('x', 'y'):
            self.readback[pln].new_value_signal[_np.ndarray].connect(
                _part(self.ioc_orbit_changed, pln))

    def setup_ui(self, add_items=[]):
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sz_pol.setHorizontalStretch(1)
        sz_pol.setVerticalStretch(0)
        sz_pol.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sz_pol)
        self.setEditable(True)
        for item in add_items:
            self.addItem(item)
        for reg in sorted(self.ctrls.keys()):
            self.addItem(reg)
        self.addItem('Out of Date')
        self.setCurrentIndex(self.count()-1)
        self.currentTextChanged.connect(self._selection_changed)

    def _selection_changed(self, text, sigs=tuple()):
        if text in self.ctrls:
            sigs = list()
            for pln in ('x', 'y'):
                orb = self.ctrls[text][pln]['getvalue']()
                if orb is None:
                    print('error')
                self.orbits[pln] = orb
                sigs.append(self.ctrls[text][pln]['signal'])
        for sig in self.signals_to_watch:
            sig.disconnect(self.slots[pln])
        for pln in ('x', 'y'):
            self.setpoint[pln].send_value_signal[_np.ndarray].emit(
                self.orbits[pln])
        self.signals_to_watch = sigs
        for sig in self.signals_to_watch:
            sig.connect(self.slots[pln])

    def ioc_orbit_changed(self, pln, orb):
        print('ioc orbit')
        self._orbit_changed(pln, orb)

    def _watch_if_changed(self, pln, orb):
        print('ctrl orbit')
        self._orbit_changed(pln, orb)

    def _orbit_changed(self, pln, orb):
        myorb = self.orbits[pln]
        if _np.allclose(orb, myorb, rtol=1e-7):
            return
        self.setCurrentIndex(self.count()-1)


class ReferenceController(_BaseController):
    def __init__(self, parent, prefix, ctrls):
        setpoint = dict()
        readback = dict()
        setpoint['x'] = SiriusConnectionSignal(prefix+'OrbitRefX-SP')
        setpoint['y'] = SiriusConnectionSignal(prefix+'OrbitRefY-SP')
        readback['x'] = SiriusConnectionSignal(prefix+'OrbitRefX-RB')
        readback['y'] = SiriusConnectionSignal(prefix+'OrbitRefY-RB')
        super().__init__(parent, ctrls, setpoint, readback)

    def _selection_changed(self, text):
        sigs = list()
        if text.lower().startswith('zero'):
            for pln in ('x', 'y'):
                self.orbits[pln] = _np.zeros(CONST.NR_BPMS, dtype=float)
        super()._selection_changed(text, sigs)

    def setup_ui(self):
        super().setup_ui(['Zero', ])


class CorrectionOrbitController(_BaseController):
    def __init__(self, parent, prefix, ctrls):
        setpoint = dict()
        readback = dict()
        setpoint['x'] = SiriusConnectionSignal(prefix+'OrbitOfflineX-SP')
        setpoint['y'] = SiriusConnectionSignal(prefix+'OrbitOfflineY-SP')
        readback['x'] = SiriusConnectionSignal(prefix+'OrbitOfflineX-RB')
        readback['y'] = SiriusConnectionSignal(prefix+'OrbitOfflineY-RB')
        super().__init__(parent, ctrls, setpoint, readback)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + pref+'SI-Glob:AP-SOFB:'
    pvs = [
        'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
        'OrbitOfflineX-RB', 'OrbitOfflineY-RB',
        'OrbitRefX-RB', 'OrbitRefY-RB']
    chans = []
    for pv in pvs:
        chans.append(SiriusConnectionSignal(prefix+pv))
    win._channels = chans
    ctrls = {
        'Online Orbit': {
            'x': {
                'signal': chans[0].new_value_signal,
                'getvalue': chans[0].getvalue},
            'y': {
                'signal': chans[1].new_value_signal,
                'getvalue': chans[1].getvalue}},
        'Offline Orbit': {
            'x': {
                'signal': chans[2].new_value_signal,
                'getvalue': chans[2].getvalue},
            'y': {
                'signal': chans[3].new_value_signal,
                'getvalue': chans[3].getvalue}},
        'Reference Orbit': {
            'x': {
                'signal': chans[4].new_value_signal,
                'getvalue': chans[4].getvalue},
            'y': {
                'signal': chans[5].new_value_signal,
                'getvalue': chans[5].getvalue}}}
    wid = ControlOrbit(win, prefix, ctrls)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
