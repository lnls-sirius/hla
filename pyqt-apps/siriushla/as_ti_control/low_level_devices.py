"""."""
import numpy as _np

from qtpy.QtCore import Qt, Slot
from qtpy.QtGui import QColor, QBrush, QIntValidator
from qtpy.QtWidgets import QLabel, QPushButton, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QMenuBar, QSplitter, QTabWidget, QWidget, \
    QSizePolicy as QSzPol, QCheckBox, QDialog, QLineEdit
import qtawesome as qta
from pydm.widgets import PyDMLabel, PyDMPushButton, PyDMLineEdit, \
    PyDMWaveformPlot
from siriushla.widgets.signal_channel import SiriusConnectionSignal

from siriuspy.search import LLTimeSearch, HLTimeSearch
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys import csdev as _cstime

from ..widgets import PyDMLed, PyDMStateButton, SiriusLedState, \
    SiriusEnumComboBox as _MyComboBox, SiriusLedAlert, SiriusLabel, \
    SiriusSpinbox, SiriusDialog
from ..widgets.windows import create_window_from_widget
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

        self.configs_wid = QGroupBox('Configurations', self)
        mylayout.addWidget(self.configs_wid, 2, 0)
        self._setup_configs_wid()

        bucketlist_wid = BucketList(self, self.device, self.prefix)
        mylayout.addWidget(bucketlist_wid, 3, 0)

        self.status_wid = QGroupBox('Status', self)
        mylayout.addWidget(self.status_wid, 2, 1, 2, 1)
        self._setup_status_wid()

        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.setHandleWidth(20)
        mylayout.addWidget(splitter, 4, 0, 1, 2)

        obj_names = [self.device.substitute(propty=dev) for dev in
                     sorted(_cstime.Const.EvtLL._fields[1:])]
        self.events_wid = EventList(
            name='Events', parent=self, prefix=self.prefix,
            obj_names=obj_names)
        self.events_wid.setObjectName('events_wid')
        self.events_wid.setStyleSheet("events_wid{min-width:40em;}")
        splitter.addWidget(self.events_wid)

        obj_names = [self.device.substitute(propty=dev) for dev in
                     sorted(_cstime.Const.ClkLL._fields)]
        self.clocks_wid = ClockList(
            name='Clocks', parent=self, prefix=self.prefix,
            props={'name', 'mux_enbl', 'frequency'},
            obj_names=obj_names, has_search=True)
        splitter.addWidget(self.clocks_wid)

    def _setupmenus(self):
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu('&Downlinks')

        downs = LLTimeSearch.get_device_names({'dev': 'Fout'})
        link = list(LLTimeSearch.In2OutMap[downs[0].dev])[0]
        downs2 = list()
        for down in downs:
            out = LLTimeSearch.get_evg_channel(down.substitute(propty=link))
            downs2.append((out.propty, down.device_name))

        for out, down in sorted(downs2):
            action = menu.addAction(out + ' --> ' + down)
            icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
            Win = create_window_from_widget(FOUT, title=down, icon=icon)
            connect_window(action, Win, None, device=down, prefix=self.prefix)
        return main_menu

    def _setup_configs_wid(self):
        suplay = QVBoxLayout(self.configs_wid)
        configlayout = QHBoxLayout()
        suplay.addItem(configlayout)
        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addStretch()
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        pvname = self.get_pvname(propty='DevEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='DevEnbl-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        layrow.addWidget(self._create_prop_widget(
                        'Dev Enable', self.configs_wid, (sp, rb)))

        pvname = self.get_pvname(propty='RFDiv-SP')
        sp = SiriusSpinbox(self, init_channel=pvname)
        sp.showStepExponent = False
        pvname = self.get_pvname(propty='RFDiv-RB')
        rb = PyDMLabel(self, init_channel=pvname)
        layrow.addWidget(self._create_prop_widget(
                        'RF Divisor', self.configs_wid, (sp, rb)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

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
        layrow.addWidget(self._create_prop_widget(
                        'RF Status', self.configs_wid, (sp, rb)))

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
        layrow.addWidget(self._create_prop_widget(
                        'Update Evts', self.configs_wid, (sp, rb)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        pvname = self.get_pvname(propty='ACEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='ACEnbl-Sts')
        rb = SiriusLedState(self, init_channel=pvname)
        layrow.addWidget(self._create_prop_widget(
                        'AC Enable', self.configs_wid, (sp, rb)))

        pvname = self.get_pvname(propty='ACStatus-Mon')
        mon = SiriusLedState(self, init_channel=pvname)
        mon.offColor = rb.Red
        layrow.addWidget(self._create_prop_widget(
                        'AC Status', self.configs_wid, (mon,)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        pvname = self.get_pvname(propty='InjRate-SP')
        sp = SiriusSpinbox(self, init_channel=pvname)
        sp.showStepExponent = False
        pvname = self.get_pvname(propty='InjRate-RB')
        rb = PyDMLabel(self, init_channel=pvname)
        layrow.addWidget(self._create_prop_widget(
                        'Pulse Rate [Hz]', self.configs_wid, (sp, rb)))

        pvname = self.get_pvname(propty='ACSrc-Sel')
        sp = _MyComboBox(self, init_channel=pvname)
        pvname = self.get_pvname(propty='ACSrc-Sts')
        rb = PyDMLabel(self, init_channel=pvname)
        layrow.addWidget(self._create_prop_widget(
                        'AC Source', self.configs_wid, (sp, rb)))

        layrow = QVBoxLayout()
        layrow.setSpacing(30)
        configlayout.addLayout(layrow)
        configlayout.addStretch()

        pvname = self.get_pvname(propty='ContinuousEvt-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='ContinuousEvt-Sts')
        rb = SiriusLedState(self, init_channel=pvname)
        layrow.addWidget(self._create_prop_widget(
                        'Continuous', self.configs_wid, (sp, rb)))

        pvname = self.get_pvname(propty='InjectionEvt-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='InjectionEvt-Sts')
        rb = SiriusLedState(self, init_channel=pvname)
        layrow.addWidget(self._create_prop_widget(
                        'Injection', self.configs_wid, (sp, rb)))

    def _setup_status_wid(self):
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(5)

        pvname = self.get_pvname(propty='STATEMACHINE')
        rb1 = PyDMLabel(self.status_wid, init_channel=pvname)
        pvname = self.get_pvname(propty='DevStatus-Mon')
        rb2 = PyDMLabel(self.status_wid, init_channel=pvname)
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
        pydmlab1 = PyDMLabel(self.status_wid, init_channel=pvname)
        pydmlab1.setStyleSheet('min-width:5em;')
        pydmlab1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pvname = self.get_pvname(propty='InjCount-Mon')
        pydmlab2 = PyDMLabel(self.status_wid, init_channel=pvname)
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
        pydmlab1 = PyDMLabel(self.status_wid, init_channel=pvname)
        pydmlab1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pvname = self.get_pvname(propty='SeqCount-SP')
        pydmlab2 = PyDMLabel(self.status_wid, init_channel=pvname)
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
        rb = PyDMLabel(self, init_channel=pvname)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 2, 0)

        lb = QLabel("<b>Network</b>")
        pvname = self.get_pvname(propty='Network-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 2, 1)

        lb = QLabel("<b>RF Sts</b>")
        pvname = self.get_pvname(propty='RFStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 2, 2)

        wids = list()
        conn = LLTimeSearch.get_connections_from_evg()
        conn = {int(dev.propty[-1]) for dev in conn if dev.dev == 'EVG'}
        for i in range(8):
            pvname = self.get_pvname(propty='Los-Mon')
            if i in conn:
                rb = SiriusLedAlert(self, init_channel=pvname, bit=i)
            else:
                rb = SiriusLedState(self, init_channel=pvname, bit=i)
                rb.onColor = rb.DarkGreen
                rb.offColor = rb.LightGreen
            wids.append(rb)
        gb = self._create_small_GB(
            'Down Connection', self.status_wid, wids, align_ver=False)
        status_layout.addWidget(gb, 3, 0, 1, 3)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(wid, Qt.AlignCenter)
        return gb

    def _create_prop_widget(self, name, parent, wids, align_ver=True):
        pwid = QWidget(parent)
        vbl = QVBoxLayout(pwid)
        lab = QLabel(name)
        lab.setAlignment(Qt.AlignCenter)
        vbl.addWidget(lab)
        hbl = QHBoxLayout()
        vbl.addItem(hbl)
        for wid in wids:
            wid.setParent(pwid)
            hbl.addWidget(wid)
            hbl.setAlignment(wid, Qt.AlignCenter)
        return pwid


class BucketListGraph(BaseWidget):
    """Bucket List Graph."""

    def __init__(self, parent=None, device='', prefix=''):
        if not device:
            device = LLTimeSearch.get_evg_name()
        super().__init__(parent, device, prefix)
        self._setupUi()

    def _setupUi(self):
        # Graph
        self.graph = PyDMWaveformPlot(self)
        self.graph.setBackgroundColor(QColor(255, 255, 255))
        self.graph.maxRedrawRate = 2
        self.graph.mouseEnabledX = True
        self.graph.setShowXGrid(True)
        self.graph.setShowYGrid(True)
        self.graph.setAutoRangeX(False)
        self.graph.setMinYRange(-0.1)
        self.graph.setMaxYRange(1.1)
        self.graph.plotItem.showButtons()
        self.graph.setAxisColor(QColor(0, 0, 0))

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

        lay = QGridLayout(self)
        lay.addWidget(self.graph, 0, 0, 3, 1)
        lay.addWidget(self.show_sp, 0, 1)
        lay.addWidget(self.show_rb, 1, 1)
        lay.addWidget(self.show_mn, 2, 1)

        self._ch_sp = SiriusConnectionSignal(
            self.get_pvname(propty='BucketList-SP'))
        self._ch_sp.new_value_signal[_np.ndarray].connect(
            self._update_curves)
        self._ch_rb = SiriusConnectionSignal(
            self.get_pvname(propty='BucketList-RB'))
        self._ch_rb.new_value_signal[_np.ndarray].connect(
            self._update_curves)
        self._ch_mn = SiriusConnectionSignal(
            self.get_pvname(propty='BucketList-Mon'))
        self._ch_mn.new_value_signal[_np.ndarray].connect(
            self._update_curves)

    @Slot(_np.ndarray)
    def _update_curves(self, new_array):
        for k in self._curves:
            if k in self.sender().address:
                curve = self._curves[k]
                break

        org_bunch = _np.arange(1, 864)
        org_curve = _np.zeros(864)
        org_curve[new_array-1] = 1

        new_bunch = _np.linspace(1, 864, 10000)
        new_bunch_indices = _np.searchsorted(
            _np.nextafter(org_bunch, -_np.inf), new_bunch, side='left')
        new_bunch_indices = new_bunch_indices.clip(
            1, len(org_bunch)).astype(_np.intp)
        new_curve = org_curve[new_bunch_indices-1]

        curve.receiveXWaveform(new_bunch)
        curve.receiveYWaveform(new_curve)


class BucketList(BaseWidget):

    def __init__(self, parent=None, device='', prefix='', min_size=38,
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

        tm = 'min-width:{0:d}em; max-width:{0:d}em; max-height:1.15em;'
        pvname = self.get_pvname("BucketList-SP")
        sp = BucketListLineEdit(wid, init_channel=pvname)
        self.bucket_ledit = sp
        sp.setStyleSheet(tm.format(self._min_size-1))
        sp.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lab = QLabel('SP : ', wid)
        pushbtn = QPushButton(wid)
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
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lab = QLabel('RB : ', wid)
        lay_rb = QHBoxLayout()
        lay_rb.addWidget(lab)
        lay_rb.addWidget(rb)
        pvname = self.get_pvname("BucketList-Mon")
        mn = BucketListLabel(wid, init_channel=pvname)
        mn.setStyleSheet(tm.format(self._min_size))
        mn.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        lab = QLabel('Mon: ', wid)
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

        rb = PyDMLabel(wid, init_channel=self.get_pvname("BucketListLen-Mon"))
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
        sp.showStepExponent = False
        pvname = self.get_pvname("RepeatBucketList-RB")
        rb = PyDMLabel(wid, init_channel=pvname)
        rb.setStyleSheet("min-width:2.5em; max-height:1.15em;")
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
        inj_prefix = 'AS-Glob:AP-InjCtrl:'

        wid = SiriusDialog(self)
        wid.setFocus(True)
        wid.setFocusPolicy(Qt.StrongFocus)
        wid.setObjectName('ASApp')

        self._sb_start = SiriusSpinbox(wid, inj_prefix+'BucketListStart-SP')
        self._sb_start.setAlignment(Qt.AlignCenter)
        self._sb_start.setStyleSheet('max-width:5em;')
        self._sb_start.showStepExponent = False
        self._lb_start = SiriusLabel(wid, inj_prefix+'BucketListStart-RB')

        self._sb_stop = SiriusSpinbox(wid, inj_prefix+'BucketListStop-SP')
        self._sb_stop.setAlignment(Qt.AlignCenter)
        self._sb_stop.setStyleSheet('max-width:5em;')
        self._sb_stop.showStepExponent = False
        self._lb_stop = SiriusLabel(wid, inj_prefix+'BucketListStop-RB')

        self._sb_step = SiriusSpinbox(wid, inj_prefix+'BucketListStep-SP')
        self._sb_step.setAlignment(Qt.AlignCenter)
        self._sb_step.setStyleSheet('max-width:5em;')
        self._sb_step.showStepExponent = False
        self._lb_step = SiriusLabel(wid, inj_prefix+'BucketListStep-RB')

        self._pb_ok = QPushButton('Ok', wid)
        self._pb_ok.setDefault(True)
        self._pb_ok.clicked.connect(wid.accept)

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
        lay.addWidget(self._pb_ok, 3, 1)

        return wid


class EventList(BaseList):
    """Template for control of Events."""

    _MIN_WIDs = {
        'ext_trig': 3, 'mode': 6.6, 'delay_type': 4.2, 'delay': 5.2,
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
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'Mode-Sts')
            rb = PyDMLabel(self, init_channel=pvname)
        elif prop == 'delay_type':
            pvname = device.substitute(propty=device.propty+'DelayType-Sel')
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'DelayType-Sts')
            rb = PyDMLabel(self, init_channel=pvname)
        elif prop == 'delay':
            pvname = device.substitute(propty=device.propty+'Delay-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = device.substitute(propty=device.propty+'Delay-RB')
            rb = PyDMLabel(self, init_channel=pvname)
        elif prop == 'delayraw':
            pvname = device.substitute(propty=device.propty+'DelayRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = device.substitute(propty=device.propty+'DelayRaw-RB')
            rb = PyDMLabel(self, init_channel=pvname)
        elif prop == 'description':
            pvname = device.substitute(propty=device.propty+'Desc-SP')
            sp = PyDMLineEdit(self, init_channel=pvname)
            pvname = device.substitute(propty=device.propty+'Desc-RB')
            rb = PyDMLabel(self, init_channel=pvname)
        elif prop == 'code':
            pvname = device.substitute(propty=device.propty+'Code-Mon')
            sp = PyDMLabel(self, init_channel=pvname)
            sp.setAlignment(Qt.AlignCenter)
        if rb is None:
            return (sp, )
        return (sp, rb)


class ClockList(BaseList):
    """Template for control of Low Level Clocks."""

    _MIN_WIDs = {
        'name': 3.8,
        'frequency': 4.8,
        'mux_div': 4.8,
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
            sp.showStepExponent = False
            pvname = device.substitute(propty=device.propty+'Freq-RB')
            rb = PyDMLabel(self, init_channel=pvname)
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
            sp.showStepExponent = False
            pvname = device.substitute(propty=device.propty+'MuxDiv-RB')
            rb = PyDMLabel(self, init_channel=pvname)
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
        self.my_layout.setVerticalSpacing(20)

        self.my_layout.addWidget(self._setupmenus(), 0, 0)

        lab = QLabel('<h1>' + self.device.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 2, 0)
        self._setup_status_wid()

    def _setupmenus(self):
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu('&Downlinks')

        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        mapping = LLTimeSearch.get_fout2trigsrc_mapping()
        downs = mapping[self.device.device_name]
        downs = sorted([(ou, dwn) for ou, dwn in downs.items()])
        for out, dwn in downs:
            dev, down = dwn.dev, dwn.device_name
            if dev == 'EVR':
                devt = EVR
            elif dev == 'EVE':
                devt = EVE
            else:
                devt = AFC
            action = menu.addAction(out + ' --> ' + down)
            Win = create_window_from_widget(devt, title=down, icon=icon)
            connect_window(action, Win, None, device=down, prefix=self.prefix)

        menu = main_menu.addMenu('&Uplink')
        link = list(LLTimeSearch.In2OutMap[self.device.dev])[0]
        evg = LLTimeSearch.get_evg_channel(
            self.device.device_name.substitute(propty=link))
        action = menu.addAction(evg)
        Win = create_window_from_widget(EVG, title=evg.device_name, icon=icon)
        connect_window(
            action, Win, None, device=evg.device_name, prefix=self.prefix)
        return main_menu

    def _setup_status_wid(self):
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(30)

        pvname = self.get_pvname(propty='DevEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname(propty='DevEnbl-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        gb = self._create_small_GB(
            'Enabled', self.status_wid, (sp, rb), align_ver=False
            )
        status_layout.addWidget(gb, 0, 0)

        lb = QLabel("<b>Alive</b>")
        rb = PyDMLabel(self, init_channel=self.get_pvname(propty='Alive-Mon'))
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 1)

        lb = QLabel("<b>Network</b>")
        pvname = self.get_pvname(propty='Network-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 2)

        lb = QLabel("<b>UP Link</b>")
        pvname = self.get_pvname(propty='LinkStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 3)

        wids = list()
        conn = LLTimeSearch.get_fout2trigsrc_mapping()[self.device.device_name]
        conn = {int(dev[-1]) for dev in conn}
        for i in range(8):
            pvname = self.get_pvname(propty='Los-Mon')
            if i in conn:
                rb = SiriusLedAlert(self, init_channel=pvname, bit=i)
            else:
                rb = SiriusLedState(self, init_channel=pvname, bit=i)
                rb.onColor = rb.DarkGreen
                rb.offColor = rb.LightGreen
            wids.append(rb)
        gb = self._create_small_GB(
            'Down Connection', self.status_wid, wids, align_ver=False)
        status_layout.addWidget(gb, 1, 0, 1, 4)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(wid, Qt.AlignCenter)
        return gb


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

        self.my_layout.addWidget(self._setupmenus(), 0, 0)

        lab = QLabel('<h1>' + self.device.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 2, 0)
        self._setup_status_wid()

        tab = QTabWidget(self)
        self.my_layout.addWidget(tab, 3, 0)

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
        self.fmcs_wid.setStyleSheet("""#fmcs_wid{min-width:60em;}""")
        tab.addTab(self.fmcs_wid, 'FMC Outputs')

        obj_names = sorted([out for out in set_ if out.startswith('CRT')])
        obj_names = [self.device.substitute(propty_name=o) for o in obj_names]
        self.crts_wid = AFCOUTList(
            name='', parent=self, props=props,
            prefix=self.prefix, obj_names=obj_names)
        self.crts_wid.setObjectName('crts_wid')
        self.crts_wid.setStyleSheet("""#crts_wid{min-width:60em;}""")
        tab.addTab(self.crts_wid, 'CRT Outputs')

    def _setupmenus(self):
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu('&Uplink')

        fout = LLTimeSearch.get_fout_channel(
            self.device.substitute(propty='CRT0'))
        action = menu.addAction(fout)
        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        Win = create_window_from_widget(
            FOUT, title=fout.device_name, icon=icon)
        connect_window(
            action, Win, None, device=fout.device_name, prefix=self.prefix)
        return main_menu

    def _setup_status_wid(self):
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(30)

        pvname = self.get_pvname('DevEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname('DevEnbl-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        gb = self._create_small_GB(
            'Enabled', self.status_wid, (sp, rb), align_ver=False)
        status_layout.addWidget(gb, 0, 0)

        lb = QLabel("<b>Alive</b>")
        pvname = self.get_pvname('Alive-Mon')
        rb = PyDMLabel(self, init_channel=pvname)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 1)

        lb = QLabel("<b>Locked</b>")
        pvname = self.get_pvname('RefClkLocked-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        rb.offColor, rb.onColor = rb.onColor, rb.offColor
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 2)

        lb = QLabel("<b>UP Link</b>")
        pvname = self.get_pvname('LinkStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        rb.offColor, rb.onColor = rb.onColor, rb.offColor
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 3)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(Qt.AlignCenter)
        return gb


class _EVR_EVE(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, device='', prefix=''):
        """Initialize object."""
        super().__init__(parent, device, prefix)
        self.device_type = _PVName(device).dev
        self.setupui()
        self.setObjectName('ASApp')

    def setupui(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)

        self.my_layout.addWidget(self.setupmenus(), 0, 0, 1, 2)

        lab = QLabel('<h1>' + self.device.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 1, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 2, 0, 1, 2)
        self._setup_status_wid()

        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.setHandleWidth(20)
        self.my_layout.addWidget(splitter, 3, 0, 1, 2)

        props = {
            'name', 'state', 'event', 'widthraw', 'polarity', 'pulses',
            'delayraw', 'timestamp'}
        obj_names = ['OTP{0:02d}'.format(i) for i in range(24)]
        obj_names = [self.device.substitute(propty=o) for o in obj_names]
        self.otps_wid = OTPList(
            name='Internal Trigger (OTP)', parent=self, prefix=self.prefix,
            props=props, obj_names=obj_names)
        self.otps_wid.setObjectName('otps_wid')
        self.otps_wid.setStyleSheet("""#otps_wid{min-width:60em;}""")
        splitter.addWidget(self.otps_wid)

        props = {
            'name', 'source', 'trigger', 'rf_delayraw', 'rf_delay_type',
            'fine_delayraw'}
        obj_names = ['OUT{0:d}'.format(i) for i in range(8)]
        obj_names = [self.device.substitute(propty=o) for o in obj_names]
        self.outs_wid = OUTList(
            name='OUT', parent=self, prefix=self.prefix,
            props=props, obj_names=obj_names)
        self.outs_wid.setObjectName('outs_wid')
        self.outs_wid.setStyleSheet("""#outs_wid{min-width:44em;}""")
        splitter.addWidget(self.outs_wid)

    def setupmenus(self):
        main_menu = QMenuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu('&Uplink')

        fout = LLTimeSearch.get_fout_channel(
            self.device.substitute(propty='OTP0'))
        action = menu.addAction(fout)
        icon = qta.icon('mdi.timer', color=get_appropriate_color('AS'))
        Win = create_window_from_widget(
            FOUT, title=fout.device_name, icon=icon)
        connect_window(
            action, Win, None, device=fout.device_name, prefix=self.prefix)
        return main_menu

    def _setup_status_wid(self):
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(30)

        pvname = self.get_pvname('DevEnbl-Sel')
        sp = PyDMStateButton(self, init_channel=pvname)
        pvname = self.get_pvname('DevEnbl-Sts')
        rb = PyDMLed(self, init_channel=pvname)
        gb = self._create_small_GB(
            'Enabled', self.status_wid, (sp, rb), align_ver=False)
        status_layout.addWidget(gb, 0, 0)

        lb = QLabel("<b>Alive</b>")
        pvname = self.get_pvname('Alive-Mon')
        rb = PyDMLabel(self, init_channel=pvname)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 1)

        lb = QLabel("<b>Network</b>")
        pvname = self.get_pvname('Network-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        rb.offColor, rb.onColor = rb.onColor, rb.offColor
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 2)

        lb = QLabel("<b>UP Link</b>")
        pvname = self.get_pvname('LinkStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 3)

        lb = QLabel("<b>Interlock Status</b>")
        pvname = self.get_pvname('IntlkStatus-Mon')
        rb = SiriusLedAlert(self, init_channel=pvname)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 4)

        lb = QLabel("<b>Interlock Enabled</b>")
        pvname = self.get_pvname('IntlkEnbl-Mon')
        rb = SiriusLedState(self, init_channel=pvname)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 0, 5)

        if self.device_type == 'EVR':
            wids = list()
            conn = LLTimeSearch.get_connections_from_evg()
            conn = {
                dev.propty for dev in conn
                if dev.device_name == self.device.device_name}
            conn = {int(p[-1]) for p in conn if p.startswith('OUT')}
            for i in range(8):
                pvname = self.get_pvname('Los-Mon')
                if i in conn:
                    rb = SiriusLedAlert(self, init_channel=pvname, bit=i)
                else:
                    rb = SiriusLedState(self, init_channel=pvname, bit=i)
                    rb.onColor = rb.DarkGreen
                    rb.offColor = rb.LightGreen
                wids.append(rb)
            gb = self._create_small_GB(
                'Down Connection', self.status_wid, wids, align_ver=False)
        else:
            sp = _MyComboBox(self, init_channel=self.get_pvname('RFOut-Sel'))
            rb = PyDMLabel(self, init_channel=self.get_pvname('RFOut-Sts'))
            gb = self._create_small_GB('RF Output', self.status_wid, (sp, rb))
        status_layout.addWidget(gb, 0, 6)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(wid, Qt.AlignCenter)
        return gb


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


# ###################### Triggers ######################
class LLTriggerList(BaseList):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {
        'name': 3.2,
        'device': 12,
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
        'dir': 4,
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
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+'Evt-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'widthraw':
            pvname = intlb.substitute(propty=intlb.propty+'WidthRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+'WidthRaw-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'width':
            pvname = intlb.substitute(propty=intlb.propty+'Width-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+'Width-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'polarity':
            pvname = intlb.substitute(propty=intlb.propty+'Polarity-Sel')
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+'Polarity-Sts')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'pulses':
            pvname = intlb.substitute(propty=intlb.propty+'NrPulses-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+'NrPulses-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'delayraw':
            pvname = intlb.substitute(propty=intlb.propty+'DelayRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+'DelayRaw-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'delay':
            pvname = intlb.substitute(propty=intlb.propty+'Delay-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+'Delay-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'timestamp':
            pvname = intlb.substitute(propty=intlb.propty+'Log-Sel')
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+'Log-Sts')
            rb = PyDMLed(self, init_channel=pvname)
        elif prop == 'source':
            pvname = outlb.substitute(propty=outlb.propty+'Src-Sel')
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+'Src-Sts')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'trigger':
            pvname = outlb.substitute(propty=outlb.propty+'SrcTrig-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+'SrcTrig-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delayraw':
            pvname = outlb.substitute(propty=outlb.propty+'RFDelayRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+'RFDelayRaw-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delay':
            pvname = outlb.substitute(propty=outlb.propty+'RFDelay-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+'RFDelay-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delay_type':
            pvname = outlb.substitute(propty=outlb.propty+'RFDelayType-Sel')
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+'RFDelayType-Sts')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'fine_delayraw':
            pvname = outlb.substitute(propty=outlb.propty+'FineDelayRaw-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+'FineDelayRaw-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'fine_delay':
            pvname = outlb.substitute(propty=outlb.propty+'FineDelay-SP')
            sp = SiriusSpinbox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+'FineDelay-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'dir':
            pvname = intlb.substitute(propty=intlb.propty+'Dir-Sel')
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+'Dir-Sts')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'evtcnt':
            pvname = intlb.substitute(propty=intlb.propty+'EvtCnt-Mon')
            sp = PyDMLabel(self, init_channel=pvname)
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


class OTPList(LLTriggerList):
    """Template for control of Timing devices Internal Triggers."""

    _ALL_PROPS = (
        'name', 'state', 'event', 'widthraw', 'width', 'polarity', 'pulses',
        'delayraw', 'delay', 'evtcnt', 'evtcntrst', 'timestamp', 'hl_trigger')


class OUTList(LLTriggerList):
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
    _MIN_WIDs = LLTriggerList._MIN_WIDs
    _MIN_WIDs['name'] = 3.7
