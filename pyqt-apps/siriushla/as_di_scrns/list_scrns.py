"""Screens list."""

from qtpy.QtWidgets import QWidget, QLabel, QPushButton, \
    QVBoxLayout, QHBoxLayout
from qtpy.QtCore import Qt
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util


def get_scrn_list(sec):
    if sec == 'TB':
        return ['TB-01:DI-Scrn-1', 'TB-01:DI-Scrn-2',
                'TB-02:DI-Scrn-1', 'TB-02:DI-Scrn-2',
                'TB-03:DI-Scrn', 'TB-04:DI-Scrn']
    elif sec == 'BO':
        return ['BO-01D:DI-Scrn-1', 'BO-01D:DI-Scrn-2',
                'BO-02U:DI-Scrn']
    elif sec == 'TS':
        return ['TS-01:DI-Scrn', 'TS-02:DI-Scrn',
                'TS-03:DI-Scrn', 'TS-04:DI-Scrn-1',
                'TS-04:DI-Scrn-2', 'TS-04:DI-Scrn-3']


class ScrnSummary(QWidget):
    """Screen Summary."""

    def __init__(self, parent=None, prefix=_vaca_prefix, scrn=''):
        """Init."""
        super().__init__(parent=parent)
        self._prefix = prefix
        self._scrn = scrn
        self._setupUi()

    def _setupUi(self):
        hlay = QHBoxLayout(self)
        hlay.addStretch()
        pbt = QPushButton(self._scrn)
        pbt.setStyleSheet("""min-width:10em;""")
        util.connect_newprocess(
            pbt, ['sirius-hla-as-di-scrn.py', '-p', self._prefix, self._scrn],
            parent=self)
        hlay.addWidget(pbt)
        hlay.addStretch()


class SelectScrns(QWidget):
    """Select Screens."""

    def __init__(self, parent=None, prefix=_vaca_prefix, sec=''):
        """Init."""
        super().__init__(parent=parent)
        self._prefix = prefix
        self._sec = sec
        self.scrn_list = get_scrn_list(self._sec)
        self.setObjectName(sec+'App')
        self._setupUi()

    def _setupUi(self):
        vlay = QVBoxLayout(self)
        vlay.setSpacing(15)
        self.setLayout(vlay)

        lab = QLabel('<h2>' + self._sec + ' Screens List</h2>',
                     alignment=Qt.AlignCenter)
        vlay.addWidget(lab)

        for scrn in self.scrn_list:
            scrn_wid = ScrnSummary(self, prefix=self._prefix, scrn=scrn)
            vlay.addWidget(scrn_wid)
