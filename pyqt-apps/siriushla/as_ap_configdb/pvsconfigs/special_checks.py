"""Module for special checks."""

from siriuspy.devices import SOFB


class SOFBSyncPSCheck:
    """."""

    def __init__(self):
        """."""
        self.sofb = SOFB(SOFB.DEVICES.SI)

    def check(self, pvs):
        """."""
        resp = ''
        if not self.sofb.connected:
            resp = (
                'SOFB device not connected! '
                'Make sure SOFB is not configured to opreate with correctors '
                'in sync mode!'
            )
        if self.sofbsynckicksts_str == 'On':
            resp = (
                'SOFB is configured to operate with correctors in sync mode! '
                'Please disable this before applying configuration!'
            )
        return resp
