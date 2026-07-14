import pytest
from siriushla.li_rf_llrf import LLRFMain
from siriushla.li_va_control import VacuumMain
from siriushla.li_pu_modltr import LIModltrWindow
from siriushla.as_ps_control import PSTabControlWindow
from siriushla.as_ap_measure import EmittanceMeasure
from siriushla.as_ap_measure import EnergyMeasure
from siriushla.li_ap_mps import MPSControl
from siriushla.li_ap_mps import MPSMonitor
from siriushla.li_di_bpms import DigBeamPosProc
from siriushla.li_di_scrns import LiBeamProfile
from siriushla.li_eg_control import LIEgunWindow


linac_scripts_config = [
    LLRFMain,
    VacuumMain,
    EnergyMeasure,
    LIModltrWindow,
    (PSTabControlWindow, {"section": 'LI'}),
    (EmittanceMeasure, {"place": "LI"}),
    MPSControl,
    MPSMonitor,
    (DigBeamPosProc, {"device_name": "LA-BI:BPM2"}),
    (DigBeamPosProc, {"device_name": "LA-BI:BPM3"}),
    LiBeamProfile,
    LIEgunWindow
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