"""."""

import numpy as _np

from mathphys.functions import save_pickle as _savep, load_pickle as _loadp, \
    get_namedtuple as _namedtuple
from siriuspy.devices import FamBPMs as _FamBPMs


class EqBPMs:
    """."""

    NR_POINTS = 2000
    MAX_MULTIPLIER = 0xffffff / (1<<24)
    Methods = _namedtuple('Methods', ('AABS', 'EABS', 'AAES'))

    def __init__(self):
        """."""
        self._method = self.Methods.AAES
        self._assume_order = True
        self.fambpms = _FamBPMs(props2init=[])

    @property
    def assume_order(self):
        """."""
        return self._assume_order

    @assume_order.setter
    def assume_order(self, val):
        self._assume_order = bool(val)

    @property
    def method_str(self):
        """."""
        return self.Methods._fields[self._method]

    @property
    def method(self):
        """."""
        return self._method

    @method.setter
    def method(self, meth):
        self._method = meth

    def get_current_gains(self):
        """Return Current BPM gains as 3D numpy array.

        Returns:
            numpy.ndarray (nrbpms, 4, 2): 3D numpy array with gains.
                 - The first index vary the BPMs, in the default high level
                convention order;
                 - The second index vary the antennas: 'A', 'B', 'C', 'D';
                 - The last index refers to the type of the gain in the
                following order: 'Direct', 'Inverse';

        """
        gains = []
        for bpm in self.fambpms:
            gaind = [getattr(bpm, 'gain_direct_{a}') for a in 'abcd']
            gaini = [getattr(bpm, 'gain_inverse_{a}') for a in 'abcd']
            gains.append([gaind, gaini])
        gains = _np.array(gains).swapaxes(-1, -2)
        return gains

    def set_gains(self, gains):
        """Set gains matrix to BPMs.

        Args:
            gains (float or numpy.ndarray, (nrbpms, 4, 2)): gain matrix. In
                the same format as the one provided by get_current_gains
                method. If a float is provided, then this same gain will be
                applied to all BPMs.

        Raises:
            ValueError: If gains is a numpy array with wrong shape.

        """
        nbpm = len(self.fambpms)
        shape = (nbpm, 4, 2)
        if not isinstance(gains, _np.ndarray):
            gains = _np.full(shape, gains)
        if gains.shape != shape:
            raise ValueError(f'Wrong shape for gains. Must be {shape}')

        for i, bpm in enumerate(self.fambpms):
            gns = gains[i]
            for j, ant in enumerate('abcd'):
                g = gns[j]
                setattr(bpm, f'gain_direct_{ant}', g[0])
                setattr(bpm, f'gain_inverse_{ant}', g[1])

    def calc_semicycles_average(self, data):
        """."""
        nbpm = len(self.fambpms)
        data = data.reshape(nbpm, 4, -1, 4)
        data = data.mean(axis=2)
        if self._assume_order:
            data = data.reshape(nbpm, 4, 2, 2)
            mean = data.mean(axis=-1)
        else:
            idcs = data - data.mean(axis=-1)[..., None] > 0
            mean = _np.zeros((nbpm, 4, 2))
            mean[:, :, 0] = data[idcs].reshape(nbpm, 4, 2).mean(axis=-1)
            mean[:, :, 1] = data[~idcs].reshape(nbpm, 4, 2).mean(axis=-1)
        return mean

    def calc_gains(self, mean):
        """Calculate gains given mean data from antennas for both semi-cycles.

        This function needs to account for the representation of the gains:
        there are 24 bits and no integer ones. Since the non-1 gain was
        already applied to acquisitions, we can simply take it into account as
        a final step.

        Args:
            mean (numpy.array, (nrbpms, 4, 2)): Mean data from antennas for
                both semi-cyles. Compatible with output of
                calc_semicycles_average.

        """
        maxm = self.MAX_MULTIPLIER
        if self._method == self.Methods.EABS:
            # equalize each antenna for both semicycles
            min_ant = mean.min(axis=-1)
            min_ant = min_ant[:, :, None]
        elif self._method == self.Methods.AABS:
            # equalize the 4 antennas for both semicycles
            min_ant = mean.min(axis=-1).min(axis=-1)
            min_ant = min_ant[:, None, None]
        elif self._method == self.Methods.AAES:
            # equalize the 4 antennas for each semicycle
            min_ant = mean.min(axis=1)
            min_ant = min_ant[:, None, :]
        min_ant *= maxm
        gains = min_ant / mean
        return gains

    def _do_equalize_bpms(self):
        """."""
        gains0 = self.get_current_gains()

        if self._assume_order:
            self.set_gains(self.MAX_MULTIPLIER)
        else:
            gains = _np.full((len(self.fambpms), 4, 2), self.MAX_MULTIPLIER)
            gains[:, :, 2:] *= 0.8
            self.set_gains(gains)

        # acquire antennas data in FOFB rate

        # calculate new gains

        # calculate orbit variation from old to new gains

        # increment orbit variation in BPMs
