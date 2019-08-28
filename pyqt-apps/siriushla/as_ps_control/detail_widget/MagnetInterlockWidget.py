"""Magnet Interlock widget."""
from epics import get_pv

from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.widgets import SiriusMainWindow
from siriushla.widgets import SiriusLedAlert
from qtpy.QtWidgets import \
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QTabWidget
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
        self._magnet_name = _PVName(magnet)
        self.setObjectName(self._magnet_name.sec+'App')

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
        self.layout = QGridLayout()
        # interlock_grid = QGridLayout()
        self.setLayout(self.layout)

        # self.layout.addWidget(QLabel("<h1>" + self._magnet_name + "</h1>"))
        # self.layout.addLayout(interlock_grid)

        pv = get_pv(_VACA_PREFIX + self._magnet_name + ':' + self._intlk_cte)
        labels = pv.get()
        # soft_layout = QVBoxLayout()
        # interlock_grid.addLayout(soft_layout)
        if labels is None:
            self.layout.addWidget(
                QLabel('Failed to get interlock labels', self))
        else:
            for bit, label in enumerate(labels):
                # Add led and label to layout
                channel = _VACA_PREFIX + self._magnet_name + ':' + \
                    self._intlk_mon
                line = bit % 8
                column = int(bit / 8)
                self.layout.addWidget(Interlock(self, channel, bit, label),
                                      line, column)


class MagnetInterlockWindow(SiriusMainWindow):

    def __init__(self, parent=None, magnet='', interlock=0):
        super().__init__(parent)
        self._magnet_name = _PVName(magnet)
        name = self._magnet_name
        secs = {'AS', 'TB', 'BO', 'TS', 'SI', 'LI'}
        if name.sec in secs:
            self.setObjectName(name.sec+'App')
        elif name.idx[:2] in secs:
            self.setObjectName(name.idx[:2]+'App')
        else:
            self.setObjectName('ASApp')
        self._interlock = interlock
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._magnet_name + (' Soft Interlock'
                            if not self._interlock else ' Hard Interlock'))
        self._central_widget = QWidget(parent=self)
        self._central_widget.layout = QVBoxLayout()
        self._central_widget.setLayout(self._central_widget.layout)
        self.setCentralWidget(self._central_widget)

        self._central_widget.layout.addWidget(
            QLabel("<h1>" + self._magnet_name + "</h1>"))
        self._central_widget.layout.addWidget(
            QLabel("<h3>" +
                   ('Soft Interlock'
                    if not self._interlock
                    else 'Hard Interlock') +
                   "</h3>"))
        self._interlock_layout = QHBoxLayout()
        self._tab_widget = QTabWidget(self)
        for ps in self._get_ps_list(self._magnet_name):
            ma = MagnetInterlockWidget(parent=self,
                                       magnet=ps,
                                       interlock=self._interlock)
            # self._interlock_layout.addWidget(ma)
            self._tab_widget.addTab(ma, ps)
        # self._central_widget.layout.addLayout(self._interlock_layout)
        self._central_widget.layout.addWidget(self._tab_widget)

    def _get_ps_list(self, magnet):
        if 'SI-Fam:MA-B1B2' in magnet:
            return ['SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2']
        elif 'BO-Fam:MA-B' in magnet:
            return ['BO-Fam:PS-B-1', 'BO-Fam:PS-B-2']
        else:
            return [magnet.replace('MA', 'PS'), ]
