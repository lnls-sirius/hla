class PVNaming(object):
    PREFIX = 'VAP-'
    CURRENT_SP_SUFFIX = ':Current-SP'
    CURRENT_RB_SUFFIX = ':Current-RB'
    RESET_CMD_SUFFIX = ':Reset-Cmd'
    PWR_STATE_SEL_PREFIX = ':PwrState-Sel'

    @staticmethod
    def get_reset_pv_name(name):
        return PVNaming.PREFIX + name + PVNaming.RESET_CMD_SUFFIX

    @staticmethod
    def get_rb_pv_name(name):
        return PVNaming.PREFIX + name + PVNaming.CURRENT_RB_SUFFIX

    @staticmethod
    def get_sp_pv_name(name):
        return PVNaming.PREFIX + name + PVNaming.CURRENT_SP_SUFFIX

    @staticmethod
    def get_pwr_state_sel_pv_name(name):
        return PVNaming.PREFIX + name + PVNaming.PWR_STATE_SEL_PREFIX
