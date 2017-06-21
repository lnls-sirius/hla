import numpy as _np
from PyQt5.QtCore import QObject
from selection_matrix import NR_BPMs


class _ComboboxController(QObject):
    def __init__(self,main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.readbackx.value_signal[_np.ndarray].connect(self.ioc_orbitx_changed)
        self.readbacky.value_signal[_np.ndarray].connect(self.ioc_orbity_changed)
        self.combo.currentTextChanged.connect(self._selection_changed)
        self.orbx = _np.zeros(NR_BPMs,dtype=float)
        self.orby = _np.zeros(NR_BPMs,dtype=float)
        self.signals_to_watch = tuple()
        self._selection_changed(self.combo.currentText())

    def _selection_changed(self,text):
        x_wave = y_wave = None
        if text.lower().startswith('register'):
            ind = text[-1]
            reg = getattr(self.main_window,'CM_Register'+ind)
            sigs = (reg.new_orbitx_signal, reg.new_orbity_signal)
            x_wave = reg.orbx
            y_wave = reg.orby
        elif text.lower().startswith('golden'):
            x_wave = self.main_window.PV_SOFBGoldenOrbitXRB.value
            y_wave = self.main_window.PV_SOFBGoldenOrbitYRB.value
            sigs = (self.main_window.PV_SOFBGoldenOrbitXRB.value_signal[_np.ndarray],
                    self.main_window.PV_SOFBGoldenOrbitYRB.value_signal[_np.ndarray])
        elif text.lower().startswith('zero'):
            x_wave = _np.zeros(NR_BPMs,dtype=float)
            y_wave = _np.zeros(NR_BPMs,dtype=float)
            sigs = tuple()
        if x_wave is None: return False
        self.orbx, self.orby = x_wave, y_wave
        for sig in self.signals_to_watch: sig.disconnect(self._watch_interface)
        for sig in sigs: sig.connect(self._watch_interface)
        self.signals_to_watch = sigs
        self.setpointx.sendValue(x_wave)
        self.setpointy.sendValue(y_wave)
        return True

    def ioc_orbitx_changed(self,orb):
        if _np.allclose(orb,self.orbx,rtol=1e-7): return
        self.combo.setCurrentIndex(self.combo.count()-1)

    def ioc_orbity_changed(self,orb):
        if _np.allclose(orb,self.orby,rtol=1e-7): return
        self.combo.setCurrentIndex(self.combo.count()-1)

    def _watch_interface(self,orb):
        self.combo.setCurrentIndex(self.combo.count()-1)


class ReferenceController(_ComboboxController):
    def __init__(self,main_window):
        self.setpointx = main_window.PV_SOFBOrbitRefXSP
        self.setpointy = main_window.PV_SOFBOrbitRefYSP
        self.readbackx = main_window.PV_SOFBOrbitRefXRB
        self.readbacky = main_window.PV_SOFBOrbitRefYRB
        self.combo = getattr(main_window,'CB_RefOrbit')
        super().__init__(main_window)


class CorrectionOrbitController(_ComboboxController):
    def __init__(self,main_window):
        self.setpointx = main_window.PV_SOFBOfflineOrbitXSP
        self.setpointy = main_window.PV_SOFBOfflineOrbitYSP
        self.readbackx = main_window.PV_SOFBOfflineOrbitXRB
        self.readbacky = main_window.PV_SOFBOfflineOrbitYRB
        self.combo = getattr(main_window,'CB_CorrectionOrbit')
        self._online = True
        main_window.PV_SOFBCorrectionModeRB.value_signal[int].connect(self.ioc_mode_changed)
        super().__init__(main_window)

    def _selection_changed(self,text):
        if text.lower().startswith('current orbit'):
            self._online = True
            self.main_window.PV_SOFBCorrectionModeSP.sendValue(1)
            self.readbackx.value_signal[_np.ndarray].disconnect(self.ioc_orbitx_changed)
            self.readbacky.value_signal[_np.ndarray].disconnect(self.ioc_orbity_changed)
            for sig in self.signals_to_watch: sig.disconnect(self._watch_interface)
            self.signals_to_watch = tuple()
            return True
        if not super()._selection_changed(text): return False
        self._online = False
        self.main_window.PV_SOFBCorrectionModeSP.sendValue(0)
        self.readbackx.value_signal[_np.ndarray].connect(self.ioc_orbitx_changed)
        self.readbacky.value_signal[_np.ndarray].connect(self.ioc_orbity_changed)
        return True

    def ioc_mode_changed(self,mode):
        if self._online and mode == 0:
            self.combo.setCurrentIndex(self.combo.count()-1)
        elif not self._online and mode == 1:
            self.combo.setCurrentIndex(0)
