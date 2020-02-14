"""SiriusHLA."""

import os as _os
with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
    __version__ = _f.read().strip()
del _os


_all_ = [
    'as_ap_configdb',
    'as_ap_currlt',
    'as_ap_energybutton',
    'as_ap_injcontrol',
    'as_ap_injection',
    'as_ap_launcher',
    'as_ap_magoffconv',
    'as_ap_measure',
    'as_ap_opticscorr',
    'as_ap_posang',
    'as_ap_sofb',
    'as_di_bpms',
    'as_di_dccts',
    'as_di_icts',
    'as_di_scrns',
    'as_di_slits',
    'as_di_tune',
    'as_di_vlight',
    'as_interlocks',
    'as_pm_control',
    'as_ps_control',
    'as_ps_cycle',
    'as_ps_diag',
    'as_ps_test',
    'as_pu_control',
    'as_rf_control',
    'as_ti_control',
    'bo_ap_ramp',
    'li_ap_mps']
