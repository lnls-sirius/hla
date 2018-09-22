"""Control the Orbit Graphic Display."""

import numpy as _np
from datetime import datetime as _datetime
from PyQt5.QtCore import Signal, QObject, QTimer
from pyqtgraph import mkBrush, mkPen
from PyQt5.QtWidgets import QFileDialog
from siriushla.si_ap_sofb.selection_matrix import NR_BPMs


class GraphicOrbitControllers(QObject):
    """Control the Orbit Graphic Display."""

    DEFAULT_DIR = '/home/fac/sirius-iocs/si-ap-sofb'
    EXT = '.txt'
    EXT_FLT = 'Text Files (*.txt)'
    FMT = '{0:8.3g}'

    averagex_str_signal = Signal(str)
    stdx_str_signal = Signal(str)
    averagey_str_signal = Signal(str)
    stdy_str_signal = Signal(str)

    def __init__(self, mWin, index):
        """Initialize the instance."""
        super().__init__(mWin)
        self.mWin = mWin
        self.last_dir = self.DEFAULT_DIR
        self.update_rate = 4  # Hz

        pbSave = getattr(self.mWin, 'PB_Line' + str(index) + 'Save')
        pbSave.clicked.connect(self._save_difference)
        cbOrb = getattr(self.mWin, 'CB_Line'+str(index) + 'Orb')
        cbRef = getattr(self.mWin, 'CB_Line'+str(index) + 'Ref')
        cbOrb.currentTextChanged.connect(self._orb_changed)
        cbRef.currentTextChanged.connect(self._ref_changed)
        mWin.PV_SOFBBPMXEnblListRB.receive_value_signal[_np.ndarray].connect(
                self._update_enable_list('x'))
        mWin.PV_SOFBBPMYEnblListRB.receive_value_signal[_np.ndarray].connect(
                self._update_enable_list('y'))
        self.orbx = _np.zeros(NR_BPMs, dtype=float)
        self.orby = _np.zeros(NR_BPMs, dtype=float)
        self.refx = _np.zeros(NR_BPMs, dtype=float)
        self.refy = _np.zeros(NR_BPMs, dtype=float)
        self.enblx = _np.ones(NR_BPMs, dtype=bool)
        self.enbly = _np.ones(NR_BPMs, dtype=bool)
        self.orbx_signal = None
        self.orby_signal = None
        self.refx_signal = None
        self.refy_signal = None
        self.offbrush = mkBrush(100, 100, 100)
        self.offpen = mkPen(100, 100, 100)

        avex = getattr(mWin, 'LB_Line' + str(index) + 'XAve')
        avey = getattr(mWin, 'LB_Line' + str(index) + 'YAve')
        stdx = getattr(mWin, 'LB_Line' + str(index) + 'XStd')
        stdy = getattr(mWin, 'LB_Line' + str(index) + 'YStd')
        self.averagex_str_signal.connect(avex.setText)
        self.averagey_str_signal.connect(avey.setText)
        self.stdx_str_signal.connect(stdx.setText)
        self.stdy_str_signal.connect(stdy.setText)

        base_ind = (4-index)*4-1

        mWin.PyDMWP_OrbitX._legend.removeItem("")
        mWin.PyDMWP_OrbitX.plotItem.showButtons()
        curves = mWin.PyDMWP_OrbitX._curves
        self.diffTracex = curves[base_ind]
        self.brushx = mkBrush(curves[base_ind].color)
        self.penx = mkPen(curves[base_ind].color)
        self.diffSetValuex = curves[base_ind].receiveYWaveform
        self.aveSetValuex = curves[base_ind-1].receiveYWaveform
        self.aveMstdSetValuex = curves[base_ind-2].receiveYWaveform
        self.avePstdSetValuex = curves[base_ind-3].receiveYWaveform
        cb = getattr(mWin, 'CB_Line'+str(index)+'Show')
        cbx = getattr(mWin, 'CB_Line'+str(index)+'ShowXStat')
        cb.toggled.connect(cbx.setEnabled)
        cb.toggled.connect(cbx.setChecked)
        for i in range(4):
            cb.toggled.connect(curves[base_ind-i].setVisible)
            if i != 0:
                cbx.toggled.connect(curves[base_ind-i].setVisible)

        mWin.PyDMWP_OrbitY._legend.removeItem("")
        mWin.PyDMWP_OrbitY.plotItem.showButtons()
        curves = mWin.PyDMWP_OrbitY._curves
        self.diffTracey = curves[base_ind]
        self.brushy = mkBrush(curves[base_ind].color)
        self.peny = mkPen(curves[base_ind].color)
        self.diffSetValuey = curves[base_ind].receiveYWaveform
        self.aveSetValuey = curves[base_ind-1].receiveYWaveform
        self.aveMstdSetValuey = curves[base_ind-2].receiveYWaveform
        self.avePstdSetValuey = curves[base_ind-3].receiveYWaveform
        cby = getattr(mWin, 'CB_Line'+str(index)+'ShowYStat')
        cb.toggled.connect(cby.setEnabled)
        cb.toggled.connect(cby.setChecked)
        for i in range(4):
            cb.toggled.connect(curves[base_ind-i].setVisible)
            if i != 0:
                cby.toggled.connect(curves[base_ind-i].setVisible)

        if index > 1:
            getattr(mWin, 'CB_Line' + str(index) + 'Show').setChecked(False)

        self._orb_changed(cbOrb.currentText())
        self._ref_changed(cbRef.currentText())

        self.timer_update_graph = QTimer()
        self.timer_update_graph.timeout.connect(self._update_graphic)
        self.timer_update_graph.start(1000/self.update_rate)  # im miliseconds

    def _orb_changed(self, text): self._some_changed('orb', text)

    def _ref_changed(self, text): self._some_changed('ref', text)

    def _some_changed(self, ref, text):
        x_sig = getattr(self, ref + 'x_signal')
        y_sig = getattr(self, ref + 'y_signal')
        x_slot = getattr(self, '_update_' + ref + 'x')
        y_slot = getattr(self, '_update_' + ref + 'y')

        main_ = self.mWin
        other_ = {
            'online orbit': (main_.PV_SOFBOnlineOrbitXMon,
                             main_.PV_SOFBOnlineOrbitYMon),
            'correction orbit': (main_.PV_SOFBCorrOrbitXMon,
                                 main_.PV_SOFBCorrOrbitYMon),
            'reference orbit': (main_.PV_SOFBOrbitRefXRB,
                                main_.PV_SOFBOrbitRefYRB),
            'golden orbit': (main_.PV_SOFBGoldenOrbitXRB,
                             main_.PV_SOFBGoldenOrbitYRB),
            }
        if x_sig is not None:
            x_sig.disconnect(x_slot)
            y_sig.disconnect(y_slot)
        if text.lower().startswith('register'):
            ind = text[-1]
            reg = getattr(self.mWin, 'CM_Register' + ind)
            x_sig = reg.new_orbitx_signal
            y_sig = reg.new_orbity_signal
            x_sig.connect(x_slot)
            y_sig.connect(y_slot)
            x_wave = reg.orbx
            y_wave = reg.orby
        elif text.lower() in other_:
            regx, regy = other_[text.lower()]
            x_sig = regx.receive_value_signal[_np.ndarray]
            y_sig = regy.receive_value_signal[_np.ndarray]
            x_sig.connect(x_slot)
            y_sig.connect(y_slot)
            x_wave = regx.value
            y_wave = regy.value
        elif text.lower().startswith('zero'):
            x_sig = None
            y_sig = None
            x_wave = _np.zeros(NR_BPMs, dtype=float)
            y_wave = _np.zeros(NR_BPMs, dtype=float)

        setattr(self, ref + 'x_signal', x_sig)
        setattr(self, ref + 'y_signal', y_sig)
        if x_wave is not None:
            setattr(self, ref + 'x', x_wave)
        if y_wave is not None:
            setattr(self, ref + 'y', y_wave)

    def _update_enable_list(self, pl):
        def update(array):
            setattr(self, 'enbl' + pl, _np.array(array, dtype=bool))
            brush = getattr(self, 'brush' + pl)
            pen = getattr(self, 'pen' + pl)
            enbl = getattr(self, 'enbl' + pl)
            trace = getattr(self, 'diffTrace' + pl)
            mask_brush = [(brush if v else self.offbrush) for v in enbl]
            mask_pen = [(pen if v else self.offpen) for v in enbl]
            trace.opts['symbolBrush'] = mask_brush
            trace.opts['symbolPen'] = mask_pen
        return update

    def _update_orbx(self, orbx):
        self.orbx = orbx

    def _update_orby(self, orby):
        self.orby = orby

    def _update_refx(self, refx):
        self.refx = refx

    def _update_refy(self, refy):
        self.refy = refy

    def _update_graphic(self, plane=None):
        unit = 1/1000  # um
        plane = ('x', 'y') if plane is None else (plane,)
        for pl in plane:
            if not getattr(self, 'diffTrace' + pl).isVisible():
                return
            diff = unit * (getattr(self, 'orb' + pl) -
                           getattr(self, 'ref' + pl))
            mask = diff[getattr(self, 'enbl' + pl)]
            ave = float(mask.mean())
            std = float(mask.std(ddof=1))

            getattr(self, 'average' + pl + '_str_signal').emit(
                                                        self.FMT.format(ave))
            getattr(self, 'std' + pl + '_str_signal').emit(
                                                    self.FMT.format(std))
            ave = _np.array(len(diff)*[ave])
            getattr(self, 'diffSetValue' + pl)(diff)
            getattr(self, 'aveSetValue' + pl)(ave)
            getattr(self, 'aveMstdSetValue' + pl)(ave-std)
            getattr(self, 'avePstdSetValue' + pl)(ave+std)

    def _save_difference(self):
        diffx = self.orbx - self.refx
        diffy = self.orby - self.refy
        header = '# ' + _datetime.now().strftime('%Y/%M/%d-%H:%M:%S') + '\n'
        filename = QFileDialog.getSaveFileName(
                            caption='Define a File Name to Save the Orbit',
                            directory=self.last_dir,
                            filter=self.EXT_FLT)
        fname = filename[0]
        fname += '' if fname.endswith(self.EXT) else self.EXT
        _np.savetxt(fname, _np.vstack([diffx, diffy]).T, header=header)
