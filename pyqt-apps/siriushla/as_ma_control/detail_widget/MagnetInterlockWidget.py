"""Magnet Interlock widget."""
from epics import get_pv

from siriushla.widgets import SiriusMainWindow
from siriushla.widgets import SiriusLedAlert
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QLabel
from siriuspy.envars import vaca_prefix as _VACA_PREFIX


class Interlock(QWidget):

    def __init__(self, parent=None, init_channel='', bit=-1, label=''):
        super().__init__(parent)
        self._channel = init_channel
        self._bit = bit
        self._label = label
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QHBoxLayout()
        self.led = SiriusLedAlert(self, self._channel, self._bit)
        self.label = QLabel(self._label, self)
        self.layout.addWidget(self.led)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)


class MagnetInterlockWidget(QWidget):
    """Widget with interlock information."""

    SOFT, HARD = range(2)

    def __init__(self, parent=None, magnet='', interlock=0):
        super().__init__(parent)
        self._magnet_name = magnet

        if interlock == self.SOFT:
            self._intlk_mon = 'IntlkSoft-Mon'
            self._intlk_cte = 'IntlkSoftLabels-Cte'
        elif interlock == self.HARD:
            self._intlk_mon = 'IntlkHard-Mon'
            self._intlk_cte = 'IntlkHardLabels-Cte'
        else:
            raise ValueError()

        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        # interlock_grid = QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("<h1>" + self._magnet_name + "</h1>"))
        # self.layout.addLayout(interlock_grid)

        pv = get_pv(_VACA_PREFIX + self._magnet_name + ':' + self._intlk_cte)
        # TODO: treat NONE!!!!
        soft_labels = pv.get()
        # soft_layout = QVBoxLayout()
        # interlock_grid.addLayout(soft_layout)
        for bit, label in enumerate(soft_labels):
            # Add led and label to layout
            channel = 'ca://' + _VACA_PREFIX + self._magnet_name + ':' + self._intlk_mon
            self.layout.addWidget(Interlock(self, channel, bit, label))


class MagnetInterlockWindow(SiriusMainWindow):

    def __init__(self, parent=None, magnet='', interlock=0):
        super().__init__(parent)
        self._magnet_name = magnet
        self._interlock = interlock
        self._setup_ui()

    def _setup_ui(self):
        self._central_widget = QWidget(parent=self)
        self._central_widget.layout = QHBoxLayout()
        self._central_widget.setLayout(self._central_widget.layout)
        self.setCentralWidget(self._central_widget)

        for ps in self._get_ps_list(self._magnet_name):
            ma = MagnetInterlockWidget(parent=self,
                                       magnet=ps,
                                       interlock=self._interlock)
            self._central_widget.layout.addWidget(ma)

    def _get_ps_list(self, magnet):
        if 'SI-Fam:MA-B1B2' in magnet:
            return ['SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2']
        elif 'BO-Fam:MA-B' in magnet:
            return ['BO-Fam:PS-B', 'BO-Fam:PS-B']
        else:
            return [magnet.replace('MA', 'PS'), ]
