from siriuspy import envars as _envars

class _PVNaming:

    def __init__(self):

        self._PREFIX = _envars.vaca_prefix
        #self._PREFIX = ''

        self._CURRENT_SP_SUFFIX = ':Current-SP'
        self._CURRENT_RB_SUFFIX = ':Current-RB'
        self._CURRENT_MON_SUFFIX = ':Current-Mon'
        self._RESET_CMD_SUFFIX = ':Reset-Cmd'
        self._PWR_STATE_SEL_SUFFIX = ':PwrState-Sel'

    @property
    def prefix(self):
        return self._PREFIX

    @property
    def current_sp_suffix(self):
        return self._CURRENT_SP_SUFFIX

    @property
    def current_rb_suffix(self):
        return self._CURRENT_RB_SUFFIX

    @property
    def reset_cmd_suffix(self):
        return self._RESET_CMD_SUFFIX

    @property
    def pwr_state_sel_suffix(self):
        return self._PWR_STATE_SEL_SUFFIX

    @property
    def current_mon_suffix(self):
        return self._CURRENT_MON_SUFFIX


_pvnaming = None
def _get_pvnaming():
    global _pvnaming
    if _pvnaming is None:
        _pvnaming = _PVNaming()
    return _pvnaming


def get_reset_pv_name(name):
    pvnaming = _get_pvnaming()
    prefix = pvnaming.prefix
    suffix = pvnaming.reset_cmd_suffix
    return prefix + name + suffix

def get_rb_pv_name(name):
    pvnaming = _get_pvnaming()
    prefix = pvnaming.prefix
    suffix = pvnaming.current_rb_suffix
    return prefix + name + suffix

def get_sp_pv_name(name):
    pvnaming = _get_pvnaming()
    prefix = pvnaming.prefix
    suffix = pvnaming.current_sp_suffix
    return prefix + name + suffix

def get_pwr_state_sel_pv_name(name):
    pvnaming = _get_pvnaming()
    prefix = pvnaming.prefix
    suffix = pvnaming.pwr_state_sel_suffix
    return prefix + name + suffix

def get_mon_pv_name(name):
    pvnaming = _get_pvnaming()
    prefix = pvnaming.prefix
    suffix = pvnaming.current_mon_suffix
    return prefix + name + suffix
