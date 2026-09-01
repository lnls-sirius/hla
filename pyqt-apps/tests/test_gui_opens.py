import pytest
from siriuspy.envars import VACA_PREFIX
from siriuspy.clientconfigdb import ConfigDBClient

from siriushla.as_ps_control import PSTabControlWindow
from siriushla.as_ap_measure import EmittanceMeasure
from siriushla.as_ap_measure import EnergyMeasure
from siriushla.as_pu_control import PUControlWindow
from siriushla.as_ap_injcontrol import TLControlWindow
from siriushla.as_ap_posang.HLPosAng import PosAngCorr
from siriushla.as_ap_sofb import MainWindow as SofbMainWindow
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
    LoopsDetails, RampsDetails, RFInputsDetails, TuningDetails, TempVariationDetails
from siriushla.as_rf_control.control import RFMainControl
from siriushla.as_rf_control.details import CavityStatusDetails, FDLDetails, \
    LLRFInterlockDetails, SlowLoopErrorDetails, SlowLoopParametersDetails, \
    SSADetailsBO, TempMonitor, TransmLineStatusDetails, TransmLineStatusDetails
from siriushla.as_ap_currinfo.current_and_lifetime import CurrLTWindow
from siriushla.as_ap_configdb import ConfigurationManager
from siriushla.as_ap_currinfo.efficiency_monitor import EfficiencyMonitor
from siriushla.as_ap_energybutton import EnergySetterWindow
from siriushla.as_ap_injection import InjCtrlWindow
from siriushla.as_ap_launcher import MainLauncher
from siriushla.as_ap_macreport import MacReportWindow
from siriushla.as_ap_magoffconv import MagOffConvApp
from siriushla.as_ap_monitor import SiriusMonitor
from siriushla.as_ap_configdb.pvsconfigs import LoadAndApplyConfig2MachineWindow
from siriushla.as_ap_configdb.pvsconfigs import PVsConfigManager
from siriushla.as_ap_rabpmmon import RaBPMMonitor
from siriushla.as_cr_control import CryoControl
from siriushla.as_ap_radmon import RadTotDoseMonitor
from siriushla.as_di_dccts import DCCTMain
from siriushla.as_ps_commands.main import PSCmdWindow
from siriushla.as_ps_cycle.cycle_window import CycleWindow
from siriushla.as_ps_diag import PSDiag
from siriushla.as_ps_control import PSDetailWindow
from siriushla.as_ps_diag import PSMonitor
from siriushla.as_ti_control import AFC
from siriushla.as_ti_control import TimingMain, MonitorWindow
from siriushla.as_di_scrns import SelectScrns, IndividualScrn
from siriushla.as_ps_diag.ps_graph_mon import PSGraphMonWindow
from siriushla.as_di_bpms import SelectBPMs, BPMMain, AcqDataSummary

from siriushla.li_rf_llrf import LLRFMain
from siriushla.li_va_control import VacuumMain
from siriushla.li_pu_modltr import LIModltrWindow
from siriushla.li_ap_mps import MPSControl
from siriushla.li_ap_mps import MPSMonitor
from siriushla.li_di_bpms import DigBeamPosProc
from siriushla.li_di_scrns import LiBeamProfile
from siriushla.li_eg_control import LIEgunWindow
from siriushla.li_eg_control import ITTIWidget

from siriushla.tb_di_slits import SlitsView

from siriushla.bl_ap_imgproc import BLImgProc

from siriushla.bo_ap_ramp import RampMain

from siriushla.si_ap_genstatus import SIGenStatusWindow
from siriushla.si_ap_fofb import MainWindow as FofbMainWindow, MatrixWidget, \
    ControllersDetailDialog
from siriushla.si_ap_fofb import FOFBAcqSYSIDWindow
from siriushla.si_ap_idff.main import IDFFWindow
from siriushla.si_ap_orbintlk import BPMOrbIntlkMainWindow
from siriushla.si_di_bbb import BbBMainWindow, BbBControlWindow
from siriushla.si_di_equalize_bpms import BPMsEqualizeSwitching
from siriushla.si_di_fpm_osc import FPMOscMain
from siriushla.si_di_scraps import ScrapersView
from siriushla.si_id_control import IDControl, APUControlWindow, \
    DELTAControlWindow, IVUControlWindow, VPUControlWindow, \
    UEControlWindow
from siriushla.si_ap_fofb import FOFBAcqLAMPWindow


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
    (SofbMainWindow, {"acc": "TS"}),
    (ICTMonitoring, {"tl": "TS", "prefix": VACA_PREFIX}),
    (PSTabControlWindow, {"section": "TS"}),
    (PUControlWindow, {"section": "TS"})
]


