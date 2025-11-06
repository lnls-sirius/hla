"""Module for special checks."""

from siriuspy.devices import InjCtrl, SOFB
from siriuspy.search import PSSearch


class ApplyCheckSOFBSyncPS:
    """."""

    def __init__(self):
        """."""
        props2init = ('CorrSync-Sts',)
        self.sofb = SOFB(SOFB.DEVICES.SI, props2init=props2init)
        self.sofb.wait_for_connection(timeout=0.1)
        self.corr_pvnames = self._create_list_of_relevant_pvnames()

    def check(self, set_pvs_tuple):
        """."""
        # check if set of selected PVs contains correctors' PVs.
        resp = ''
        config_pvnames = {tpl[0] for tpl in set_pvs_tuple}
        collision = bool(set(config_pvnames) & set(self.corr_pvnames))
        if not collision:
            return resp

        if not self.sofb.connected:
            resp = (
                'SOFB device not connected! '
                'Make sure SOFB is configured not to operate with correctors '
                'in SlowRef mode! '
            )
        if self.sofb.synckicksts_str != 'Off':
            resp = (
                'SOFB is configured not to operate '
                'with correctors in SlowRef! '
                'Please correct this before applying configuration! '
            )
        return resp

    @staticmethod
    def _create_list_of_relevant_pvnames():
        filters = {'sec': 'SI', 'sub': '.*(M|C).*', 'dev': 'C(H|V)'}
        psnames = PSSearch.get_psnames(filters)
        corr_pvnames = set()
        corr_pvnames.update(psname + ':Current-SP' for psname in psnames)
        corr_pvnames.update(psname + ':WfmOffset-SP' for psname in psnames)
        return corr_pvnames


class ReadCheckInjMode:
    """."""

    def __init__(self):
        """."""
        self.props2init = (
            'TopUpBOInjKckrStandbyEnbl-Sts',
            'TopUpBOEjeKckrStandbyEnbl-Sts',
            'TopUpSIInjDpKckrStandbyEnbl-Sts',
            'TopUpSIInjNLKckrStandbyEnbl-Sts',
            'TopUpTBInjSeptStandbyEnbl-Sts',
            'TopUpTSEjeSeptFStandbyEnbl-Sts',
            'TopUpTSEjeSeptGStandbyEnbl-Sts',
            'TopUpTSInjSeptFStandbyEnbl-Sts',
            'TopUpTSInjSeptG1StandbyEnbl-Sts',
            'TopUpTSInjSeptG2StandbyEnbl-Sts',
        )
        self.injctrl = InjCtrl(props2init=self.props2init)
        self.injctrl.wait_for_connection(timeout=0.1)

    def check(self):
        """."""
        resp = ''

        if not self.injctrl.connected:
            resp = (
                'InjCtrl device not connected! '
                'Make sure InjCtrl is configured not to operate with '
                'PUs in Standby! '
            )
        for prop in self.props2init:
            if self.injctrl[prop] != 0:
                resp = (
                    'InjCtrl is configured to operate '
                    'with PUs in Standby! '
                    'Please correct this before applying configuration! '
                )
                break
        return resp
