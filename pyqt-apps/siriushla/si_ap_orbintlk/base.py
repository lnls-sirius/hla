"""Base Object."""

from siriuspy.search import BPMSearch
from siriuspy.clientconfigdb import ConfigDBClient


class BaseObject:
    """Base SI BPM info object."""

    CONV_NM2M = 1e-9  # [nm] --> [m]
    CONV_NM2UM = 1e-3  # [nm] --> [um]
    CONV_UM2NM = 1e+3  # [um] --> [nm]

    BPM_NAMES = BPMSearch.get_names({'sec': 'SI', 'dev': 'BPM'})
    BPM_NICKNAMES = BPMSearch.get_nicknames(BPM_NAMES)
    BPM_POS = BPMSearch.get_positions(BPM_NAMES)

    DOWN_2_UP = {
        'M1': 'M2',
        'C1-1': 'C1-2',
        'C2': 'C3-1',
        'C3-2': 'C4',
    }
    UP_2_DOWN = {val: key for key, val in DOWN_2_UP.items()}

    def __init__(self):
        self._oper = {
            'mean': self._mean,
            'diff': self._diff,
        }

        self._client = ConfigDBClient(config_type='si_orbit')

    @staticmethod
    def get_down_up_bpms(bpmname):
        """Return down and up BPM names for bpmname."""

        def _parse_nick_down_up(name, nick):
            if '-' in nick:
                sub, idx = nick.split('-')
            else:
                sub, idx = nick, ''
            return name.substitute(sub=name.sub[:2]+sub, idx=idx)

        nick = bpmname.sub[2:]+('-' + bpmname.idx if bpmname.idx else '')
        if nick in BaseObject.DOWN_2_UP:
            down = bpmname
            upnick = BaseObject.DOWN_2_UP[nick]
            upn = _parse_nick_down_up(bpmname, upnick)
        elif nick in BaseObject.UP_2_DOWN:
            upn = bpmname
            downnick = BaseObject.UP_2_DOWN[nick]
            down = _parse_nick_down_up(bpmname, downnick)
        else:
            down, upn = '', ''
        return down, upn

    def get_intlk_metric(self, posarray, operation='', metric=''):
        """Return interlock metric, translation or angulation."""
        if not operation:
            if not metric:
                raise ValueError(
                    'either the operation or the metric is required')
            operation = 'mean' if 'trans' in metric.lower() else 'diff'

        data_values = list()
        for bpm in BaseObject.BPM_NAMES:
            down, upn = BaseObject.get_down_up_bpms(bpm)
            if down:
                dval = posarray[BaseObject.BPM_NAMES.index(down)]
                uval = posarray[BaseObject.BPM_NAMES.index(upn)]
                func = self._oper[operation]
                val = func(dval, uval)
            else:
                val = 0
            data_values.append(val)
        return data_values

    def get_ref_orb(self, configname):
        """Get reference orbit from config [um]."""
        return self._client.get_config_value(configname)

    @staticmethod
    def _mean(var1, var2):
        return (var1 + var2)/2

    @staticmethod
    def _diff(var1, var2):
        return var1 - var2
