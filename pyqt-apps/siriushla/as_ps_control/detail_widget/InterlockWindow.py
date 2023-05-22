"""Magnet Interlock widget."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QTabWidget
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch
from siriuspy.pwrsupply.csdev import ETypes as _et
from siriuspy.pwrsupply.csdev import get_ps_propty_database
from siriushla.widgets import SiriusMainWindow, SiriusLedAlert, PyDMLed, \
    SiriusLabel


class InterlockWidget(QWidget):
    """InterlockWidget class."""

    def __init__(self, parent=None, init_channel='', bit=-1, label=''):
        """."""
        super().__init__(parent)
        self.led = SiriusLedAlert(self, init_channel, bit)
        self.label = QLabel(label, self)
        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(self.led)
        lay.addWidget(self.label)
        self.setLayout(lay)


class InterlockListWidget(QWidget):
    """Widget with interlock information."""

    def __init__(self, parent=None, devname='', interlock='', labels=None):
        """."""
        super().__init__(parent)
        self._devname = _PVName(devname)
        self._interlock = interlock
        self._labels = labels
        self._setup_ui()

    def _setup_ui(self):
        ch = self._devname.substitute(
            prefix=_VACA_PREFIX, propty=self._interlock+'-Mon')
        lay = QGridLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Value: ', self))
        hbox.addWidget(SiriusLabel(self, ch))
        hbox.addStretch()
        lay.addLayout(hbox, 0, 0, 1, len(self._labels)/8)
        for bit, label in enumerate(self._labels):
            # Add led and label to layout
            line = (bit % 8) + 1
            column = int(bit / 8)
            lay.addWidget(InterlockWidget(self, ch, bit, label), line, column)
        self.setLayout(lay)


class InterlockWindow(SiriusMainWindow):
    """InterlockWindow class."""

    def __init__(self, parent=None, devname='', database=None,
                 interlock=None, auxdev=None, auxdev2mod=None):
        """Init."""
        super().__init__(parent)
        self._devname = _PVName(devname)
        self._db = database
        self._auxdev = auxdev
        self._auxdev2mod = auxdev2mod
        self._interlock = interlock
        if isinstance(interlock, str):
            self._interlock = [interlock, ]

        secs = {'AS', 'TB', 'BO', 'TS', 'SI', 'IT'}
        if self._devname.sub.endswith(('SA', 'SB', 'SP', 'ID')):
            self.setObjectName('IDApp')
        elif self._devname.sec in secs:
            self.setObjectName(self._devname.sec+'App')
        elif self._devname.idx[:2] in secs:
            self.setObjectName(self._devname.idx[:2]+'App')
        else:
            self.setObjectName('ASApp')

        self._intlktype = ''
        auxlabel = 'Alarms' if 'Alarm' in self._interlock[0] else 'Interlocks'
        if 'IntlkSoft' in self._interlock[0]:
            self._intlktype = 'Soft'
        elif 'IntlkHard' in self._interlock[0]:
            self._intlktype = 'Hard'
        elif 'IntlkIIB' in self._interlock[0]:
            self._intlktype = 'IIB'
        elif self._devname.dev in ['FCH', 'FCV']:
            self._intlktype = 'Amp'

        self._intlkname = self._intlktype + ' ' + auxlabel
        self.setWindowTitle(self._devname + ' - ' + self._intlkname)
        self._setup_ui()

    def _setup_ui(self):
        self.cwid = QWidget(parent=self)
        self.setCentralWidget(self.cwid)
        lay = QVBoxLayout(self.cwid)
        lay.addWidget(QLabel("<h1>" + self._devname + "</h1>"))
        lay.addWidget(QLabel("<h3>" + self._intlkname + "</h3>"))

        if len(self._interlock) == 1:
            labels = self._db[self._interlock[0]+'Labels-Cte']['value']
            wid = InterlockListWidget(
                parent=self, devname=self._devname,
                interlock=self._interlock[0], labels=labels)
            lay.addWidget(wid)
        else:
            self._tab_widget = QTabWidget(self)
            for aux in self._auxdev:
                devaux = self._devname + aux
                for intlk in self._interlock:
                    name = intlk.replace('Alarms', '').replace('Intlk', '')
                    if 'Mod' in name:
                        mod = name.split('Mod')[1]
                        tab_lbl = 'IIB Mod'.replace(self._intlktype, '')
                        tab_lbl += self._auxdev2mod[devaux][mod] \
                            if devaux in self._auxdev2mod else mod
                    else:
                        tab_lbl = 'IIB' if 'IIB' in intlk else 'Main'
                    if tab_lbl == 'Main' and aux:
                        continue
                    labels = self._db[intlk+'Labels-Cte']['value']
                    wid = InterlockListWidget(
                        parent=self, devname=devaux, interlock=intlk,
                        labels=labels)
                    self._tab_widget.addTab(wid, tab_lbl)
            lay.addWidget(self._tab_widget)


class LIInterlockWindow(SiriusMainWindow):
    """LIInterlockWindow class."""

    BIT_MAPS = {
        'IntlkWarn-Mon':
            {idx: name for idx, name in enumerate(_et.LINAC_INTLCK_WARN)},
        'IntlkSignalIn-Mon':
            {idx: name for idx, name in enumerate(_et.LINAC_INTLCK_SGIN)},
        'IntlkSignalOut-Mon':
            {idx: name for idx, name in enumerate(_et.LINAC_INTLCK_SGOUT)},
    }
    COLOR_MAPS = {
        'IntlkWarn-Mon': {
            'on': PyDMLed.Yellow,
            'off': PyDMLed.LightGreen,
        },
        'IntlkSignalIn-Mon': {
            'on': PyDMLed.Red,
            'off': PyDMLed.LightGreen,
        },
        'IntlkRdSignalInMask-Mon': {
            'on': PyDMLed.LightGreen,
            'off': PyDMLed.DarkGreen,
        },
        'IntlkSignalOut-Mon': {
            'on': PyDMLed.Yellow,
            'off': PyDMLed.LightGreen,
        },
        'IntlkRdSignalOutMask-Mon': {
            'on': PyDMLed.LightGreen,
            'off': PyDMLed.DarkGreen,
        },
    }

    def __init__(self, parent=None, devname=''):
        """."""
        super().__init__(parent)
        self._devname = _PVName(devname)
        self.setObjectName('LIApp')
        self.setWindowTitle(self._devname + ' Interlock Window')
        self._setup_ui()

    def _setup_ui(self):
        self.cwid = QWidget(parent=self)
        self.setCentralWidget(self.cwid)
        lay = QGridLayout(self.cwid)
        lay.setHorizontalSpacing(20)

        self.label_warn = QLabel('Warn Status')
        self.grid_warn = QGridLayout()
        for bit, text in self.BIT_MAPS['IntlkWarn-Mon'].items():
            led = PyDMLed(self, self._devname+':IntlkWarn-Mon', bit=bit)
            led.setOnColor(self.COLOR_MAPS['IntlkWarn-Mon']['on'])
            led.setOffColor(self.COLOR_MAPS['IntlkWarn-Mon']['off'])
            lbl = QLabel(text, self)
            self.grid_warn.addWidget(led, bit, 0)
            self.grid_warn.addWidget(lbl, bit, 1)

        self.label_digin = QLabel('Digital Input')
        self.label_digout = QLabel('Digital Output')
        for typ in ['In', 'Out']:
            gridname = 'grid_dig'+typ.lower()
            setattr(self, gridname, QGridLayout())
            grd = getattr(self, gridname)
            grd.setHorizontalSpacing(9)
            sgch = 'IntlkSignal'+typ+'-Mon'
            mskch = 'IntlkRdSignal'+typ+'Mask-Mon'
            for bit, text in self.BIT_MAPS[sgch].items():
                led = PyDMLed(self, self._devname+':'+sgch, bit=bit)
                led.setOnColor(self.COLOR_MAPS[sgch]['on'])
                led.setOffColor(self.COLOR_MAPS[sgch]['off'])
                lbl = QLabel(text, self)
                led_msk = PyDMLed(self, self._devname+':'+mskch, bit=bit)
                led_msk.setOnColor(self.COLOR_MAPS[mskch]['on'])
                led_msk.setOffColor(self.COLOR_MAPS[mskch]['off'])
                grd.addWidget(led, bit, 0)
                grd.addWidget(lbl, bit, 1)
                grd.addWidget(led_msk, bit, 2)

        lay.addWidget(QLabel("<h1>" + self._devname + "</h1>"), 0, 0, 1, 3)
        lay.addWidget(QLabel("<h3>Interlocks</h3>"), 1, 0, 1, 3)
        lay.addWidget(self.label_warn, 2, 0)
        lay.addLayout(self.grid_warn, 3, 0, Qt.AlignTop)
        lay.addWidget(self.label_digin, 2, 1)
        lay.addWidget(QLabel('Mask', self, alignment=Qt.AlignRight), 2, 2)
        lay.addLayout(self.grid_digin, 3, 1, 1, 2, Qt.AlignTop)
        lay.addWidget(self.label_digout, 2, 3)
        lay.addWidget(QLabel('Mask', self, alignment=Qt.AlignRight), 2, 4)
        lay.addLayout(self.grid_digout, 3, 3, 1, 2, Qt.AlignTop)
