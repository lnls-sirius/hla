"""."""
import logging as _log
import numpy as _np

from qtpy.QtCore import Qt, Slot
from qtpy.QtGui import QColor, QBrush
from qtpy.QtWidgets import QLabel, QPushButton, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QMenuBar, QSplitter, QTabWidget, QWidget, \
    QSizePolicy as QSzPol, QCheckBox, QFrame, QAbstractItemView, QHeaderView
import qtawesome as qta
from pydm.widgets import PyDMLineEdit, PyDMPushButton

from siriuspy.search import LLTimeSearch, HLTimeSearch
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys import csdev as _cstime

from ..widgets import PyDMLed, PyDMStateButton, SiriusLedState, \
    SiriusEnumComboBox, SiriusLedAlert, SiriusLabel, \
    SiriusSpinbox, SiriusConnectionSignal, SiriusWaveformTable, \
    SiriusPushButton, SiriusWaveformPlot
from ..widgets.windows import create_window_from_widget, SiriusDialog
from ..util import connect_window, get_appropriate_color

from .base import BaseList, BaseWidget


# ###################### Event Generator ######################
class BucketListLineEdit(PyDMLineEdit):

    def value_changed(self, value):
        super().value_changed(value)
        self.channeltype = _np.ndarray
        self.subtype = int


class BucketListLabel(SiriusLabel):

    def value_changed(self, value):
        maxele = 20
        if isinstance(value, _np.ndarray):
            zeros = _np.where(value == 0)[0]
            if zeros.size > 0:
                value = value[:zeros[0]]
            txt = '[ ' + ' '.join([str(i) for i in value[:maxele]])
            txt += ' ...]' if value.size > maxele else ']'
            self.setText(txt)
        else:
            super().value_changed(value)


