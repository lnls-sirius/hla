"""Magnet Interlock widget."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QTabWidget
from pydm.widgets import PyDMLabel
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch
from siriuspy.pwrsupply.csdev import ETypes as _et
from siriuspy.pwrsupply.csdev import get_ps_propty_database
from siriushla.widgets import SiriusMainWindow, SiriusLedAlert, PyDMLed


class InterlockWidget(QWidget):
    """InterlockWidget class."""

    def __init__(self, parent=None, init_channel='', bit=-1, label=''):
        """."""
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
        """."""
        super().__init__(parent)
        self._devname = _PVName(devname)
        self._interlock = interlock
        self._setup_ui()

    def _setup_ui(self):
        key = self._interlock+'Labels-Cte'
        psmodel = PSSearch.conv_psname_2_psmodel(self._devname)
        pstype = PSSearch.conv_psname_2_pstype(self._devname)
        db = get_ps_propty_database(psmodel, pstype)
        labels = db[key]['value']

        ch = self._devname.substitute(
            prefix=_VACA_PREFIX, propty=self._interlock+'-Mon')
        lay = QGridLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Value: ', self))
        hbox.addWidget(PyDMLabel(self, ch))
        hbox.addStretch()
        lay.addLayout(hbox, 0, 0, 1, len(labels)/8)
        for bit, label in enumerate(labels):
            # Add led and label to layout
            line = (bit % 8) + 1
            column = int(bit / 8)
            lay.addWidget(InterlockWidget(self, ch, bit, label), line, column)
        self.setLayout(lay)


class InterlockWindow(SiriusMainWindow):
    """InterlockWindow class."""

    def __init__(self, parent=None, devname='', interlock=None, auxdev=list(),
                 auxdev2mod=dict()):
        """Init."""
        super().__init__(parent)
        self._devname = _PVName(devname)
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

        auxlabel = 'Interlocks'
        if 'Soft' in self._interlock[0]:
            self._intlktype = 'Soft'
        elif 'Hard' in self._interlock[0]:
            self._intlktype = 'Hard'
        elif 'IIB' in self._interlock[0]:
            self._intlktype = 'IIB'
            if 'Alarms' in self._interlock[0]:
                auxlabel = 'Alarms'
        elif self._devname.dev in ['FCH', 'FCV']:
            self._intlktype = 'Amp'
            auxlabel = 'Alarms'

        self._intlkname = self._intlktype + ' ' + auxlabel
        self.setWindowTitle(self._devname + ' - ' + self._intlkname)
        self._setup_ui()

    def _setup_ui(self):
        self.cw = QWidget(parent=self)
        self.setCentralWidget(self.cw)
        lay = QVBoxLayout(self.cw)
        lay.addWidget(QLabel("<h1>" + self._devname + "</h1>"))
        lay.addWidget(QLabel("<h3>" + self._intlkname + "</h3>"))

        if len(self._interlock) == 1:
            wid = InterlockListWidget(parent=self, devname=self._devname,
                                      interlock=self._interlock[0])
            lay.addWidget(wid)
        else:
            self._tab_widget = QTabWidget(self)
            for aux in self._auxdev:
                for intlk in self._interlock:
                    tab_lbl = intlk.replace(self._intlktype, '').replace(
                        'Alarms', '').replace('Intlk', '')
                    if self._devname+aux in self._auxdev2mod:
                        tab_lbl = 'Mod' + self._auxdev2mod[
                            self._devname+aux][tab_lbl.split('Mod')[1]]
                    wid = InterlockListWidget(
                        parent=self, devname=self._devname+aux,
                        interlock=intlk)
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
        self.cw = QWidget(parent=self)
        self.setCentralWidget(self.cw)
        lay = QGridLayout(self.cw)
        lay.setHorizontalSpacing(20)

        self.label_warn = QLabel('Warn Status')
        self.grid_warn = QGridLayout()
        i = 0
        for bit, text in self.BIT_MAPS['IntlkWarn-Mon'].items():
            led = PyDMLed(self, self._devname+':IntlkWarn-Mon', bit=i)
            led.setOnColor(self.COLOR_MAPS['IntlkWarn-Mon']['on'])
            led.setOffColor(self.COLOR_MAPS['IntlkWarn-Mon']['off'])
            lbl = QLabel(text, self)
            self.grid_warn.addWidget(led, i, 0)
            self.grid_warn.addWidget(lbl, i, 1)
            i += 1

        self.label_digin = QLabel('Digital Input')
        self.label_digout = QLabel('Digital Output')
        for typ in ['In', 'Out']:
            i = 0
            gridname = 'grid_dig'+typ.lower()
            setattr(self, gridname, QGridLayout())
            grd = getattr(self, gridname)
            grd.setHorizontalSpacing(9)
            sgch = 'IntlkSignal'+typ+'-Mon'
            mskch = 'IntlkRdSignal'+typ+'Mask-Mon'
            for bit, text in self.BIT_MAPS[sgch].items():
                led = PyDMLed(self, self._devname+':'+sgch, bit=i)
                led.setOnColor(self.COLOR_MAPS[sgch]['on'])
                led.setOffColor(self.COLOR_MAPS[sgch]['off'])
                lbl = QLabel(text, self)
                led_msk = PyDMLed(self, self._devname+':'+mskch, bit=i)
                led_msk.setOnColor(self.COLOR_MAPS[mskch]['on'])
                led_msk.setOffColor(self.COLOR_MAPS[mskch]['off'])
                grd.addWidget(led, i, 0)
                grd.addWidget(lbl, i, 1)
                grd.addWidget(led_msk, i, 2)
                i += 1

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
