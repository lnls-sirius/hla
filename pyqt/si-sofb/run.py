import sys
import numpy as _np
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from pydm import PyDMApplication
from pydm.widgets.widget import PyDMWidget
from selection_matrix import SelectionMatrix, NR_BPMs
from register_menu import RegisterMenu

def create_additional_PVs(main_window):
    opts = dict(parent=main_window, visible = False)
    main_window.PV_SOFBOnOffline = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitOnOffline-Sel', **opts)

    main_window.PV_SOFBOfflineOrbitXSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitX-SP', **opts)
    main_window.PV_SOFBOfflineOrbitXRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitX-RB', **opts)
    main_window.PV_SOFBOfflineOrbitYSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitY-SP', **opts)
    main_window.PV_SOFBOfflineOrbitYRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitY-RB', **opts)

    main_window.PV_SOFBOrbitRefXSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitRefX-SP', **opts)
    main_window.PV_SOFBOrbitRefXRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitRefX-RB', **opts)
    main_window.PV_SOFBOrbitRefYSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitRefY-SP', **opts)
    main_window.PV_SOFBOrbitRefYRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitRefY-RB', **opts)

    main_window.PV_SOFBGoldenOrbitXSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitX-SP', **opts)
    main_window.PV_SOFBGoldenOrbitXRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitX-RB', **opts)
    main_window.PV_SOFBGoldenOrbitYSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitY-SP', **opts)
    main_window.PV_SOFBGoldenOrbitYRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitY-RB', **opts)

    main_window.PV_SOFBOrbitXMon = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitX-Mon', **opts)
    main_window.PV_SOFBOrbitYMon = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitY-Mon', **opts)

    main_window.PV_OrbitOrbitXMon = PyDMWidget(init_channel='ca://SI-Glob:AP-Orbit:OrbitX-Mon', **opts)
    main_window.PV_OrbitOrbitYMon = PyDMWidget(init_channel='ca://SI-Glob:AP-Orbit:OrbitY-Mon', **opts)

    main_window.PV_SOFBBPMXEnblListRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:BPMXEnblList-RB', **opts)
    main_window.PV_SOFBBPMYEnblListRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:BPMYEnblList-RB', **opts)

def create_additional_widgets(main_window):
    ## Create Matrix with Selection List of BPMs and Correctors:
    for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
        wid = getattr(main_window,'Widget_'+dev+'List')
        SelectionMatrix(wid,dev)

def main():
    app = PyDMApplication()
    main_win = uic.loadUi('main_window.ui')
    create_additional_PVs(main_win)
    create_additional_widgets(main_win)

    IndividualInteligence(main_win)
    # Signal2Slots(main_win)
    main_win.show()
    sys.exit(app.exec_())

class Signal2Slots:
    def __init__(self,main_window):
        self.main_window = main_window
        self.main_window.PyDMCB_OrbitMode.valueChanged.connect(self.PyDMCB_OrbitMode_2_OfflineOrbit)

    def PyDMCB_OrbitMode_2_OfflineOrbit(self,int_):
        if int_:
            self.main_window.LB_OfflineOrbit.setDisabled()
            self.main_window.CB_OfflineOrbit.setDisabled()
        else:
            self.main_window.LB_OfflineOrbit.setEnabled()
            self.main_window.CB_OfflineOrbit.setEnabled()

class IndividualInteligence:
    def __init__(self,main_window):
        self.main_window = main_window
        self.setup()

    def setup(self):
        # Create Context Menus for Registers and assign them to the clicked signal
        for i in range(1,10):
            cm  = RegisterMenu(self.main_window,i)
            setattr(self.main_window,'CM_Register'+str(i),cm)
            pb = getattr(self.main_window,'PB_Register'+str(i))
            pb.setContextMenuPolicy(Qt.CustomContextMenu)
            pb.setMenu(cm)
            pb.clicked.connect(pb.showMenu)

        # Define Behaviour of Orbit Visualization buttons
        for i in range(1,4):
            orbC = OrbitControllers(self.main_window,i)

class GraphicControllers:

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

        stdx_signal.connect(main_window.LB_Line1XAve.setText)
        stdy_signal.connect(main_window.LB_Line1YAve.setText)

        diffx_signal.connect(main_window.PyDMMWP_Orbitx.setTrace0Value)
        averagex_signal.connect(main_window.PyDMMWP_Orbitx.setTrace1Value)
        aveMstdx_signal.connect(main_window.PyDMMWP_Orbitx.setTrace2Value)
        avePstdx_signal.connect(main_window.PyDMMWP_Orbitx.setTrace3Value)
        maskx_signal.connect(main_window.PyDMMWP_Orbitx.setTrace4Value)
        diffy_signal.connect(main_window.PyDMMWP_Orbity.setTrace0Value)
        averagey_signal.connect(main_window.PyDMMWP_Orbity.setTrace1Value)
        aveMstdy_signal.connect(main_window.PyDMMWP_Orbity.setTrace2Value)
        avePstdy_signal.connect(main_window.PyDMMWP_Orbity.setTrace3Value)
        masky_signal.connect(main_window.PyDMMWP_Orbity.setTrace4Value)

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


#    QtCore.QMetaObject.connectSlotsByName(Form)
if __name__ == '__main__':
    main()