class EVG(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix='', device=''):
        """Initialize object."""
        super().__init__(parent, prefix=prefix)
        self.device = _PVName(device or LLTimeSearch.get_evg_name())
        self.setupui()
        self.setObjectName('ASApp')

    def setupui(self):
        mylayout = QGridLayout(self)
        mylayout.setHorizontalSpacing(20)
        mylayout.setVerticalSpacing(20)

        mylayout.addWidget(self._setupmenus(), 0, 0, 1, 2)

        lab = QLabel('<h1>' + self.device.device_name + '</h1>', self)
        mylayout.addWidget(lab, 1, 0, 1, 2)
        mylayout.setAlignment(lab, Qt.AlignCenter)

        # status
        self.status_wid = QGroupBox('Status', self)
        mylayout.addWidget(self.status_wid, 2, 0)
        self._setup_status_wid()

        # configurations
        conftab = QTabWidget(self)
        conftab.setObjectName('ASTab')
        conftab.setSizePolicy(QSzPol.Preferred, QSzPol.Maximum)
        mylayout.addWidget(conftab, 2, 1)

        confwid = QWidget()
        conflay = QVBoxLayout(confwid)
        maintab = QTabWidget(self)
        maintab.setObjectName('ASTab')
        maintab.setStyleSheet("""
            QTabWidget::pane{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        self.configs_wid = self._setup_configs_wid()
        maintab.addTab(self.configs_wid, 'Main')
        self.info_wid = self._setup_info_wid()
        maintab.addTab(self.info_wid, 'Fw && IOC')
        conflay.addWidget(maintab)
        self.bucketlist_wid = BucketList(self, self.device, self.prefix)
        conflay.addWidget(self.bucketlist_wid)
        conflay.setContentsMargins(0, 6, 0, 0)
        conftab.addTab(confwid, 'Configurations')

        # interlock map
        self.intlkmap_wid = self._setup_intlkmap_wid()
        conftab.addTab(self.intlkmap_wid, 'Interlock Map')

        # outtab
        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.setHandleWidth(20)
        mylayout.addWidget(splitter, 3, 0, 1, 2)

        obj_names = [
            self.device.substitute(propty=dev) for dev in
            sorted(_cstime.Const.EvtLL._fields) if 0 < int(dev[3:]) < 64]
        self.events_wid = EventList(
            name='Events', parent=self, prefix=self.prefix,
            obj_names=obj_names)
        splitter.addWidget(self.events_wid)

        obj_names = [self.device.substitute(propty=dev) for dev in
                     sorted(_cstime.Const.ClkLL._fields)]
        self.clocks_wid = ClockList(
            name='Clocks', parent=self, prefix=self.prefix,
            obj_names=obj_names, has_search=True)
        splitter.addWidget(self.clocks_wid)

        splitter.setSizePolicy(QSzPol.Preferred, QSzPol.MinimumExpanding)

    def _setupmenus(self):
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)

        try:
            fouts = LLTimeSearch.get_evg2fout_mapping()
        except KeyError:
            return main_menu

        menu = main_menu.addMenu('&Downlinks')
        for out, down in sorted(fouts.items()):
            action = menu.addAction(out + ' --> ' + down)
            icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
            Win = create_window_from_widget(FOUT, title=down, icon=icon)
            connect_window(action, Win, None, device=down, prefix=self.prefix)
        return main_menu

    def _setup_configs_wid(self):
        configs_wid = QWidget()
        lay = QGridLayout(configs_wid)

        # general configs
        pvname = self.get_pvname(propty='DevEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='DevEnbl-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        pg = self._create_prop_widget('Dev Enable', configs_wid, (sp, rb))
        lay.addWidget(pg, 0, 0, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='UpdateEvt-Cmd')
        sp = PyDMPushButton(self, init_channel=pvname, pressValue=1)
        sp.setIcon(qta.icon('fa5s.sync'))
        sp.setToolTip('Update Events Table')
        sp.setObjectName('but')
        sp.setStyleSheet(
            '#but{min-width:25px; max-width:25px; icon-size:20px;}')
        pvname = self.get_pvname(propty='EvtSyncStatus-Mon')
        rb = SiriusLedState(self, init_channel=pvname)
        rb.offColor = rb.Red
        pg = self._create_prop_widget('Update Evts', configs_wid, (sp, rb))
        lay.addWidget(pg, 0, 1, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='ContinuousEvt-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='ContinuousEvt-Sts')
        rb = SiriusLedState(self, init_channel=pvname)
        pg = self._create_prop_widget('Continuous', configs_wid, (sp, rb))
        lay.addWidget(pg, 0, 2, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='InjectionEvt-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='InjectionEvt-Sts')
        rb = SiriusLedState(self, init_channel=pvname)
        pg = self._create_prop_widget('Injection', configs_wid, (sp, rb))
        lay.addWidget(pg, 0, 3, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='InjRate-SP')
        sp = SiriusSpinbox(self, init_channel=pvname)
        pvname = self.get_pvname(propty='InjRate-RB')
        rb = SiriusLabel(self, init_channel=pvname)
        pg = self._create_prop_widget('Pulse Rate [Hz]', configs_wid, (sp, rb))
        lay.addWidget(pg, 0, 4, alignment=Qt.AlignCenter)

        # ac line configs
        pvname = self.get_pvname(propty='ACEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='ACEnbl-Sts')
        rb = SiriusLedState(self, init_channel=pvname)
        pg = self._create_prop_widget('AC Enable', configs_wid, (sp, rb))
        lay.addWidget(pg, 1, 0, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='ACStatus-Mon')
        mon = SiriusLedState(self, init_channel=pvname)
        mon.offColor = rb.Red
        pg = self._create_prop_widget('AC Status', configs_wid, (mon,))
        lay.addWidget(pg, 1, 1, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='ACSrc-Sel')
        sp = SiriusEnumComboBox(self, init_channel=pvname)
        pvname = self.get_pvname(propty='ACSrc-Sts')
        rb = SiriusLabel(self, init_channel=pvname)
        pg = self._create_prop_widget('AC Source', configs_wid, (sp, rb))
        lay.addWidget(pg, 1, 2, alignment=Qt.AlignCenter)

        # rf configs
        pvname = self.get_pvname(propty='RFReset-Cmd')
        sp = PyDMPushButton(self, init_channel=pvname, pressValue=1)
        sp.setIcon(qta.icon('fa5s.sync'))
        sp.setToolTip('Reset RF Status')
        sp.setObjectName('but')
        sp.setStyleSheet(
            '#but{min-width:25px; max-width:25px; icon-size:20px;}')
        pvname = self.get_pvname(propty='RFStatus-Mon')
        rb = SiriusLedState(self, init_channel=pvname)
        rb.offColor = rb.Red
        pg = self._create_prop_widget('RF Status', configs_wid, (sp, rb))
        lay.addWidget(pg, 1, 3, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='RFDiv-SP')
        sp = SiriusSpinbox(self, init_channel=pvname)
        pvname = self.get_pvname(propty='RFDiv-RB')
        rb = SiriusLabel(self, init_channel=pvname)
        pg = self._create_prop_widget('RF Divisor', configs_wid, (sp, rb))
        lay.addWidget(pg, 1, 4, alignment=Qt.AlignCenter)

        return configs_wid

    def _setup_status_wid(self):
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(5)

        pvname = self.get_pvname(propty='STATEMACHINE')
        rb1 = SiriusLabel(self.status_wid, init_channel=pvname)
        pvname = self.get_pvname(propty='DevStatus-Mon')
        rb2 = SiriusLabel(self.status_wid, init_channel=pvname)
        hlay = QHBoxLayout()
        hlay.addStretch()
        hlay.addWidget(rb1)
        hlay.addStretch()
        hlay.addWidget(rb2)
        hlay.addStretch()
        status_layout.addItem(hlay, 0, 0, 1, 3)
        status_layout.setAlignment(hlay, Qt.AlignCenter)

        hlay = QHBoxLayout()
        wid = QWidget(self.status_wid)
        wid.setLayout(QHBoxLayout())
        wid.layout().setContentsMargins(0, 0, 0, 0)
        pvname = self.get_pvname(propty='TotalInjCount-Mon')
        pydmlab1 = SiriusLabel(self.status_wid, init_channel=pvname)
        pydmlab1.setStyleSheet('min-width:5em;')
        pydmlab1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pvname = self.get_pvname(propty='InjCount-Mon')
        pydmlab2 = SiriusLabel(self.status_wid, init_channel=pvname)
        pydmlab2.setAlignment(Qt.AlignCenter)
        lab1 = QLabel(
            '(', self.status_wid, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lab2 = QLabel(
            ')', self.status_wid, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        wid.layout().addStretch()
        wid.layout().addWidget(pydmlab1)
        wid.layout().addWidget(lab1)
        wid.layout().addWidget(pydmlab2)
        wid.layout().addWidget(lab2)
        wid.layout().addStretch()
        hlay.addWidget(self._create_prop_widget(
            '<b>Inj Count: All (Now)</b>', self.status_wid, (wid, )))

        wid = QWidget(self.status_wid)
        wid.setLayout(QHBoxLayout())
        wid.layout().setContentsMargins(0, 0, 0, 0)
        pvname = self.get_pvname(propty='SeqStatus-Mon')
        pydmlab1 = SiriusLabel(self.status_wid, init_channel=pvname)
        pydmlab1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pvname = self.get_pvname(propty='SeqCount-SP')
        pydmlab2 = SiriusLabel(self.status_wid, init_channel=pvname)
        lab1 = QLabel(
            '(', self.status_wid, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lab2 = QLabel(
            ')', self.status_wid, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        wid.layout().addStretch()
        wid.layout().addWidget(pydmlab1)
        wid.layout().addWidget(lab1)
        wid.layout().addWidget(pydmlab2)
        wid.layout().addWidget(lab2)
        wid.layout().addStretch()
        hlay.addWidget(self._create_prop_widget(
            '<b>Sequence: Table (Count)</b>', self.status_wid, (wid, )))
        status_layout.addItem(hlay, 1, 0, 1, 3)

        lb = QLabel("<b>Alive</b>")
        pvname = self.get_pvname(propty='Alive-Mon')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', self.status_wid, (lb, rb))
        status_layout.addWidget(gb, 2, 0)

        lb = QLabel("<b>Network</b>")
        pvname = self.get_pvname(propty='Network-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_group('', self.status_wid, (lb, rb))
        status_layout.addWidget(gb, 2, 1)

        lb = QLabel("<b>RF Sts</b>")
        pvname = self.get_pvname(propty='RFStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_group('', self.status_wid, (lb, rb))
        status_layout.addWidget(gb, 2, 2)

        wids = list()
        try:
            conn = LLTimeSearch.get_connections_from_evg()
            conn = {int(dev.propty[-1]) for dev in conn if dev.dev == 'EVG'}
        except KeyError:
            conn = set()
        for i in range(8):
            pvname = self.get_pvname(propty='Los-Mon')
            if i in conn:
                rb = SiriusLedAlert(self, init_channel=pvname, bit=i)
            else:
                rb = SiriusLedState(self, init_channel=pvname, bit=i)
                rb.onColor = rb.DarkGreen
                rb.offColor = rb.LightGreen
            wids.append(rb)
        but = QPushButton(self)
        but.setToolTip('Open Down Connections Details')
        but.setIcon(qta.icon('fa5s.ellipsis-v'))
        but.setObjectName('but')
        but.setDefault(False)
        but.setAutoDefault(False)
        but.setStyleSheet(
            '#but{min-width:15px; max-width:15px;\
            min-height:25px; max-height:25px;\
            icon-size:20px;}')
        but.clicked.connect(self._open_downconn_dialog)
        wids.append(but)
        gb = self._create_small_group(
            'Down Connection', self.status_wid, wids, align_ver=False)
        status_layout.addWidget(gb, 3, 0, 1, 3)

    def _setup_info_wid(self):
        info_wid = QWidget()
        lay = QGridLayout(info_wid)

        lb = QLabel("<b>IP</b>")
        pvname = self.get_pvname(propty='IPAddr-Mon')
        addr = SiriusLabel(self, init_channel=pvname)
        pvname = self.get_pvname(propty='IPPort-Mon')
        port = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, addr, port))
        lay.addWidget(gb, 0, 0, alignment=Qt.AlignHCenter)

        lb = QLabel("<b>DevFun</b>")
        pvname = self.get_pvname(propty='DevFun-Sel')
        sp = SiriusEnumComboBox(self, init_channel=pvname)
        pvname = self.get_pvname(propty='DevFun-Sts')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, sp, rb))
        lay.addWidget(gb, 0, 1, alignment=Qt.AlignHCenter)

        lb = QLabel("<b>Device Status</b>")
        pvname = self.get_pvname(propty='DevStatus-Mon')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, rb))
        lay.addWidget(gb, 0, 2, alignment=Qt.AlignHCenter)

        lb = QLabel("<b>FPGA Clk</b>")
        pvname = self.get_pvname('FPGAClk-Cte')
        mon = SiriusLabel(self, init_channel=pvname)
        mon.showUnits = True
        mon.precisionFromPV = False
        mon.precision = 3
        gb = self._create_small_group('', info_wid, (lb, mon))
        lay.addWidget(gb, 0, 3, alignment=Qt.AlignCenter)

        lb = QLabel("<b>Download</b>")
        pvname = self.get_pvname('Download-Cmd')
        sp = SiriusPushButton(
            self, label='', icon=qta.icon('fa5s.download'),
            pressValue=1, releaseValue=0, init_channel=pvname)  # ?
        gb = self._create_small_group('', info_wid, (lb, sp))
        lay.addWidget(gb, 1, 0, alignment=Qt.AlignHCenter)

        lb = QLabel("<b>Save Settings</b>")
        pvname = self.get_pvname('Save-Cmd')
        sp = PyDMPushButton(
            self, label='Save', init_channel=pvname, pressValue=1)  # ?
        gb = self._create_small_group('', info_wid, (lb, sp))
        lay.addWidget(gb, 1, 1, alignment=Qt.AlignHCenter)

        lb = QLabel("<b>RF Ref.</b>")
        pvname = self.get_pvname('RFRef-Mon')
        mon = SiriusLabel(self, init_channel=pvname)
        mon.showUnits = True
        pvname = self.get_pvname('RFRef-Mon', field='INP')
        inp = PyDMLineEdit(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, mon, inp))
        lay.addWidget(gb, 1, 2, alignment=Qt.AlignHCenter)

        lb = QLabel("<b>Fw.Version</b>")
        pvname = self.get_pvname(propty='FwVersion-Cte.SVAL')
        frmv = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, frmv))
        gb.layout().setSpacing(3)
        lay.addWidget(gb, 1, 3, alignment=Qt.AlignHCenter)

        but = QPushButton(self)
        but.setToolTip('Open Timestamp Controls')
        but.setIcon(qta.icon('fa5s.ellipsis-v'))
        but.setObjectName('but')
        but.setStyleSheet(
            '#but{min-width:25px; max-width:25px;\
            min-height:25px; max-height:25px;\
            icon-size:20px;}')
        but.clicked.connect(self._open_tstamp_dialog)
        lay.addWidget(but, 0, 4, alignment=Qt.AlignTop)

        return info_wid

    def _setup_intlkmap_wid(self):
        wid = QGroupBox()
        lay = QGridLayout(wid)
        lay.setHorizontalSpacing(30)

        # controls
        pvname = self.get_pvname(propty='IntlkCtrlEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='IntlkCtrlEnbl-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        gb = self._create_prop_widget('Intlk. Enable', wid, (sp, rb))
        lay.addWidget(gb, 0, 0, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='IntlkCtrlRst-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='IntlkCtrlRst-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        gb = self._create_prop_widget('Intlk. Reset', wid, (sp, rb))
        lay.addWidget(gb, 1, 0, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='IntlkCtrlRepeat-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='IntlkCtrlRepeat-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        gb = self._create_prop_widget('Intlk. Repeat', wid, (sp, rb))
        lay.addWidget(gb, 2, 0, alignment=Qt.AlignCenter)

        pvname = self.get_pvname(propty='IntlkCtrlRepeatTime-SP')
        sp = PyDMLineEdit(self, init_channel=pvname)
        pvname = self.get_pvname(propty='IntlkCtrlRepeatTime-RB')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_prop_widget('Intlk. Repeat Time', wid, (sp, rb))
        lay.addWidget(gb, 3, 0, alignment=Qt.AlignCenter)

        # table
        # columns in
        lay_grid = QGridLayout()
        lay_grid.setHorizontalSpacing(6)
        lay_grid.setVerticalSpacing(4)
        for idx in range(7):
            idxstr = str(idx)
            hd = QLabel('Evt'+idxstr, self, alignment=Qt.AlignCenter)
            hd.setObjectName('hd')
            le = PyDMLineEdit(self, self.get_pvname('IntlkEvtIn'+idxstr+'-SP'))
            le.setObjectName('le')
            le.setAlignment(Qt.AlignCenter)
            lb = SiriusLabel(self, self.get_pvname('IntlkEvtIn'+idxstr+'-RB'))
            lb.setObjectName('lb')
            lb.setAlignment(Qt.AlignCenter)
            ld = SiriusLedState(
                self, self.get_pvname('IntlkEvtStatus-Mon'), bit=idx)
            lay_grid.addWidget(hd, 0, idx+2, alignment=Qt.AlignCenter)
            lay_grid.addWidget(le, 1, idx+2, alignment=Qt.AlignCenter)
            lay_grid.addWidget(lb, 2, idx+2, alignment=Qt.AlignCenter)
            lay_grid.addWidget(ld, 3, idx+2, alignment=Qt.AlignCenter)
        # column out
        hd = QLabel('EvtOut', self, alignment=Qt.AlignCenter)
        hd.setObjectName('hd')
        le = PyDMLineEdit(self, self.get_pvname('IntlkEvtOut-SP'))
        le.setObjectName('le')
        le.setAlignment(Qt.AlignCenter)
        lb = SiriusLabel(self, self.get_pvname('IntlkEvtOut-RB'))
        lb.setObjectName('lb')
        lb.setAlignment(Qt.AlignCenter)
        ld = SiriusLedState(self, self.get_pvname('IntlkEvtStatus-Mon'), bit=7)
        lay_grid.addWidget(hd, 0, 9, alignment=Qt.AlignCenter)
        lay_grid.addWidget(le, 1, 9, alignment=Qt.AlignCenter)
        lay_grid.addWidget(lb, 2, 9, alignment=Qt.AlignCenter)
        lay_grid.addWidget(ld, 3, 9, alignment=Qt.AlignCenter)

        evt, row, col, colini = 0, 4, 2, 2
        for idx in range(28):
            biti = idx % 16
            bith = hex(biti).split('x')[1].capitalize()
            bitg = '0to15' if idx < 16 else '16to27'

            pvsp = self.get_pvname('IntlkTbl'+bitg+'-Sel', field='B'+bith)
            sp = PyDMStateButton(self, pvsp)
            sp.setStyleSheet(
                'PyDMStateButton{min-height: 0.98em; max-height: 0.98em;}')

            pvrb = self.get_pvname('IntlkTbl'+bitg+'-Sts')
            rb = SiriusLedState(self, pvrb, bit=biti)
            rb.setStyleSheet(
                'SiriusLedState{min-width: 0.98em; max-width: 0.98em;}')

            gb = self._create_small_group('', wid, (sp, rb), align_ver=False)
            gb.layout().setSpacing(3)
            gb.layout().setContentsMargins(3, 1, 3, 1)
            gb.setSizePolicy(QSzPol.Preferred, QSzPol.Maximum)
            lay_grid.addWidget(gb, row, col)

            col += 1
            if idx in [6, 12, 17, 21, 24, 26, 27]:
                evtlb = QLabel('Evt'+str(evt), self, alignment=Qt.AlignRight)
                lay_grid.addWidget(evtlb, row, 0, alignment=Qt.AlignVCenter)
                line = QFrame(self)
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Plain)
                lay_grid.addWidget(line, row, 1, 1, colini-1)
                evt += 1
                row += 1
                colini += 1
                col = colini
        lay.addLayout(lay_grid, 0, 1, 4, 1)

        wid.setStyleSheet("#hd, #le, #lb{max-width: 3em;}")
        return wid

    def _create_prop_widget(self, name, parent, wids, align_ver=True):
        pwid = QWidget(parent)
        vbl = QVBoxLayout(pwid)
        lab = QLabel('<b>' + name + '</b>')
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        hbl = QHBoxLayout()
        vbl.addItem(hbl)
        for wid in wids:
            wid.setParent(pwid)
            hbl.addWidget(wid)
            hbl.setAlignment(wid, Qt.AlignCenter)
        return pwid

    def _create_tstamp_dialog(self):
        dialog = SiriusDialog()
        dialog.setObjectName('ASApp')
        dialog.setWindowTitle(self.device + ' Timestamp Control')
        dialog.setWindowIcon(self.windowIcon())
        lay = QVBoxLayout(dialog)

        gbox = QGroupBox('Timestamp', self)
        lay.addWidget(gbox)
        lay_box = QGridLayout(gbox)
        lay_box.setHorizontalSpacing(30)

        lb = QLabel('<b>Get UTC</b>')
        pvname = self.get_pvname('GetUTC-Cmd')
        sp = PyDMPushButton(
            self, label='Get UTC', init_channel=pvname,
            pressValue=1)  # ?
        gb = self._create_small_group('', gbox, (lb, sp))
        lay_box.addWidget(gb, 0, 0, alignment=Qt.AlignTop)

        lb = QLabel("<b>Mismatch</b>")
        pvname = self.get_pvname(propty='UTCMismatch-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        gb = self._create_small_group('', gbox, (lb, rb))
        lay_box.addWidget(gb, 0, 1, alignment=Qt.AlignTop)

        lb = QLabel("<b>UTC Source</b>")
        pvname = self.get_pvname(propty='UTCRefSrc-Sel')
        sp = SiriusEnumComboBox(self, init_channel=pvname)
        gb = self._create_small_group('', gbox, (lb, sp))
        lay_box.addWidget(gb, 1, 0, alignment=Qt.AlignTop)

        lb = QLabel("<b>PPS Source</b>")
        pvname = self.get_pvname(propty='TimestampSrc-Sel')
        sp = SiriusEnumComboBox(self, init_channel=pvname)
        pvname = self.get_pvname(propty='TimestampSrc-Sts')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', gbox, (lb, sp, rb))
        lay_box.addWidget(gb, 1, 1, alignment=Qt.AlignTop)

        lb = QLabel("<b>UTC</b>")
        pvname = self.get_pvname(propty='UTC-SP')
        sp = PyDMLineEdit(self, init_channel=pvname)
        pvname = self.get_pvname(propty='UTC-RB')
        rb = SiriusLabel(self, init_channel=pvname)
        rb.showUnits = True
        gb = self._create_small_group('', gbox, (lb, sp, rb))
        lay_box.addWidget(gb, 2, 0, alignment=Qt.AlignTop)

        lb = QLabel('<b>Subsec</b>')
        mon = SiriusLabel(self, self.get_pvname('SubSecond-Mon'))
        mon.showUnits = True
        gb = self._create_small_group('', gbox, (lb, mon))
        lay_box.addWidget(gb, 2, 1, alignment=Qt.AlignTop)

        lb = QLabel('<b>Control Room UTC</b>')
        mon = SiriusLabel(self, self.get_pvname('CtrlRoomUTC'))
        mon.showUnits = True
        gb = self._create_small_group('', gbox, (lb, mon))
        lay_box.addWidget(gb, 3, 0, alignment=Qt.AlignTop)

        return dialog

    def _open_tstamp_dialog(self):
        if not hasattr(self, 'tstamp_wind'):
            self.tstamp_wind = self._create_tstamp_dialog()
            self.tstamp_wind.show()
        else:
            self.tstamp_wind.showNormal()

    def _create_downconn_dialog(self):
        dialog = SiriusDialog()
        dialog.setObjectName('ASApp')
        dialog.setWindowTitle(self.device + ' Down Connections')
        dialog.setWindowIcon(self.windowIcon())

        lay = QVBoxLayout(dialog)
        obj_names = [
            self.device.substitute(idx=self.device.idx+'_'+str(i))
            for i in range(8)]
        downconn_wid = EVGFOUTOUTList(
            name='Down Connections', parent=self, prefix=self.prefix,
            obj_names=obj_names)
        lay.addWidget(downconn_wid)
        return dialog

    def _open_downconn_dialog(self):
        if not hasattr(self, 'downconn_wind'):
            self.downconn_wind = self._create_downconn_dialog()
            self.downconn_wind.show()
        else:
            self.downconn_wind.showNormal()


class BucketListGraph(BaseWidget):
    """Bucket List Graph."""

    def __init__(self, parent=None, device='', prefix=''):
        if not device:
            device = LLTimeSearch.get_evg_name()
        super().__init__(parent, device, prefix)
        self._setupUi()

    def _setupUi(self):
        # Graph
        self.graph = SiriusWaveformPlot(self)
        self.graph.setBackgroundColor(QColor(255, 255, 255))
        self.graph.maxRedrawRate = 2
        self.graph.mouseEnabledX = True
        self.graph.setShowXGrid(True)
        self.graph.setShowYGrid(True)
        self.graph.setAutoRangeX(False)
        self.graph.setMinYRange(-0.1)
        self.graph.setMaxYRange(1.1)
        self.graph.setAxisColor(QColor(0, 0, 0))
        self.graph.setLabel('left', 'Buckets', color='gray')
        self.graph.setObjectName('graph')
        self.graph.setStyleSheet('#graph{min-height: 5em;}')
        self.graph.setSizePolicy(QSzPol.Expanding, QSzPol.Expanding)

        self._curves = dict()
        self.graph.addChannel(
            y_channel='FAKE:SP', name='SP', color='red', lineWidth=2)
        self._curves['SP'] = self.graph.curveAtIndex(0)
        self._curves['SP'].setFillLevel(0)
        self._curves['SP'].setBrush(QBrush(QColor('red')))
        self.graph.addChannel(
            y_channel='FAKE:RB', name='RB', color='blue', lineWidth=2)
        self._curves['RB'] = self.graph.curveAtIndex(1)
        self._curves['RB'].setFillLevel(0)
        self._curves['RB'].setBrush(QBrush(QColor('blue')))
        self.graph.addChannel(
            y_channel='FAKE:Mon', name='Mon', color='green', lineWidth=2)
        self._curves['Mon'] = self.graph.curveAtIndex(2)
        self._curves['Mon'].setFillLevel(0)
        self._curves['Mon'].setBrush(QBrush(QColor('green')))

        # Show
        self.show_sp = QCheckBox('SP')
        self.show_sp.setChecked(True)
        self.show_sp.setStyleSheet('color: red;')
        self.show_sp.stateChanged.connect(self._curves['SP'].setVisible)
        self.show_rb = QCheckBox('RB')
        self.show_rb.setChecked(True)
        self.show_rb.setStyleSheet('color: blue;')
        self.show_rb.stateChanged.connect(self._curves['RB'].setVisible)
        self.show_mn = QCheckBox('Mon')
        self.show_mn.setChecked(True)
        self.show_mn.setStyleSheet('color: green;')
        self.show_mn.stateChanged.connect(self._curves['Mon'].setVisible)
        wid_show = QWidget()
        lay_show = QVBoxLayout(wid_show)
        lay_show.setContentsMargins(0, 0, 0, 0)
        lay_show.addWidget(self.show_sp)
        lay_show.addWidget(self.show_rb)
        lay_show.addWidget(self.show_mn)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.graph)
        lay.addWidget(wid_show)

        self._ch_sp = SiriusConnectionSignal(
            self.get_pvname(propty='BucketList-SP'))
        self._ch_sp.new_value_signal[_np.ndarray].connect(self._update_curves)
        self._ch_sp.new_value_signal[int].connect(self._update_curves)
        self._ch_rb = SiriusConnectionSignal(
            self.get_pvname(propty='BucketList-RB'))
        self._ch_rb.new_value_signal[_np.ndarray].connect(self._update_curves)
        self._ch_rb.new_value_signal[int].connect(self._update_curves)
        self._ch_mn = SiriusConnectionSignal(
            self.get_pvname(propty='BucketList-Mon'))
        self._ch_mn.new_value_signal[_np.ndarray].connect(self._update_curves)
        self._ch_mn.new_value_signal[int].connect(self._update_curves)

    @Slot(int)
    @Slot(_np.ndarray)
    def _update_curves(self, new_array):
        new_array = _np.asarray(new_array)

        for k in self._curves:
            if self.sender().address.endswith(k):
                curve = self._curves[k]
                break

        org_bunch = _np.arange(1, 864) - 0.5
        org_curve = _np.zeros(864)
        # trying to catch bug observed where new_array
        # had strange values greater than 864
        try:
            org_curve[new_array-1] = 1
        except IndexError:
            _log.warning(
                'IndexError: Received array for '
                f'{self.sender().address} with values out of [1, 864]')
            _log.warning(f'IndexError: new_array: {new_array}')

        new_bunch = _np.linspace(1, 864, 10000) - 0.5
        new_bunch_indices = _np.searchsorted(
            _np.nextafter(org_bunch, -_np.inf), new_bunch, side='left')
        new_bunch_indices = new_bunch_indices.clip(
            1, len(org_bunch)).astype(_np.int_)
        new_curve = org_curve[new_bunch_indices-1]

        curve.receiveXWaveform(new_bunch)
        curve.receiveYWaveform(new_curve)


class BucketList(BaseWidget):

    def __init__(self, parent=None, device='', prefix='', min_size=25,
                 show_graph=False):
        if not device:
            device = LLTimeSearch.get_evg_name()
        super().__init__(parent, device, prefix)
        self.setObjectName('ASApp')
        self._min_size = min_size
        self._show_graph = show_graph
        self.setupui()

    def setupui(self):
        self.setLayout(QHBoxLayout(self))
        wid = QGroupBox('Bucket List', self)
        self.layout().addWidget(wid)
        self.layout().setContentsMargins(0, 0, 0, 0)
        lay = QGridLayout(wid)

        tm = 'min-width:{0:d}em; max-height:1.15em;'
        pvname = self.get_pvname("BucketList-SP")
        sp = BucketListLineEdit(wid, init_channel=pvname)
        self.bucket_ledit = sp
        sp.setStyleSheet(tm.format(self._min_size-1))
        sp.setSizePolicy(QSzPol.MinimumExpanding, QSzPol.Maximum)
        lab = QLabel('SP : ', wid)
        lab.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        pushbtn = QPushButton(wid)
        pushbtn.setObjectName('but')
        pushbtn.setStyleSheet(
            '#but{min-width:25px; max-width:25px; icon-size:20px;}')
        pushbtn.setIcon(qta.icon('mdi.basket-fill'))
        self._wid_fill = self._setup_bucket_list_fill()
        pushbtn.clicked.connect(self._wid_fill.open)
        lay_sp = QHBoxLayout()
        lay_sp.addWidget(lab)
        lay_sp.addWidget(sp)
        lay_sp.addWidget(pushbtn)
        pvname = self.get_pvname("BucketList-RB")
        rb = BucketListLabel(wid, init_channel=pvname)
        rb.setStyleSheet(tm.format(self._min_size))
        rb.setSizePolicy(QSzPol.MinimumExpanding, QSzPol.Maximum)
        lab = QLabel('RB : ', wid)
        lab.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lay_rb = QHBoxLayout()
        lay_rb.addWidget(lab)
        lay_rb.addWidget(rb)
        pvname = self.get_pvname("BucketList-Mon")
        mn = BucketListLabel(wid, init_channel=pvname)
        mn.setStyleSheet(tm.format(self._min_size))
        mn.setSizePolicy(QSzPol.MinimumExpanding, QSzPol.Maximum)
        lab = QLabel('Mon: ', wid)
        lab.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lay_mn = QHBoxLayout()
        lay_mn.addWidget(lab)
        lay_mn.addWidget(mn)
        vlay = QVBoxLayout()
        vlay.setSpacing(1)
        vlay.addLayout(lay_sp)
        vlay.addLayout(lay_rb)
        vlay.addLayout(lay_mn)
        lay.addLayout(vlay, 0, 0)

        pvname = self.get_pvname("BucketListSyncStatus-Mon")
        rb = PyDMLed(wid, init_channel=pvname)
        rb.setOffColor(rb.Red)
        rb.setOnColor(rb.LightGreen)
        lab = QLabel('Sync', wid)
        lab.setStyleSheet("min-width:4em; max-height:1.15em;")
        lab.setAlignment(Qt.AlignCenter)
        vlay = QVBoxLayout()
        vlay.setSpacing(1)
        vlay.addWidget(lab)
        vlay.addWidget(rb)
        lay.addLayout(vlay, 0, 1)

        rb = SiriusLabel(
            wid, init_channel=self.get_pvname("BucketListLen-Mon"))
        rb.setStyleSheet("min-width:4em; max-height:1.15em;")
        rb.setAlignment(Qt.AlignCenter)
        lab = QLabel('Size', wid)
        lab.setStyleSheet("min-width:4em; max-height:1.15em;")
        lab.setAlignment(Qt.AlignCenter)
        vlay = QVBoxLayout()
        vlay.setSpacing(1)
        vlay.addWidget(lab)
        vlay.addWidget(rb)
        lay.addLayout(vlay, 0, 2)

        pvname = self.get_pvname("RepeatBucketList-SP")
        sp = SiriusSpinbox(wid, init_channel=pvname)
        pvname = self.get_pvname("RepeatBucketList-RB")
        rb = SiriusLabel(wid, init_channel=pvname)
        rb.setStyleSheet("min-width:4em; max-height:1.15em;")
        lab = QLabel('Repeat', wid, alignment=Qt.AlignCenter)
        hlay = QHBoxLayout()
        hlay.setSpacing(1)
        hlay.addWidget(sp)
        hlay.addWidget(rb)
        vlay = QVBoxLayout()
        vlay.setSpacing(1)
        vlay.addWidget(lab)
        vlay.addLayout(hlay)
        lay.addLayout(vlay, 0, 3)

        if self._show_graph:
            graph = BucketListGraph(self, self.device, self.prefix)
            lay.addWidget(graph, 1, 0, 1, 4)

    def _setup_bucket_list_fill(self):
        inj_prefix = _PVName('AS-Glob:AP-InjCtrl').substitute(
            prefix=self.prefix)

        wid = SiriusDialog(self)
        wid.setFocus(True)
        wid.setFocusPolicy(Qt.StrongFocus)
        wid.setObjectName('ASApp')

        self._sb_start = SiriusSpinbox(
            wid, inj_prefix.substitute(propty='BucketListStart-SP'))
        self._sb_start.setAlignment(Qt.AlignCenter)
        self._sb_start.setStyleSheet('max-width:5em;')
        self._lb_start = SiriusLabel(
            wid, inj_prefix.substitute(propty='BucketListStart-RB'))

        self._sb_stop = SiriusSpinbox(
            wid, inj_prefix.substitute(propty='BucketListStop-SP'))
        self._sb_stop.setAlignment(Qt.AlignCenter)
        self._sb_stop.setStyleSheet('max-width:5em;')
        self._lb_stop = SiriusLabel(
            wid, inj_prefix.substitute(propty='BucketListStop-RB'))

        self._sb_step = SiriusSpinbox(
            wid, inj_prefix.substitute(propty='BucketListStep-SP'))
        self._sb_step.setAlignment(Qt.AlignCenter)
        self._sb_step.setStyleSheet('max-width:5em;')
        self._lb_step = SiriusLabel(
            wid, inj_prefix.substitute(propty='BucketListStep-RB'))

        self._pb_ok = QPushButton('Ok', wid)
        self._pb_ok.clicked.connect(self._sb_start.send_value)
        self._pb_ok.clicked.connect(wid.accept)

        self._pb_cancel = QPushButton('Cancel', wid)
        self._pb_cancel.setDefault(True)
        self._pb_cancel.clicked.connect(wid.reject)

        lay_pbrow = QHBoxLayout()
        lay_pbrow.setContentsMargins(0, 0, 0, 0)
        lay_pbrow.addWidget(self._pb_cancel)
        lay_pbrow.addWidget(self._pb_ok)

        lay = QGridLayout(wid)
        lay.addWidget(QLabel('Start:', wid), 0, 0)
        lay.addWidget(self._sb_start, 0, 1)
        lay.addWidget(self._lb_start, 0, 2)
        lay.addWidget(QLabel('Stop:', wid), 1, 0)
        lay.addWidget(self._sb_stop, 1, 1)
        lay.addWidget(self._lb_stop, 1, 2)
        lay.addWidget(QLabel('Step:', wid), 2, 0)
        lay.addWidget(self._sb_step, 2, 1)
        lay.addWidget(self._lb_step, 2, 2)
        lay.addLayout(lay_pbrow, 3, 0, 1, 3)

        return wid


class EventList(BaseList):
    """Template for control of Events."""

    _MIN_WIDs = {
        'ext_trig': 4, 'mode': 6.6, 'delay_type': 4.2, 'delay': 5.2,
        'delayraw': 5.2, 'description': 9.7, 'code': 3.2, 'name': 4.8,
        }
    _LABELS = {
        'ext_trig': 'Trig.', 'mode': 'Mode', 'description': 'Description',
        'delay_type': 'Type', 'delay': 'Delay [us]', 'delayraw': 'Raw Delay',
        'code': 'Code', 'name': 'Name'}
    _ALL_PROPS = (
        'ext_trig', 'name', 'mode', 'delay_type', 'delay', 'delayraw',
        'description', 'code')

    def __init__(self, **kwargs):
        kwargs['props2search'] = set(
            ('name', 'mode', 'delay_type'))
        super().__init__(**kwargs)
        self.setObjectName('ASApp')

    def _createObjs(self, device, prop):
        sp = rb = None
        if prop == 'ext_trig':
            pvname = device.substitute(propty=device.propty+'ExtTrig-Cmd')
            sp = QWidget(self)
            but = PyDMPushButton(sp, init_channel=pvname, pressValue=1)
            but.setIcon(qta.icon('fa5s.step-forward'))
            but.setObjectName('but')
            but.setStyleSheet(
                '#but{min-width:40px; min-height:30px; icon-size:20px;}')
            but.setToolTip('Run event asynchronously')
            hbl = QHBoxLayout(sp)
            hbl.addWidget(but)
        elif prop == 'name':
            sp = QLabel(device.propty, self, alignment=Qt.AlignCenter)
        elif prop == 'mode':
            pvname = device.substitute(propty=device.propty+'Mode-Sel')
            sp = SiriusEnumComboBox(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'Mode-Sts')
            rb = SiriusLabel(self, init_channel=pvname)
        elif prop == 'delay_type':
            pvname = device.substitute(propty=device.propty+'DelayType-Sel')
            sp = SiriusEnumComboBox(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'DelayType-Sts')
            rb = SiriusLabel(self, init_channel=pvname)
        elif prop == 'delay':
            pvname = device.substitute(propty=device.propty+'Delay-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'Delay-RB')
            rb = SiriusLabel(self, init_channel=pvname)
        elif prop == 'delayraw':
            pvname = device.substitute(propty=device.propty+'DelayRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'DelayRaw-RB')
            rb = SiriusLabel(self, init_channel=pvname)
        elif prop == 'description':
            pvname = device.substitute(propty=device.propty+'Desc-SP')
            sp = PyDMLineEdit(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'Desc-RB')
            rb = SiriusLabel(self, init_channel=pvname)
        elif prop == 'code':
            pvname = device.substitute(propty=device.propty+'Code-Mon')
            sp = SiriusLabel(self, init_channel=pvname)
            sp.setAlignment(Qt.AlignCenter)
        if rb is None:
            return (sp, )
        return (sp, rb)


class ClockList(BaseList):
    """Template for control of Low Level Clocks."""

    _MIN_WIDs = {
        'name': 3.8,
        'frequency': 4.8,
        'mux_div': 6,
        'mux_enbl': 4.8,
        }
    _LABELS = {
        'name': 'Name',
        'frequency': 'Freq. [Hz]',
        'mux_div': 'Mux Divisor',
        'mux_enbl': 'Enabled',
        }
    _ALL_PROPS = ('name', 'mux_enbl', 'frequency', 'mux_div')

    def __init__(self, name=None, parent=None, prefix='',
                 props=set(), obj_names=list(), has_search=False):
        """Initialize object."""
        super().__init__(
            name=name, parent=parent, prefix=prefix, props=props,
            obj_names=obj_names, has_search=has_search,
            props2search={'name', 'mux_enbl'})
        self.setObjectName('ASApp')

    def _createObjs(self, device, prop):
        if prop == 'frequency':
            pvname = device.substitute(propty=device.propty+'Freq-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.limitsFromChannel = False
            sp.setMinimum(1)
            sp.setMaximum(2**31 - 1)
            pvname = device.substitute(propty=device.propty+'Freq-RB')
            rb = SiriusLabel(self, init_channel=pvname)
        elif prop == 'name':
            rb = QLabel(device.propty, self)
            rb.setAlignment(Qt.AlignCenter)
            return (rb, )
        elif prop == 'mux_enbl':
            pvname = device.substitute(propty=device.propty+'MuxEnbl-Sel')
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'MuxEnbl-Sts')
            rb = PyDMLed(self, init_channel=pvname)
        elif prop == 'mux_div':
            pvname = device.substitute(propty=device.propty+'MuxDiv-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'MuxDiv-RB')
            rb = SiriusLabel(self, init_channel=pvname)
        return sp, rb


# ###################### Event Distributors ######################
class FOUT(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, device='', prefix=''):
        """Initialize object."""
        super().__init__(parent, device, prefix)
        self._setupUi()
        self.setObjectName('ASApp')

    def _setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(15)

        self.my_layout.addWidget(self._setupmenus(), 0, 0)

        lab = QLabel('<h1>' + self.device.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        stattab = QTabWidget(self)
        stattab.setObjectName('ASTab')
        stattab.setStyleSheet("""
            QTabWidget::pane{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        self.status_wid = self._setup_status_wid()
        stattab.addTab(self.status_wid, 'Status')
        self.info_wid = self._setup_info_wid()
        stattab.addTab(self.info_wid, 'Fw && IOC')
        self.my_layout.addWidget(stattab, 2, 0)
        stattab.setSizePolicy(QSzPol.Preferred, QSzPol.Maximum)

    def _setupmenus(self):
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)

        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))

        try:
            mapping = LLTimeSearch.get_fout2trigsrc_mapping()
            downs = mapping[self.device.device_name]
            downs = sorted([(ou, dwn) for ou, dwn in downs.items()])
            menu = main_menu.addMenu('&Downlinks')
        except KeyError:
            downs = list()

        for out, dwn in downs:
            dev, down = dwn.dev, dwn.device_name
            devt = EVR if dev == 'EVR' else EVE if dev == 'EVE' else AFC
            action = menu.addAction(out + ' --> ' + down)
            Win = create_window_from_widget(devt, title=down, icon=icon)
            connect_window(action, Win, None, device=down, prefix=self.prefix)

        try:
            link = list(LLTimeSearch.In2OutMap[self.device.dev])[0]
            evg = LLTimeSearch.get_evg_channel(
                self.device.device_name.substitute(propty=link))
        except KeyError:
            return main_menu

        menu = main_menu.addMenu('&Uplink')
        action = menu.addAction(evg)
        Win = create_window_from_widget(EVG, title=evg.device_name, icon=icon)
        connect_window(
            action, Win, None, device=evg.device_name, prefix=self.prefix)

        return main_menu

    def _setup_status_wid(self):
        status_wid = QWidget(self)
        status_lay = QGridLayout(status_wid)
        status_lay.setHorizontalSpacing(30)
        status_lay.setVerticalSpacing(30)

        pvname = self.get_pvname(propty='DevEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='DevEnbl-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        gb = self._create_small_group(
            'Enabled', status_wid, (sp, rb), align_ver=False)
        status_lay.addWidget(gb, 0, 0)

        lb = QLabel("<b>Alive</b>")
        rb = SiriusLabel(
            self, init_channel=self.get_pvname(propty='Alive-Mon'))
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 1)

        lb = QLabel("<b>Network</b>")
        pvname = self.get_pvname(propty='Network-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 2)

        lb = QLabel("<b>UP Link</b>")
        pvname = self.get_pvname(propty='LinkStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 3)

        wids = list()
        try:
            mapping = LLTimeSearch.get_fout2trigsrc_mapping()
            conn = mapping[self.device.device_name]
            conn = {int(dev[-1]) for dev in conn}
        except KeyError:
            conn = set()
        for i in range(8):
            pvname = self.get_pvname(propty='Los-Mon')
            if i in conn:
                rb = SiriusLedAlert(self, init_channel=pvname, bit=i)
            else:
                rb = SiriusLedState(self, init_channel=pvname, bit=i)
                rb.onColor = rb.DarkGreen
                rb.offColor = rb.LightGreen
            wids.append(rb)
        but = QPushButton(self)
        but.setToolTip('Open Down Connections Details')
        but.setIcon(qta.icon('fa5s.ellipsis-v'))
        but.setObjectName('but')
        but.setDefault(False)
        but.setAutoDefault(False)
        but.setStyleSheet(
            '#but{min-width:15px; max-width:15px;\
            min-height:25px; max-height:25px;\
            icon-size:20px;}')
        but.clicked.connect(self._open_downconn_dialog)
        wids.append(but)
        gb = self._create_small_group(
            'Down Connection', status_wid, wids, align_ver=False)
        gb.layout().setContentsMargins(6, 6, 0, 6)
        status_lay.addWidget(gb, 1, 0, 1, 4)

        return status_wid

    def _setup_info_wid(self):
        info_wid = QWidget(self)
        info_lay = QGridLayout(info_wid)
        info_lay.setHorizontalSpacing(30)

        lb = QLabel("<b>IP</b>")
        pvname = self.get_pvname(propty='IPAddr-Mon')
        addr = SiriusLabel(self, init_channel=pvname)
        pvname = self.get_pvname(propty='IPPort-Mon')
        port = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, addr, port))
        info_lay.addWidget(gb, 0, 0, alignment=Qt.AlignTop)

        lb = QLabel("<b>DevFun</b>")
        pvname = self.get_pvname(propty='DevFun-Sts')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, rb))
        info_lay.addWidget(gb, 0, 1, alignment=Qt.AlignTop)

        lb = QLabel("<b>Device Status</b>")
        pvname = self.get_pvname(propty='DevStatus-Mon')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, rb))
        info_lay.addWidget(gb, 0, 2, alignment=Qt.AlignTop)

        lb = QLabel("<b>Download</b>")
        pvname = self.get_pvname('Download-Cmd')
        sp = SiriusPushButton(
            self, label='', icon=qta.icon('fa5s.download'),
            pressValue=1, releaseValue=0, init_channel=pvname)  # ?
        gb = self._create_small_group('', info_wid, (lb, sp))
        info_lay.addWidget(gb, 1, 0, alignment=Qt.AlignTop)

        lb = QLabel("<b>Save Settings</b>")
        pvname = self.get_pvname('Save-Cmd')
        sp = PyDMPushButton(
            self, label='Save', init_channel=pvname, pressValue=1)  # ?
        gb = self._create_small_group('', info_wid, (lb, sp))
        info_lay.addWidget(gb, 1, 1, alignment=Qt.AlignTop)

        lb = QLabel("<b>Fw.Version</b>")
        pvname = self.get_pvname(propty='FwVersion-Cte.SVAL')
        frmv = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, frmv))
        gb.layout().setSpacing(3)
        info_lay.addWidget(gb, 1, 2, alignment=Qt.AlignTop)

        return info_wid

    def _create_downconn_dialog(self):
        dialog = SiriusDialog()
        dialog.setObjectName('ASApp')
        dialog.setWindowTitle(self.device + ' Down Connections')
        dialog.setWindowIcon(self.windowIcon())

        lay = QVBoxLayout(dialog)
        obj_names = [
            self.device.substitute(idx=self.device.idx+'_'+str(i))
            for i in range(8)]
        downconn_wid = EVGFOUTOUTList(
            name='Down Connections', parent=self, prefix=self.prefix,
            obj_names=obj_names)
        lay.addWidget(downconn_wid)
        return dialog

    def _open_downconn_dialog(self):
        if not hasattr(self, 'downconn_wind'):
            self.downconn_wind = self._create_downconn_dialog()
            self.downconn_wind.show()
        else:
            self.downconn_wind.showNormal()


