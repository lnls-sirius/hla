import numpy as _np

class GraphicOrbitControllers:

    averagex_signal  = pyqtSignal(float)
    stdx_signal      = pyqtSignal(float)
    aveMstdx_signal  = pyqtSignal(float)
    avePstdx_signal  = pyqtSignal(float)
    maskx_signal     = pyqtSignal(_np.ndarray)
    diffx_signal     = pyqtSignal(_np.ndarray)
    averagey_signal  = pyqtSignal(float)
    stdy_signal      = pyqtSignal(float)
    aveMstdy_signal  = pyqtSignal(float)
    avePstdy_signal  = pyqtSignal(float)
    masky_signal     = pyqtSignal(_np.ndarray)
    diffy_signal     = pyqtSignal(_np.ndarray)

    def __init__(self,main_window,index):
        self.main_window = main_window
        cbOrb = getattr(self.main_window,'CB_Line'+str(index)+'Orb')
        cbRef = getattr(self.main_window,'CB_Line'+str(index)+'Ref')
        cbOrb.currentTextChanged.connect(self._orb_changed)
        cbRef.currentTextChanged.connect(self._ref_changed)
        self.main_window.PV_SOFBBPMXEnblListRB.value_signal.connect(self.update_enable_list_x)
        self.main_window.PV_SOFBBPMYEnblListRB.value_signal.connect(self.update_enable_list_y)
        self.orbx = _np.zeros(NR_BPMs,dtype=float)
        self.orby = _np.zeros(NR_BPMs,dtype=float)
        self.refx = _np.zeros(NR_BPMs,dtype=float)
        self.refy = _np.zeros(NR_BPMs,dtype=float)
        self.orbx_signal = None
        self.orby_signal = None
        self.refx_signal = None
        self.refy_signal = None

        avex = getattr(main_window,'LB_Line'+str(index)+'XAve')
        avey = getattr(main_window,'LB_Line'+str(index)+'YAve')
        stdx = getattr(main_window,'LB_Line'+str(index)+'XStd')
        stdy = getattr(main_window,'LB_Line'+str(index)+'YStd')
        averagex_signal.connect(avex.setText)
        averagey_signal.connect(avey.setText)
        stdx_signal.connect(stdx.setText)
        stdy_signal.connect(stdy.setText)

        diffx = getattr(main_window.PyDMMWP_Orbitx,'setTrace'+str(index-1)+'Value')
        avex = getattr(main_window.PyDMMWP_Orbitx,'setTrace'+str(index)+'Value')
        aveMstdx = getattr(main_window.PyDMMWP_Orbitx,'setTrace'+str(index+1)+'Value')
        avePstdx = getattr(main_window.PyDMMWP_Orbitx,'setTrace'+str(index+2)+'Value')
        maskx = getattr(main_window.PyDMMWP_Orbitx,'setTrace'+str(index+3)+'Value')
        diffx_signal.connect(diffx)
        averagex_signal.connect(avex)
        aveMstdx_signal.connect(aveMstdx)
        avePstdx_signal.connect(avePstdx)
        maskx_signal.connect(maskx)

        diffy = getattr(main_window.PyDMMWP_Orbity,'setTrace'+str(index-1)+'Value')
        avey = getattr(main_window.PyDMMWP_Orbity,'setTrace'+str(index)+'Value')
        aveMstdy = getattr(main_window.PyDMMWP_Orbity,'setTrace'+str(index+1)+'Value')
        avePstdy = getattr(main_window.PyDMMWP_Orbity,'setTrace'+str(index+2)+'Value')
        masky = getattr(main_window.PyDMMWP_Orbity,'setTrace'+str(index+3)+'Value')
        diffy_signal.connect(diffy)
        averagey_signal.connect(avey)
        aveMstdy_signal.connect(aveMstdy)
        avePstdy_signal.connect(avePstdy)
        masky_signal.connect(masky)

    def _orb_changed(self,text): self._some_changed('orb',text)
    def _ref_changed(self,text): self._some_changed('ref',text)
    def _some_changed(self,ref,text):
        x_sig = getattr(self, ref+'x_signal')
        y_sig = getattr(self, ref+'y_signal')
        x_slot = getattr(self,'update_'+ref+'x')
        y_slot = getattr(self,'update_'+ref+'y')

        main_ = self.main_window
        other_ = {
                'current raw orbit':(main_.PV_OrbitOrbitXMon, main_.PV_OrbitOrbitXMon),
                'sofb orbit':(main.PV_SOFBOrbitXMon, main.PV_SOFBOrbitYMon),
                'sofb reference':(main.PV_SOFBOrbitRefXRB, main.PV_SOFBOrbitRefYRB),
                'golden':(main.PV_SOFBGoldenOrbitXRB , main.PV_SOFBGoldenOrbitYRB),
                }
        if x_sig is not None:
            x_sig.disconnect(x_slot)
            y_sig.disconnect(y_slot)
        if text.startswith('Register'):
            ind = text[-1]
            reg = getattr(self.main_window,'CM_Register'+ind)
            x_sig = reg.new_orbitx_signal
            y_sig = reg.new_orbity_signal
            x_sig.connect(x_slot)
            y_sig.connect(y_slot)
            x_wave = reg.orbx
            y_wave = reg.orby
        elif text.lower() in other_:
            regx, regy = other_[orbit_text.lower()]
            x_sig = regx.value_signal
            y_sig = regy.value_signal
            x_sig.connect(x_slot)
            y_sig.connect(y_slot)
            x_wave = regx.value
            y_wave = regy.value
        elif orbit_text.lower().startswith('Zero')
            x_sig = None
            y_sig = None
            x_wave = _np.zeros(NR_BPMs,dtype=float)
            y_wave = _np.zeros(NR_BPMs,dtype=float)

        setattr(self, ref+'x_signal', x_sig)
        setattr(self, ref+'y_signal', y_sig)
        if x_wave is not None: setattr(self,ref+'x', x_wave)
        if y_wave is not None: setattr(self,ref+'y', y_wave)

        self.update_graphic()

    def update_enable_list_x(self,array):
        self.enblx = array
        self.update_graphic('x')

    def update_enable_list_y(self,array):
        self.enbly = array
        self.update_graphic('y')

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
        plane = ('x','y') if plane is None else (plane,)
        for pl in plane:
            diff = getattr(self,'orb'pl) - getattr(self,'ref'pl)
            mask = diff[getattr(self,'enbl'pl)]
            ave = mask.mean()
            std = mask.std(ddof=1)
            mask = self.diff.copy()
            mask[getattr(self,'enbl'pl)] = _np.nan
            getattr(self,'average'+pl+'_signal').emit(ave)
            getattr(self,'std'+pl+'_signal').emit(std)
            getattr(self,'aveMstd'+pl+'_signal').emit(ave-std)
            getattr(self,'avePstd'+pl+'_signal').emit(ave+std)
            getattr(self,'mask'+pl+'_signal').emit(mask)
            getattr(self,'diff'+pl+'_signal').emit(diff)
