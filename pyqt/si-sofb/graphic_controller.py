import numpy as _np
import datetime as _datetime
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from pyqtgraph import  mkBrush, mkPen
from PyQt5.QtWidgets import QFileDialog
from selection_matrix import NR_BPMs

class GraphicOrbitControllers(QObject):
    DEFAULT_DIR = '/home/fernando'
    EXT = '.txt'
    EXT_FLT = 'Text Files (*.txt)'
    FMT = '{0:8.3g}'

    averagex_str_signal  = pyqtSignal(str)
    stdx_str_signal      = pyqtSignal(str)
    averagey_str_signal  = pyqtSignal(str)
    stdy_str_signal      = pyqtSignal(str)

    def __init__(self,main_window,index):
        super().__init__(main_window)
        self.main_window = main_window
        self.last_dir = self.DEFAULT_DIR

        pbSave= getattr(self.main_window,'PB_Line'+str(index)+'Save')
        pbSave.clicked.connect(self._save_difference)
        cbOrb = getattr(self.main_window,'CB_Line'+str(index)+'Orb')
        cbRef = getattr(self.main_window,'CB_Line'+str(index)+'Ref')
        cbOrb.currentTextChanged.connect(self._orb_changed)
        cbRef.currentTextChanged.connect(self._ref_changed)
        self.main_window.PV_SOFBBPMXEnblListRB.value_signal[_np.ndarray].connect(self.update_enable_list('x'))
        self.main_window.PV_SOFBBPMYEnblListRB.value_signal[_np.ndarray].connect(self.update_enable_list('y'))
        self.orbx = _np.zeros(NR_BPMs,dtype=float)
        self.orby = _np.zeros(NR_BPMs,dtype=float)
        self.refx = _np.zeros(NR_BPMs,dtype=float)
        self.refy = _np.zeros(NR_BPMs,dtype=float)
        self.enblx= _np.ones(NR_BPMs,dtype=bool)
        self.enbly= _np.ones(NR_BPMs,dtype=bool)
        self.orbx_signal = None
        self.orby_signal = None
        self.refx_signal = None
        self.refy_signal = None
        self.offbrush = mkBrush(100,100,100)
        self.offpen   = mkPen(100,100,100)

        avex = getattr(main_window,'LB_Line'+str(index)+'XAve')
        avey = getattr(main_window,'LB_Line'+str(index)+'YAve')
        stdx = getattr(main_window,'LB_Line'+str(index)+'XStd')
        stdy = getattr(main_window,'LB_Line'+str(index)+'YStd')
        self.averagex_str_signal.connect(avex.setText)
        self.averagey_str_signal.connect(avey.setText)
        self.stdx_str_signal.connect(stdx.setText)
        self.stdy_str_signal.connect(stdy.setText)


        base_ind = (4-index)*4-1
        wid = main_window.PyDMMWP_OrbitX
        self.diffTracex = getattr(wid,'trace')[base_ind]
        self.brushx = mkBrush(getattr(wid,'trace'+str(base_ind)+'Color'))
        self.penx   =   mkPen(getattr(wid,'trace'+str(base_ind)+'Color'))
        self.diffSetValuex = getattr(wid,'setTrace'+str(base_ind)+'Value')
        self.aveSetValuex = getattr(wid,'setTrace'+str(base_ind-1)+'Value')
        self.aveMstdSetValuex = getattr(wid,'setTrace'+str(base_ind-2)+'Value')
        self.avePstdSetValuex = getattr(wid,'setTrace'+str(base_ind-3)+'Value')

        wid = main_window.PyDMMWP_OrbitY
        self.diffTracey = getattr(wid,'trace')[base_ind]
        self.brushy  = mkBrush(getattr(wid,'trace'+str(base_ind)+'Color'))
        self.peny    =   mkPen(getattr(wid,'trace'+str(base_ind)+'Color'))
        self.diffSetValuey = getattr(wid,'setTrace'+str(base_ind)+'Value')
        self.aveSetValuey = getattr(wid,'setTrace'+str(base_ind-1)+'Value')
        self.aveMstdSetValuey = getattr(wid,'setTrace'+str(base_ind-2)+'Value')
        self.avePstdSetValuey = getattr(wid,'setTrace'+str(base_ind-3)+'Value')

        if index > 1: getattr(main_window,'CB_Line'+str(index)+'Show').setChecked(False)

        self._orb_changed(cbOrb.currentText())
        self._ref_changed(cbRef.currentText())

    def _orb_changed(self,text): self._some_changed('orb',text)
    def _ref_changed(self,text): self._some_changed('ref',text)
    def _some_changed(self,ref,text):
        x_sig = getattr(self, ref+'x_signal')
        y_sig = getattr(self, ref+'y_signal')
        x_slot = getattr(self,'update_'+ref+'x')
        y_slot = getattr(self,'update_'+ref+'y')

        main_ = self.main_window
        other_ = {
                'online orbit':(main_.PV_SOFBOnlineOrbitXMon, main_.PV_SOFBOnlineOrbitYMon),
                'correction orbit':(main_.PV_SOFBCorrOrbitXMon, main_.PV_SOFBCorrOrbitYMon),
                'reference orbit':(main_.PV_SOFBOrbitRefXRB, main_.PV_SOFBOrbitRefYRB),
                'golden orbit':(main_.PV_SOFBGoldenOrbitXRB , main_.PV_SOFBGoldenOrbitYRB),
                }
        if x_sig is not None:
            x_sig.disconnect(x_slot)
            y_sig.disconnect(y_slot)
        if text.lower().startswith('register'):
            ind = text[-1]
            reg = getattr(self.main_window,'CM_Register'+ind)
            x_sig = reg.new_orbitx_signal
            y_sig = reg.new_orbity_signal
            x_sig.connect(x_slot)
            y_sig.connect(y_slot)
            x_wave = reg.orbx
            y_wave = reg.orby
        elif text.lower() in other_:
            regx, regy = other_[text.lower()]
            x_sig = regx.value_signal[_np.ndarray]
            y_sig = regy.value_signal[_np.ndarray]
            x_sig.connect(x_slot)
            y_sig.connect(y_slot)
            x_wave = regx.value
            y_wave = regy.value
        elif text.lower().startswith('zero'):
            x_sig = None
            y_sig = None
            x_wave = _np.zeros(NR_BPMs,dtype=float)
            y_wave = _np.zeros(NR_BPMs,dtype=float)

        setattr(self, ref+'x_signal', x_sig)
        setattr(self, ref+'y_signal', y_sig)
        if x_wave is not None: setattr(self,ref+'x', x_wave)
        if y_wave is not None: setattr(self,ref+'y', y_wave)

        self.update_graphic()

    def update_enable_list(self,pl):
        def update(array):
            setattr(self,'enbl'+pl, _np.array(array,dtype=bool))
            brush = getattr(self,'brush'+pl)
            pen   = getattr(self,'pen'+pl)
            enbl  = getattr(self,'enbl'+pl)
            trace = getattr(self,'diffTrace'+pl)
            mask_brush = [  (brush if v else self.offbrush)  for v in enbl   ]
            mask_pen   = [  (pen   if v else self.offpen)    for v in enbl   ]
            trace.opts['symbolBrush'] = mask_brush
            trace.opts['symbolPen']   = mask_pen
            self.update_graphic(pl)
        return update


    def update_orbx(self,orbx):
        self.orbx = orbx
        self.update_graphic('x')

    def update_orby(self,orby):
        self.orby = orby
        self.update_graphic('y')

    def update_refx(self,refx):
        self.refx = refx
        self.update_graphic('x')

    def update_refy(self,refy):
        self.refy = refy
        self.update_graphic('y')

    def update_graphic(self,plane=None):
        unit = 1/1000 #um
        plane = ('x','y') if plane is None else (plane,)
        for pl in plane:
            if not getattr(self,'diffTrace'+pl).isVisible(): return
            diff = unit * ( getattr(self,'orb'+pl) - getattr(self,'ref'+pl) )
            mask = diff[getattr(self,'enbl'+pl)]
            ave = float(mask.mean())
            std = float(mask.std(ddof=1))

            getattr(self,'average'+pl+'_str_signal').emit(self.FMT.format(ave))
            getattr(self,'std'+pl+'_str_signal').emit(self.FMT.format(std))

            getattr(self,'diffSetValue'+pl)(diff)
            getattr(self,'aveSetValue'+pl)(ave)
            getattr(self,'aveMstdSetValue'+pl)(ave-std)
            getattr(self,'avePstdSetValue'+pl)(ave+std)

    def _save_difference(self):
        diffx = self.orbx - self.refx
        diffy = self.orby - self.refy
        header = '# ' + _datetime.datetime.now().strftime('%Y/%M/%d-%H:%M:%S') + '\n'
        filename = QFileDialog.getSaveFileName(caption='Define a File Name to Save the Orbit',
                                               directory=self.last_dir,
                                               filter=self.EXT_FLT)
        fname = filename[0]
        fname += '' if fname.endswith(self.EXT) else self.EXT
        _np.savetxt(fname,_np.vstack([diffx,diffy]).T, header=header)
