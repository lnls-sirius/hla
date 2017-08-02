"""Define Controllers for the orbits displayed in the graphic."""

import numpy as _np
from PyQt5.QtCore import QObject
from selection_matrix import NR_BPMs


class _ComboboxController(QObject):
    def __init__(self, mWin):
        super().__init__(mWin)
        self.mWin = mWin
        self.readbackx.value_signal[_np.ndarray].connect(
                self.ioc_orbitx_changed)
        self.readbacky.value_signal[_np.ndarray].connect(
                self.ioc_orbity_changed)
        self.combo.currentTextChanged.connect(self._selection_changed)
        self.orbx = _np.zeros(NR_BPMs, dtype=float)
        self.orby = _np.zeros(NR_BPMs, dtype=float)
        self.signals_to_watch = tuple()
        self._selection_changed(self.combo.currentText())

    def _selection_changed(self, text):
        x_wave = y_wave = None
        if text.lower().startswith('register'):
            ind = text[-1]
            reg = getattr(self.mWin, 'CM_Register' + ind)
            sigs = (reg.new_orbitx_signal, reg.new_orbity_signal)
            x_wave = reg.orbx
            y_wave = reg.orby
        elif text.lower().startswith('golden'):
            x_wave = self.mWin.PV_SOFBGoldenOrbitXRB.value
            y_wave = self.mWin.PV_SOFBGoldenOrbitYRB.value
            sigs = (self.mWin.PV_SOFBGoldenOrbitXRB.value_signal[_np.ndarray],
                    self.mWin.PV_SOFBGoldenOrbitYRB.value_signal[_np.ndarray])
        elif text.lower().startswith('zero'):
            x_wave = _np.zeros(NR_BPMs, dtype=float)
            y_wave = _np.zeros(NR_BPMs, dtype=float)
            sigs = tuple()
        if x_wave is None:
            return False
        self.orbx, self.orby = x_wave, y_wave
        for sig in self.signals_to_watch:
            sig.disconnect(self._watch_interface)
        for sig in sigs:
            sig.connect(self._watch_interface)
        self.signals_to_watch = sigs
        self.setpointx.sendValue(x_wave)
        self.setpointy.sendValue(y_wave)
        return True

    def ioc_orbitx_changed(self, orb):
        if _np.allclose(orb, self.orbx, rtol=1e-7):
            return
        self.combo.setCurrentIndex(self.combo.count()-1)

    def ioc_orbity_changed(self, orb):
        if _np.allclose(orb, self.orby, rtol=1e-7):
            return
        self.combo.setCurrentIndex(self.combo.count()-1)

    def _watch_interface(self, orb):
        self.combo.setCurrentIndex(self.combo.count()-1)


class ReferenceController(_ComboboxController):
    """Create controller for reference orbit."""

    def __init__(self, mWin):
        """Initialize the instance."""
        self.setpointx = mWin.PV_SOFBOrbitRefXSP
        self.setpointy = mWin.PV_SOFBOrbitRefYSP
        self.readbackx = mWin.PV_SOFBOrbitRefXRB
        self.readbacky = mWin.PV_SOFBOrbitRefYRB
        self.combo = getattr(mWin, 'CB_RefOrbit')
        super().__init__(mWin)


class CorrectionOrbitController(_ComboboxController):
    """Create controller for displayed orbit."""

    def __init__(self, mWin):
        """Initialize the instance."""
        self.setpointx = mWin.PV_SOFBOfflineOrbitXSP
        self.setpointy = mWin.PV_SOFBOfflineOrbitYSP
        self.readbackx = mWin.PV_SOFBOfflineOrbitXRB
        self.readbacky = mWin.PV_SOFBOfflineOrbitYRB
        self.combo = getattr(mWin, 'CB_CorrectionOrbit')
        self._online = True
        mWin.PV_SOFBCorrectionModeRB.value_signal[int].connect(
                self._ioc_mode_changed)
        super().__init__(mWin)

    def _selection_changed(self, text):
        if text.lower().startswith('current orbit'):
            self._online = True
            self.mWin.PV_SOFBCorrectionModeSP.sendValue(1)
            self.readbackx.value_signal[_np.ndarray].disconnect(
                    self.ioc_orbitx_changed)
            self.readbacky.value_signal[_np.ndarray].disconnect(
                    self.ioc_orbity_changed)
            for sig in self.signals_to_watch:
                sig.disconnect(self._watch_interface)
            self.signals_to_watch = tuple()
            return True
        if not super()._selection_changed(text):
            return False
        self._online = False
        self.mWin.PV_SOFBCorrectionModeSP.sendValue(0)
        self.readbackx.value_signal[_np.ndarray].connect(
                self.ioc_orbitx_changed)
        self.readbacky.value_signal[_np.ndarray].connect(
                self.ioc_orbity_changed)
        return True

    def _ioc_mode_changed(self, mode):
        if self._online and mode == 0:
            self.combo.setCurrentIndex(self.combo.count()-1)
        elif not self._online and mode == 1:
            self.combo.setCurrentIndex(0)
