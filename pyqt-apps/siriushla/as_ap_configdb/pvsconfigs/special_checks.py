"""Module for special checks."""

from siriuspy.devices import SOFB, InjCtrl


class ApplyCheckSOFBSyncPS:
    """."""

    def __init__(self):
        """."""
        props2init = ('CorrSync-Sts',)
        self.sofb = SOFB(SOFB.DEVICES.SI, props2init=props2init)
        self.sofb.wait_for_connection(timeout=0.1)

    def check(self, set_pvs_tuple):
        """."""
        # NOTE: add filter to check if correctors setpoints are
        # in set_pvs_tuple.
        _ = set_pvs_tuple
        resp = ''
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
