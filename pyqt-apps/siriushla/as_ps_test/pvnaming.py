''' This class return PV names for a specified
    power supply name.
'''
from siriuspy import envars as _envars

class PVNaming:

    _PREFIX = _envars.vaca_prefix
    #self._PREFIX = ''

    _CURRENT_SP_SUFFIX = ':Current-SP'
    _CURRENT_RB_SUFFIX = ':Current-RB'
    _CURRENT_MON_SUFFIX = ':Current-Mon'
    _RESET_CMD_SUFFIX = ':Reset-Cmd'
    _PWR_STATE_SEL_SUFFIX = ':PwrState-Sel'

    def get_rb_pv_name(name):
        return PVNaming._PREFIX + name + PVNaming._CURRENT_RB_SUFFIX

    def get_sp_pv_name(name):
        return PVNaming._PREFIX + name + PVNaming._CURRENT_SP_SUFFIX

    def get_mon_pv_name(name):
        return PVNaming._PREFIX + name + PVNaming._CURRENT_MON_SUFFIX

    def get_pwr_state_sel_pv_name(name):
        return PVNaming._PREFIX + name + PVNaming._PWR_STATE_SEL_SUFFIX

    def get_reset_pv_name(name):
        return PVNaming._PREFIX + name + PVNaming._RESET_CMD_SUFFIX
