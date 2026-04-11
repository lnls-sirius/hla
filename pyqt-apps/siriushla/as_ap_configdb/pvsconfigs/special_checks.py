"""Module for special checks."""

from siriuspy.clientconfigdb.types.global_config import PVS_AS_PU, \
    PVS_SI_PS_CH, PVS_SI_PS_CV
from siriuspy.devices import InjCtrl, SOFB


class ApplyCheckSOFBSyncPS:
    """."""

    def __init__(self):
        """."""
        self.pvnames = self._create_list_of_relevant_pvnames()
        props2init = ('CorrSync-Sts',)
        self.sofb = SOFB(SOFB.DEVICES.SI, props2init=props2init)
        self.sofb.wait_for_connection(timeout=0.1)

    def check(self, set_pvs_tuple):
        """."""
        # check if set of selected PVs contains correctors' PVs.
        resp = ''
        config_pvnames = {tpl[0] for tpl in set_pvs_tuple}
        collision = bool(config_pvnames & self.pvnames)
        if not collision:
            return resp

        if not self.sofb.connected:
            resp = (
                'SOFB device not connected!\n'
                'Make sure SOFB is configured to operate '
                'correctors in SlowRef!'
            )
        if self.sofb.synckicksts_str != 'Off':
            resp = (
                'SOFB is not configured to operate correctors in SlowRef!\n'
                'Please correct this before applying configuration!'
            )
        return resp

    @staticmethod
    def _create_list_of_relevant_pvnames():
        pvnames = set()
        pvnames.update(tlp[0] for tlp in PVS_SI_PS_CH)
        pvnames.update(tlp[0] for tlp in PVS_SI_PS_CV)
        return pvnames


class ReadCheckInjMode:
    """."""

    def __init__(self):
        """."""
        self.pvnames = self._create_list_of_relevant_pvnames()
        self.props2init = (
            'Mode-Sts',
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

    def check(self, set_pvs_tuple):
        """."""
        # check if set of selected PVs contains PU' PVs.
        resp = ''
        config_pvnames = {tpl[0] for tpl in set_pvs_tuple}
        collision = bool(config_pvnames & self.pvnames)
        if not collision:
            return resp

        # injctrl device not connected
        if not self.injctrl.connected:
            resp = (
                'InjCtrl device not connected!\n'
                'Make sure InjCtrl is not configured to operate in \n'
                'TopUp with PUs in Standby! '
            )

        # not in TopUp mode
        if self.injctrl.injmode_str != 'TopUp':
            return resp

        # PU in standby
        for prop in self.props2init:
            if self.injctrl[prop] != 0:
                resp = (
                    'InjCtrl is configured to operate in TopUp'
                    'with PUs in Standby! '
                    'Please correct this before saving configuration! '
                )
                break
        return resp

    @staticmethod
    def _create_list_of_relevant_pvnames():
        pvnames = set()
        pvnames.update(tlp[0] for tlp in PVS_AS_PU)
        return pvnames