# ###################### Event Receivers ######################
class AFC(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, device='', prefix=''):
        """Initialize object."""
        super().__init__(parent, device, prefix)
        self._setupUi()
        self.setObjectName('ASApp')

    def _setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)

        # menu
        self.my_layout.addWidget(self._setupmenus(), 0, 0)

        # title
        lab = QLabel('<h1>' + self.device.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        # status
        stattab = QTabWidget(self)
        stattab.setObjectName('ASTab')
        stattab.setStyleSheet("""
            QTabWidget::pane{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        self.status_wid = self._setup_status_wid()
        stattab.addTab(self.status_wid, 'Status')
        self.info_wid = self._setup_info_wid()
        stattab.addTab(self.info_wid, 'Fw && IOC')
        self.my_layout.addWidget(stattab, 2, 0)
        stattab.setSizePolicy(QSzPol.Preferred, QSzPol.Maximum)

        # frequency feedback
        self.freqff_wid = QGroupBox('Frequency feedback', self)
        freqtab = QTabWidget(self)
        freqtab.setObjectName('ASTab')
        afcfrefb_wid = self._setup_freqfb_wid('AFC')
        freqtab.addTab(afcfrefb_wid, 'AFC')
        rtmfreqfb_wid = self._setup_freqfb_wid('RTM')
        freqtab.addTab(rtmfreqfb_wid, 'RTM')
        freqff_lay = QVBoxLayout(self.freqff_wid)
        freqff_lay.setContentsMargins(0, 6, 0, 0)
        freqff_lay.addWidget(freqtab)
        self.my_layout.addWidget(self.freqff_wid, 3, 0)
        self.freqff_wid.setSizePolicy(QSzPol.Preferred, QSzPol.Maximum)

        # output tabs
        outtab = QTabWidget(self)
        outtab.setObjectName('ASTab')
        self.my_layout.addWidget(outtab, 4, 0)

        props = {
            'name', 'state', 'event', 'source', 'width', 'polarity', 'pulses',
            'delay', 'timestamp'}
        set_ = LLTimeSearch.In2OutMap['AMCFPGAEVR']['SFP8']

        obj_names = sorted([out for out in set_ if out.startswith('FMC')])
        obj_names = [self.device.substitute(propty_name=o) for o in obj_names]
        self.fmcs_wid = AFCOUTList(
            name='', parent=self, props=props,
            prefix=self.prefix, obj_names=obj_names)
        self.fmcs_wid.setObjectName('fmcs_wid')
        outtab.addTab(self.fmcs_wid, 'FMC Outputs')

        obj_names = sorted([out for out in set_ if out.startswith('CRT')])
        obj_names = [self.device.substitute(propty_name=o) for o in obj_names]
        self.crts_wid = AFCOUTList(
            name='', parent=self, props=props,
            prefix=self.prefix, obj_names=obj_names)
        self.crts_wid.setObjectName('crts_wid')
        outtab.addTab(self.crts_wid, 'CRT Outputs')

    def _setupmenus(self):
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)

        try:
            fout = LLTimeSearch.get_fout_channel(
                self.device.substitute(propty='CRT0'))
        except KeyError:
            return main_menu

        menu = main_menu.addMenu('&Uplink')
        action = menu.addAction(fout)
        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        Win = create_window_from_widget(
            FOUT, title=fout.device_name, icon=icon)
        connect_window(
            action, Win, None, device=fout.device_name, prefix=self.prefix)
        return main_menu

    def _setup_status_wid(self):
        status_wid = QWidget(self)
        status_lay = QGridLayout(status_wid)
        status_lay.setHorizontalSpacing(30)

        pvname = self.get_pvname('DevEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname('DevEnbl-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        gb = self._create_small_group(
            'Enabled', status_wid, (sp, rb), align_ver=False)
        status_lay.addWidget(gb, 0, 0)

        lb = QLabel("<b>Alive</b>")
        pvname = self.get_pvname('Alive-Mon')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 1)

        for i, locktype in enumerate(['', 'Ltc']):
            lb = QLabel(
                '<b>Locked' + (' Latch' if locktype else '') + '</b>')
            widlbl = QWidget()
            hbxlbl = QHBoxLayout(widlbl)
            hbxlbl.setSpacing(10)
            hbxlbl.setContentsMargins(0, 0, 0, 0)
            hbxlbl.setAlignment(Qt.AlignLeft)
            widctl = QWidget()
            hbxctl = QHBoxLayout(widctl)
            hbxctl.setSpacing(1)
            hbxctl.setContentsMargins(0, 0, 0, 0)
            for dev in ['AFC', 'RTM', 'GT0']:
                pvname = self.get_pvname(f'{dev}ClkLocked{locktype}-Mon')
                rb = SiriusLedAlert(self, init_channel=pvname)
                rb.offColor, rb.onColor = rb.onColor, rb.offColor
                hbxctl.addWidget(rb)
                hbxlbl.addWidget(QLabel(dev, self))

            if locktype == 'Ltc':
                rst = SiriusPushButton(
                    self, label='', icon=qta.icon('fa5s.sync'), pressValue=1,
                    init_channel=self.get_pvname('ClkLockedLtcRst-Cmd'))
                hbxctl.addWidget(rst)
                hbxlbl.addWidget(QLabel('   ', self))

            gb = self._create_small_group('', status_wid, (lb, widctl, widlbl))
            status_lay.addWidget(gb, 0, 2+i)

        lb = QLabel("<b>UP Link</b>")
        pvname = self.get_pvname('LinkStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        rb.offColor, rb.onColor = rb.onColor, rb.offColor
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 4)

        return status_wid

    def _setup_info_wid(self):
        info_wid = QWidget(self)
        info_lay = QGridLayout(info_wid)
        info_lay.setHorizontalSpacing(30)

        lb = QLabel("<b>FPGA Clk</b>")
        pvname = self.get_pvname('FPGAClk-Cte')
        mon = SiriusLabel(self, init_channel=pvname)
        mon.showUnits = True
        mon.precisionFromPV = False
        mon.precision = 3
        pvname = self.get_pvname('FPGAClk-Cte', field='DOL')
        dol = PyDMLineEdit(self, init_channel=pvname)
        omsl = SiriusPushButton(
            self, label='', icon=qta.icon('fa5s.sync'), pressValue=1,
            init_channel=self.get_pvname('FPGAClk-Cte', field='OMSL'))
        proc = QWidget()
        hlproc = QHBoxLayout(proc)
        hlproc.setContentsMargins(0, 0, 0, 0)
        hlproc.addWidget(dol)
        hlproc.addWidget(omsl)
        gb = self._create_small_group('', info_wid, (lb, mon, proc))
        info_lay.addWidget(gb, 0, 0)

        return info_wid

    def _setup_freqfb_wid(self, subdev):
        gbox = QWidget(self)

        # Controls
        ld_phskp = QLabel('<b>Phase KP</b>', self, alignment=Qt.AlignCenter)
        sb_phskp = SiriusSpinbox(
            self, self.get_pvname(propty=subdev+'PhasePropGain-SP'))
        sb_phskp.limitsFromChannel = False
        sb_phskp.setMinimum(-2**31)
        sb_phskp.setMaximum(2**31-1)
        lb_phskp = SiriusLabel(
            self, self.get_pvname(propty=subdev+'PhasePropGain-RB'))

        ld_phski = QLabel('<b>Phase KI</b>', self, alignment=Qt.AlignCenter)
        sb_phski = SiriusSpinbox(
            self, self.get_pvname(propty=subdev+'PhaseIntgGain-SP'))
        sb_phski.limitsFromChannel = False
        sb_phski.setMinimum(-2**31)
        sb_phski.setMaximum(2**31-1)
        lb_phski = SiriusLabel(
            self, self.get_pvname(propty=subdev+'PhaseIntgGain-RB'))

        ld_frqkp = QLabel('<b>Freq. KP</b>', self, alignment=Qt.AlignCenter)
        sb_frqkp = SiriusSpinbox(
            self, self.get_pvname(propty=subdev+'FreqPropGain-SP'))
        sb_frqkp.limitsFromChannel = False
        sb_frqkp.setMinimum(-2**31)
        sb_frqkp.setMaximum(2**31-1)
        lb_frqkp = SiriusLabel(
            self, self.get_pvname(propty=subdev+'FreqPropGain-RB'))

        ld_frqki = QLabel('<b>Freq. KI</b>', self, alignment=Qt.AlignCenter)
        sb_frqki = SiriusSpinbox(
            self, self.get_pvname(propty=subdev+'FreqIntgGain-SP'))
        sb_frqki.limitsFromChannel = False
        sb_frqki.setMinimum(-2**31)
        sb_frqki.setMaximum(2**31-1)
        lb_frqki = SiriusLabel(
            self, self.get_pvname(propty=subdev+'FreqIntgGain-RB'))

        ld_phnvg = QLabel('<b>Phs.Navg</b>', self, alignment=Qt.AlignCenter)
        sb_phnvg = SiriusSpinbox(
            self, self.get_pvname(propty=subdev+'PhaseNavg-SP'))
        sb_phnvg.limitsFromChannel = False
        sb_phnvg.setMinimum(-2**31)
        sb_phnvg.setMaximum(2**31-1)
        lb_phnvg = SiriusLabel(
            self, self.get_pvname(propty=subdev+'PhaseNavg-RB'))

        ld_phdiv = QLabel(
            '<b>Phs.Div 2<sup>n</sup></b>', self, alignment=Qt.AlignCenter)
        sb_phdiv = SiriusSpinbox(
            self, self.get_pvname(propty=subdev+'PhaseDiv-SP'))
        sb_phdiv.limitsFromChannel = False
        sb_phdiv.setMinimum(-2**31)
        sb_phdiv.setMaximum(2**31-1)
        lb_phdiv = SiriusLabel(
            self, self.get_pvname(propty=subdev+'PhaseDiv-RB'))

        ld_rfrlo = QLabel('<b>RFreqLo</b>', self, alignment=Qt.AlignCenter)
        lb_rfrlo = SiriusLabel(
            self, self.get_pvname(propty=subdev+'RFreqLo-Mon'))
        lb_rfrlo.displayFormat = SiriusLabel.DisplayFormat.Hex

        ld_rfrhi = QLabel('<b>RFreqHi</b>', self, alignment=Qt.AlignCenter)
        lb_rfrhi = SiriusLabel(
            self, self.get_pvname(propty=subdev+'RFreqHi-Mon'))
        lb_rfrhi.displayFormat = SiriusLabel.DisplayFormat.Hex

        ld_n1 = QLabel('<b>N1</b>', self, alignment=Qt.AlignCenter)
        ld_n1.setObjectName('n1')
        lb_n1 = SiriusLabel(
            self, self.get_pvname(propty=subdev+'N1-Mon'))
        lb_n1.setObjectName('n1')
        lb_n1.displayFormat = SiriusLabel.DisplayFormat.Hex

        ld_hsdiv = QLabel('<b>HSDiv</b>', self, alignment=Qt.AlignCenter)
        lb_hsdiv = SiriusLabel(
            self, self.get_pvname(propty=subdev+'HSDiv-Mon'))

        # Equation
        ld_fpgaclk = QLabel('(FPGA Clk) x ', self, alignment=Qt.AlignRight)
        ld_fpgaclk.setObjectName('fpgaclk')
        ld_fraqdiv = QLabel('------ = ', self, alignment=Qt.AlignCenter)
        lb_freqmult = PyDMLineEdit(
            self, self.get_pvname(propty=subdev+'FreqMult-Cte'))
        lb_freqmult.setObjectName('frac')
        lb_freqdiv = PyDMLineEdit(
            self, self.get_pvname(propty=subdev+'FreqDiv-Cte'))
        lb_freqdiv.setObjectName('frac')
        ld_freqdsc = QLabel('<b>Frequency</b>', self, alignment=Qt.AlignCenter)
        ld_freqdsc.setObjectName('freq')
        ld_freqsp = PyDMLineEdit(
            self, self.get_pvname(propty=subdev+'Freq-SP'))
        ld_freqsp.setObjectName('freq')
        ld_freqrb = SiriusLabel(
            self, self.get_pvname(propty=subdev+'Freq-RB'), keep_unit=True)
        ld_freqrb.setObjectName('freq')
        ld_freqrb.showUnits = True

        lay_sett1 = QGridLayout()
        lay_sett1.setHorizontalSpacing(30)
        lay_sett1.setVerticalSpacing(6)
        lay_sett1.addWidget(ld_phskp, 0, 0)
        lay_sett1.addWidget(sb_phskp, 1, 0, alignment=Qt.AlignCenter)
        lay_sett1.addWidget(lb_phskp, 2, 0)
        lay_sett1.addWidget(ld_phski, 0, 1)
        lay_sett1.addWidget(sb_phski, 1, 1, alignment=Qt.AlignCenter)
        lay_sett1.addWidget(lb_phski, 2, 1)
        lay_sett1.addWidget(ld_frqkp, 0, 2)
        lay_sett1.addWidget(sb_frqkp, 1, 2, alignment=Qt.AlignCenter)
        lay_sett1.addWidget(lb_frqkp, 2, 2)
        lay_sett1.addWidget(ld_frqki, 0, 3)
        lay_sett1.addWidget(sb_frqki, 1, 3, alignment=Qt.AlignCenter)
        lay_sett1.addWidget(lb_frqki, 2, 3)
        lay_sett1.addWidget(ld_phnvg, 0, 4)
        lay_sett1.addWidget(sb_phnvg, 1, 4, alignment=Qt.AlignCenter)
        lay_sett1.addWidget(lb_phnvg, 2, 4)
        lay_sett1.addWidget(ld_phdiv, 0, 5)
        lay_sett1.addWidget(sb_phdiv, 1, 5, alignment=Qt.AlignCenter)
        lay_sett1.addWidget(lb_phdiv, 2, 5)

        lay_sett2 = QGridLayout()
        lay_sett2.setHorizontalSpacing(30)
        lay_sett2.addWidget(ld_rfrlo, 0, 0)
        lay_sett2.addWidget(lb_rfrlo, 1, 0)
        lay_sett2.addWidget(ld_rfrhi, 0, 1)
        lay_sett2.addWidget(lb_rfrhi, 1, 1)
        lay_sett2.addWidget(ld_n1, 0, 2)
        lay_sett2.addWidget(lb_n1, 1, 2)
        lay_sett2.addWidget(ld_hsdiv, 0, 3)
        lay_sett2.addWidget(lb_hsdiv, 1, 3)

        lay_eq = QGridLayout()
        lay_eq.setHorizontalSpacing(12)
        lay_eq.setVerticalSpacing(6)
        lay_eq.addWidget(ld_fpgaclk, 1, 0)
        lay_eq.addWidget(lb_freqmult, 0, 1)
        lay_eq.addWidget(ld_fraqdiv, 1, 1)
        lay_eq.addWidget(lb_freqdiv, 2, 1)
        lay_eq.addWidget(ld_freqdsc, 0, 2)
        lay_eq.addWidget(ld_freqsp, 1, 2)
        lay_eq.addWidget(ld_freqrb, 2, 2)

        lay = QGridLayout(gbox)
        lay.setHorizontalSpacing(30)
        lay.setVerticalSpacing(15)
        lay.addLayout(lay_sett1, 0, 0, 1, 2, alignment=Qt.AlignLeft)
        lay.addLayout(lay_sett2, 1, 0, alignment=Qt.AlignLeft)
        lay.addLayout(lay_eq, 1, 1, alignment=Qt.AlignRight)

        gbox.setStyleSheet("""
            .SiriusSpinbox{max-width: 4.5em;}
            QComboBox, #n1 {max-width: 2.7em;}
            #frac {max-width: 1.5em;}
            #freq, #fpgaclk {max-width: 6.5em;}
            SiriusLabel{qproperty-alignment: AlignCenter;}
        """)

        return gbox


class _EVR_EVE(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, device='', prefix=''):
        """Initialize object."""
        super().__init__(parent, device, prefix)
        self.device_type = _PVName(device).dev
        self.setupUi()
        self.setObjectName('ASApp')

    def setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)

        self.my_layout.addWidget(self.setupmenus(), 0, 0)

        lab = QLabel('<h1>' + self.device.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        # status
        stattab = QTabWidget(self)
        stattab.setObjectName('ASTab')
        stattab.setStyleSheet("""
            QTabWidget::pane{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        self.status_wid = self._setup_status_wid()
        stattab.addTab(self.status_wid, 'Status')
        self.info_wid = self._setup_info_wid()
        stattab.addTab(self.info_wid, 'Fw && IOC')
        self.my_layout.addWidget(stattab, 2, 0)
        stattab.setSizePolicy(QSzPol.Preferred, QSzPol.Maximum)

        # outputs
        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.setHandleWidth(20)
        self.my_layout.addWidget(splitter, 3, 0)

        props = {
            'name', 'state', 'event', 'widthraw', 'polarity', 'pulses',
            'delayraw', 'timestamp'}
        obj_names = ['OTP{0:02d}'.format(i) for i in range(24)]
        obj_names = [self.device.substitute(propty=o) for o in obj_names]
        self.otps_wid = EVREVEOTPList(
            name='Internal Trigger (OTP)', parent=self, prefix=self.prefix,
            props=props, obj_names=obj_names)
        self.otps_wid.setObjectName('otps_wid')
        splitter.addWidget(self.otps_wid)

        props = {
            'name', 'source', 'trigger', 'rf_delayraw', 'rf_delay_type',
            'fine_delayraw'}
        obj_names = ['OUT{0:d}'.format(i) for i in range(8)]
        obj_names = [self.device.substitute(propty=o) for o in obj_names]
        self.outs_wid = EVREVEOUTList(
            name='OUT', parent=self, prefix=self.prefix,
            props=props, obj_names=obj_names)
        self.outs_wid.setObjectName('outs_wid')
        splitter.addWidget(self.outs_wid)

        splitter.setSizePolicy(QSzPol.Preferred, QSzPol.MinimumExpanding)

    def setupmenus(self):
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)

        try:
            fout = LLTimeSearch.get_fout_channel(
                self.device.substitute(propty='OTP0'))
        except KeyError:
            return main_menu

        menu = main_menu.addMenu('&Uplink')
        action = menu.addAction(fout)
        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        Win = create_window_from_widget(
            FOUT, title=fout.device_name, icon=icon)
        connect_window(
            action, Win, None, device=fout.device_name, prefix=self.prefix)
        return main_menu

    def _setup_status_wid(self):
        status_wid = QWidget(self)
        status_lay = QGridLayout(status_wid)
        status_lay.setVerticalSpacing(30)

        pvname = self.get_pvname('DevEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname('DevEnbl-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        gb = self._create_small_group(
            'Enabled', status_wid, (sp, rb), align_ver=False)
        status_lay.addWidget(gb, 0, 0)

        lb = QLabel("<b>Alive</b>")
        pvname = self.get_pvname('Alive-Mon')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 1)

        lb = QLabel("<b>Network</b>")
        pvname = self.get_pvname('Network-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        rb.offColor, rb.onColor = rb.onColor, rb.offColor
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 2)

        lb = QLabel("<b>UP Link</b>")
        pvname = self.get_pvname('LinkStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 3)

        lb = QLabel("<b>Interlock Status</b>")
        pvname = self.get_pvname('IntlkStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 4)

        lb = QLabel("<b>Interlock Enabled</b>")
        pvname = self.get_pvname('IntlkEnbl-Mon')
        rb = SiriusLedState(self, init_channel=pvname)
        gb = self._create_small_group('', status_wid, (lb, rb))
        status_lay.addWidget(gb, 0, 5)

        if self.device_type == 'EVR':
            wids = list()
            try:
                conn = LLTimeSearch.get_connections_from_evg()
                conn = {
                    dev.propty for dev in conn
                    if dev.device_name == self.device.device_name}
                conn = {int(p[-1]) for p in conn if p.startswith('OUT')}
            except KeyError:
                conn = set()
            for i in range(8):
                pvname = self.get_pvname('Los-Mon')
                if i in conn:
                    rb = SiriusLedAlert(self, init_channel=pvname, bit=i)
                else:
                    rb = SiriusLedState(self, init_channel=pvname, bit=i)
                    rb.onColor = rb.DarkGreen
                    rb.offColor = rb.LightGreen
                wids.append(rb)
            gb = self._create_small_group(
                'Down Connection', status_wid, wids, align_ver=False)
        else:
            sp = SiriusEnumComboBox(
                self, init_channel=self.get_pvname('RFOut-Sel'))
            rb = SiriusLabel(self, init_channel=self.get_pvname('RFOut-Sts'))
            gb = self._create_small_group('RF Output', status_wid, (sp, rb))
        status_lay.addWidget(gb, 0, 6)

        but = QPushButton(self)
        but.setToolTip('Open Timestamp, Log and\nDigital Input Controls')
        but.setIcon(qta.icon('fa5s.ellipsis-v'))
        but.setDefault(False)
        but.setAutoDefault(False)
        but.setObjectName('but')
        but.setStyleSheet(
            '#but{min-width:25px; max-width:25px;\
            min-height:25px; max-height:25px;\
            icon-size:20px;}')
        but.clicked.connect(self._open_detail_dialog)
        status_lay.addWidget(but, 0, 7, alignment=Qt.AlignTop)

        return status_wid

    def _setup_info_wid(self):
        info_wid = QWidget(self)
        info_lay = QGridLayout(info_wid)
        info_lay.setHorizontalSpacing(15)

        lb = QLabel("<b>IP</b>")
        pvname = self.get_pvname(propty='IPAddr-Mon')
        addr = SiriusLabel(self, init_channel=pvname)
        pvname = self.get_pvname(propty='IPPort-Mon')
        port = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, addr, port))
        info_lay.addWidget(gb, 0, 0, alignment=Qt.AlignTop)

        lb = QLabel("<b>DevFun</b>")
        pvname = self.get_pvname(propty='DevFun-Sel')
        sp = SiriusEnumComboBox(self, init_channel=pvname)
        pvname = self.get_pvname(propty='DevFun-Sts')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, sp, rb))
        info_lay.addWidget(gb, 0, 1, alignment=Qt.AlignTop)

        lb = QLabel("<b>Device Status</b>")
        pvname = self.get_pvname(propty='DevStatus-Mon')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, rb))
        info_lay.addWidget(gb, 0, 2, alignment=Qt.AlignTop)

        lb = QLabel("<b>Download</b>")
        pvname = self.get_pvname('Download-Cmd')
        sp = SiriusPushButton(
            self, label='', icon=qta.icon('fa5s.download'),
            pressValue=1, releaseValue=0, init_channel=pvname)  # ?
        gb = self._create_small_group('', info_wid, (lb, sp))
        info_lay.addWidget(gb, 0, 3, alignment=Qt.AlignTop)

        lb = QLabel("<b>Save Settings</b>")
        pvname = self.get_pvname('Save-Cmd')
        sp = PyDMPushButton(
            self, label='Save', init_channel=pvname, pressValue=1)
        gb = self._create_small_group('', info_wid, (lb, sp))
        info_lay.addWidget(gb, 0, 4, alignment=Qt.AlignTop)

        # if self.device_type == 'EVE':
        lb = QLabel("<b>Clk Mode</b>")
        pvname = self.get_pvname(propty='ClkMode-RB')
        rb = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, rb))
        info_lay.addWidget(gb, 0, 5, alignment=Qt.AlignTop)

        lb = QLabel("<b>FPGA Clk</b>")
        pvname = self.get_pvname('FPGAClk-Cte')
        mon = SiriusLabel(self, init_channel=pvname)
        mon.showUnits = True
        pvname = self.get_pvname('FPGAClk-Cte', field='INP')
        inp = PyDMLineEdit(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, mon, inp))
        info_lay.addWidget(gb, 0, 6, alignment=Qt.AlignTop)

        lb = QLabel("<b>Fw.Version</b>")
        pvname = self.get_pvname(propty='FwVersion-Cte.SVAL')
        frmv = SiriusLabel(self, init_channel=pvname)
        gb = self._create_small_group('', info_wid, (lb, frmv))
        gb.layout().setSpacing(3)
        info_lay.addWidget(gb, 0, 7, alignment=Qt.AlignTop)

        return info_wid

    def _create_detail_dialog(self):
        dialog = SiriusDialog()
        dialog.setObjectName('ASApp')
        dialog.setWindowTitle(self.device + ' Timestamp and Log Control')
        dialog.setWindowIcon(self.windowIcon())

        # Timestamp
        gbox_tim = QGroupBox('Timestamp', self)

        ld_timsrc = QLabel('<b>Source</b>', self)
        self.ec_timsrc = SiriusEnumComboBox(
            self, self.get_pvname('TimestampSrc-Sel'))
        self.lb_timsrc = SiriusLabel(self, self.get_pvname('TimestampSrc-Sts'))
        gb_timsrc = self._create_small_group(
            '', gbox_tim, (ld_timsrc, self.ec_timsrc, self.lb_timsrc))

        fr_tim = QFrame()
        fr_tim.setStyleSheet('.QFrame{border: 1px solid gray;}')
        ld_timutc = QLabel('<b>UTC</b>', self)
        self.lb_timutc = SiriusLabel(self, self.get_pvname('UTC-RB'))
        self.lb_timutc.showUnits = True
        ld_timsub = QLabel('<b>Subsec</b>')
        self.lb_timsub = SiriusLabel(self, self.get_pvname('SubSecond-Mon'))
        self.lb_timsub.showUnits = True
        lay_tim = QGridLayout(fr_tim)
        lay_tim.setAlignment(Qt.AlignVCenter)
        lay_tim.setContentsMargins(0, 0, 0, 0)
        lay_tim.addWidget(ld_timutc, 0, 0, alignment=Qt.AlignCenter)
        lay_tim.addWidget(self.lb_timutc, 1, 0, alignment=Qt.AlignCenter)
        lay_tim.addWidget(ld_timsub, 0, 1, alignment=Qt.AlignCenter)
        lay_tim.addWidget(self.lb_timsub, 1, 1, alignment=Qt.AlignCenter)

        lay_tstamp = QGridLayout(gbox_tim)
        lay_tstamp.addWidget(gb_timsrc, 0, 0)
        lay_tstamp.addWidget(fr_tim, 0, 1)

        # Timestamp Log
        gbox_log = QGroupBox('Timestamp Log', self)

        ld_logstp = QLabel('<b>Stop Log</b>', self)
        self.sb_logstp = PyDMStateButton(self, self.get_pvname('stoplog'))
        self.led_logstp = SiriusLedState(self, self.get_pvname('STOPLOGRBV'))
        gb_logstp = self._create_small_group(
            '', gbox_log, (ld_logstp, self.sb_logstp, self.led_logstp))

        ld_logrst = QLabel('<b>Reset Log</b>', self)
        self.sb_logrst = PyDMStateButton(self, self.get_pvname('rstlog'))
        self.led_logrst = SiriusLedState(self, self.get_pvname('RSTLOGRBV'))
        gb_logrst = self._create_small_group(
            '', gbox_log, (ld_logrst, self.sb_logrst, self.led_logrst))

        ld_logpul = QLabel('<b>Pull</b>', self)
        self.bt_logpul = SiriusPushButton(
            parent=self, init_channel=self.get_pvname('pull'),
            pressValue=1, releaseValue=0)  # ?
        self.bt_logpul.setIcon(qta.icon('fa5s.arrow-down'))
        self.bt_logpul.setObjectName('bt')
        self.bt_logpul.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;}')
        gb_logpul = self._create_small_group(
            '', gbox_log, (ld_logpul, self.bt_logpul))

        ld_logcnt = QLabel('<b>Log Count</b>', self, alignment=Qt.AlignCenter)
        self.lb_logcnt = SiriusLabel(self, self.get_pvname('LOGCOUNT'))
        self.lb_logcnt.showUnits = True
        self.lb_logcnt.setAlignment(Qt.AlignCenter)
        ld_logful = QLabel('Full', self)
        self.led_logful = SiriusLedState(self, self.get_pvname('FULL'))
        ld_logemp = QLabel('Empty', self)
        self.led_logemp = SiriusLedState(self, self.get_pvname('EMPTY'))
        fr_logcnt = QFrame(gbox_log)
        fr_logcnt.setStyleSheet('.QFrame{border: 1px solid gray;}')
        lay_logcnt = QGridLayout(fr_logcnt)
        lay_logcnt.setAlignment(Qt.AlignCenter)
        lay_logcnt.setContentsMargins(0, 0, 0, 0)
        lay_logcnt.addWidget(ld_logcnt, 0, 0, 1, 4)
        lay_logcnt.addWidget(self.lb_logcnt, 1, 0, 1, 4)
        lay_logcnt.addWidget(ld_logful, 2, 0, alignment=Qt.AlignRight)
        lay_logcnt.addWidget(self.led_logful, 2, 1, alignment=Qt.AlignTop)
        lay_logcnt.addWidget(ld_logemp, 2, 2, alignment=Qt.AlignRight)
        lay_logcnt.addWidget(self.led_logemp, 2, 3, alignment=Qt.AlignTop)

        ld_logevt = QLabel('<b>Event</b>', self)
        self.lb_logevt = SiriusLabel(self, self.get_pvname('LOGEVENT'))
        gb_logevt = self._create_small_group(
            '', gbox_log, (ld_logevt, self.lb_logevt))

        ld_logutc = QLabel('<b>Log UTC</b>', self)
        self.lb_logutc = SiriusLabel(self, self.get_pvname('LOGUTC'))
        self.lb_logutc.showUnits = True
        gb_logutc = self._create_small_group(
            '', gbox_log, (ld_logutc, self.lb_logutc))

        ld_logsub = QLabel('<b>Log Subsec</b>', self)
        self.lb_logsub = SiriusLabel(self, self.get_pvname('LOGSUBSEC'))
        self.lb_logsub.showUnits = True
        gb_logsub = self._create_small_group(
            '', gbox_log, (ld_logsub, self.lb_logsub))

        lay_log = QGridLayout(gbox_log)
        lay_log.addWidget(gb_logstp, 0, 0, alignment=Qt.AlignTop)
        lay_log.addWidget(gb_logrst, 0, 1, alignment=Qt.AlignTop)
        lay_log.addWidget(gb_logpul, 0, 2, alignment=Qt.AlignTop)
        lay_log.addWidget(gb_logevt, 1, 0, alignment=Qt.AlignTop)
        lay_log.addWidget(gb_logutc, 1, 1, alignment=Qt.AlignTop)
        lay_log.addWidget(gb_logsub, 1, 2, alignment=Qt.AlignTop)
        lay_log.addWidget(fr_logcnt, 0, 3, 2, 1, alignment=Qt.AlignCenter)

        # Timestamp Log Buffer
        gbox_buf = QGroupBox('Timestamp Log Buffer', self)

        ld_bufcnt = QLabel('<b>Log Count</b>', self)
        self.lb_bufcnt = SiriusLabel(self, self.get_pvname('LOGSOFTCNT'))
        self.lb_bufcnt.showUnits = True
        gb_bufcnt = self._create_small_group(
            '', gbox_buf, (ld_bufcnt, self.lb_bufcnt))

        ld_bufrst = QLabel('<b>Reset</b>', self)
        self.bt_bufrst = SiriusPushButton(
            parent=self, init_channel=self.get_pvname('rstSoftBuff'),
            pressValue=1, releaseValue=0)  # ?
        self.bt_bufrst.setIcon(qta.icon('fa5s.sync'))
        self.bt_bufrst.setObjectName('bt')
        self.bt_bufrst.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;}')
        gb_bufrst = self._create_small_group(
            '', gbox_buf, (ld_bufrst, self.bt_bufrst))

        ld_bufutc = QLabel('<b>UTC buffer</b>', self)
        self.tb_bufutc = self._create_logbuffer_table('UTCbuffer')
        gb_bufutc = self._create_small_group(
            '', gbox_buf, (ld_bufutc, self.tb_bufutc))

        ld_bufsub = QLabel('<b>Subsec buffer</b>', self)
        self.tb_bufsub = self._create_logbuffer_table('SUBSECbuffer')
        gb_bufsub = self._create_small_group(
            '', gbox_buf, (ld_bufsub, self.tb_bufsub))

        ld_bufevt = QLabel('<b>Event buffer</b>', self)
        self.tb_bufevt = self._create_logbuffer_table('EVENTbuffer')
        gb_bufevt = self._create_small_group(
            '', gbox_buf, (ld_bufevt, self.tb_bufevt))

        lay_logbuf = QGridLayout(gbox_buf)
        lay_logbuf.addWidget(gb_bufcnt, 0, 0, 1, 3)
        lay_logbuf.addWidget(gb_bufrst, 0, 3, 1, 3)
        lay_logbuf.addWidget(gb_bufutc, 1, 0, 1, 2)
        lay_logbuf.addWidget(gb_bufsub, 1, 2, 1, 2)
        lay_logbuf.addWidget(gb_bufevt, 1, 4, 1, 2)

        wid_timlog = QWidget()
        lay_timlog = QVBoxLayout(wid_timlog)
        lay_timlog.addWidget(gbox_tim)
        lay_timlog.addWidget(gbox_log)
        lay_timlog.addWidget(gbox_buf)

        # Digital Inputs
        obj_names = [self.device.substitute(idx=str(i)) for i in range(3)]
        self.dis_wid = EVREVEDIList(
            name='', parent=self, prefix=self.prefix, obj_names=obj_names)
        self.dis_wid.setObjectName('dis_wid')

        # tab and layout
        tab = QTabWidget()
        tab.setObjectName('ASTab')
        tab.addTab(wid_timlog, 'Timestamp && Log')
        tab.addTab(self.dis_wid, 'Digital Inputs (DI)')

        lay = QVBoxLayout(dialog)
        lay.addWidget(tab)

        return dialog

    def _create_logbuffer_table(self, prop):
        table = SiriusWaveformTable(self, self.get_pvname(prop))
        table.setObjectName('tb')
        table.setEnabled(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        table.horizontalHeader().setVisible(False)
        table.setStyleSheet(
            '#tb{min-width:6em; max-width:12em; max-height: 16em;}')
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setColumnCount(1)
        table.setSizePolicy(QSzPol.MinimumExpanding, QSzPol.Preferred)
        return table

    def _open_detail_dialog(self):
        if not hasattr(self, 'detail_wind'):
            self.detail_wind = self._create_detail_dialog()
            self.detail_wind.show()
        else:
            self.detail_wind.showNormal()


class EVR(_EVR_EVE):

    def __init__(self, parent=None, device='', prefix=''):
        if 'EVR' not in device:
            raise ValueError('device has to be an EVR')
        super().__init__(parent, device, prefix)


class EVE(_EVR_EVE):

    def __init__(self, parent=None, device='', prefix=''):
        if 'EVE' not in device:
            raise ValueError('device has to be an EVE')
        super().__init__(parent, device, prefix)


# ###################### EVG & FOUT OUT ######################

class EVGFOUTOUTList(BaseList):
    """Template for control of Timing devices Internal Triggers."""

    _MIN_WIDs = {
        'name': 3,
        'connected': 8,
        'tripdelay': 4.8,
        'position': 4.8,
        'outdelay': 4.8,
        'rxenbl': 4,
        'connection': 12,
    }
    _LABELS = {
        'name': 'Name',
        'connected': 'Connected',
        'tripdelay': 'TripDelay',
        'position': 'Position',
        'outdelay': 'OutDelay',
        'rxenbl': 'RX Enbl',
        'connection': 'Connection',
    }
    _ALL_PROPS = ('name', 'connected', 'tripdelay', 'position',
                  'outdelay', 'rxenbl', 'connection')

    def __init__(self, **kwargs):
        srch = set(('name', 'connection'))
        kwargs['props2search'] = srch
        super().__init__(**kwargs)

    def _get_connections(self, device):
        if not hasattr(self, 'conn_idcs'):
            try:
                if device.dev == 'EVG':
                    conn_names = LLTimeSearch.get_evg2fout_mapping()
                else:
                    conn_map = LLTimeSearch.get_fout2trigsrc_mapping()
                    conn_names = conn_map[device.device_name]
                conn_idcs = [int(dev[-1]) for dev in conn_names]
            except KeyError:
                conn_idcs, conn_names = list(), list()
            self.conn_idcs, self.conn_names = conn_idcs, conn_names

        return self.conn_idcs, self.conn_names

    def _createObjs(self, device, prop):
        idx_orig = device.idx.split('_')[0]
        idx = int(device.idx[-1])
        device = device.substitute(idx=idx_orig)
        conn_idcs, conn_names = self._get_connections(device)

        sp = rb = None
        if prop == 'name':
            sp = QLabel('OUT'+str(idx), self)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'connected':
            pvname = device.substitute(propty='Los-Mon')
            if idx in conn_idcs:
                sp = SiriusLedAlert(self, init_channel=pvname, bit=idx)
            else:
                sp = SiriusLedState(self, init_channel=pvname, bit=idx)
                sp.onColor = sp.DarkGreen
                sp.offColor = sp.LightGreen
        elif prop == 'tripdelay':
            pvname = device.substitute(propty='OUT'+str(idx)+'TripDelay-Mon')
            sp = SiriusLabel(self, pvname)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'position':
            pvname = device.substitute(propty='OUT'+str(idx)+'FramePos-Mon')
            sp = SiriusLabel(self, pvname)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'outdelay':
            pvname = device.substitute(propty='OUT'+str(idx)+'Delay-SP')
            sp = SiriusSpinbox(self, pvname)
            sp.limitsFromChannel = False
            sp.setMinimum(0)
            sp.setMaximum(2**31 - 1)
            pvname = device.substitute(propty='OUT'+str(idx)+'Delay-RB')
            rb = SiriusLabel(self, pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rxenbl':
            pvname = device.substitute(propty='RxEnbl-SP', field='B'+str(idx))
            sp = PyDMStateButton(self, pvname)
            pvname = device.substitute(propty='RxEnbl-RB')
            rb = SiriusLedState(self, init_channel=pvname, bit=idx)
        elif prop == 'connection':
            txtn = ''
            if idx in conn_idcs:
                out = _PVName(conn_names['OUT'+str(idx)])
                if device.dev == 'EVG':
                    link = list(LLTimeSearch.In2OutMap['Fout'])[0]
                else:
                    link = list(LLTimeSearch.In2OutMap[out.dev])[0]
                txtn = out+'\n'+link
            sp = QLabel(txtn, self, alignment=Qt.AlignCenter)

        if rb is None:
            return (sp, )
        return sp, rb


# ###################### Triggers ######################

class LLTriggerList(BaseList):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {
        'name': 4.5,
        'device': 14,
        'state': 5.8,
        'event': 4.8,
        'widthraw': 4.8,
        'width': 4.8,
        'polarity': 5,
        'pulses': 4.8,
        'delayraw': 4.8,
        'delay': 4.8,
        'timestamp': 3.2,
        'source': 6.5,
        'trigger': 4,
        'rf_delayraw': 4.8,
        'rf_delay': 6.5,
        'fine_delayraw': 4.8,
        'fine_delay': 6.5,
        'rf_delay_type': 6.5,
        'hl_trigger': 10,
        'dir': 4.5,
        'evtcnt': 5,
        'evtcntrst': 4,
        }
    _LABELS = {
        'name': 'Name',
        'device': 'Device',
        'state': 'State',
        'event': 'Event',
        'widthraw': 'Width',
        'width': 'Width [us]',
        'polarity': 'Polarity',
        'pulses': 'Nr Pulses',
        'delayraw': 'Delay',
        'delay': 'Delay [us]',
        'timestamp': 'Log',
        'source': 'Source',
        'trigger': 'Trigger',
        'rf_delayraw': 'RF Delay',
        'rf_delay': 'RF Delay [ns]',
        'fine_delayraw': 'Fine Delay',
        'fine_delay': 'Fine Delay [ps]',
        'rf_delay_type': 'RF Delay Type',
        'hl_trigger': 'HL Trigger',
        'dir': 'Direction',
        'evtcnt': 'Evt. Cnt.',
        'evtcntrst': 'Rst. Cnt.',
        }
    _ALL_PROPS = (
        'device', 'name', 'state', 'event', 'widthraw', 'width',
        'polarity', 'pulses', 'delayraw', 'delay', 'timestamp', 'source',
        'trigger', 'rf_delayraw', 'rf_delay', 'rf_delay_type', 'fine_delayraw',
        'fine_delay', 'hl_trigger', 'dir', 'evtcnt', 'evtcntrst')

    def __init__(self, **kwargs):
        srch = set(('device', 'name', 'polarity', 'source', 'dir'))
        kwargs['props2search'] = srch
        super().__init__(**kwargs)

    def _createObjs(self, device, prop):
        intlb = LLTimeSearch.get_channel_internal_trigger_pvname(device)
        outlb = LLTimeSearch.get_channel_output_port_pvname(device)
        sp = rb = None
        if prop == 'device':
            devt = outlb.dev
            if devt == 'EVR':
                devt = EVR
            elif devt == 'EVE':
                devt = EVE
            else:
                devt = AFC
            sp = QPushButton(outlb.device_name, self)
            sp.setAutoDefault(False)
            sp.setDefault(False)
            icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
            Win = create_window_from_widget(
                devt, title=outlb.device_name, icon=icon)
            connect_window(
                sp, Win, None, device=outlb.device_name, prefix=self.prefix)
        elif prop == 'name':
            sp = QLabel(outlb.propty, self)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'hl_trigger':
            trig = HLTimeSearch.get_hl_from_ll_triggers(device)
            sp = QLabel(trig, self)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'state':
            pvname = intlb.substitute(propty=intlb.propty+'State-Sel')
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+'State-Sts')
            rb = PyDMLed(self, init_channel=pvname)
        elif prop == 'event':
            pvname = intlb.substitute(propty=intlb.propty+'Evt-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.limitsFromChannel = False
            sp.setMinimum(0)
            sp.setMaximum(255)
            pvname = intlb.substitute(propty=intlb.propty+'Evt-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'widthraw':
            pvname = intlb.substitute(propty=intlb.propty+'WidthRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.limitsFromChannel = False
            sp.setMinimum(1)
            sp.setMaximum(2**31 - 1)
            pvname = intlb.substitute(propty=intlb.propty+'WidthRaw-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'width':
            pvname = intlb.substitute(propty=intlb.propty+'Width-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+'Width-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'polarity':
            pvname = intlb.substitute(propty=intlb.propty+'Polarity-Sel')
            sp = SiriusEnumComboBox(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+'Polarity-Sts')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'pulses':
            pvname = intlb.substitute(propty=intlb.propty+'NrPulses-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.limitsFromChannel = False
            sp.setMinimum(1)
            sp.setMaximum(2**31 - 1)
            pvname = intlb.substitute(propty=intlb.propty+'NrPulses-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'delayraw':
            pvname = intlb.substitute(propty=intlb.propty+'DelayRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.limitsFromChannel = False
            sp.setMinimum(0)
            sp.setMaximum(2**31 - 1)
            pvname = intlb.substitute(propty=intlb.propty+'DelayRaw-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'delay':
            pvname = intlb.substitute(propty=intlb.propty+'Delay-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+'Delay-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'timestamp':
            pvname = intlb.substitute(propty=intlb.propty+'Log-Sel')
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+'Log-Sts')
            rb = PyDMLed(self, init_channel=pvname)
        elif prop == 'source':
            pvname = outlb.substitute(propty=outlb.propty+'Src-Sel')
            sp = SiriusEnumComboBox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+'Src-Sts')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'trigger':
            pvname = outlb.substitute(propty=outlb.propty+'SrcTrig-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+'SrcTrig-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delayraw':
            pvname = outlb.substitute(propty=outlb.propty+'RFDelayRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+'RFDelayRaw-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delay':
            pvname = outlb.substitute(propty=outlb.propty+'RFDelay-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+'RFDelay-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delay_type':
            pvname = outlb.substitute(propty=outlb.propty+'RFDelayType-Sel')
            sp = SiriusEnumComboBox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+'RFDelayType-Sts')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'fine_delayraw':
            pvname = outlb.substitute(propty=outlb.propty+'FineDelayRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+'FineDelayRaw-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'fine_delay':
            pvname = outlb.substitute(propty=outlb.propty+'FineDelay-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+'FineDelay-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'dir':
            pvname = intlb.substitute(propty=intlb.propty+'Dir-Sel')
            sp = SiriusEnumComboBox(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+'Dir-Sts')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'evtcnt':
            pvname = intlb.substitute(propty=intlb.propty+'EvtCnt-Mon')
            sp = SiriusLabel(self, init_channel=pvname)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'evtcntrst':
            pvname = intlb.substitute(propty=intlb.propty+'EvtCntRst-Cmd')
            sp = PyDMPushButton(
                self, icon=qta.icon('fa5s.sync'), label='',
                init_channel=pvname, pressValue=1)
            sp.setObjectName('rst')
            sp.setStyleSheet(
                '#rst{min-width:25px; max-width:25px; icon-size:20px;}')
        if rb is None:
            return (sp, )
        return sp, rb


class EVREVEOTPList(LLTriggerList):
    """Template for control of Timing devices Internal Triggers."""

    _ALL_PROPS = (
        'name', 'state', 'event', 'widthraw', 'width', 'polarity', 'pulses',
        'delayraw', 'delay', 'evtcnt', 'evtcntrst', 'timestamp', 'hl_trigger')


class EVREVEOUTList(LLTriggerList):
    """Template for control of Timing Devices Output Channels."""

    _ALL_PROPS = (
        'name', 'source', 'trigger', 'rf_delayraw', 'rf_delay',
        'rf_delay_type', 'fine_delayraw', 'fine_delay', 'hl_trigger')


class AFCOUTList(LLTriggerList):
    """Template for control of Timing devices Internal Triggers."""

    _ALL_PROPS = (
        'name', 'state', 'event', 'source', 'widthraw', 'width', 'polarity',
        'pulses', 'delayraw', 'delay', 'dir', 'evtcnt', 'evtcntrst',
        'timestamp', 'hl_trigger')


# ###################### Digital Inputs ######################

class EVREVEDIList(BaseList):
    """Template for control of Timing devices Internal Triggers."""

    _MIN_WIDs = {
        'name': 3,
        'state': 5.8,
        'polarity': 5,
        'event': 4.8,
        'timestamp': 3.2,
    }
    _LABELS = {
        'name': 'Name',
        'state': 'State',
        'polarity': 'Polarity',
        'event': 'Event',
        'timestamp': 'Log',
    }
    _ALL_PROPS = ('name', 'state', 'polarity', 'event', 'timestamp')

    def __init__(self, **kwargs):
        srch = {'name', 'polarity'}
        kwargs['props2search'] = srch
        super().__init__(**kwargs)

    def _createObjs(self, device, prop):
        di_idx = device.idx
        device = device.substitute(idx='')
        sp = rb = None
        if prop == 'name':
            sp = QLabel('DI'+di_idx, self)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'state':
            pvname = device.substitute(propty='DIEnbl'+di_idx+'-Sel')
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = device.substitute(propty='DIEnbl'+di_idx+'-Sts')
            rb = PyDMLed(self, init_channel=pvname)
        elif prop == 'polarity':
            pvname = device.substitute(propty='DIPol'+di_idx+'-Sel')
            sp = SiriusEnumComboBox(self, init_channel=pvname)
            pvname = device.substitute(propty='DIPol'+di_idx+'-Sts')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'event':
            pvname = device.substitute(propty='DIEvent'+di_idx+'-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.limitsFromChannel = False
            sp.setMinimum(0)
            sp.setMaximum(255)
            pvname = device.substitute(propty='DIEvent'+di_idx+'-RB')
            rb = SiriusLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'timestamp':
            pvname = device.substitute(propty='DILog'+di_idx+'-Sel')
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = device.substitute(propty='DILog'+di_idx+'-Sts')
            rb = PyDMLed(self, init_channel=pvname)
        if rb is None:
            return (sp, )
        return sp, rb
