import pytest
from siriuspy.envars import VACA_PREFIX

from siriushla.as_ps_control import PSTabControlWindow
from siriushla.as_ap_measure import EmittanceMeasure
from siriushla.as_ap_measure import EnergyMeasure
from siriushla.as_pu_control import PUControlWindow
from siriushla.as_ap_injcontrol import TLControlWindow
from siriushla.as_ap_posang.HLPosAng import PosAngCorr
from siriushla.as_ap_sofb import MainWindow
from siriushla.as_ap_sofb.graphics import ShowMatrixWidget
from siriushla.as_ps_control import PlotWfmErrorWindow
from siriushla.as_di_icts import ICTMonitoring
from siriushla.as_ap_configdb.normconfigs import ConfigManagerWindow
from siriushla.as_di_vlight import VLightCamView
from siriushla.as_di_tune import Tune
from siriushla.as_ap_opticscorr import OpticsCorrWindow
from siriushla.as_ap_injcontrol import InjBOControlWindow
from siriushla.as_ap_currinfo.charge_monitor import BOMonitor
from siriushla.as_rf_control.advanced_details import ADCDACDetails, \
    AutoStartDetails, CalEqDetails, CalSysDetails, HardwareDetails, \
    LoopsDetails, RampsDetails, RFInputsDetails, TuningDetails
from siriushla.as_rf_control.control import RFMainControl
from siriushla.as_rf_control.details import CavityStatusDetails, FDLDetails, \
    LLRFInterlockDetails, SlowLoopErrorDetails, SlowLoopParametersDetails, \
    SSADetailsBO, TempMonitor, TransmLineStatusDetails

from siriushla.li_rf_llrf import LLRFMain
from siriushla.li_va_control import VacuumMain
from siriushla.li_pu_modltr import LIModltrWindow
from siriushla.li_ap_mps import MPSControl
from siriushla.li_ap_mps import MPSMonitor
from siriushla.li_di_bpms import DigBeamPosProc
from siriushla.li_di_scrns import LiBeamProfile
from siriushla.li_eg_control import LIEgunWindow

from siriushla.tb_di_slits import SlitsView

from siriushla.bl_ap_imgproc import BLImgProc

from siriushla.bo_ap_ramp import RampMain


linac_scripts_config = [
    LLRFMain,
    VacuumMain,
    EnergyMeasure,
    LIModltrWindow,
    (PSTabControlWindow, {"section": "LI"}),
    (EmittanceMeasure, {"place": "LI"}),
    MPSControl,
    MPSMonitor,
    (DigBeamPosProc, {"device_name": "LA-BI:BPM2"}),
    (DigBeamPosProc, {"device_name": "LA-BI:BPM3"}),
    LiBeamProfile,
    LIEgunWindow
]


ts_scripts_config = [
    (TLControlWindow, {"tl": "ts"}),
    (PosAngCorr, {"tl": "ts"}),
    (ShowMatrixWidget, {"device": "TS-Glob:AP-SOFB", "acc": "TS"}),
    (MainWindow, {"acc": "TS"}),
    (ICTMonitoring, {"tl": "TS", "prefix": VACA_PREFIX}),
    (PSTabControlWindow, {"section": "TS"}),
    (PUControlWindow, {"section": "TS"})
]


tb_scripts_config = [
    (TLControlWindow, {"tl": "tb"}),
    (PosAngCorr, {"tl": "tb"}),
    (ShowMatrixWidget, {"device": "TB-Glob:AP-SOFB", "acc": "TB"}),
    (MainWindow, {"acc": "TB"}),
    (ICTMonitoring, {"tl": "TB", "prefix": VACA_PREFIX}),
    (PSTabControlWindow, {"section": "TB"}),
    (PUControlWindow, {"section": "TB"}),
    SlitsView,
    (EmittanceMeasure, {"place": "TB-QF2A"})
]


bl_scripts_config = [
    (BLImgProc, {"dvf": "CAX:A:BASLER01"}),
    (BLImgProc, {"dvf": "CAX:B:BASLER01"})
]


bo_scripts_config = [
    (ShowMatrixWidget, {"device": "BO-Glob:AP-SOFB", "acc": "BO"}),
    (MainWindow, {"acc": "BO"}),
    (PSTabControlWindow, {"section": "BO"}),
    (PUControlWindow, {"section": "BO"}),
    (ConfigManagerWindow, {"config_type": "bo_normalized"}),
    (VLightCamView, {"section": "BO"}),
    (Tune, {"section": "BO"}),
    (OpticsCorrWindow, {"opticsparam": "tune", "acc": "bo"}),
    (OpticsCorrWindow, {"opticsparam": "chrom", "acc": "bo"}),
    RampMain,
    InjBOControlWindow,
    BOMonitor,
    (ADCDACDetails, {"section": "BO"}),
    (AutoStartDetails, {"section": "BO"}),
    (CalEqDetails, {"section": "BO"}),
    (CalSysDetails, {"section": "BO"}),
    (HardwareDetails, {"section": "BO"}),
    (LoopsDetails, {"section": "BO"}),
    (RampsDetails, {"section": "BO"}),
    (RFInputsDetails, {"section": "BO"}),
    (TuningDetails, {"section": "BO"}),
    (FDLDetails, {"section": "BO"}),
    (CavityStatusDetails, {"section": "BO"}),
    (LLRFInterlockDetails, {"section": "BO"}),
    (SlowLoopErrorDetails, {"section": "BO"}),
    (SlowLoopParametersDetails, {"section": "BO"}),
    (TempMonitor, {"section": "BO"}),
    (TransmLineStatusDetails, {"section": "BO"}),
    (RFMainControl, {"section": "BO"}),
    SSADetailsBO
]


@pytest.fixture
def open_gui(gui_config, qtbot):
    if isinstance(gui_config, tuple):
        gui_class = gui_config[0]
        kwargs = gui_config[1]
    else:
        gui_class = gui_config
        kwargs = {}
    gui = gui_class(parent=None, **kwargs)
    qtbot.waitExposed(gui)
    gui.show()
    qtbot.waitUntil(lambda: gui.isVisible(), timeout=10000)
    qtbot.wait(1500)
    yield True
    gui.close()
    qtbot.waitUntil(lambda: not gui.isVisible(), timeout=10000)

@pytest.mark.parametrize("gui_config", linac_scripts_config)
def test_linac_gui_opens(open_gui):
    assert open_gui

@pytest.mark.parametrize("gui_config", ts_scripts_config)
def test_ts_gui_opens(open_gui):
    assert open_gui

@pytest.mark.parametrize("gui_config", tb_scripts_config)
def test_tb_gui_opens(open_gui):
    assert open_gui

@pytest.mark.parametrize("gui_config", bl_scripts_config)
def test_bl_gui_opens(open_gui):
    assert open_gui

@pytest.mark.parametrize("gui_config", bo_scripts_config)
def test_bo_gui_opens(open_gui):
    assert open_gui