tb_scripts_config = [
    (TLControlWindow, {"tl": "tb"}),
    (PosAngCorr, {"tl": "tb"}),
    (ShowMatrixWidget, {"device": "TB-Glob:AP-SOFB", "acc": "TB"}),
    (SofbMainWindow, {"acc": "TB"}),
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
    (SofbMainWindow, {"acc": "BO"}),
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


si_scripts_config = [
        (OpticsCorrWindow, {"opticsparam": "tune", "acc": "si"}),
        (OpticsCorrWindow, {"opticsparam": "chrom", "acc": "si"}),
        CurrLTWindow,
        SIGenStatusWindow,
        (MatrixWidget, {"device": "SI-Glob:AP-FOFB", "prefix": VACA_PREFIX, "propty": "RespMat-Mon"}),
        (MatrixWidget, {"device": "SI-Glob:AP-FOFB", "prefix": VACA_PREFIX, "propty": "InvRespMat-Mon"}),
        (MatrixWidget, {"device": "SI-Glob:AP-FOFB", "prefix": VACA_PREFIX, "propty": "RespMatHw-Mon"}),
        (MatrixWidget, {"device": "SI-Glob:AP-FOFB", "prefix": VACA_PREFIX, "propty": "InvRespMatHw-Mon"}),
        (MatrixWidget, {"device": "SI-Glob:AP-FOFB", "prefix": VACA_PREFIX, "propty": "CorrCoeffs-Mon"}),
        (FofbMainWindow, {"device": "SI-Glob:AP-FOFB", "prefix": VACA_PREFIX}),
        (ControllersDetailDialog, {"device": "SI-Glob:AP-FOFB", "prefix": VACA_PREFIX, "tab_selected": 2}),
        (FOFBAcqSYSIDWindow, {"prefix": VACA_PREFIX, "device": "IA-01RaBPM:BS-FOFBCtrl"}),
        (IDFFWindow, {"prefix": VACA_PREFIX, "idname": "SI-10SB:AP-IDFF"}),
        BPMOrbIntlkMainWindow,
        (ShowMatrixWidget, {"device": "SI-Glob:AP-SOFB", "acc": "SI"}),
        (SofbMainWindow, {"acc": "SI"}),
        BbBMainWindow,
        BPMsEqualizeSwitching,
        (FPMOscMain, {"prefix": VACA_PREFIX}),
        (ScrapersView, {"prefix": VACA_PREFIX}),
        (Tune, {"section": "SI"}),
        (VLightCamView, {"section": "SI"}),
        IDControl,
        (UEControlWindow, {"device": "SI-11SP:ID-UE44"}),
        (APUControlWindow, {"device": "SI-17SA:ID-APU22"}),
        (APUControlWindow, {"device": "SI-20SB:ID-APU22"}),
        (APUControlWindow, {"device": "SI-09SA:ID-APU22"}),
        (DELTAControlWindow, {"device": "SI-10SB:ID-DELTA52"}),
        (VPUControlWindow, {"device": "SI-06SB:ID-VPU29"}),
        (VPUControlWindow, {"device": "SI-07SP:ID-VPU29"}),
        (APUControlWindow, {"device": "SI-08SB:ID-IVU18"}),
        (APUControlWindow, {"device": "SI-14SB:ID-IVU18"}),
        (ConfigManagerWindow, {"config_type": "si_normalized"}),
        (PSTabControlWindow, {"section": "LI"}),
        (FOFBAcqLAMPWindow, {"prefix": VACA_PREFIX, "device": "IA-01RaBPM:BS-FOFBCtrl"}),
        (PUControlWindow, {"section": "SI"}),
        (PUControlWindow, {"section": "InjSI"}),
        (PUControlWindow, {"section": "PingSI"}),
        (CavityStatusDetails, {"section": "SI", "prefix": VACA_PREFIX}),
        (LLRFInterlockDetails, {"section": "SI", "prefix": VACA_PREFIX}),
        (SlowLoopErrorDetails, {"section": "SI", "prefix": VACA_PREFIX}),
        (SlowLoopParametersDetails, {"section": "SI", "prefix": VACA_PREFIX}),
        (TempMonitor, {"section": "SI", "prefix": VACA_PREFIX}),
        (TransmLineStatusDetails, {"section": "SI", "prefix": VACA_PREFIX}),
        (ADCDACDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (AutoStartDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (CalEqDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (CalSysDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (HardwareDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (LoopsDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (RampsDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (RFInputsDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (TuningDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (FDLDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (TempVariationDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "A"}),
        (ADCDACDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (AutoStartDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (CalEqDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (CalSysDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (HardwareDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (LoopsDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (RampsDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (RFInputsDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (TuningDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (FDLDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
        (TempVariationDetails, {"section": "SI", "prefix": VACA_PREFIX, "system": "B"}),
]
    

it_scripts_config = [
    (ITTIWidget, {"prefix": VACA_PREFIX}),
    (PSTabControlWindow, {"section": "IT"}),
    (VLightCamView, {"section": "IT"}),
    (LIEgunWindow, {"is_it": True})
]


as_scripts_config = [
    (ConfigurationManager, {"model": ConfigDBClient()}),
    EfficiencyMonitor,
    EnergySetterWindow,
    (InjCtrlWindow, {"prefix": VACA_PREFIX}),
    (MainLauncher, {"prefix": VACA_PREFIX}),
    MacReportWindow,
    MagOffConvApp,
    SiriusMonitor,
    (LoadAndApplyConfig2MachineWindow, {"client": ConfigDBClient()}),
    PVsConfigManager,
    (RaBPMMonitor, {"prefix": VACA_PREFIX}),
    CryoControl,
    RadTotDoseMonitor,
    (DCCTMain, {"prefix": VACA_PREFIX, "device": "SI-13C4:DI-DCCT"}),     
    (DCCTMain, {"prefix": VACA_PREFIX, "device": "SI-14C4:DI-DCCT"}),     
    (DCCTMain, {"prefix": VACA_PREFIX, "device": "BO-35D:DI-DCCT"}),
    PSCmdWindow,
    CycleWindow,
    PSDiag,
    (PSDetailWindow, {"psname": "BO-01D:PU-InjKckr"}),
    (PSDetailWindow, {"psname": "TB-04:PU-InjSept"}),
    (PSDetailWindow, {"psname": "SI-19C4:PU-PingV"}),
    PSMonitor,
    (PUControlWindow, {"section": "AS", "main_secs": ('InjBO', 'EjeBO', 'InjSI', 'PingSI')}),
    (PUControlWindow, {"section": "AS", "main_secs": ('TB', 'BO', 'TS', 'SI')}),
    (AFC, {"prefix": VACA_PREFIX, "device": "SI-04C3:DI-BPM-1"}),
    (AFC, {"prefix": VACA_PREFIX, "device": "SI-02C1:DI-BPM-1"}),
    (AFC, {"prefix": VACA_PREFIX, "device": "SI-03C1:DI-BPM-2"}),
    (TimingMain, {"prefix": VACA_PREFIX}),
    (MonitorWindow, {"prefix": VACA_PREFIX}),
    (SelectScrns, {"sec": "BO"}),
    (SelectScrns, {"sec": "TS"}),
    (SelectScrns, {"sec": "TB"}),
    (IndividualScrn, {"scrn": "TB-01:DI-Scrn-1"}),
    (IndividualScrn, {"scrn": "TB-01:DI-Scrn-2"}),
    (IndividualScrn, {"scrn": "TB-02:DI-Scrn-1"}),
    (IndividualScrn, {"scrn": "TB-02:DI-Scrn-2"}),
    (IndividualScrn, {"scrn": "TB-03:DI-Scrn"}),
    (IndividualScrn, {"scrn": "BO-01D:DI-Scrn-1"}),
    (IndividualScrn, {"scrn": "BO-01D:DI-Scrn-2"}),
    (IndividualScrn, {"scrn": "BO-02U:DI-Scrn"}),
    (IndividualScrn, {"scrn": "TS-01:DI-Scrn"}),
    (IndividualScrn, {"scrn": "TS-02:DI-Scrn"}),
    (IndividualScrn, {"scrn": "TS-03:DI-Scrn"}),
    (IndividualScrn, {"scrn": "TS-04:DI-Scrn-1"}),
    (IndividualScrn, {"scrn": "TS-04:DI-Scrn-2"}),
    (IndividualScrn, {"scrn": "TS-04:DI-Scrn-3"}),
    PSGraphMonWindow,
    (AcqDataSummary, {"prefix": VACA_PREFIX, "bpm_list": []}),
    (SelectBPMs, {"prefix": VACA_PREFIX, "bpm_list": []})
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

@pytest.mark.parametrize("gui_config", si_scripts_config)
def test_si_gui_opens(open_gui):
    assert open_gui

@pytest.mark.parametrize("gui_config", it_scripts_config)
def test_it_gui_opens(open_gui):
    assert open_gui

@pytest.mark.parametrize("gui_config", as_scripts_config)
def test_as_gui_opens(open_gui):
    assert open_gui