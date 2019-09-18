"""Magnet Interlock widget."""

from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QTabWidget
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import MASearch, PSSearch
from siriuspy.csdevice.pwrsupply import \
    get_ps_propty_database, get_ma_propty_database
from siriushla.widgets import SiriusMainWindow, SiriusLedAlert


class InterlockWidget(QWidget):

    def __init__(self, parent=None, init_channel='', bit=-1, label=''):
        super().__init__(parent)
        self.led = SiriusLedAlert(self, init_channel, bit)
        self.label = QLabel(label, self)
        lay = QHBoxLayout()
        lay.addWidget(self.led)
        lay.addWidget(self.label)
        self.setLayout(lay)


class InterlockListWidget(QWidget):
    """Widget with interlock information."""

    def __init__(self, parent=None, devname='', interlock=''):
        super().__init__(parent)
        self._devname = _PVName(devname)
        self.setObjectName(self._devname.sec+'App')
        self._interlock = interlock
        self._setup_ui()

    def _setup_ui(self):
        if self._devname.dis == 'PS':
            psmodel = PSSearch.conv_psname_2_psmodel(self._devname)
            pstype = PSSearch.conv_psname_2_pstype(self._devname)
            db = get_ps_propty_database(psmodel, pstype)
            labels = db['Intlk'+self._interlock+'Labels-Cte']['value']
        else:
            db = get_ma_propty_database(self._devname)
            psname = MASearch.conv_maname_2_psnames(self._devname)[0]
            labels = db[psname]['Intlk'+self._interlock+'Labels-Cte']['value']

        lay = QGridLayout()
        for bit, label in enumerate(labels):
            # Add led and label to layout
            ch = _VACA_PREFIX+self._devname+':Intlk'+self._interlock+'-Mon'
            line = bit % 8
            column = int(bit / 8)
            lay.addWidget(InterlockWidget(self, ch, bit, label), line, column)
        self.setLayout(lay)


class InterlockWindow(SiriusMainWindow):

    def __init__(self, parent=None, devname='', interlock=0):
        super().__init__(parent)
        self._devname = _PVName(devname)

        secs = {'AS', 'TB', 'BO', 'TS', 'SI', 'LI'}
        if self._devname.sec in secs:
            self.setObjectName(self._devname.sec+'App')
        elif self._devname.idx[:2] in secs:
            self.setObjectName(self._devname.idx[:2]+'App')
        else:
            self.setObjectName('ASApp')

        self._interlock = 'Soft' if not interlock else 'Hard'
        self.setWindowTitle(self._devname + ' ' +
                            self._interlock + ' Interlock')
        self._setup_ui()

    def _setup_ui(self):
        self.cw = QWidget(parent=self)
        self.setCentralWidget(self.cw)
        lay = QVBoxLayout(self.cw)
        lay.addWidget(QLabel("<h1>" + self._devname + "</h1>"))
        lay.addWidget(QLabel("<h3>" + self._interlock + " Interlock</h3>"))

        ps_list = [self._devname, ]
        if self._devname.dis == 'MA':
            ps_list = MASearch.conv_maname_2_psnames(self._devname)
        if len(ps_list) == 1:
            wid = InterlockListWidget(parent=self, devname=self._devname,
                                      interlock=self._interlock)
            lay.addWidget(wid)
        else:
            self._tab_widget = QTabWidget(self)
            for ps in ps_list:
                wid = InterlockListWidget(parent=self, devname=ps,
                                          interlock=self._interlock)
                self._tab_widget.addTab(wid, ps)
            lay.addWidget(self._tab_widget)
