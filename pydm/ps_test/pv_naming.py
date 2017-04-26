from siriuspy import envars as _envars

class PVNaming(object):
    _PREFIX = _envars.vaca_prefix
    _CURRENT_SP_SUFFIX = ':Current-SP'
    _CURRENT_RB_SUFFIX = ':Current-RB'
    _RESET_CMD_SUFFIX = ':Reset-Cmd'
    _PWR_STATE_SEL_PREFIX = ':PwrState-Sel'

    @staticmethod
    def get_reset_pv_name(name):
        return PVNaming._PREFIX + name + PVNaming._RESET_CMD_SUFFIX

    @staticmethod
    def get_rb_pv_name(name):
        return PVNaming._PREFIX + name + PVNaming._CURRENT_RB_SUFFIX

    @staticmethod
    def get_sp_pv_name(name):
        return PVNaming._PREFIX + name + PVNaming._CURRENT_SP_SUFFIX

    @staticmethod
    def get_pwr_state_sel_pv_name(name):
        return PVNaming._PREFIX + name + PVNaming._PWR_STATE_SEL_PREFIX
